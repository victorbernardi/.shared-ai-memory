# OpenCode Context Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portar o `context-agent` completo do `antigravity-awesome-skills-main` para o Stout/OpenCode, preservando a memoria operacional completa e acoplando o wiki apenas como etapa posterior e separada.

**Architecture:** A skill sera copiada para `.opencode/skills/context-agent/` com o core intacto (`save`, `load`, `status`, `search`, `maintain`, `archive`). Os dados operacionais saem de `~/.gemini/antigravity/...` e passam a viver em `C:/Projetos/Stout/memory/`, enquanto o transcript bruto continua vindo do ambiente Claude/OpenCode em `~/.claude/`. O carregamento automatico no inicio da sessao passa a ocorrer via `memory/MEMORY.md` incluso em `.opencode/opencode.json`; o handoff para wiki fica fora do core e nao deve ser implementado nesta etapa.

**Tech Stack:** Python 3 stdlib, Markdown, SQLite FTS5, OpenCode config JSON

---

## File Map

| Arquivo | Acao | Responsabilidade |
|---|---|---|
| `C:/Users/victor.bernardi/antigravity-awesome-skills-main/skills/context-agent/SKILL.md` | Referencia | Skill fonte limpa |
| `C:/Users/victor.bernardi/antigravity-awesome-skills-main/skills/context-agent/scripts/*.py` | Referencia | Core da memoria operacional |
| `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md` | Criar | Skill portada para OpenCode |
| `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/*.py` | Criar | Core portado e adaptado ao Stout/OpenCode |
| `C:/Projetos/Stout/.opencode/skills/context-agent/references/*.md` | Criar | Referencias da skill |
| `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_parser_latest_session.py` | Criar | Testa resolucao da sessao mais recente no formato atual do OpenCode |
| `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_memory_sync.py` | Criar | Testa sincronizacao `ACTIVE_CONTEXT.md` -> `MEMORY.md` |
| `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_context_manager_init.py` | Criar | Testa bootstrap dos diretorios/arquivos |
| `C:/Projetos/Stout/.opencode/opencode.json` | Modificar | Carregar `memory/MEMORY.md` no prompt do OpenCode |
| `C:/Projetos/Stout/.opencode/skills/SKILLS_CHANGELOG.md` | Modificar | Registrar a portacao |
| `C:/Projetos/Stout/memory/ACTIVE_CONTEXT.md` | Criar em runtime | Estado curto consolidado |
| `C:/Projetos/Stout/memory/MEMORY.md` | Criar em runtime | Arquivo carregado no inicio da sessao |
| `C:/Projetos/Stout/memory/PROJECT_REGISTRY.md` | Criar em runtime | Registro de projetos ativos |
| `C:/Projetos/Stout/memory/context-agent/sessions/session-NNN.md` | Criar em runtime | Historico resumido por sessao |
| `C:/Projetos/Stout/memory/context-agent/archive/` | Criar em runtime | Arquivo de sessoes antigas |
| `C:/Projetos/Stout/memory/context-agent/context.db` | Criar em runtime | Busca FTS5 |

---

## Task 1: Portar a skill fonte para o Stout

**Files:**
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/config.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/active_context.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/compressor.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_loader.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/models.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/project_registry.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/requirements.txt`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/search.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/session_parser.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/session_summary.py`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/references/compression-rules.md`
- Create: `C:/Projetos/Stout/.opencode/skills/context-agent/references/context-format.md`

- [ ] **Step 1: Criar a estrutura de diretorios destino**

Run:

```powershell
New-Item -ItemType Directory -Force "C:\Projetos\Stout\.opencode\skills\context-agent\scripts"
New-Item -ItemType Directory -Force "C:\Projetos\Stout\.opencode\skills\context-agent\references"
New-Item -ItemType Directory -Force "C:\Projetos\Stout\.opencode\skills\context-agent\tests"
```

Expected: os tres diretorios existem sem erro.

- [ ] **Step 2: Copiar os arquivos fonte sem alterar conteudo ainda**

Run:

```powershell
Copy-Item "C:\Users\victor.bernardi\antigravity-awesome-skills-main\skills\context-agent\SKILL.md" "C:\Projetos\Stout\.opencode\skills\context-agent\SKILL.md"
Copy-Item "C:\Users\victor.bernardi\antigravity-awesome-skills-main\skills\context-agent\scripts\*.py" "C:\Projetos\Stout\.opencode\skills\context-agent\scripts\"
Copy-Item "C:\Users\victor.bernardi\antigravity-awesome-skills-main\skills\context-agent\scripts\requirements.txt" "C:\Projetos\Stout\.opencode\skills\context-agent\scripts\requirements.txt"
Copy-Item "C:\Users\victor.bernardi\antigravity-awesome-skills-main\skills\context-agent\references\*.md" "C:\Projetos\Stout\.opencode\skills\context-agent\references\"
```

Expected: todos os arquivos listados no File Map existem em `.opencode/skills/context-agent/`.

- [ ] **Step 3: Verificar a copia base**

Run:

```powershell
Get-ChildItem "C:\Projetos\Stout\.opencode\skills\context-agent" -Recurse | Select-Object FullName
```

Expected: `SKILL.md`, `scripts/*.py`, `scripts/requirements.txt`, `references/*.md`, `tests/`.

- [ ] **Step 4: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/skills/context-agent"
git -C "C:\Projetos\Stout" commit -m "feat: port clean context-agent into opencode skills"
```

---

## Task 2: Adaptar paths e storage para o Stout

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/config.py`
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/active_context.py`
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py`

- [ ] **Step 1: Escrever o teste de bootstrap dos caminhos do Stout**

Create `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_context_manager_init.py`:

```python
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class ContextManagerInitTest(unittest.TestCase):
    def test_init_creates_stout_memory_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"STOUT_CONTEXT_AGENT_ROOT": tmp}, clear=False):
                import importlib
                config = importlib.import_module("config")
                importlib.reload(config)
                context_manager = importlib.import_module("context_manager")
                importlib.reload(context_manager)

                args = type("Args", (), {})()
                context_manager.cmd_init(args)

                self.assertTrue((Path(tmp) / "sessions").exists())
                self.assertTrue((Path(tmp).parent / "ACTIVE_CONTEXT.md").exists())
                self.assertTrue((Path(tmp).parent / "PROJECT_REGISTRY.md").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar o teste e confirmar falha antes da adaptacao**

Run:

```powershell
python -m unittest "C:\Projetos\Stout\.opencode\skills\context-agent\tests\test_context_manager_init.py" -v
```

Expected: FAIL porque o `config.py` ainda aponta para paths do ambiente original.

- [ ] **Step 3: Adaptar `config.py` para o layout do Stout**

Substituir o bloco de paths por:

```python
import os
from pathlib import Path

STOUT_ROOT = Path(os.environ.get("STOUT_ROOT", r"C:/Projetos/Stout"))
MEMORY_ROOT = STOUT_ROOT / "memory"
CONTEXT_AGENT_DATA_ROOT = MEMORY_ROOT / "context-agent"

DATA_DIR = CONTEXT_AGENT_DATA_ROOT
SESSIONS_DIR = DATA_DIR / "sessions"
ARCHIVE_DIR = DATA_DIR / "archive"
LOGS_DIR = DATA_DIR / "logs"
ACTIVE_CONTEXT_PATH = MEMORY_ROOT / "ACTIVE_CONTEXT.md"
PROJECT_REGISTRY_PATH = MEMORY_ROOT / "PROJECT_REGISTRY.md"
DB_PATH = DATA_DIR / "context.db"
MEMORY_DIR = MEMORY_ROOT
MEMORY_MD_PATH = MEMORY_ROOT / "MEMORY.md"

CLAUDE_HOME = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".claude"
CLAUDE_SESSIONS_DIR = CLAUDE_HOME / "sessions"
CLAUDE_HISTORY_PATH = CLAUDE_HOME / "history.jsonl"
```

- [ ] **Step 4: Adaptar o cabecalho do `MEMORY.md` em `active_context.py`**

Substituir o cabecalho hardcoded por:

```python
header = (
    "<!-- Auto-generated by context-agent. Para detalhes: "
    "python C:\\Projetos\\Stout\\.opencode\\skills\\context-agent\\scripts\\context_manager.py load -->\n\n"
)
```

- [ ] **Step 5: Rodar o teste novamente e confirmar sucesso**

Run:

```powershell
python -m unittest "C:\Projetos\Stout\.opencode\skills\context-agent\tests\test_context_manager_init.py" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/skills/context-agent/scripts/config.py" ".opencode/skills/context-agent/scripts/active_context.py" ".opencode/skills/context-agent/tests/test_context_manager_init.py"
git -C "C:\Projetos\Stout" commit -m "feat: move context-agent storage into Stout memory"
```

---

## Task 3: Adaptar o parser para o formato atual do OpenCode/Claude

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/session_parser.py`
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py`
- Test: `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_parser_latest_session.py`

- [ ] **Step 1: Escrever o teste para resolver a sessao mais recente no formato atual**

Create `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_parser_latest_session.py`:

```python
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class SessionParserLatestSessionTest(unittest.TestCase):
    def test_latest_session_uses_history_jsonl_and_latest_session_id(self):
        with tempfile.TemporaryDirectory() as home:
            claude_dir = Path(home) / ".claude"
            sessions_dir = claude_dir / "sessions"
            sessions_dir.mkdir(parents=True)

            latest = sessions_dir / "44212.json"
            latest.write_text(json.dumps({
                "pid": 44212,
                "sessionId": "latest-session-id",
                "cwd": "C:/Projetos/Stout",
                "startedAt": 1776880983825,
                "version": "2.1.117",
                "kind": "interactive",
                "entrypoint": "cli"
            }), encoding="utf-8")

            history_path = claude_dir / "history.jsonl"
            history_path.write_text(
                json.dumps({"type": "user", "sessionId": "other-session", "message": {"role": "user", "content": "old"}}) + "\n" +
                json.dumps({"type": "user", "sessionId": "latest-session-id", "message": {"role": "user", "content": "current"}}) + "\n",
                encoding="utf-8"
            )

            with mock.patch.dict(os.environ, {"USERPROFILE": home}, clear=False):
                import importlib
                config = importlib.import_module("config")
                importlib.reload(config)
                parser = importlib.import_module("session_parser")
                importlib.reload(parser)

                resolved = parser.get_latest_session_file()

                self.assertEqual(resolved, history_path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar o teste e confirmar falha antes da adaptacao**

Run:

```powershell
python -m unittest "C:\Projetos\Stout\.opencode\skills\context-agent\tests\test_parser_latest_session.py" -v
```

Expected: FAIL porque a versao atual ainda procura `*.jsonl` dentro de `~/.claude/sessions/`.

- [ ] **Step 3: Adaptar `session_parser.py` para resolver a sessao atual do OpenCode**

Adicionar helpers e ajustar `get_latest_session_file()` para:

```python
def _get_latest_session_id() -> str | None:
    if not CLAUDE_SESSIONS_DIR.exists():
        return None
    session_files = sorted(CLAUDE_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not session_files:
        return None
    raw = json.loads(session_files[0].read_text(encoding="utf-8"))
    return raw.get("sessionId")


def get_latest_session_file() -> Optional[Path]:
    if CLAUDE_HISTORY_PATH.exists() and _get_latest_session_id():
        return CLAUDE_HISTORY_PATH
    return None
```

- [ ] **Step 4: Filtrar o `history.jsonl` pela sessao mais recente em `parse_session_file()`**

Atualizar o loop de parse para:

```python
latest_session_id = _get_latest_session_id() if path == CLAUDE_HISTORY_PATH else None

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue

        if latest_session_id and raw.get("sessionId") != latest_session_id:
            continue

        entry = _parse_raw_entry(raw)
        if entry:
            entries.append(entry)
```

- [ ] **Step 5: Rodar o teste novamente e confirmar sucesso**

Run:

```powershell
python -m unittest "C:\Projetos\Stout\.opencode\skills\context-agent\tests\test_parser_latest_session.py" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/skills/context-agent/scripts/session_parser.py" ".opencode/skills/context-agent/tests/test_parser_latest_session.py"
git -C "C:\Projetos\Stout" commit -m "fix: adapt context-agent parser to current OpenCode session format"
```

---

## Task 4: Sincronizar `ACTIVE_CONTEXT.md` com `MEMORY.md` e carregar no OpenCode

**Files:**
- Test: `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_memory_sync.py`
- Modify: `C:/Projetos/Stout/.opencode/opencode.json`

- [ ] **Step 1: Escrever o teste de sincronizacao para `MEMORY.md`**

Create `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_memory_sync.py`:

```python
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class MemorySyncTest(unittest.TestCase):
    def test_sync_to_memory_copies_active_context_with_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            stout_root = Path(tmp) / "Stout"
            memory_root = stout_root / "memory"
            memory_root.mkdir(parents=True)
            active_path = memory_root / "ACTIVE_CONTEXT.md"
            active_path.write_text("# Contexto Ativo\n\n## Tarefas Pendentes\n- [ ] testar\n", encoding="utf-8")

            with mock.patch.dict(os.environ, {"STOUT_ROOT": str(stout_root)}, clear=False):
                import importlib
                config = importlib.import_module("config")
                importlib.reload(config)
                active_context = importlib.import_module("active_context")
                importlib.reload(active_context)

                active_context.sync_to_memory()

                memory_path = memory_root / "MEMORY.md"
                self.assertTrue(memory_path.exists())
                content = memory_path.read_text(encoding="utf-8")
                self.assertIn("Auto-generated by context-agent", content)
                self.assertIn("## Tarefas Pendentes", content)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Rodar o teste e confirmar sucesso**

Run:

```powershell
python -m unittest "C:\Projetos\Stout\.opencode\skills\context-agent\tests\test_memory_sync.py" -v
```

Expected: PASS.

- [ ] **Step 3: Adicionar `memory/MEMORY.md` ao carregamento do OpenCode**

Atualizar `.opencode/opencode.json` para:

```json
"instructions": [
  "GEMINI.md",
  "MISSION_STOUT.md",
  "memory/ecosystem.md",
  "memory/preferences.md",
  "memory/MEMORY.md"
]
```

- [ ] **Step 4: Verificar o diff estrutural do config**

Run:

```powershell
git -C "C:\Projetos\Stout" diff -- ".opencode/opencode.json"
```

Expected: apenas uma nova entrada em `instructions` para `memory/MEMORY.md`.

- [ ] **Step 5: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/opencode.json" ".opencode/skills/context-agent/tests/test_memory_sync.py"
git -C "C:\Projetos\Stout" commit -m "feat: load context-agent memory into OpenCode instructions"
```

---

## Task 5: Registrar a skill e explicitar que o wiki e posterior

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/SKILL.md`
- Modify: `C:/Projetos/Stout/.opencode/skills/SKILLS_CHANGELOG.md`

- [ ] **Step 1: Ajustar o `SKILL.md` para o Stout/OpenCode**

Atualizar os trechos de localizacao/uso para:

```md
## Localizacao

```
C:/Projetos/Stout/.opencode/skills/context-agent/
```

## Fluxo De Trabalho

```
[Sessao termina]
  -> save -> session-NNN.md + ACTIVE_CONTEXT.md + MEMORY.md + PROJECT_REGISTRY.md + context.db

[Nova sessao]
  -> MEMORY.md ja esta no OpenCode instructions
  -> load -> briefing detalhado

[Wiki]
  -> etapa posterior, fora do core do context-agent
```
```

- [ ] **Step 2: Registrar no changelog**

Adicionar ao final de `.opencode/skills/SKILLS_CHANGELOG.md`:

```md
## [context-agent] — 2026-04-22
**Origem:** Custom (portado do antigravity-awesome-skills-main)
**Modificação:** Portacao completa para o OpenCode com armazenamento em `C:/Projetos/Stout/memory/` e adaptacao ao formato atual de sessao do Claude/OpenCode.
**Motivo:** Preservar o potencial completo do context-agent no Stout sem acoplar o wiki ao core da memoria operacional.
**Arquivo:** .opencode/skills/context-agent/SKILL.md
```

- [ ] **Step 3: Verificar a documentacao da skill**

Run:

```powershell
python -c "from pathlib import Path; print(Path(r'C:\Projetos\Stout\.opencode\skills\context-agent\SKILL.md').read_text(encoding='utf-8')[:800])"
```

Expected: caminhos do Stout/OpenCode e menção explicita de que o wiki e posterior.

- [ ] **Step 4: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/skills/context-agent/SKILL.md" ".opencode/skills/SKILLS_CHANGELOG.md"
git -C "C:\Projetos\Stout" commit -m "docs: register context-agent port for OpenCode"
```

---

## Task 6: Verificacao funcional do core sem wiki

**Files:**
- Test: `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_context_manager_init.py`
- Test: `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_parser_latest_session.py`
- Test: `C:/Projetos/Stout/.opencode/skills/context-agent/tests/test_memory_sync.py`
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py` (somente se algum ajuste final for necessario)

- [ ] **Step 1: Rodar a suite local da skill**

Run:

```powershell
python -m unittest discover "C:\Projetos\Stout\.opencode\skills\context-agent\tests" -v
```

Expected: todos os testes PASS.

- [ ] **Step 2: Fazer smoke test do bootstrap**

Run:

```powershell
python "C:\Projetos\Stout\.opencode\skills\context-agent\scripts\context_manager.py" init
```

Expected output contains:

```text
Context Agent inicializado com sucesso!
```

- [ ] **Step 3: Fazer smoke test do status**

Run:

```powershell
python "C:\Projetos\Stout\.opencode\skills\context-agent\scripts\context_manager.py" status
```

Expected: gera `## Status Rapido` sem stack trace.

- [ ] **Step 4: Confirmar que o wiki nao e tocado pelo core**

Run:

```powershell
git -C "C:\Projetos\Stout" diff --name-only
```

Expected: nenhum arquivo sob `wiki-compiler/` ou `wiki/` foi modificado pelo smoke test do core.

- [ ] **Step 5: Commit**

```powershell
git -C "C:\Projetos\Stout" add ".opencode/skills/context-agent" ".opencode/opencode.json"
git -C "C:\Projetos\Stout" commit -m "test: verify OpenCode context-agent core without wiki coupling"
```

---

## Task 7: Reservar o ponto de handoff posterior para o wiki (sem implementar wiki agora)

**Files:**
- Modify: `C:/Projetos/Stout/.opencode/skills/context-agent/scripts/context_manager.py`
- Create: `C:/Projetos/Stout/memory/context-agent/WIKI_HANDOFF.md`

- [ ] **Step 1: Criar o arquivo sentinela do handoff**

Create `C:/Projetos/Stout/memory/context-agent/WIKI_HANDOFF.md`:

```md
# Wiki Handoff

Este arquivo reserva o ponto de integracao posterior entre o context-agent e o fluxo de wiki.

Regras:
- O core do context-agent nao escreve no wiki.
- O handoff sera implementado depois, fora desta etapa.
- NotebookLM, `_pending` e revisao humana pertencem ao pipeline de publicacao, nao ao pipeline de memoria operacional.
```

- [ ] **Step 2: Adicionar comentario explicito no `context_manager.py`**

Inserir acima do fim de `cmd_save`:

```python
# Integracao com wiki e posterior e nao faz parte do core da memoria operacional.
# Quando o handoff for implementado, ele deve consumir artefatos ja salvos em
# `C:/Projetos/Stout/memory/context-agent/` sem escrever diretamente no wiki daqui.
```

- [ ] **Step 3: Verificar que nao ha efeito funcional**

Run:

```powershell
python -m unittest discover "C:\Projetos\Stout\.opencode\skills\context-agent\tests" -v
```

Expected: todos os testes continuam PASS.

- [ ] **Step 4: Commit**

```powershell
git -C "C:\Projetos\Stout" add "memory/context-agent/WIKI_HANDOFF.md" ".opencode/skills/context-agent/scripts/context_manager.py"
git -C "C:\Projetos\Stout" commit -m "docs: reserve later wiki handoff for context-agent"
```

---

## Self-Review

- **Spec coverage:** o plano cobre portacao completa, storage no Stout, parser do formato atual do OpenCode, carregamento da memoria no prompt e separacao do wiki como etapa posterior.
- **Placeholder scan:** removidos placeholders; todos os passos tem caminhos reais, comandos reais ou codigo real.
- **Type consistency:** mantidos os nomes do core (`cmd_save`, `cmd_load`, `sync_to_memory`, `get_latest_session_file`, `parse_session_file`, `generate_briefing`, `get_quick_status`).
