# Spec: Correção de Indexação do Context Agent

## Objetivo
Corrigir a instabilidade e perda de dados no índice de busca (FTS5) do Context Agent causada pela mudança no formato dos nomes de arquivos de sessão (de sequencial para timestamped).

## Contexto e Problema
O Context Agent migrou de um formato de nome de arquivo `session-NNN.md` para `session-YYYYMMDD-HHMMSS-origin-id.md`. No entanto, a lógica de indexação atual em `search.py` e `session_summary.py` ainda assume que a segunda parte do nome (separada por hífen) é um número sequencial único.

### Pontos de Falha:
1. **Colisão de Índices:** Se múltiplas sessões ocorrerem no mesmo dia, o `split("-")[1]` (que retorna o YYYYMMDD) será o mesmo para todas. A função `index_session` apaga entradas anteriores com o mesmo "número", resultando em apenas a última sessão do dia sendo indexada.
2. **Tipagem de Dados:** O sistema tenta converter o timestamp/data para `int`, o que funciona para datas (ex: 20260429), mas perde a precisão do horário e gera IDs gigantescos e não sequenciais.
3. **Inconsistência Visual:** O resumo da sessão exibe "Sessão 20260429" no cabeçalho em vez de um número amigável ou o timestamp completo.

## Proposta de Solução
1. **Refatorar Identificador de Sessão:** Mudar a chave primária do índice de busca de `session_number` (int) para `session_id` (string/filename) para garantir unicidade absoluta.
2. **Atualizar Lógica de Reindexação:** Ajustar `reindex_all` em `search.py` para extrair o identificador único corretamente dos novos nomes de arquivos.
3. **Preservar Compatibilidade:** Garantir que sessões antigas (`session-001.md`) continuem sendo indexadas corretamente.
4. **Interface de Status:** Ajustar o comando `status` para lidar com a ausência de números sequenciais se necessário, ou recalcular uma sequência virtual para exibição.

## Critérios de Sucesso
- Busca FTS5 retorna resultados de todas as sessões, mesmo as que ocorreram no mesmo dia.
- O comando `maintain` (reindex_all) processa todos os arquivos sem erros de conversão.
- `ACTIVE_CONTEXT.md` e `MEMORY.md` são atualizados corretamente com os novos identificadores.
