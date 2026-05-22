# PLANO: Ajuste de Conformidade de Colunas (Motor CEVAP v3)

## 1. Pesquisa
- Ler o Dicionário de Dados para extrair a lista exata de colunas esperadas.

## 2. Execução (Build)
- Editar `consolidate_cevap.py` via `replace` para renomear e incluir as colunas faltantes.
- Criar script `tests/test_columns.py` (TDD) que carrega o Excel gerado e compara com o Dicionário.

## 3. Deployment
- Aplicar `audit-canary-deployment` antes de rodar o script final.
- Validar se o output final passa no teste de colunas.
