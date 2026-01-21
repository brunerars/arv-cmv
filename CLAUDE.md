# Sistema de Análise de CMV - ARV Industrial

## 1. VISÃO GERAL

### Contexto de Negócio
Atualmente, a compradora da ARV extrai manualmente dados de CMV (Custo de Mercadoria Vendida) do sistema interno e cria relatórios comparativos entre valores orçados e realizados. Este processo manual é demorado, propenso a erros e dificulta a análise estratégica em tempo real.

### Problema a Resolver
- Análise manual de grandes volumes de dados de compras por projeto
- Dificuldade em visualizar gastos por família de produtos
- Falta de filtros dinâmicos para análise por OS (Ordem de Serviço)
- Impossibilidade de gerar relatórios de saldo de CMV em tempo real
- Comparação trabalhosa entre orçado vs. realizado

### Solução Proposta
Sistema web (Streamlit) que automatiza a ingestão, processamento e visualização de dados de CMV, permitindo análises interativas e relatórios instantâneos.

---

## 2. ESTRUTURA DE DADOS

### 2.1 Planilha de Input (Excel - Pivot Table)

**Origem**: Exportação direta do sistema de gestão de compras  
**Formato**: XLSX com estrutura de pivot table  
**Localização**: Upload via interface Streamlit

#### Colunas Principais
```
- OS: Ordem de Serviço (string, pode conter múltiplas OSs separadas por "/")
- (%) Status: Percentual de conclusão (float, ex: 85.71%)
- CLIENTE: Nome do cliente (string)
- PROPOSTA: Código da proposta (string, ex: "2844/A", "2821")
- CMV PREVISTO SEM REDUÇÃO: Valor orçado original (float, R$)
- CMV PREVISTO: Valor orçado final (float, R$)
- CMV REALIZADO ATÉ [DATA1]: Valor gasto até primeira data (float, R$)
- CMV REALIZADO ATÉ [DATA2]: Valor gasto até segunda data (float, R$)
- SALDO CMV: Saldo restante (float, R$)
- ANÁLISE CMV: Percentual de análise (float, %)
```

#### Características Especiais
- **Linhas de Subtotal**: Contêm "SUB-TOTAL" na coluna PROPOSTA
- **Linhas de Total Global**: Contêm "TOTAL" e "GLOBAL" nas primeiras colunas
- **Agrupamentos**: Múltiplas seções separadas por linhas escuras (header repeats)
- **OSs Compostas**: Ex: "1159/1160/1161/1162" (múltiplas OSs em um mesmo projeto)

### 2.2 Banco de Dados de Projetos (projetos.json)

**Finalidade**: Base temporária de referência enquanto não há integração com sistema interno  
**Formato**: JSON estruturado

#### Estrutura Proposta
```json
{
  "projetos": [
    {
      "os": "3185",
      "cliente": "FESTO",
      "proposta": "2844/A",
      "status_percentual": 85.71,
      "cmv_previsto_sem_reducao": 293652.55,
      "cmv_previsto": 276283.76,
      "familias": [
        {
          "nome": "Estruturas Metálicas",
          "cmv_previsto": 120000.00
        },
        {
          "nome": "Componentes Elétricos",
          "cmv_previsto": 80000.00
        },
        {
          "nome": "Automação",
          "cmv_previsto": 76283.76
        }
      ]
    },
    {
      "os": "1175",
      "cliente": "HUNTER",
      "proposta": "2821",
      "status_percentual": 43.88,
      "cmv_previsto_sem_reducao": 1083869.90,
      "cmv_previsto": 1016149.00,
      "familias": [...]
    }
  ]
}
```

---

## 3. FUNCIONALIDADES CORE

### 3.1 Ingestão e Processamento de Dados

#### F1.1: Upload de Planilha
- **Input**: Arquivo XLSX via file_uploader do Streamlit
- **Validação**: 
  - Verificar extensão (.xlsx)
  - Validar estrutura de colunas esperadas
  - Detectar e sinalizar inconsistências
- **Output**: DataFrame pandas limpo e normalizado

#### F1.2: Parsing Inteligente da Pivot Table
- **Desafios**:
  - Headers repetidos em múltiplas seções
  - Linhas de subtotal e total global
  - OSs compostas (ex: "1159/1160/1161/1162")
  - Valores numéricos formatados com separadores brasileiros
- **Estratégia**:
  - Identificar e remover linhas de header duplicadas
  - Classificar linhas (dados, subtotal, total)
  - Expandir OSs compostas para análise individual
  - Normalizar valores numéricos (R$ 1.234,56 → 1234.56)

#### F1.3: Integração com projetos.json
- Carregar dados de referência dos projetos
- Enriquecer dados da planilha com informações de família
- Validar correspondência OS ↔ Projeto

### 3.2 Visualizações e Análises

#### F2.1: Dashboard Principal
```
┌─────────────────────────────────────────────────┐
│  📊 RELATÓRIO DE CMV - ARV INDUSTRIAL           │
├─────────────────────────────────────────────────┤
│  [Upload Planilha]  [Atualizar Dados]           │
├─────────────────────────────────────────────────┤
│  RESUMO GLOBAL                                   │
│  • Total Previsto: R$ 2.712.067,65              │
│  • Total Realizado: R$ 1.345.358,26             │
│  • Saldo: R$ 1.366.709,39                       │
│  • Execução: 49,61%                             │
├─────────────────────────────────────────────────┤
│  [Gráficos]  [Tabelas]  [Filtros]               │
└─────────────────────────────────────────────────┘
```

#### F2.2: Gráfico de Gastos por Família
- **Tipo**: Gráfico de barras horizontais ou pizza
- **Dados**: Soma de CMV realizado por família de produtos
- **Interatividade**: 
  - Hover para detalhes
  - Click para drill-down em projetos da família
  - Toggle entre valores absolutos e percentuais
- **Biblioteca**: Plotly (interativo) ou Matplotlib (estático)

**Exemplo**:
```python
import plotly.express as px

fig = px.bar(
    df_familia,
    x='cmv_realizado',
    y='familia',
    orientation='h',
    title='Gastos por Família de Produtos',
    labels={'cmv_realizado': 'CMV Realizado (R$)', 'familia': 'Família'},
    color='cmv_realizado',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig, use_container_width=True)
```

#### F2.3: Filtros Dinâmicos
- **Por OS**: Multiselect para selecionar uma ou mais OSs
- **Por Cliente**: Dropdown de clientes
- **Por Status**: Slider de percentual (ex: 0-100%)
- **Por Saldo**: Range de valores de saldo CMV
- **Por Data de Realização**: Escolher coluna de data para análise

**Interface**:
```python
with st.sidebar:
    st.header("Filtros")
    
    os_selecionadas = st.multiselect(
        "Ordem de Serviço",
        options=df['OS'].unique(),
        default=None
    )
    
    cliente_selecionado = st.selectbox(
        "Cliente",
        options=['Todos'] + list(df['CLIENTE'].unique())
    )
    
    status_min, status_max = st.slider(
        "Status (%)",
        0.0, 100.0, (0.0, 100.0)
    )
```

#### F2.4: Relatório de Saldo de CMV por Projeto
**Formato Tabular**:
```
┌────┬─────────────┬─────────────┬──────────────┬────────────┬────────────┐
│ OS │ Cliente     │ CMV Previsto│ CMV Realizado│ Saldo CMV  │ % Execução │
├────┼─────────────┼─────────────┼──────────────┼────────────┼────────────┤
│3185│ FESTO       │ 276.283,76  │ 709,33       │ 292.943,22 │ 0,04%      │
│1175│ HUNTER      │ 1.016.149,00│ 335.148,33   │ 748.721,57 │ 30,97%     │
│1095│ SIN IMPLANTE│ 860.795,34  │ 571.609,70   │ 460.426,76 │ 55,29%     │
└────┴─────────────┴─────────────┴──────────────┴────────────┴────────────┘
```

**Funcionalidades**:
- Ordenação por colunas
- Exportação para Excel/CSV
- Highlight de projetos com saldo crítico (< 10%)
- Cores condicionais baseadas em % de execução

#### F2.5: Análise Temporal (Comparação entre Datas)
- Gráfico de linhas mostrando evolução do CMV Realizado
- Comparação "CMV REALIZADO ATÉ 22/12/2025" vs "CMV REALIZADO ATÉ 14/01/2026"
- Taxa de burn rate por projeto

### 3.3 Exportação e Relatórios

#### F3.1: Exportação de Dados Filtrados
- CSV para análise externa
- Excel com formatação preservada
- PDF para apresentações

#### F3.2: Relatório Executivo
- Resumo automático com insights:
  - Projetos com maior variação orçamentária
  - Famílias com maior gasto
  - Alertas de projetos com saldo negativo ou muito baixo
  - Projetos com execução atrasada (baixo % vs. tempo decorrido)

---

## 4. ESPECIFICAÇÕES TÉCNICAS

### 4.1 Stack Tecnológico

#### Backend
- **Linguagem**: Python 3.11+
- **Framework Web**: Streamlit 1.30+
- **Manipulação de Dados**: pandas 2.1+, numpy 1.24+
- **Visualização**: plotly 5.18+ (interativo), matplotlib 3.8+ (estático)
- **Leitura de Excel**: openpyxl 3.1+

#### Estrutura de Arquivos
```
cmv-analysis/
│
├── app.py                 # Aplicação principal Streamlit
├── requirements.txt       # Dependências Python
├── projetos.json         # Base de dados temporária de projetos
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py    # Funções de carregamento de dados
│   ├── data_processor.py # Limpeza e transformação de dados
│   ├── analytics.py      # Cálculos e agregações
│   └── visualizations.py # Geração de gráficos
│
├── utils/
│   ├── __init__.py
│   ├── validators.py     # Validação de dados
│   └── formatters.py     # Formatação de valores (R$, %, etc)
│
└── tests/
    ├── test_data_loader.py
    ├── test_data_processor.py
    └── sample_data/
        └── pivot_sample.xlsx
```

### 4.2 Arquitetura de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT APP                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────┐ │
│  │ File Uploader│──▶│Data Processor│──▶│  Analytics │ │
│  └──────────────┘   └──────────────┘   └────────────┘ │
│                                              │          │
│  ┌──────────────┐   ┌──────────────┐        │          │
│  │projetos.json │──▶│Data Enricher │────────┘          │
│  └──────────────┘   └──────────────┘                   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Visualization Layer                    │  │
│  │  • Dashboard  • Charts  • Tables  • Filters      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Export Layer                           │  │
│  │  • CSV  • Excel  • PDF                           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Fluxo de Processamento de Dados

```python
# Pseudocódigo do fluxo principal

def processar_planilha(arquivo_excel):
    # 1. Leitura bruta
    df_raw = pd.read_excel(arquivo_excel)
    
    # 2. Detecção de estrutura
    linhas_header = detectar_headers_duplicados(df_raw)
    linhas_subtotal = detectar_subtotais(df_raw)
    linhas_total_global = detectar_totais_globais(df_raw)
    
    # 3. Limpeza
    df_clean = remover_linhas_invalidas(df_raw, linhas_header, linhas_subtotal, linhas_total_global)
    
    # 4. Normalização
    df_norm = normalizar_valores_numericos(df_clean)
    df_norm = expandir_os_compostas(df_norm)
    
    # 5. Enriquecimento
    projetos_ref = carregar_projetos_json()
    df_enriched = adicionar_dados_familia(df_norm, projetos_ref)
    
    # 6. Validação
    validar_integridade(df_enriched)
    
    return df_enriched
```

### 4.4 Estrutura de Dados Processados (DataFrame Final)

```python
# Colunas após processamento completo

df_final.columns = [
    'os',                          # String, OS individual
    'os_original',                 # String, OS composta original se aplicável
    'status_percentual',           # Float, 0-100
    'cliente',                     # String
    'proposta',                    # String
    'cmv_previsto_sem_reducao',   # Float
    'cmv_previsto',               # Float
    'cmv_realizado_data1',        # Float
    'cmv_realizado_data2',        # Float
    'saldo_cmv',                  # Float
    'analise_cmv_percentual',     # Float, 0-100
    'familia',                    # String (enriquecido de projetos.json)
    'tipo_linha'                  # String: 'dados', 'subtotal', 'total'
]
```

---

## 5. ROADMAP DE DESENVOLVIMENTO

### Fase 1: MVP - Funcionalidades Básicas (1-2 dias)
**Objetivo**: Sistema funcional com funcionalidades essenciais

- [ ] Setup do projeto (estrutura de pastas, requirements.txt)
- [ ] Interface básica de upload de planilha
- [ ] Parsing da pivot table (limpeza básica)
- [ ] Exibição de dados em tabela
- [ ] Cálculos básicos: total previsto, total realizado, saldo
- [ ] Gráfico simples de gastos (barras)

**Entregável**: App Streamlit rodando localmente que aceita upload e mostra dados básicos

### Fase 2: Análises e Filtros (2-3 dias)
**Objetivo**: Adicionar capacidades analíticas e interatividade

- [ ] Implementar projetos.json e enriquecimento de dados
- [ ] Filtros laterais (OS, Cliente, Status)
- [ ] Gráfico de gastos por família (interativo com Plotly)
- [ ] Tabela de saldo de CMV por projeto com ordenação
- [ ] Análise temporal (comparação entre datas)

**Entregável**: App com análises interativas e visualizações completas

### Fase 3: Refinamentos e Exportação (1-2 dias)
**Objetivo**: Polimento da UX e funcionalidades de export

- [ ] Exportação de dados (CSV, Excel)
- [ ] Formatação brasileira (R$, separadores de milhar)
- [ ] Cores condicionais e highlights
- [ ] Relatório executivo com insights automáticos
- [ ] Validações robustas de input
- [ ] Mensagens de erro user-friendly

**Entregável**: App production-ready para uso interno

### Fase 4: Otimização e Testes (1 dia)
**Objetivo**: Garantir qualidade e performance

- [ ] Testes unitários para parsing de dados
- [ ] Teste com planilhas reais variadas
- [ ] Otimização de performance (caching com st.cache_data)
- [ ] Documentação de uso (README para compradora)
- [ ] Deploy em servidor interno ou Streamlit Cloud

**Entregável**: Sistema estável e documentado

### Fase 5: Evolução Futura (Backlog)
**Funcionalidades Avançadas**:

- [ ] Integração direta com banco de dados interno (substituir projetos.json)
- [ ] Previsão de burn rate e alertas proativos
- [ ] Comparação entre múltiplos períodos (histórico)
- [ ] Dashboard executivo com KPIs consolidados
- [ ] Autenticação e permissões por usuário
- [ ] Agendamento de relatórios automáticos (email)
- [ ] API REST para integração com outros sistemas

---

## 6. CONSIDERAÇÕES DE UX

### 6.1 Perfil do Usuário Principal
- **Cargo**: Compradora
- **Familiaridade técnica**: Intermediária (usa Excel, sistemas ERP)
- **Frequência de uso**: Semanal/Quinzenal para atualização de relatórios
- **Objetivo**: Reduzir tempo de análise de horas para minutos

### 6.2 Princípios de Design
1. **Simplicidade**: Interface limpa, sem sobrecarga de informações
2. **Feedback Imediato**: Indicadores de loading, mensagens claras de erro/sucesso
3. **Consistência**: Formatação brasileira em todos os valores (R$, %)
4. **Eficiência**: Máximo 3 clicks para qualquer funcionalidade
5. **Tolerância a Erros**: Validação clara, sugestões de correção

### 6.3 Fluxo de Uso Típico
```
1. Usuária abre app no navegador
2. Faz upload da planilha exportada do sistema
   ↓
3. Sistema processa e exibe dashboard instantaneamente
   ↓
4. Usuária aplica filtros (ex: ver apenas OS 1175)
   ↓
5. Visualiza gráfico de família para essa OS
   ↓
6. Exporta tabela filtrada para Excel
   ↓
7. Compartilha com gestão
```

**Tempo total**: < 2 minutos (vs. 30-60 minutos manual)

### 6.4 Mensagens e Feedback

**Exemplo de mensagens**:
```python
# Sucesso
st.success("✅ Planilha carregada com sucesso! 12 projetos encontrados.")

# Aviso
st.warning("⚠️ 3 OSs não encontradas no banco de dados de projetos. Dados de família indisponíveis.")

# Erro
st.error("❌ Estrutura da planilha inválida. Certifique-se de exportar a Pivot Table corretamente.")

# Info
st.info("ℹ️ Dica: Use os filtros laterais para análises mais específicas.")
```

---

## 7. CRITÉRIOS DE SUCESSO

### Métricas de Produto
- [ ] Redução de 80%+ no tempo de geração de relatórios
- [ ] Zero erros de cálculo vs. processo manual
- [ ] Adoção de 100% pela equipe de compras (atualmente 1 usuária)
- [ ] Satisfação do usuário: 4/5 ou superior

### Métricas Técnicas
- [ ] Processamento de planilhas com até 100 projetos em < 5 segundos
- [ ] Taxa de erro de parsing < 1%
- [ ] Cobertura de testes > 80%
- [ ] Zero crashes em operação normal

### Indicadores de Valor de Negócio
- [ ] Aumento na frequência de análises de CMV (semanal → diária)
- [ ] Identificação proativa de desvios orçamentários
- [ ] Base para decisões de compra mais data-driven
- [ ] Potencial extensão para outras áreas (vendas, projetos)

---

## 8. REFERÊNCIAS TÉCNICAS

### Exemplos de Código Principais

#### 8.1 Parsing de Pivot Table
```python
def parse_pivot_table(df_raw):
    """
    Remove headers duplicados e linhas de total/subtotal
    """
    # Identificar linhas de header (repetições)
    header_mask = df_raw.iloc[:, 0] == 'OS'
    
    # Identificar linhas de subtotal/total
    subtotal_mask = df_raw['PROPOSTA'].str.contains('SUB-TOTAL', na=False)
    total_mask = df_raw.iloc[:, 0].str.contains('TOTAL', na=False)
    
    # Manter apenas linhas de dados
    df_clean = df_raw[~(header_mask | subtotal_mask | total_mask)].copy()
    
    return df_clean
```

#### 8.2 Expansão de OSs Compostas
```python
def expandir_os_compostas(df):
    """
    Transforma "1159/1160/1161" em 3 linhas individuais
    """
    expanded_rows = []
    
    for _, row in df.iterrows():
        os_str = str(row['OS'])
        if '/' in os_str:
            # Múltiplas OSs
            os_list = os_str.split('/')
            for os_individual in os_list:
                new_row = row.copy()
                new_row['os'] = os_individual.strip()
                new_row['os_original'] = os_str
                expanded_rows.append(new_row)
        else:
            # OS única
            row['os'] = os_str
            row['os_original'] = os_str
            expanded_rows.append(row)
    
    return pd.DataFrame(expanded_rows)
```

#### 8.3 Formatação Brasileira
```python
def formatar_moeda(valor):
    """
    Formata valor numérico para padrão brasileiro
    1234.56 → R$ 1.234,56
    """
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def formatar_percentual(valor):
    """
    Formata percentual
    0.1234 → 12,34%
    """
    return f"{valor:.2f}%".replace('.', ',')
```

#### 8.4 Gráfico de Família (Plotly)
```python
import plotly.express as px

def criar_grafico_familia(df):
    """
    Cria gráfico interativo de gastos por família
    """
    df_familia = df.groupby('familia').agg({
        'cmv_realizado_data2': 'sum',
        'cmv_previsto': 'sum'
    }).reset_index()
    
    df_familia['percentual_gasto'] = (
        df_familia['cmv_realizado_data2'] / df_familia['cmv_previsto'] * 100
    )
    
    fig = px.bar(
        df_familia,
        x='cmv_realizado_data2',
        y='familia',
        orientation='h',
        title='Gastos por Família de Produtos',
        labels={
            'cmv_realizado_data2': 'CMV Realizado (R$)',
            'familia': 'Família'
        },
        color='percentual_gasto',
        color_continuous_scale='RdYlGn_r',  # Vermelho=alto, Verde=baixo
        hover_data=['cmv_previsto', 'percentual_gasto']
    )
    
    fig.update_layout(
        height=400,
        coloraxis_colorbar_title="% Gasto"
    )
    
    return fig
```

---

## 9. PRÓXIMOS PASSOS IMEDIATOS

### Ação Imediata (Hoje)
1. Criar estrutura de pastas do projeto
2. Inicializar `requirements.txt` com dependências básicas
3. Obter planilha real de exemplo da compradora
4. Iniciar implementação do parsing básico

### Validação Rápida (Primeira Semana)
- Mostrar protótipo para compradora com upload + visualização simples
- Coletar feedback sobre prioridades de funcionalidades
- Ajustar estrutura de projetos.json baseado em dados reais

### Evolução Incremental
- Lançar MVP funcional em 1 semana
- Coletar feedback real de uso
- Iterar rapidamente baseado em necessidades emergentes
- Planejar integração com sistema interno (substituir JSON)

---

## 10. CONTATO E SUPORTE

**Desenvolvedor**: Bruno  
**Stakeholder Principal**: Compradora ARV  
**Repositório**: [definir localização]  
**Ambiente de Produção**: [definir URL Streamlit ou servidor interno]

---

**Última Atualização**: Janeiro 2026  
**Versão do Documento**: 1.0
