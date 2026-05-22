---
name: explore
version: 1.0.0
description: Use when you need to explore codebase structure, dependencies, and call hierarchies via SQL queries. Permite explorar a estrutura do código, dependências e hierarquias de chamadas usando consultas SQL.
when_to_use: explorar código, estrutura do projeto, dependências, quem chama, hierarquia, call hierarchy, dependency chain, who calls, what depends on, files importing a symbol, codebase exploration
allowed-tools: Bash(sqlite3:*) Bash(git:*) Bash(yomu:*)
argument-hint: "[natural language question about codebase structure]"
---

# explore

## Prerequisite

Run `yomu status` first and read the counts.

| State             | Action                                                              |
| ----------------- | ------------------------------------------------------------------- |
| Index missing     | Tell user to run `yomu rebuild` (full), then re-invoke              |
| Stale after edits | Tell user to run `yomu index` (incremental), then re-invoke         |
| References: 0     | Caller/import queries will be empty. Fallback to `yomu search` or Grep |

DB path: `<project_root>/.yomu/index.db` (`git rev-parse --show-toplevel`). If not a git repo, ask user for the DB path.

## Schema

Run queries via `sqlite3 -readonly <db_path> "<query>"`.

```sql
chunks (
  id INTEGER PRIMARY KEY,
  file_path TEXT NOT NULL,
  chunk_type TEXT NOT NULL,   -- e.g. rust_fn, rust_struct, rust_impl, rust_trait, rust_enum, md_section, other. Language-dependent.
  name TEXT,                  -- nullable
  content TEXT NOT NULL,
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL,
  file_hash TEXT NOT NULL,
  parent_chunk_id INTEGER REFERENCES chunks(id)
)

file_references (
  id INTEGER PRIMARY KEY,
  source_file TEXT NOT NULL,  -- file using the symbol
  target_file TEXT NOT NULL,  -- file defining the symbol
  symbol_name TEXT,           -- nullable
  ref_kind TEXT NOT NULL      -- e.g. named
)

file_context (file_path TEXT PRIMARY KEY, imports_text TEXT)

-- FTS5 external content. rowid = chunks.id for JOIN
fts_chunks (name, content, file_path)
```

Do not query `vec_chunks` (requires sqlite-vec extension; semantic search belongs to `yomu search`).

## When to Use

| Question                                           | Tool                       |
| -------------------------------------------------- | -------------------------- |
| Who uses symbol X?                                 | explore (file_references)  |
| Full impact analysis of File X                     | `yomu impact <file>`       |
| Aggregate dependencies by ref_kind                 | explore (ad-hoc SQL)       |
| Search for "Authentication Flow" (concept)         | use-cli-yomu (semantic)    |
| Grep for literal string / regex                    | Grep                       |
| Keyword search in code content chunks              | explore (fts_chunks MATCH) |

## Query Archetypes

Start from an archetype → refine based on previous results. Do not hardcode today's only enum value (e.g. `ref_kind='named'` will expand).

### 1. Caller lookup (who uses this symbol)

```sql
SELECT source_file, ref_kind, COUNT(*) AS uses
FROM file_references
WHERE symbol_name = 'TargetSymbol'
GROUP BY source_file, ref_kind
ORDER BY uses DESC;
```

### 2. Import chain (what a file imports)

```sql
SELECT file_path, imports_text
FROM file_context
WHERE imports_text LIKE '%target_module%';
```

### 3. Keyword FTS (where keyword appears in code content)

```sql
SELECT c.file_path, c.start_line, c.name, c.chunk_type
FROM fts_chunks f
JOIN chunks c ON f.rowid = c.id
WHERE fts_chunks MATCH 'keyword'
LIMIT 20;
```

## Output

- Lead with the direct answer (file list, count, chain)
- Cite `file_path:line` for every claim
- Confidence marker:
  - [✓] direct row from query result
  - [→] inferred by JOIN / aggregation / naming

Example:

```
TargetSymbol uses in 3 files [✓]
  src/handlers/user.rs:42
  src/handlers/admin.rs:18
  src/tests/integration.rs:205

ref_kind is 'named' only → import vs call distinction unknown [→]
```

## Related Skills

- **use-workflow-spec-validation**: After exploring the structure, use this to validate implementation against specs.
- **adr**: Document architectural decisions found or proposed during exploration.
- **doc-workflow-orchestrator**: Master guide for the documentation lifecycle.

## Instalação

Requer o indexador `yomu` instalado e acessível no PATH.
```bash
# Instalado via skill-manager no ambiente Stout
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/explore [pergunta]` | Analisa a estrutura do código via SQL |

## Governança e Segurança

- **Nível de Governança:** 1 (Logging).
- **Segurança:** Acesso em modo `--readonly` ao banco de dados SQLite.
