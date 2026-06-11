# Especificação Técnica: Mesorregião no CEVAP & Painel de Indicadores de Acompanhamento

> **Versão:** 2.0
> **Status:** Em Brainstorming/Validação
> **Data:** 2026-06-01
> **Autor:** Gemini CLI Builder / Analista de Dados e Engenheiro de Software

---

## 1. Introdução e Objetivo

Esta especificação define:
1. A inclusão da coluna `Mesoregiao` na planilha final de ativação do Motor CEVAP, utilizando como fonte o arquivo de mapeamento JSON localizado em:
   `"C:\Projetos\Inova\projects\BUP-base-unica-pós-venda\data\config\cidade_mesoregiao.json"`
2. A criação de indicadores de acompanhamento para monitorar o resultado do trabalho comercial que está sendo realizado através do CEVAP, gerando:
   - Um relatório Markdown resumido em `docs/RELATORIO_KPIs_CEVAP.md`
   - Um painel interativo HTML autossuficiente (Dashboard) em `docs/dashboard_cevap.html`

---

## 2. Inclusão da Coluna `Mesoregiao`

### 2.1 Fonte de Dados
O arquivo JSON contém chaves no formato `"CIDADE / UF"` ou `"CIDADE"` mapeadas para o nome da mesorregião.
Exemplo:
```json
{
  "ABADIA DOS DOURADOS / MG": "Triangulo Mineiro / Alto Paranaiba",
  "ABADIA DOS DOURADOS": "Triangulo Mineiro / Alto Paranaiba"
}
```

### 2.2 Algoritmo de Mapeamento (polimento_final_v5.py)
1. **Leitura:** Carregar o arquivo JSON usando explicitamente `encoding='utf-8'` (Vacina de Encoding).
2. **Normalização:** Converter o campo `Cidade` (que está no formato `"Cidade/UF"`, ex: `"Belo Horizonte/MG"`) para maiúsculas e espaçar a barra `" / "` (ex: `"BELO HORIZONTE / MG"`).
3. **Busca com Fallback:**
   - **Passo 1:** Procurar chave exata normalizada (ex: `"BELO HORIZONTE / MG"`).
   - **Passo 2:** Caso não encontrada, procurar apenas pelo nome da cidade (ex: `"BELO HORIZONTE"`).
   - **Passo 3:** Se ainda assim não encontrada, retornar `"Indisponível"`.
4. **Alinhamento do Contrato de Colunas (Gold V5):**
   - Preservar `Potencial_Grupo` e `N_Orcamento_12m` conforme esperado pelo `tests/test_columns.py` e remover a renomeação indevida de `N_Orcamento_12m` para `Qtd_Orcamento_12m`.
   - Adicionar `Mesoregiao` na ordem correta, imediatamente após `Cidade`.

---

## 3. Painel de Indicadores e KPIs de Acompanhamento

Para acompanhar o resultado do trabalho executado, criaremos o script `scripts/generate_cevap_kpis.py`.

### 3.1 KPIs Principais
- **Total de Clientes no CEVAP:** Quantidade absoluta de clientes na fila de ativação.
- **Volume de Faturamento Inativo (12 meses):** Soma total do `Valor_12m` sob gestão do CEVAP.
- **Faturamento e Potencial por Classificação:** Distribuição por segmentos (A1, A2, B1, B2, C1) para identificar a concentração de valor.
- **Status do Trabalho Comercial (Funil de Ativação):**
  - **Não Trabalhado (Pendente):** Clientes com `Status_Contato_1` vazio ou igual a "Pendente" ou "Sem Contato".
  - **Tentativa 1 Efetuada:** Contato inicial realizado.
  - **Tentativa 2 Efetuada:** Segundo contato realizado para casos sem retorno.
  - **Resultado do Contato:** Análise de motivos (ex: "Sem Retorno", "Não tem interesse", "Ativado - Compra Realizada", "Oportunidade Aberta").
- **Distribuição Geográfica (Mesorregião):** Número de clientes e faturamento por mesorregião.

### 3.2 Entregáveis de Analytics
1. **Relatório Executivo (`docs/RELATORIO_KPIs_CEVAP.md`):** Relatório estático em markdown gerado automaticamente pelo pipeline.
2. **Dashboard Interativo (`docs/dashboard_cevap.html`):** Arquivo HTML premium e responsivo (Tailwind + Chart.js) com gráficos dinâmicos de rosca/barra para distribuição de status, mesorregiões e classificação, permitindo filtros por Mesorregião e Classificação.

---

## 4. Próximos Passos (Plano)

1. Atualizar o script de polimento para usar o caminho correto de `cidade_mesoregiao.json` sob o BUP e corrigir os desvios de colunas detectados pelo teste.
2. Desenvolver o script de indicadores `scripts/generate_cevap_kpis.py`.
3. Integrar a execução do gerador de indicadores no final da execução do pipeline do CEVAP.
4. Validar todas as implementações executando o pipeline e a suite de testes.
