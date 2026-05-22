# SPEC: Ajuste de Conformidade de Colunas (Motor CEVAP v3)

## 1. Problema Identificado
- **Divergência:** A planilha gerada mantém "Segmento" (que deveria ser removido) e não contém "Classificacao". Algumas colunas do Dicionário (como Cidade) estão ausentes no script de consolidação.
- **Governança:** Falha na validação de sucesso. O script não está produzindo o output conforme o contrato definido no dicionário.

## 2. Escopo de Ajuste
- **Mapeamento:**
    - Garantir que a coluna oficial seja `Classificacao` (A1, A2, etc).
    - Incluir todas as colunas listadas no Dicionário (`DICIONARIO_DADOS_CEVAP.md`).
    - Remover `Segmento`.
- **Validação:** Criar teste automático de colunas que rodará após a consolidação para garantir que o Excel gerado contém exatamente as colunas do dicionário.
