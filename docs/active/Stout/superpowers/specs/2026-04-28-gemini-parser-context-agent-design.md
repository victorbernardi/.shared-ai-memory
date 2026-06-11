# Spec: Gemini Parser para Context-Agent

**Data:** 2026-04-28
**Projeto pai:** LLM Wiki Reforma — Fase 1 (context-agent unificado)
**Plano de referência:** `docs/superpowers/plans/2026-04-23-fase1-context-agent-unificado.md`
**Versão:** 2 (revisada após auditoria)

---

## Problema

O `session_parser.py` do context-agent lê arquivos JSONL (formato Claude Code). O Gemini CLI / Antigravity armazena sessões em `brain/<UUID>/task.md.resolved` e `walkthrough.md.resolved` (Markdown) com metadados em `*.metadata.json`. O comando `save` não encontra nenhum arquivo JSONL no `brain/` e gera sessões vazias — o context-agent é silenciosamente não-funcional para sessões Gemini/Antigravity.

**Prova:** 60 UUIDs em `brain/`, apenas `session-001.md` registrada em toda a história.

---

## Escopo

Este spec cobre exclusivamente o **Gemini Parser** — novo módulo `gemini_parser.py` que habilita o `save` a ler sessões do `brain/`. Entra como **Task 0 da Fase 1**, executada antes das demais.

Fora de escopo: parser para `conversations/<UUID>.pb` (binário), unificação de storage (Tasks 1-11 da Fase 1), instalação Claude Code.

---

## Formato das Sessões Gemini

Cada sessão Gemini = **uma pasta `brain/<UUID>/`** com até 4 arquivos:

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| `task.md.resolved` | Markdown | Checklist de tarefas com status `[x]`/`[/]` |
| `task.md.metadata.json` | JSON | `{ artifactType, summary, updatedAt }` |
| `walkthrough.md.resolved` | Markdown | Sumário narrativo: mudanças, decisões, próximos passos |
| `walkthrough.md.metadata.json` | JSON | `{ artifactType, summary, updatedAt }` |

**Regra de granularidade:** 1 UUID = 1 sessão Gemini = **1 arquivo `session-NNN-antigravity.md`**. Não consolidar UUIDs em uma única sessão.

`walkthrough` pode estar ausente em sessões curtas. `task` é o artefato mínimo garantido. Outros `artifactType` (futuros) são lidos como `.resolved` genérico se existirem.

---

## Arquitetura

### Módulo separado `gemini_parser.py`

Retorna `list[SessionSummary]` (não `SessionEntry`). Por quê: cada UUID já é uma sessão completa; converter para `SessionEntry` e depois remontar via `session_summary.py` é redundante e perde informação. O parser produz `SessionSummary` direto.

`context_manager.py` roteia via `SESSION_ORIGIN`:

```python
# em cmd_save() de context_manager.py
if SESSION_ORIGIN == "antigravity":
    from gemini_parser import save_brain_sessions
    save_brain_sessions()  # processa UUIDs novos, gera N sessões
else:
    # fluxo existente para claude/opencode
    path = get_latest_session_file()
    entries = parse_session_file(path)
    summary = generate_summary(entries, ...)
    save_session_summary(summary)
```

`SESSION_ORIGIN = "gemini"` **não existe** — Gemini CLI compartilha skill com Antigravity, então só `"antigravity"` é usado.

---

## Deduplicação por UUID

**Mecanismo:** arquivo `memory/context-agent/processed_uuids.json` rastreia UUIDs já convertidos em sessão.

```json
{
  "0bc6a84a-5b5a-43bc-a0d2-de73d47880d7": {
    "session_number": 2,
    "saved_at": "2026-04-28T20:30:00Z",
    "walkthrough_updated_at": "2026-04-28T20:23:36Z"
  }
}
```

**Reprocessamento:** UUID já processado é re-salvo (sobrescrevendo `session-NNN-antigravity.md`) **se** `walkthrough_updated_at` no metadata do brain for posterior ao registrado. Caso contrário, pula.

**Por que não usar `last_session_time()` baseado em filename:** o header gerado por `session_summary.py` é `# Sessão NNN — YYYY-MM-DD` (sem hora), granularidade insuficiente para filtrar UUIDs do mesmo dia. Dedup por UUID é o único caminho correto.

---

## Modelo de Dados

### `BrainArtifact` — adicionado em `models.py`

```python
@dataclass
class BrainArtifact:
    uuid: str
    updated_at: datetime              # max(walkthrough_updated_at, task_updated_at)
    walkthrough_updated_at: datetime | None
    task_updated_at: datetime | None
    task_content: str | None
    task_summary: str | None
    walkthrough_content: str | None
    walkthrough_summary: str | None
```

### Mapeamento `BrainArtifact` → `SessionSummary`

| Campo `SessionSummary` | Fonte |
|---|---|
| `session_number` | `get_next_session_number()` |
| `session_id` | `artifact.uuid` |
| `slug` | `walkthrough_summary` ou `task_summary` (fallback) ou `""` |
| `date` | `updated_at.strftime("%Y-%m-%d")` |
| `start_time` / `end_time` | `updated_at.isoformat()` (sem janela real) |
| `duration_minutes` | `0` (Gemini não expõe duração) |
| `model` | `"gemini-antigravity"` (literal) |
| `total_input_tokens` / `output_tokens` / `cache_tokens` | `0` |
| `message_count` / `tool_call_count` | `0` |
| `topics` | extraído de `walkthrough_content` via heurística (headers `## ...`) |
| `decisions` | extraído via `DECISION_MARKERS` em `walkthrough_content` |
| `tasks_completed` | linhas `- [x]` em `task_content` |
| `tasks_pending` | linhas `- [ ]` em `task_content` (com prioridade `media`) |
| `files_modified` | `[]` (não disponível) |
| `findings` | extraído via heurística de `walkthrough_content` |

**Campos vazios são intencionais e não bloqueiam `session_summary.save_session_summary()`** — verificado: a função só itera listas, não divide por contagens.

---

## Funções principais

### `gemini_parser.py`

```python
def list_brain_uuids() -> list[Path]:
    """Lista subpastas UUID dentro de BRAIN_DIR. Tolerante a permissões."""

def parse_brain_artifact(uuid_dir: Path) -> BrainArtifact | None:
    """Lê os 4 arquivos. Retorna None se nem task nem walkthrough existirem.
    Tolerante a metadata.json mal-formado ou ausente (usa mtime do .resolved)."""

def artifact_to_summary(artifact: BrainArtifact, session_number: int) -> SessionSummary:
    """Converte para SessionSummary. Aplica heurísticas de extração."""

def load_processed_uuids() -> dict[str, dict]:
    """Lê processed_uuids.json. Retorna {} se não existir."""

def save_processed_uuids(state: dict[str, dict]) -> None:
    """Escreve processed_uuids.json atomicamente (write+rename)."""

def save_brain_sessions() -> list[Path]:
    """Entry point chamado por context_manager.py.
    1. Lista UUIDs em brain/
    2. Filtra os já processados (exceto se walkthrough_updated_at mudou)
    3. Para cada UUID: parse → summary → save_session_summary
    4. Atualiza processed_uuids.json
    Retorna lista de paths das sessões salvas (vazia se nada novo)."""
```

### `context_manager.py`

Refatorar `cmd_save()` para o routing:

```python
def cmd_save() -> None:
    """Salva contexto da sessão atual."""
    if config.SESSION_ORIGIN == "antigravity":
        from gemini_parser import save_brain_sessions
        saved = save_brain_sessions()
        print(f"[OK] {len(saved)} sessao(oes) salva(s).")
    else:
        # fluxo existente
        path = get_latest_session_file()
        ...
```

---

## Configuração

### `config.py` — sem mudanças necessárias para Task 0

`BRAIN_DIR` já existe:
```python
BRAIN_DIR = USER_PROFILE / ".gemini" / "antigravity" / "brain"
```

Adicionar apenas:
```python
PROCESSED_UUIDS_PATH = DATA_DIR / "processed_uuids.json"
```

### Ajuste necessário na **Fase 1 Task 2**

A versão atual do plano define `CLAUDE_SESSION_DIR` no config do Antigravity:
```python
CLAUDE_SESSION_DIR = CLAUDE_PROJECTS_DIR / "C--Projetos-Stout"
```

Antigravity não usa `CLAUDE_SESSION_DIR` (esse fluxo passa a ser apenas para Claude Code). **Remover essa linha do config Antigravity** quando executar Task 2 da Fase 1.

---

## Deploy — sem tocar no `Plugins/`

`C:\Projetos\Stout\Plugins\antigravity-awesome-skills\` é um clone do repo público `github.com/sickn33/antigravity-awesome-skills`. **NÃO modificar** — qualquer mudança lá vai gerar conflito no próximo `git pull`.

**Estratégia de deploy:** `gemini_parser.py` é criado diretamente em:
- `C:\Projetos\Stout\antigravity\skills\context-agent\scripts\` (golden copy efetiva do Stout)
- `C:\Motores-LLM\antigravity\skills\context-agent\scripts\` (cópia espelhada)
- `C:\Users\victor.bernardi\.gemini\antigravity\skills\context-agent\scripts\` (runtime Gemini CLI)

Sync entre os 3 locais é feito manualmente nessa task; automação fica para `promote-to-prod.ps1` (planejado em fase posterior). Novos arquivos no Plugins/ ficam como **trabalho upstream** — opcional submeter PR depois.

---

## Testes

Arquivo: `C:\Projetos\Stout\tests\context_agent\test_gemini_parser.py`

### Unitários — parsing

| Teste | O que valida |
|---|---|
| `test_parse_brain_artifact_reads_walkthrough_and_task` | UUID completo → todos os campos preenchidos |
| `test_parse_brain_artifact_tolerates_missing_walkthrough` | Só task → `walkthrough_*=None`, sem exceção |
| `test_parse_brain_artifact_returns_none_for_empty_dir` | UUID sem `.resolved` → `None` |
| `test_parse_brain_artifact_handles_malformed_metadata` | JSON inválido → cai para `mtime` do arquivo, não crasha |
| `test_artifact_updated_at_uses_max_of_walkthrough_and_task` | Pega o mais recente entre os dois |

### Unitários — conversão

| Teste | O que valida |
|---|---|
| `test_artifact_to_summary_extracts_tasks_completed_from_brackets_x` | `- [x] foo` → `tasks_completed=["foo"]` |
| `test_artifact_to_summary_extracts_tasks_pending_from_brackets_empty` | `- [ ] bar` → `tasks_pending=["bar"]` |
| `test_artifact_to_summary_extracts_topics_from_h2_headers` | `## Mudanças Realizadas` → topic |
| `test_artifact_to_summary_uses_walkthrough_summary_as_slug` | `walkthrough_summary` → `slug` |
| `test_artifact_to_summary_falls_back_to_task_summary_for_slug` | Sem walkthrough → usa `task_summary` |
| `test_artifact_to_summary_model_is_gemini_antigravity` | `model == "gemini-antigravity"` |

### Unitários — dedup

| Teste | O que valida |
|---|---|
| `test_save_brain_sessions_skips_processed_uuids` | UUID em `processed_uuids.json` não é reprocessado |
| `test_save_brain_sessions_reprocesses_if_walkthrough_changed` | `walkthrough_updated_at` mais recente → reprocessa |
| `test_save_brain_sessions_creates_one_file_per_uuid` | 3 UUIDs novos → 3 arquivos `session-NNN-antigravity.md` |
| `test_save_brain_sessions_updates_processed_uuids_atomically` | Write+rename, `.tmp` removido |

### Routing

| Teste | O que valida |
|---|---|
| `test_cmd_save_uses_gemini_parser_when_origin_is_antigravity` | `SESSION_ORIGIN="antigravity"` → chama `save_brain_sessions` |
| `test_cmd_save_uses_jsonl_parser_when_origin_is_claude` | `SESSION_ORIGIN="claude"` → chama `parse_session_file` |

**Total:** 16 testes. **Execução:** `pytest tests/context_agent/ -v` (junto com Fase 1).

---

## Ordem de Execução (Fase 1 revisada)

```
Task 0: Gemini Parser (este spec)        ← NOVO, executa primeiro
Task 1: Estrutura unificada               ← Fase 1 original
Task 2: config.py Antigravity             ← Fase 1, ajustar para remover CLAUDE_SESSION_DIR
Task 3: SESSION_ORIGIN OpenCode
Task 4: Migrar dados Antigravity
Task 5: Origin tagging                    ← Após este, save_brain_sessions já gera com sufixo
Task 6: Instalar Claude Code
Task 7: Stop hook Claude Code
Task 8: Limpar SKILL.md Antigravity
Task 9: Atualizar SKILL.md OpenCode
Task 10: MEMORY.md
Task 11: Integração end-to-end
```

**Dependência crítica:** Task 5 (origin tagging) só pode ser executada DEPOIS de Task 0. Task 0 inicialmente gera `session-NNN.md` (sem sufixo); Task 5 muda para `session-NNN-antigravity.md` e refatora `save_brain_sessions` junto.

---

## Critérios de Sucesso

- [ ] `python context_manager.py save` em ambiente Antigravity processa UUIDs em `brain/` e gera múltiplos `session-NNN-antigravity.md` (1 por UUID)
- [ ] `processed_uuids.json` criado em `memory/context-agent/`; segundo `save` não reprocessa
- [ ] Edição manual em `brain/<UUID>/walkthrough.md.resolved` (mudando timestamp do metadata) → terceiro `save` reprocessa só esse UUID
- [ ] `pytest tests/context_agent/test_gemini_parser.py -v` → 16 passed
- [ ] Sessões Claude Code/OpenCode continuam funcionando sem regressão (regressão checada via `pytest tests/context_agent/ -v` completo)
- [ ] `gemini_parser.py` presente em 3 locais (Stout antigravity/, Motores-LLM, .gemini); `Plugins/` intocado

---

## Riscos Conhecidos

1. **Heurística de extração de topics/decisions pode ser ruidosa.** O walkthrough é prosa livre; markers podem capturar falsos positivos. Mitigação: revisar primeiras 5 sessões reais geradas e ajustar markers se necessário.

2. **`updatedAt` em formato ISO 8601 com timezone Z.** Python 3.11+ aceita via `datetime.fromisoformat()`; em versões anteriores precisa de `dateutil` ou parsing manual. Verificar `python --version` no ambiente alvo antes de implementar.

3. **Conflito de `session_number` em paralelo.** Se Claude Code e Antigravity rodarem `save` simultaneamente, ambos chamam `get_next_session_number()` e podem alocar o mesmo número. Risco baixo no uso atual (não há paralelismo); fica documentado como limitação.

4. **Acúmulo histórico — 60 UUIDs no primeiro save.** Primeira execução vai gerar 60 sessões de uma vez. Aceitável; é catch-up de histórico. Documentado para o usuário não estranhar.
