# Pendências Wiki-LLM Pipeline — Sessão 2026-05-21

## Concluído nesta sessão
- [x] Diagnóstico: 15 falhas mapeadas (5 críticas, 5 altas, 5 médias)
- [x] Adapters criados: session_to_cleaned.py + commandcode_to_cleaned.py
- [x] wiki-stage.sh estendido com passos 1.5 e 1.6
- [x] ACTIVE_CONTEXT.md limpo (truncamento removido)
- [x] Paths hardcoded corrigidos (wiki-stage.sh, context_manager.py, active_context.py)
- [x] Ingest fracionada: 252 → 0 arquivos no _raw/
- [x] 11 páginas novas, 6 atualizadas, 1 journal, 1 índice

## Pendente para próxima sessão (6 itens)

### Médio impacto
- [x] Corrigir parse de JSONL silencioso em session_parser.py — logar linhas inválidas com warning
- [x] Substituir descoberta de sessão por mtime — usar timestamp no nome do arquivo como fonte primária
- [x] Corrigir FTS5 reindex com session_number string vs int em search.py

### Baixo impacto
- [x] Implementar checkpoint atômico no raw mode do wiki-ingest para evitar double-processing
- [x] Tornar DRIFT detection robusto contra edições manuais no MEMORY.md
- [x] Integrar wiki_health_check.py ao pipeline como step pós-save

## Sessão 2026-05-21 (segunda parte) — Todos os 6 itens concluídos

### Mudanças realizadas

1. **session_parser.py** — Adicionado `logging` com `logger.warning()` para linhas JSON inválidas, contagem de perdas, e `logger.debug()` para tipos desconhecidos e linhas vazias.

2. **session_parser.py** — `_discover_session_files()` agora extrai timestamp do nome do arquivo (`session-YYYYMMDD-HHMMSS`) como chave primária de ordenação, com fallback para `st_mtime`.

3. **search.py** — `reindex_all()` não pula mais arquivos sem número sequencial. `session_id` agora é sempre string (número ou stem). `SearchResult.session_number: int` → `session_id: str`. `index_session()` aceita `str`.

4. **subprocess_ingest_orchestrator.py** — Adicionado `_filter_already_processed()` que compara hash SHA-256 dos arquivos em `_raw/` com `.manifest.json` antes de processar, prevenindo double-processing.

5. **active_context.py** — `check_drift()` agora detecta edições manuais no MEMORY.md (conteúdo extra) e faz merge reverso automático para ACTIVE_CONTEXT.md. Drift real (ambos editados) ainda requer intervenção manual.

6. **wiki_health_check.py** (novo) — Script de health check pós-save com 4 verificações: órfãos, links quebrados, frontmatter faltante, stale content. Integrado ao `wiki-stage.sh` como passo 3.
