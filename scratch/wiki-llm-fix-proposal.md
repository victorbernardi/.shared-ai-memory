# Proposta de Correção: Gap Command Code → Wiki-LLM

## Padrão existente (referência)

O pipeline wiki-llm já tem um padrão arquitetural bem definido em 2 fases:

**Fase 1 — Adapter de coleta** (`adapters/`): Varre uma fonte, aplica limpeza/transformação, escreve em `cleaned/`
**Fase 2 — Bridge para o vault** (`pending_to_ar9av_raw.py`): Move `cleaned/*.md` → `vault/_raw/`

O `wiki-stage.sh` é o orquestrador que chama ambos em sequência.

```
[FONTE] ──► adapter (limpa) ──► cleaned/ ──► pending_to_ar9av_raw ──► _raw/
                                                                           │
                                                                   /wiki-ingest (manual)
```

**Fontes já cobertas:**
| Fonte | Adapter | O que coleta |
|-------|---------|-------------|
| `Stout/docs/` + `Inova/**/docs/` | `superpowers_cleaner.py` | specs, plans, walkthroughs, decisions, business |
| `brain/` (Gemini) | `brain-watcher.py` + `stout_promote.py` | implementation_plan.md, walkthrough.md |

**Fontes NÃO cobertas (gaps):**
| Fonte | O que contém | Volume |
|-------|-------------|--------|
| `sessions/session-NNN.md` (context-agent) | Decisões, tarefas, descobertas, erros de 392 sessões | ~392 arquivos |
| `ACTIVE_CONTEXT.md` | Contexto vivo: projetos, tarefas, decisões recentes | 1 arquivo (149 linhas) |
| `~/.commandcode/plans/*.md` | Planos gerados pelo Command Code | 2 arquivos (crescendo) |

---

## Solução: Seguir o padrão, adicionar adapters

### O que NÃO fazer
- Não criar um script monolítico novo
- Não mudar o fluxo do `wiki-stage.sh` existente
- Não quebrar o contrato `cleaned/` → `_raw/`

### O que fazer

#### 1. Novo adapter: `session_to_cleaned.py`

Adicionar em `wiki-compiler/adapters/session_to_cleaned.py`:

```python
"""
Adapter: session-NNN.md (context-agent) → cleaned/
Transforma cada sessão em um artefato limpo pronto para ingest.
Preserva: tópicos, decisões, tarefas completadas, descobertas, erros.
Descarta: métricas de token, lista de arquivos modificados, tarefas já obsoletas.
"""

def session_to_cleaned(sessions_dir: Path, out_dir: Path) -> dict:
    """
    Varre sessions/ por arquivos ainda não processados.
    Para cada session-NNN.md:
      1. Extrai seções relevantes (tópicos, decisões, tarefas, descobertas, erros)
      2. Remove ruído (token counts, file lists, back-links internos)
      3. Gera frontmatter {type: session, source_session: NNN, date: YYYY-MM-DD}
      4. Salva como cleaned/<slug>.md (idempotente: pula se já existe)
    """
```

#### 2. Novo adapter: `commandcode_to_cleaned.py`

Adicionar em `wiki-compiler/adapters/commandcode_to_cleaned.py`:

```python
"""
Adapter: ~/.commandcode/plans/*.md → cleaned/
Copia planos gerados pelo Command Code para o pipeline.
Preserva: conteúdo integral (já é markdown limpo).
Adiciona: frontmatter {type: plan, source: command-code, date: YYYY-MM-DD}
"""

def commandcode_to_cleaned(plans_dir: Path, out_dir: Path) -> dict:
    """
    Varre ~/.commandcode/plans/*.md
    Para cada plano:
      1. Lê o arquivo
      2. Adiciona frontmatter se não tiver
      3. Copia para cleaned/<slug>.md (idempotente)
    """
```

#### 3. Estender `wiki-stage.sh` com os novos adapters

Adicionar ao `wiki-stage.sh` existente, após o `superpowers_cleaner` e antes do `pending_to_ar9av_raw`:

```bash
# Passo 1.5: session_to_cleaned — varre context-agent/sessions/
echo "[wiki-stage] Coletando sessões do context-agent..."
python -c "
import sys
sys.path.insert(0, '$WIN_ADAPTERS')
from session_to_cleaned import session_to_cleaned
from pathlib import Path
sessions = Path.home() / '.shared-ai-memory' / 'context-agent' / 'sessions'
report = session_to_cleaned(sessions, Path('$WIN_CLEANED'))
print(f'  Sessions: {report[\"processed\"]} processados, {report[\"skipped_existing\"]} ja existentes')
"

# Passo 1.6: commandcode_to_cleaned — varre ~/.commandcode/plans/
echo "[wiki-stage] Coletando planos do Command Code..."
python -c "
import sys
sys.path.insert(0, '$WIN_ADAPTERS')
from commandcode_to_cleaned import commandcode_to_cleaned
from pathlib import Path
plans_dir = Path.home() / '.commandcode' / 'plans'
report = commandcode_to_cleaned(plans_dir, Path('$WIN_CLEANED'))
print(f'  Planos: {report[\"processed\"]} processados, {report[\"skipped_existing\"]} ja existentes')
"
```

Ordem final do `wiki-stage.sh`:
1. `superpowers_cleaner` (docs de projeto) → `cleaned/`
2. `session_to_cleaned` (sessões) → `cleaned/`
3. `commandcode_to_cleaned` (planos CC) → `cleaned/`
4. `pending_to_ar9av_raw` (tudo) → `vault/_raw/`

#### 4. ACTIVE_CONTEXT.md como fonte especial

O ACTIVE_CONTEXT.md é diferente — é um arquivo vivo que muda a cada sessão. Não faz sentido versioná-lo como arquivos separados. Em vez disso:

**Opção A (simples):** Copiar o ACTIVE_CONTEXT.md inteiro para `_raw/` como `active_context_latest.md` a cada execução. O `/wiki-ingest` vai detectar mudança e criar/atualizar a página `Active Context` no vault.

**Opção B (ideal, mais complexo):** Um adapter `active_context_to_cleaned.py` que extrai apenas as mudanças incrementais (novas decisões, tarefas adicionadas/removidas) e gera um diff markdown.

**Recomendação:** Opção A para já. Simples, sem risco, e o idempotente do `pending_to_ar9av_raw` (que sobrescreve `dst` se existir) garante que só a versão mais recente fica em `_raw/`.

---

## Diagrama pós-correção

```
                    ┌──────────────────────────────────────┐
                    │         wiki-stage.sh                 │
                    │         (orquestrador)                 │
                    └────────┬─────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 superpowers_cleaner   session_to_cleaned   commandcode_to_cleaned
 (Stout/Inova docs)    (context-agent       (~/.commandcode/plans/)
                        sessions/)                │
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                         cleaned/
                             │
                             ▼
                   pending_to_ar9av_raw
                             │
                             ▼
                        vault/_raw/
                             │
                             ▼
                      /wiki-ingest (manual)
                             │
                             ▼
                    wiki-compiler-vault/
                    ├── concepts/
                    ├── projects/
                    ├── journal/       ← sessões viram journal entries
                    ├── references/    ← planos viram references
                    └── synthesis/     ← active context vira synthesis
```

---

## Plano de implementação

| # | Tarefa | Arquivo |
|---|--------|---------|
| 1 | Criar `session_to_cleaned.py` | `wiki-compiler/adapters/` |
| 2 | Criar `commandcode_to_cleaned.py` | `wiki-compiler/adapters/` |
| 3 | Estender `wiki-stage.sh` com novos passos | `wiki-compiler/wiki-stage.sh` |
| 4 | Testar com `bash wiki-stage.sh` seco | terminal |
| 5 | Rodar `/wiki-ingest` para processar os 116+ arquivos acumulados | sessão agent |
