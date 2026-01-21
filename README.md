# Sistema de Análise de CMV - ARV Industrial

Sistema web para automatizar análise de CMV (Custo de Mercadoria Vendida), substituindo o processo manual de criação de relatórios.

## 🚀 Quick Start

### Instalação

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv

# 2. Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt
```

### Rodar a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
cmv-analysis/
│
├── app.py              # Aplicação principal Streamlit (MVP funcional)
├── projetos.json       # Base temporária de dados de projetos
├── requirements.txt    # Dependências Python
├── CLAUDE.md          # Especificação completa do projeto
└── README.md          # Este arquivo
```

## 💡 Como Usar

1. **Abra a aplicação** rodando `streamlit run app.py`
2. **Faça upload** da planilha Pivot GRV exportada (formato .xlsx)
3. **Visualize automaticamente**:
   - Resumo global de CMV (previsto, realizado, saldo)
   - Gráficos interativos de análise
   - Tabela detalhada por projeto
4. **Use os filtros** no menu lateral para análises específicas
5. **Exporte** os dados em CSV se necessário

## 📊 Status Atual

✅ **MVP Implementado** (Fase 1):
- Interface de upload de planilha
- Parsing básico da pivot table
- Limpeza e normalização de dados
- Dashboard com resumo global
- Gráficos de CMV realizado e % execução por cliente
- Tabela detalhada formatada
- Exportação para CSV

🚧 **Próximos Passos** (Fase 2):
- [ ] Integração efetiva com `projetos.json` (dados de família)
- [ ] Gráfico de gastos por **família de produtos**
- [ ] Filtros funcionais (cliente, OS, status)
- [ ] Análise temporal (comparação entre datas)
- [ ] Expandir OSs compostas (ex: "1159/1160/1161/1162")

📋 **Backlog** (Fases 3-5):
- [ ] Exportação Excel com formatação
- [ ] Relatório executivo com insights automáticos
- [ ] Validações robustas de input
- [ ] Deploy em servidor/cloud
- [ ] Integração com banco de dados interno (substituir JSON)

## 📖 Documentação Completa

Para especificações técnicas detalhadas, roadmap completo e arquitetura, consulte **[CLAUDE.md](CLAUDE.md)**.

## 🔧 Tecnologias

- **Python 3.11+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **OpenPyXL** - Leitura de Excel

## 📝 Notas de Desenvolvimento

### Estrutura da Planilha (Input)

A planilha exportada do sistema tem a seguinte estrutura:

**Colunas principais:**
- `OS` - Ordem de Serviço (pode conter múltiplas OSs: "1159/1160/1161/1162")
- `(%) Status` - Percentual de conclusão
- `CLIENTE` - Nome do cliente
- `PROPOSTA` - Código da proposta
- `CMV PREVISTO SEM REDUÇÃO` - Orçamento original
- `CMV PREVISTO` - Orçamento ajustado
- `CMV REALIZADO ATÉ [DATA]` - Valores realizados (múltiplas colunas com datas variáveis)
- `SALDO CMV` - Saldo restante
- `ANÁLISE CMV` - Percentual de análise

**Características especiais:**
- Headers repetidos em múltiplas seções
- Linhas de subtotal ("SUB-TOTAL")
- Linhas de total global ("TOTAL GLOBAL")
- Valores formatados em padrão brasileiro (R$ 1.234,56)

### Decisões Técnicas

1. **Streamlit**: Escolhido por simplicidade e velocidade de desenvolvimento
2. **Plotly**: Gráficos interativos > matplotlib estático
3. **JSON temporário**: `projetos.json` serve como base até integração com sistema interno
4. **Processamento in-memory**: Sem persistência, processamento a cada upload
5. **Caching**: `@st.cache_data` usado para otimizar leituras repetidas

### Próximos Desafios Técnicos

1. **Parsing robusto**: Lidar com variações de formato entre exportações
2. **OSs compostas**: Expandir "1159/1160/1161/1162" → análise individual por OS
3. **Datas variáveis**: Detectar automaticamente colunas "CMV REALIZADO ATÉ [DATA]"
4. **Enriquecimento**: Matchear dados da planilha com `projetos.json` por OS
5. **Validações**: Detectar e reportar inconsistências nos dados

## 🤝 Contribuindo

Este é um projeto interno ARV. Para melhorias:

1. Teste com planilhas reais
2. Documente bugs ou edge cases encontrados
3. Sugira novas funcionalidades baseadas em necessidades reais da compradora
4. Valide com stakeholders antes de mudanças grandes

## 📧 Contato

**Desenvolvedor**: Bruno  
**Stakeholder**: Equipe de Compras ARV  
**Data**: Janeiro 2026

---

**Última atualização**: Janeiro 2026  
**Versão**: 1.0 (MVP)
