"""
Sistema de Análise de CMV - ARV Industrial
Aplicação Principal Streamlit
"""

import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Análise de CMV - ARV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para os cards
st.markdown("""
<style>
    .os-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }
    .os-card-estourado {
        background-color: rgba(231, 76, 60, 0.2);
        border-left-color: #e74c3c;
    }
    .os-card-critico {
        background-color: rgba(230, 126, 34, 0.2);
        border-left-color: #e67e22;
    }
    .os-card-atencao {
        background-color: rgba(241, 196, 15, 0.2);
        border-left-color: #f1c40f;
    }
    .os-card-ok {
        background-color: rgba(39, 174, 96, 0.2);
        border-left-color: #27ae60;
    }
    .os-card-cinza {
        background-color: rgba(149, 165, 166, 0.2);
        border-left-color: #95a5a6;
    }
    .os-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .os-metric {
        display: inline-block;
        margin-right: 20px;
        margin-bottom: 5px;
    }
    .os-metric-label {
        font-size: 11px;
        color: #888;
        text-transform: uppercase;
    }
    .os-metric-value {
        font-size: 14px;
        font-weight: bold;
    }
    .os-exec-bar {
        height: 8px;
        background-color: rgba(255,255,255,0.2);
        border-radius: 4px;
        margin-top: 10px;
        overflow: hidden;
    }
    .os-exec-fill {
        height: 100%;
        border-radius: 4px;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        float: right;
    }
    .badge-estourado { background-color: #e74c3c; color: white; }
    .badge-critico { background-color: #e67e22; color: white; }
    .badge-atencao { background-color: #f1c40f; color: black; }
    .badge-ok { background-color: #27ae60; color: white; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES DE PROCESSAMENTO
# =====================================================

def processar_planilha(uploaded_file):
    """Pipeline de processamento da planilha"""
    df_raw = pd.read_excel(uploaded_file, header=None)

    header_row = None
    for idx in range(min(10, len(df_raw))):
        first_cell = str(df_raw.iloc[idx, 0]).strip().upper()
        if first_cell in ['O_S', 'OS', 'O.S.', 'O.S']:
            header_row = idx
            break

    if header_row is None:
        st.error("❌ Não foi possível identificar o cabeçalho.")
        return None

    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = ['OS', 'FAMILIA', 'PREVISTO', 'REALIZADO', 'SALDO']
    df = df.reset_index(drop=True)

    df = df[df['OS'].notna()].copy()
    df = df[~df['OS'].astype(str).str.upper().isin(['O_S', 'OS', 'O.S.', 'O.S'])].copy()

    for col in ['PREVISTO', 'REALIZADO', 'SALDO']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['OS'] = df['OS'].astype(str).str.strip()
    df['FAMILIA'] = df['FAMILIA'].astype(str).str.strip()

    return df

def agregar_por_os(df):
    """Agrega dados por OS"""
    return df.groupby('OS').agg({
        'PREVISTO': 'sum',
        'REALIZADO': 'sum',
        'SALDO': 'sum'
    }).reset_index()

def agregar_por_familia(df):
    """Agrega dados por família"""
    return df.groupby('FAMILIA').agg({
        'PREVISTO': 'sum',
        'REALIZADO': 'sum',
        'SALDO': 'sum'
    }).reset_index()

def classificar_risco(row):
    """Classifica o risco baseado na execução"""
    if row['PREVISTO'] == 0:
        if row['REALIZADO'] > 0:
            return 'CRÍTICO'
        return 'SEM ORÇAMENTO'

    exec_pct = (row['REALIZADO'] / row['PREVISTO']) * 100

    if exec_pct > 100:
        return 'ESTOURADO'
    elif exec_pct >= 90:
        return 'CRÍTICO'
    elif exec_pct >= 70:
        return 'ATENÇÃO'
    else:
        return 'OK'

def formatar_moeda(valor):
    """Formata valor para padrão brasileiro"""
    if pd.isna(valor):
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_moeda_compacto(valor):
    """Formata valor de forma compacta"""
    if pd.isna(valor) or valor == 0:
        return "R$ 0"
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f}M"
    if abs(valor) >= 1_000:
        return f"R$ {valor/1_000:.0f}K"
    return f"R$ {valor:.0f}"

def criar_card_os(os_data):
    """Cria HTML do card de uma OS"""
    os_num = os_data['OS']
    previsto = os_data['PREVISTO']
    realizado = os_data['REALIZADO']
    saldo = os_data['SALDO']
    exec_pct = os_data['EXECUCAO_%']
    risco = os_data['RISCO']

    # Classe CSS baseada no risco
    css_class = {
        'ESTOURADO': 'os-card-estourado',
        'CRÍTICO': 'os-card-critico',
        'ATENÇÃO': 'os-card-atencao',
        'OK': 'os-card-ok',
        'SEM ORÇAMENTO': 'os-card-cinza'
    }.get(risco, 'os-card-cinza')

    badge_class = {
        'ESTOURADO': 'badge-estourado',
        'CRÍTICO': 'badge-critico',
        'ATENÇÃO': 'badge-atencao',
        'OK': 'badge-ok'
    }.get(risco, 'badge-ok')

    # Cor da barra de execução
    bar_color = {
        'ESTOURADO': '#e74c3c',
        'CRÍTICO': '#e67e22',
        'ATENÇÃO': '#f1c40f',
        'OK': '#27ae60'
    }.get(risco, '#95a5a6')

    # Limitar barra a 100% visualmente
    bar_width = min(exec_pct, 100)

    # Saldo formatado com cor
    saldo_color = '#e74c3c' if saldo < 0 else '#27ae60'

    html = f"""
    <div class="os-card {css_class}">
        <div class="os-title">
            OS {os_num}
            <span class="status-badge {badge_class}">{risco}</span>
        </div>
        <div>
            <div class="os-metric">
                <div class="os-metric-label">Previsto</div>
                <div class="os-metric-value">{formatar_moeda(previsto)}</div>
            </div>
            <div class="os-metric">
                <div class="os-metric-label">Realizado</div>
                <div class="os-metric-value">{formatar_moeda(realizado)}</div>
            </div>
            <div class="os-metric">
                <div class="os-metric-label">Saldo</div>
                <div class="os-metric-value" style="color: {saldo_color}">{formatar_moeda(saldo)}</div>
            </div>
            <div class="os-metric">
                <div class="os-metric-label">Execução</div>
                <div class="os-metric-value">{exec_pct:.1f}%</div>
            </div>
        </div>
        <div class="os-exec-bar">
            <div class="os-exec-fill" style="width: {bar_width}%; background-color: {bar_color}"></div>
        </div>
    </div>
    """
    return html

def criar_excel_download(df):
    """Cria arquivo Excel para download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

# =====================================================
# INTERFACE PRINCIPAL
# =====================================================

st.title("📊 Análise de CMV - ARV Industrial")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    uploaded_file = st.file_uploader(
        "Carregar Planilha CMV",
        type=["xlsx", "xls"],
        help="Estrutura: O_S | FAMILIA | PREVISTO | REALIZADO | SALDO"
    )
    st.markdown("---")

if uploaded_file is not None:
    with st.spinner("Processando..."):
        df = processar_planilha(uploaded_file)

    if df is not None:
        # Filtros na sidebar
        with st.sidebar:
            st.header("🔍 Filtros")

            # Filtro por status/risco
            filtro_status = st.multiselect(
                "Status",
                options=['ESTOURADO', 'CRÍTICO', 'ATENÇÃO', 'OK'],
                default=None,
                help="Filtrar por classificação de risco"
            )

            os_list = sorted(df['OS'].unique().tolist())
            os_selecionadas = st.multiselect("Ordem de Serviço", options=os_list)

            familias_list = sorted(df['FAMILIA'].unique().tolist())
            familias_selecionadas = st.multiselect("Família", options=familias_list)

        # Aplicar filtros básicos
        df_filtrado = df.copy()
        if os_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['OS'].isin(os_selecionadas)]
        if familias_selecionadas:
            df_filtrado = df_filtrado[df_filtrado['FAMILIA'].isin(familias_selecionadas)]

        # Agregar por OS
        df_os = agregar_por_os(df_filtrado)
        df_os['EXECUCAO_%'] = (df_os['REALIZADO'] / df_os['PREVISTO'].replace(0, float('nan')) * 100).fillna(0)
        df_os['RISCO'] = df_os.apply(classificar_risco, axis=1)

        # Aplicar filtro de status
        if filtro_status:
            df_os = df_os[df_os['RISCO'].isin(filtro_status)]

        # Ordenar por execução (maior primeiro)
        df_os = df_os.sort_values('EXECUCAO_%', ascending=False)

        # Contadores por risco (do total, não filtrado)
        df_os_total = agregar_por_os(df)
        df_os_total['EXECUCAO_%'] = (df_os_total['REALIZADO'] / df_os_total['PREVISTO'].replace(0, float('nan')) * 100).fillna(0)
        df_os_total['RISCO'] = df_os_total.apply(classificar_risco, axis=1)

        n_estourado = len(df_os_total[df_os_total['RISCO'] == 'ESTOURADO'])
        n_critico = len(df_os_total[df_os_total['RISCO'] == 'CRÍTICO'])
        n_atencao = len(df_os_total[df_os_total['RISCO'] == 'ATENÇÃO'])
        n_ok = len(df_os_total[df_os_total['RISCO'] == 'OK'])

        # ===== PAINEL DE RESUMO =====
        st.markdown("---")

        # Métricas principais
        total_previsto = df_os['PREVISTO'].sum()
        total_realizado = df_os['REALIZADO'].sum()
        total_saldo = df_os['SALDO'].sum()
        exec_geral = (total_realizado / total_previsto * 100) if total_previsto > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Previsto", formatar_moeda_compacto(total_previsto))
        with col2:
            st.metric("💸 Realizado", formatar_moeda_compacto(total_realizado))
        with col3:
            st.metric("📊 Saldo", formatar_moeda_compacto(total_saldo),
                     delta="Negativo!" if total_saldo < 0 else None,
                     delta_color="inverse" if total_saldo < 0 else "normal")
        with col4:
            st.metric("📈 Execução", f"{exec_geral:.1f}%")

        # Status cards
        st.markdown("### 🚦 Resumo por Status")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e74c3c, #c0392b); padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 36px;">{n_estourado}</h1>
                <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">ESTOURADAS</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e67e22, #d35400); padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 36px;">{n_critico}</h1>
                <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">CRÍTICAS</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f1c40f, #f39c12); padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: #333; margin: 0; font-size: 36px;">{n_atencao}</h1>
                <p style="color: #333; margin: 5px 0 0 0; font-weight: bold;">ATENÇÃO</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #27ae60, #1e8449); padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 36px;">{n_ok}</h1>
                <p style="color: white; margin: 5px 0 0 0; font-weight: bold;">OK</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ===== ABAS =====
        tab1, tab2, tab3 = st.tabs(["🎯 OSs por Execução", "📦 Por Família", "📋 Exportar"])

        # ===== ABA 1: OSs =====
        with tab1:
            st.markdown(f"### 📋 Lista de OSs ({len(df_os)} projetos)")
            st.caption("Ordenado por % de execução (maior para menor)")

            if len(df_os) == 0:
                st.warning("Nenhuma OS encontrada com os filtros selecionados.")
            else:
                # Renderizar cards em colunas
                # 2 cards por linha
                for i in range(0, len(df_os), 2):
                    col1, col2 = st.columns(2)

                    with col1:
                        if i < len(df_os):
                            os_data = df_os.iloc[i]
                            st.markdown(criar_card_os(os_data), unsafe_allow_html=True)

                    with col2:
                        if i + 1 < len(df_os):
                            os_data = df_os.iloc[i + 1]
                            st.markdown(criar_card_os(os_data), unsafe_allow_html=True)

        # ===== ABA 2: FAMÍLIAS =====
        with tab2:
            df_familia = agregar_por_familia(df_filtrado)
            df_familia['EXECUCAO_%'] = (df_familia['REALIZADO'] / df_familia['PREVISTO'].replace(0, float('nan')) * 100).fillna(0)
            df_familia['RISCO'] = df_familia.apply(classificar_risco, axis=1)
            df_familia = df_familia.sort_values('EXECUCAO_%', ascending=False)

            st.markdown(f"### 📦 Análise por Família ({len(df_familia)} categorias)")

            # Tabela formatada
            df_fam_display = df_familia.copy()
            df_fam_display['Previsto'] = df_fam_display['PREVISTO'].apply(formatar_moeda)
            df_fam_display['Realizado'] = df_fam_display['REALIZADO'].apply(formatar_moeda)
            df_fam_display['Saldo'] = df_fam_display['SALDO'].apply(formatar_moeda)
            df_fam_display['Execução'] = df_fam_display['EXECUCAO_%'].apply(lambda x: f"{x:.1f}%")

            st.dataframe(
                df_fam_display[['FAMILIA', 'Previsto', 'Realizado', 'Saldo', 'Execução', 'RISCO']].rename(columns={
                    'FAMILIA': 'Família',
                    'RISCO': 'Status'
                }),
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "Família": st.column_config.TextColumn("Família", width="large"),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            )

        # ===== ABA 3: EXPORTAR =====
        with tab3:
            st.markdown("### 📥 Exportar Dados")

            # Dados completos
            df_export = df_filtrado.copy()
            df_export_os = df_os.copy()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Dados Detalhados (OS + Família)")
                csv1 = df_export.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "📥 Baixar CSV Detalhado",
                    data=csv1,
                    file_name="cmv_detalhado.csv",
                    mime="text/csv"
                )

            with col2:
                st.markdown("#### Resumo por OS")
                df_export_os_fmt = df_export_os[['OS', 'PREVISTO', 'REALIZADO', 'SALDO', 'EXECUCAO_%', 'RISCO']].copy()
                csv2 = df_export_os_fmt.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "📥 Baixar CSV por OS",
                    data=csv2,
                    file_name="cmv_por_os.csv",
                    mime="text/csv"
                )

            st.markdown("---")
            st.markdown("#### 📋 Preview dos Dados")

            df_preview = df_export.head(100).copy()
            df_preview['PREVISTO'] = df_preview['PREVISTO'].apply(formatar_moeda)
            df_preview['REALIZADO'] = df_preview['REALIZADO'].apply(formatar_moeda)
            df_preview['SALDO'] = df_preview['SALDO'].apply(formatar_moeda)

            st.dataframe(df_preview, use_container_width=True, height=400, hide_index=True)

else:
    st.info("👆 Faça upload da planilha CMV para começar")

    st.markdown("""
    ### Como usar:
    1. Exporte a planilha de CMV do sistema
    2. Faça upload usando o menu lateral
    3. Visualize os cards de cada OS ordenados por execução
    4. Use os filtros para focar em status específicos

    ### Classificação de Risco:
    - 🔴 **ESTOURADO**: Execução > 100% (gastou mais que o previsto)
    - 🟠 **CRÍTICO**: Execução ≥ 90%
    - 🟡 **ATENÇÃO**: Execução entre 70% e 90%
    - 🟢 **OK**: Execução < 70%
    """)

    st.markdown("---")
    st.caption("Desenvolvido por Bruno | ARV Industrial | 2026")
