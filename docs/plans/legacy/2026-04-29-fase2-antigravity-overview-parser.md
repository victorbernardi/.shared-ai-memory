# Fase 2 — Parser de sessões Antigravity (overview.txt)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer `context_manager save` funcionar no Antigravity/Gemini CLI lendo as sessões reais do brain.

**Architecture:** O brain do Antigravity grava cada sessão em `brain/<uuid>/.system_generated/logs/overview.txt` no formato **NDJSON** (uma linha por step). O `_parse_raw_entry()` em `session_parser.py` já entende esse formato — falta só a descoberta dos arquivos: hoje faz `glob("*.jsonl")` flat na raiz, precisa fazer `glob("**/overview.txt")` recursivo. Sem novo parser, sem dependência de Protobuf.

**Tech Stack:** Python 3.13, pytest, NDJSON nativo (`json.loads` linha a linha — já implementado).

---

## Diagnóstico (debug Antigravity, 2026-04-29)

| Componente | Estado atual | Bug |
|---|---|---|
| `_parse_raw_entry()` (session_parser.py L45–L95) | Já trata `USER_INPUT`, `PLANNER_RESPONSE`, `step_index`, `created_at`, `tool_calls.args` | ✅ funciona |
| `get_latest_session_file()` (L209–L218) | `CLAUDE_SESSION_DIR.glob("*.jsonl")` flat na raiz | ❌ Antigravity tem subdirs `<uuid>/.system_generated/logs/overview.txt` |
| `get_all_session_files()` (L221–L229) | Idem | ❌ idem |
| `CLAUDE_SESSION_DIR` (config.py) | `BRAIN_DIR = ~/.gemini/antigravity/brain` | ✅ apontamento correto, só falta busca recursiva |

**Conclusão:** ~30 linhas de código + ajuste no config.py. Não precisa parser .pb.

---

## Estrutura de arquivos

| Arquivo | Mudança |
|---|---|
| `antigravity/skills/context-agent/scripts/session_parser.py` | Modify: 2 funções de discovery |
| `antigravity/skills/context-agent/scripts/config.py` | Modify: remover `CLAUDE_SESSION_DIR = BRAIN_DIR` (já está correto, só atualiza comentário) |
| `tests/context_agent/test_antigravity_parser.py` | Create: testes de discovery + parse end-to-end |
| `tests/context_agent/test_session_parser_source.py` | Modify: regression test atual espera `None` — invertir para esperar Path |

---

## Task 1 — Descoberta recursiva de overview.txt

**Files:**
- Modify: `antigravity/skills/context-agent/scripts/session_parser.py:209-229`

- [ ] **Step 1: Escrever teste falhando**

`tests/context_agent/test_antigravity_parser.py` (novo):
```python
"""
Fase 2 — parser do brain Antigravity (overview.txt em NDJSON).
"""
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(r"C:\Projetos\Stout\antigravity\skills\context-agent\scripts")


def _load(mod_name: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPTS / f"{mod_name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_get_latest_session_file_returns_overview_txt():
    parser = _load("session_parser")
    result = parser.get_latest_session_file()
    assert result is not None, "Esperava overview.txt mais recente, recebeu None"
    assert result.name == "overview.txt", f"Esperava overview.txt, recebeu {result.name}"
    assert ".system_generated" in str(result), (
        f"Esperava caminho com .system_generated, recebeu {result}"
    )


def test_get_all_session_files_returns_multiple_overviews():
    parser = _load("session_parser")
    result = parser.get_all_session_files()
    assert len(result) >= 2, f"Esperava pelo menos 2 sessões, recebeu {len(result)}"
    assert all(p.name == "overview.txt" for p in result), (
        "Todos os resultados devem ser overview.txt"
    )


def test_files_sorted_by_mtime_desc():
    parser = _load("session_parser")
    files = parser.get_all_session_files()
    mtimes = [f.stat().st_mtime for f in files]
    assert mtimes == sorted(mtimes, reverse=True), "Arquivos devem estar em ordem desc por mtime"
```

- [ ] **Step 2: Rodar teste, verificar que falha**

Run: `python -m pytest tests/context_agent/test_antigravity_parser.py -v`
Expected: 3 FAIL — `get_latest_session_file` retorna None / lista vazia.

- [ ] **Step 3: Implementar discovery recursivo**

Em `session_parser.py`, substituir as duas funções de discovery (linhas 209–229):

```python
def get_latest_session_file() -> Optional[Path]:
    """Encontra o overview.txt mais recente em qualquer subdir do brain."""
    if not CLAUDE_SESSION_DIR.exists():
        return None
    overviews = sorted(
        CLAUDE_SESSION_DIR.glob("*/.system_generated/logs/overview.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return overviews[0] if overviews else None


def get_all_session_files() -> list[Path]:
    """Retorna todos os overview.txt do brain ordenados por mtime desc."""
    if not CLAUDE_SESSION_DIR.exists():
        return []
    return sorted(
        CLAUDE_SESSION_DIR.glob("*/.system_generated/logs/overview.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
```

⚠️ **Por que `*/.system_generated/...` e não `**/overview.txt`:** o glob recursivo `**` percorreria toda a árvore do brain. O padrão `*/.system_generated/logs/overview.txt` lê apenas o diretório imediatamente abaixo do brain (`<uuid>/`), que é exatamente onde o Antigravity grava — mais rápido e mais correto (não pega `overview.txt` em outros lugares).

- [ ] **Step 4: Rodar teste, verificar que passa**

Run: `python -m pytest tests/context_agent/test_antigravity_parser.py -v`
Expected: 3 PASS.

- [ ] **Step 5: Atualizar regression test contraditório**

`tests/context_agent/test_session_parser_source.py` tem hoje:
```python
def test_get_latest_session_file_returns_none_gracefully():
    result = parser.get_latest_session_file()
    assert result is None, ...
```

Inverter para o novo comportamento:
```python
def test_get_latest_session_file_returns_overview():
    result = parser.get_latest_session_file()
    assert result is not None, "Após Fase 2, deve retornar overview.txt"
    assert result.suffix == ".txt"


def test_get_all_session_files_returns_overviews():
    result = parser.get_all_session_files()
    assert len(result) > 0, "Brain tem sessões — não deve mais retornar []"
```

E remover `test_brain_has_no_jsonl_files` (era um sanity check de Fase 1, agora obsoleto).

- [ ] **Step 6: Rodar suite completa**

Run: `python -m pytest tests/context_agent/ -v`
Expected: todos os testes passam (38 atuais + 3 novos – 2 invertidos = 39 PASS).

- [ ] **Step 7: Commit**

```bash
git add antigravity/skills/context-agent/scripts/session_parser.py \
        tests/context_agent/test_antigravity_parser.py \
        tests/context_agent/test_session_parser_source.py
git commit -m "feat(fase2-t1): discovery recursivo de overview.txt no brain Antigravity

session_parser.py agora encontra brain/<uuid>/.system_generated/logs/overview.txt
em vez de procurar .jsonl flat. _parse_raw_entry() já tratava o formato
NDJSON do Antigravity (USER_INPUT/PLANNER_RESPONSE). Não precisou parser .pb."
```

---

## Task 2 — Smoke test end-to-end (parse + save)

**Files:**
- Test: `tests/context_agent/test_antigravity_e2e.py`

- [ ] **Step 1: Escrever teste e2e**

```python
"""
Fase 2 — e2e: discovery → parse → SessionSummary.
"""
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(r"C:\Projetos\Stout\antigravity\skills\context-agent\scripts")


def _load(mod_name: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(mod_name, SCRIPTS / f"{mod_name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_parse_latest_session_extracts_user_messages():
    parser = _load("session_parser")
    latest = parser.get_latest_session_file()
    assert latest is not None
    entries = parser.parse_session_file(latest)
    user_msgs = parser.extract_user_messages(entries)
    assert user_msgs, "Sessão real deve ter pelo menos uma mensagem de usuário"


def test_parse_extracts_tool_calls():
    parser = _load("session_parser")
    latest = parser.get_latest_session_file()
    entries = parser.parse_session_file(latest)
    tool_calls = parser.extract_tool_calls(entries)
    assert tool_calls, "Sessão real deve ter chamadas de ferramentas"
    # Antigravity tools: view_file, list_dir, edit_file, run_command, etc.
    names = {tc.get("name") for tc in tool_calls}
    assert names, f"tool_calls devem ter campo 'name'. Recebido: {tool_calls[:2]}"


def test_parse_extracts_metadata():
    parser = _load("session_parser")
    latest = parser.get_latest_session_file()
    entries = parser.parse_session_file(latest)
    meta = parser.get_session_metadata(entries)
    assert meta.get("start_time"), "Metadata deve ter start_time"
    assert meta.get("message_count", 0) > 0
```

- [ ] **Step 2: Rodar teste**

Run: `python -m pytest tests/context_agent/test_antigravity_e2e.py -v`
Expected: 3 PASS (parser já lida com formato Antigravity).

- [ ] **Step 3: Smoke test do CLI**

```bash
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py save
```
Expected stdout: cria `memory/context-agent/sessions/session-YYYYMMDD-HHMMSS-antigravity-XXXXXXXX.md`.

Validar:
```bash
ls -lt C:/Projetos/Stout/memory/context-agent/sessions/ | head -3
```

- [ ] **Step 4: Inspecionar conteúdo do save**

Abrir o arquivo gerado e conferir:
- Título com data correta
- Pelo menos uma seção (Tópicos / Decisões / Tarefas)
- Tool calls do Antigravity convertidos (view_file, edit_file, etc.)

Se algum campo estiver vazio (ex.: `model` em branco, `duration_minutes=0`), abrir issue na Task 3 — não bloqueia.

- [ ] **Step 5: Commit**

```bash
git add tests/context_agent/test_antigravity_e2e.py
git commit -m "test(fase2-t2): e2e test parse → SessionSummary do brain Antigravity"
```

---

## Task 3 — Polimento de campos extraídos (opcional)

**Disparar apenas se Task 2 Step 4 mostrar campos vazios significativos.**

Possíveis ajustes em `_parse_raw_entry()`:

- `model`: Antigravity grava em `model` ou em `metadata.model`? Inspecionar `overview.txt` cru.
- `duration_minutes`: `created_at` no Antigravity é ISO 8601 — já deve funcionar via `datetime.fromisoformat`, validar.
- `slug`: Antigravity não tem slug — ok manter vazio.

- [ ] **Step 1: Inspecionar 1 overview.txt completo**

```bash
head -200 C:/Users/victor.bernardi/.gemini/antigravity/brain/<uuid>/.system_generated/logs/overview.txt
```

- [ ] **Step 2: Para cada campo vazio, ajustar `_parse_raw_entry()` com fallback**

Padrão: `raw.get("campo_claude", raw.get("campo_antigravity", default))`.

- [ ] **Step 3: Adicionar teste de regressão para o campo**

- [ ] **Step 4: Commit por campo ajustado**

---

## Task 4 — Documentar no plano de Fase 1 que o gap fechou

**Files:**
- Modify: `docs/superpowers/plans/2026-04-28-fase1-correcoes.md` (seção "Fase 2 pendente")
- Modify: `antigravity/skills/context-agent/scripts/config.py:40-45` (atualizar comentário TODO)

- [ ] **Step 1: Atualizar comentário em config.py**

Substituir:
```python
# ATENÇÃO: o brain do Antigravity armazena sessões como .pb (protobuf),
# NÃO como .jsonl. Por isso get_latest_session_file() retorna None aqui —
# comportamento esperado e tratado com graceful degradation.
# TODO (Fase 2): implementar parser .pb para Antigravity ou exportar
#   sessões do brain para um formato legível pelo session_parser.
CLAUDE_SESSION_DIR = BRAIN_DIR
```

Por:
```python
# Brain do Antigravity grava cada sessão em <uuid>/.system_generated/logs/overview.txt
# (NDJSON). session_parser.py faz discovery recursiva nesse padrão.
# Os arquivos .pb existem no brain mas não são necessários — overview.txt já
# contém o histórico legível com USER_INPUT, PLANNER_RESPONSE, tool_calls.
CLAUDE_SESSION_DIR = BRAIN_DIR
```

- [ ] **Step 2: Marcar Fase 2 como concluída no plano de correções**

Em `2026-04-28-fase1-correcoes.md`, seção final:
```markdown
- [x] Fase 2 — parser overview.txt (concluído em 2026-04-29, ver `2026-04-29-fase2-antigravity-overview-parser.md`)
```

- [ ] **Step 3: Commit**

```bash
git add antigravity/skills/context-agent/scripts/config.py \
        docs/superpowers/plans/2026-04-28-fase1-correcoes.md
git commit -m "docs(fase2-t4): fechar gap Fase 2 — overview.txt em vez de parser .pb"
```

---

## Self-review

**Cobertura:**
- [x] Bug 1 (filtro `.jsonl` restritivo) → Task 1 Step 3 (`overview.txt`)
- [x] Bug 2 (busca rasa) → Task 1 Step 3 (glob com `*/.system_generated/...`)
- [x] Bug 3 (formato `.pb`) → não aplica, `overview.txt` é NDJSON parseável

**O que NÃO está no escopo:**
- Parser de `.pb` (Protobuf) — desnecessário, `overview.txt` cobre o caso
- Mudança em `config.py` que afete OpenCode/Claude Code — eles usam `CLAUDE_SESSION_DIR` próprio, não o do brain
- Refatorar `_parse_raw_entry()` — já trata o formato Antigravity

**Risco de regressão:**
- Claude Code (motor `claude`) lê `~/.claude/projects/C--Projetos-Stout/*.jsonl` — discovery diferente. Como o `session_parser.py` é compartilhado entre os 3 motores, **o discovery precisa ser polimórfico**. Decidir em Task 1 Step 3:
  - (a) Detectar formato pelo `CLAUDE_SESSION_DIR.name` ou existência de `*.jsonl` na raiz vs subdirs.
  - (b) Manter dois métodos (`_discover_jsonl()`, `_discover_overview()`) e escolher por env/config.
  - **Recomendado:** (a) — fallback automático: tenta `*.jsonl` flat primeiro, se vazio tenta `*/.system_generated/logs/overview.txt`. Mais simples e funciona para qualquer motor.

**Ajuste no Task 1 Step 3 dado o risco acima:**

```python
def _discover_session_files() -> list[Path]:
    if not CLAUDE_SESSION_DIR.exists():
        return []
    # Claude Code: <project>/<uuid>.jsonl
    flat = list(CLAUDE_SESSION_DIR.glob("*.jsonl"))
    if flat:
        return sorted(flat, key=lambda p: p.stat().st_mtime, reverse=True)
    # Antigravity/Gemini: <uuid>/.system_generated/logs/overview.txt
    nested = list(CLAUDE_SESSION_DIR.glob("*/.system_generated/logs/overview.txt"))
    return sorted(nested, key=lambda p: p.stat().st_mtime, reverse=True)


def get_latest_session_file() -> Optional[Path]:
    files = _discover_session_files()
    return files[0] if files else None


def get_all_session_files() -> list[Path]:
    return _discover_session_files()
```

Isso preserva compatibilidade com Claude Code (formato `.jsonl`) sem ramificação por motor.
