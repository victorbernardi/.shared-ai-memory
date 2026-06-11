# Plano de Implementação: Mesorregião e Indicadores CEVAP

> **Versão:** 2.0
> **Status:** Pronto para Execução
> **Data:** 2026-06-01
> **Autor:** Gemini CLI Builder / Analista de Dados e Engenheiro de Software

---

## 🛠️ Detalhamento das Etapas

### Passo 1: Correção do JSON de Mesorregiões e Contrato de Colunas
* No arquivo `C:\Projetos\Inova\projects\motor-cevap\scripts\polimento_final_v5.py`:
  - Alterar o caminho em `carregar_mesoregioes()` para `r"C:\Projetos\Inova\projects\BUP-base-unica-pós-venda\data\config\cidade_mesoregiao.json"`.
  - Manter as colunas corretas de acordo com a suite de testes. A lista de `cols_finais` deve conter `"Potencial_Grupo"` e manter `"N_Orcamento_12m"` em vez de renomear para `"Qtd_Orcamento_12m"` para evitar quebras em testes de QA e em processos subsequentes.
  - Saneamento completo de acentos e encoding (`encoding='utf-8'`) na leitura do JSON.

### Passo 2: Criação do Script de KPIs e Dashboard (`scripts/generate_cevap_kpis.py`)
* Implementar um script Python autônomo que:
  1. Localize a planilha mais recente do OneDrive (`C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\CEVAP_ATIVACAO.xlsx`) ou a última gerada em `data/`.
  2. Carregue o arquivo Excel em um DataFrame pandas.
  3. Calcule indicadores de volume (Total de Clientes, Soma de Faturamento 12m).
  4. Analise a distribuição do funil comercial com base nos status de contato (`Status_Contato_1`, `Status_Contato_2`).
  5. Calcule a distribuição por mesorregião e por classificação.
  6. Escreva um sumário executivo conciso em `docs/RELATORIO_KPIs_CEVAP.md`.
  7. Gere o painel interativo `docs/dashboard_cevap.html` com layout de Grid, cartões de KPI, gráficos Chart.js responsivos e uma tabela detalhada com filtro de busca.

### Passo 3: Ajuste na Suite de Testes e Integração no Pipeline
* Integrar a chamada para `generate_cevap_kpis.py` após o término do polimento final em `polimento_final_v5.py` ou criar um script de orquestração fácil.
* Executar o pipeline completo e rodar os testes automatizados com `python -m pytest tests/ -v`.

---

## 🛡️ Trava de Segurança e Verificação
- Validação local dos dados e ausência de NaNs/NaTs nos campos cruciais.
- Verificação de encoding `utf-8` em todas as leituras e escritas.
