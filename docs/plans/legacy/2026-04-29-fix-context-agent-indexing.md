# Plano de Correção: Indexação do Context Agent

## Problema
O Context Agent utiliza o campo `session_number` como identificador único no índice SQLite FTS5. Com a transição para nomes de arquivos baseados em timestamp (`session-YYYYMMDD-HHMMSS...`), a lógica de extração atual (`split("-")[1]`) retorna apenas a data (`YYYYMMDD`). 

Isso causa:
- **Colisões:** Múltiplas sessões no mesmo dia recebem o mesmo ID no índice.
- **Perda de Dados:** O sistema apaga a entrada anterior do mesmo ID ao indexar uma nova, mantendo apenas a última sessão de cada dia na busca.

## Mudanças Propostas

### 1. Modelos (`scripts/models.py`)
- Alterar `session_number` para `session_id` (string) em `SearchResult` e `SessionSummary`.
- Manter `session_number` como opcional para compatibilidade.

### 2. Indexação (`scripts/search.py`)
- Alterar o esquema da tabela FTS5 para usar `session_id` (TEXT).
- Atualizar `index_session` para remover e inserir usando o ID único (nome do arquivo ou timestamp completo).
- Atualizar `reindex_all` para passar o identificador correto.

### 3. Sumarização (`scripts/session_summary.py`)
- Ajustar `get_next_session_number` para ser mais resiliente ou lidar com o fato de que números sequenciais não são mais a chave primária.
- Garantir que o cabeçalho markdown reflita o ID correto.

## Plano de Validação
- **Teste de Colisão:** Gerar duas sessões rápidas e verificar se ambas são retornadas em buscas.
- **Teste de Reindexação:** Rodar `maintain` e confirmar que o número de entradas no índice condiz com o número de arquivos.
