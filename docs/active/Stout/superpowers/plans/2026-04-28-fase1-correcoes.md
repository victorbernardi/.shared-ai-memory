# Plano de Correções — Fase 1 Context-agent Unificado

> **Pré-requisito:** ler `C:\Projetos\Stout\memory\ARCHITECTURE.md` (versão pós-auditoria de symlinks) antes de começar.

**Goal:** Atacar as 10 falhas identificadas na auditoria do plano `2026-04-28-fase1-context-agent-unificado-reformulado.md`, gerando um plano executável que respeita a topologia real (source em Stout, demais paths são symlinks).

**Architecture:** Mover storage unificado para `C:\Projetos\Stout\memory\context-agent\` (fonte) e expor via symlink em `~/.shared-ai-memory\context-agent\` para Antigravity/Gemini chegarem nele sem mudar config. OpenCode e Claude Code apontam por path absoluto.

**Tech Stack:** Python 3.13, pytest, `cmd /c mklink` (junction `/J` para diretórios, hardlink `/H` para arquivos — symlink puro requer admin no Windows e é evitado), Bash para validações.

**Convenção de links no Windows (descoberta em execução T1/T4):**
- **Diretório:** `cmd /c mklink /J <link> <target>` (junction — não precisa admin)
- **Arquivo:** `cmd /c mklink /H <link> <target>` (hardlink — não precisa admin)
- **NÃO usar** `New-Item -ItemType SymbolicLink` — exige privilégio elevado.

---

## Estratégia geral

Trocamos a abordagem do plano original em três pontos:

| Antes | Depois |
|---|---|
| Storage em `C:\Motores-LLM\memory\context-agent\` | Storage em `C:\Projetos\Stout\memory\context-agent\` |
| Tratar Antigravity e Gemini CLI como instalações separadas | Tratar como instalação única (já são) |
| Migrar de path inventado | Migrar do path real (`Stout/antigravity/skills/context-agent/data/`) |
| Reescrever `CLAUDE_SESSION_DIR` no config Antigravity | Não tocar — é fonte de leitura específica |
| Copiar SKILL.md OpenCode → Claude Code 1:1 | Criar SKILL.md no formato Claude Code |

---

## Falhas mapeadas → Tasks

| # | Falha | Task |
|---|---|---|
| 1 | Symlink chain invertida (Stout é source, não Motores-LLM) | T1 — corrigir paths-alvo |
| 2 | Antigravity ≠ Gemini CLI tratados como separados | T2 — instalação única |
| 3 | `CLAUDE_SESSION_DIR` reescrito incorretamente | T3 — preservar fonte original |
| 4 | `MEMORY_DIR` mudou de location, dados antigos órfãos | T4 — migração explícita de MEMORY.md |
| 5 | Task 6 lê de path inexistente | T5 — corrigir migração |
| 6 | SKILL.md frontmatter incompatível (Antigravity vs Claude) | T6 — SKILL.md por motor |
| 7 | Localização no SKILL.md desatualizada | T6 (mesmo) |
| 8 | `governance.py` ignorado | T7 — auditoria de paridade de scripts |
| 9 | ARCHITECTURE.md não bate com disco | ✅ resolvido (este commit) |
| 10 | Skill discovery do Gemini/Antigravity não tocado | T8 — validar discovery via `activate_skill` |
| 11 | Concorrência SQLite — Stop+SessionEnd hooks simultâneos | T8.5 — WAL mode + busy_timeout |
| 12 | Contador `NNN` colide entre motores | T8.6 — timestamp + UUID curto |

---

## Task 1 — Reapontar storage unificado para Stout

**Files:**
- Modify: `Stout/antigravity/skills/context-agent/scripts/config.py`
- Create: `Stout/memory/context-agent/{sessions,archive,logs,cleaned}/.gitkeep`
- Create symlink: `~/.shared-ai-memory/context-agent` → `Stout/memory/context-agent`

- [ ] **Step 1: Criar diretórios reais em Stout**
```bash
mkdir -p C:/Projetos/Stout/memory/context-agent/{sessions,archive,logs,cleaned}
touch C:/Projetos/Stout/memory/context-agent/{sessions,archive,logs,cleaned}/.gitkeep
```

- [ ] **Step 2: Criar junction em `~/.shared-ai-memory/`**
```powershell
cmd /c "mklink /J `"C:\Users\victor.bernardi\.shared-ai-memory\context-agent`" `"C:\Projetos\Stout\memory\context-agent`""
```
Junction não exige admin e funciona como symlink para diretórios.

- [ ] **Step 3: Validar junction (regra 2 do ANTIGRAVITY.md)**
```bash
ls -la C:/Users/victor.bernardi/.shared-ai-memory/context-agent
# deve mostrar: ... context-agent -> /c/Projetos/Stout/memory/context-agent
ls -la C:/Users/victor.bernardi/.gemini/antigravity/context-agent  # via chain
# deve resolver pro mesmo lugar
```

- [ ] **Step 4: Atualizar `config.py` da skill Antigravity (caminho via Stout)**

Substituir bloco "Raízes" + "Dados do agente" por:
```python
import os
from pathlib import Path

def _env_path(name: str, default: Path) -> Path:
    val = os.getenv(name)
    return Path(val) if val else default

# Source of truth: Stout. Acessível via symlink em ~/.shared-ai-memory/context-agent.
STOUT_ROOT = _env_path("STOUT_ROOT", Path(r"C:\Projetos\Stout"))
DATA_DIR = _env_path("CONTEXT_AGENT_DATA", STOUT_ROOT / "memory" / "context-agent")

SESSIONS_DIR = DATA_DIR / "sessions"
ARCHIVE_DIR  = DATA_DIR / "archive"
LOGS_DIR     = DATA_DIR / "logs"
CLEANED_DIR  = DATA_DIR / "cleaned"
ACTIVE_CONTEXT_PATH   = DATA_DIR / "ACTIVE_CONTEXT.md"
PROJECT_REGISTRY_PATH = DATA_DIR / "PROJECT_REGISTRY.md"
DB_PATH               = DATA_DIR / "context.db"

SESSION_ORIGIN = "antigravity"  # também usado por Gemini CLI (instalação compartilhada)
```

**Não mexer** em `CLAUDE_SESSION_DIR`, `BRAIN_DIR`, `MEMORY_DIR`, `MEMORY_MD_PATH`, `DECISION_MARKERS`, `KNOWN_PROJECTS`. Fontes de leitura ficam onde estão.

- [ ] **Step 5: Teste**
```python
# Stout/tests/context_agent/test_unified_storage.py
def test_data_dir_is_in_stout():
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("cfg", r"C:\Projetos\Stout\antigravity\skills\context-agent\scripts\config.py")
    cfg = module_from_spec(spec); spec.loader.exec_module(cfg)
    assert cfg.DATA_DIR == Path(r"C:\Projetos\Stout\memory\context-agent")
```
Run: `pytest tests/context_agent/test_unified_storage.py -v` → PASS.

- [ ] **Step 6: Commit**
```bash
git add antigravity/skills/context-agent/scripts/config.py memory/context-agent/ tests/
git commit -m "fix: storage unificado em Stout (source of truth) com symlink em shared-ai-memory"
```

---

## Task 2 — Reconhecer Antigravity+Gemini CLI como instalação única

**Files:**
- Modify: ARCHITECTURE.md (já feito)
- Modify: plano original (deprecar referências separadas)

- [ ] **Step 1: Remover do plano original menções a "instalar context-agent em Gemini CLI"**
Adicionar comentário no plano antigo: `[DEPRECATED — ver 2026-04-28-fase1-correcoes.md]`.

- [ ] **Step 2: Documentar no SKILL.md que a instalação cobre 2 motores**
Em `Stout/antigravity/skills/context-agent/SKILL.md`, atualizar seção **Localização**:
```markdown
## Localização

Source of truth: `C:\Projetos\Stout\antigravity\skills\context-agent\`

Acessível por:
- **Antigravity:** `~/.antigravity/skills/context-agent/` (via `skills` → `.shared-ai-memory/skills` → Stout)
- **Gemini CLI:** `~/.gemini/antigravity/skills/context-agent/` (via `antigravity` → `.shared-ai-memory` → ...)

Storage de dados (compartilhado): `C:\Projetos\Stout\memory\context-agent\`
```

- [ ] **Step 3: Teste — confirmar que os 4 paths levam ao mesmo arquivo**
```python
# Stout/tests/context_agent/test_symlink_chain.py
import os
STOUT = r"C:\Projetos\Stout\antigravity\skills\context-agent\SKILL.md"

def test_four_paths_same_skill_md():
    paths = [
        STOUT,
        r"C:\Users\victor.bernardi\.antigravity\skills\context-agent\SKILL.md",
        r"C:\Users\victor.bernardi\.gemini\antigravity\skills\context-agent\SKILL.md",
        r"C:\Motores-LLM\antigravity\skills\context-agent\SKILL.md",  # via wrapper
    ]
    reals = {os.path.realpath(p) for p in paths}
    assert len(reals) == 1, f"Paths divergem: {reals}"
```
**Cobre 4 chains:** Stout (source), `~/.antigravity`, `~/.gemini`, e `Motores-LLM` (wrapper).

- [ ] **Step 4: Commit**

---

## Task 3 — Preservar `CLAUDE_SESSION_DIR` original

**Problema:** o plano original sobrescrevia para apontar nos JSONLs do Claude Code, quebrando o parser do Antigravity.

- [ ] **Step 1: Manter no `config.py` Antigravity:**
```python
# Antigravity lê seu PRÓPRIO brain — não os logs do Claude Code.
AGENT_ROOT = Path.home() / ".gemini" / "antigravity"  # via symlink chain → .shared-ai-memory
BRAIN_DIR  = AGENT_ROOT / "brain"
CLAUDE_SESSION_DIR = BRAIN_DIR  # nome legado — mantido por compat com session_parser.py
```

- [ ] **Step 2: Teste de regressão para `session_parser.py`**
Rodar `python context_manager.py status` antes e depois das mudanças de Task 1. Output deve ser idêntico em quantidade de sessões parseadas.

- [ ] **Step 3: Renomear `CLAUDE_SESSION_DIR` em commit futuro**
Criar issue/TODO: nome é enganoso, não é Claude Code. Fora do escopo desta fase.

---

## Task 4 — Migrar `MEMORY.md` legado

**Problema:** `~/.shared-ai-memory/memory/MEMORY.md` (e `Stout/memory/MEMORY.md`) existem hoje. Plano original ignorava.

- [ ] **Step 1: Inventariar arquivos legacy**
```bash
ls -la C:/Users/victor.bernardi/.shared-ai-memory/memory/
ls -la C:/Projetos/Stout/memory/
# Esperado: MEMORY.md em ambos, possivelmente conteúdo diferente
diff C:/Users/victor.bernardi/.shared-ai-memory/memory/MEMORY.md C:/Projetos/Stout/memory/MEMORY.md
```

- [ ] **Step 2: Decidir conteúdo canônico**
Se idênticos: nenhum trabalho. Se divergentes: mesclar manualmente em `Stout/memory/MEMORY.md` (source of truth).

- [ ] **Step 3: Substituir o de `~/.shared-ai-memory/memory/` por hardlink**
```powershell
Remove-Item C:\Users\victor.bernardi\.shared-ai-memory\memory\MEMORY.md -Force
cmd /c "mklink /H `"C:\Users\victor.bernardi\.shared-ai-memory\memory\MEMORY.md`" `"C:\Projetos\Stout\memory\MEMORY.md`""
```
**Hardlink** (`/H`) — não exige admin para arquivos. Symlink puro exigiria.
Hardlink compartilha inode: qualquer write em um lado reflete imediatamente no outro.

- [ ] **Step 4: Teste — mesmo inode**
```python
import os
def test_memory_md_same_inode():
    a = os.stat(r"C:\Projetos\Stout\memory\MEMORY.md")
    b = os.stat(r"C:\Users\victor.bernardi\.shared-ai-memory\memory\MEMORY.md")
    assert a.st_ino == b.st_ino, "MEMORY.md divergiu — recriar hardlink"
```
Não usar `realpath` para hardlink: ambos os paths "são reais" (não há resolução), mas inode é igual.

---

## Task 5 — Migração de dados: caminho correto

**Problema do plano original:** lia de `antigravity/skills/context-management/context-agent/data/` (não existe).
**Caminho real:** `Stout/antigravity/skills/context-agent/data/`.

**Estratégia:** copiar (não mover) primeiro, validar destino, só então remover origem e criar junction. Evita estado intermediário irrecuperável caso algum step falhe.

- [ ] **Step 1: Verificar que SQLite não está locked**
```bash
python -c "
import sqlite3
db = r'C:\Projetos\Stout\antigravity\skills\context-agent\data\context.db'
con = sqlite3.connect(db, timeout=2)
con.execute('PRAGMA quick_check')
con.close()
print('DB acessível')
"
```
Se falhar com `database is locked`: identificar processo (`Get-Process | ? { $_.Name -like '*python*' }`), encerrar, repetir.

- [ ] **Step 2: Backup completo**
```bash
cp -r "C:/Projetos/Stout/antigravity/skills/context-agent/data" \
      "C:/Projetos/Stout/antigravity/skills/context-agent/data.backup-2026-04-29"
```

- [ ] **Step 3: COPIAR sessões para storage unificado (não mover)**
```bash
SRC=C:/Projetos/Stout/antigravity/skills/context-agent/data
DST=C:/Projetos/Stout/memory/context-agent

count_src=0; count_dst=0
for f in "$SRC/sessions"/session-*.md; do
  [ -f "$f" ] || continue
  base=$(basename "$f" .md)
  cp "$f" "$DST/sessions/${base}-antigravity.md"
  count_src=$((count_src+1))
done
count_dst=$(ls "$DST/sessions"/session-*-antigravity.md 2>/dev/null | wc -l)
echo "Copiadas: $count_src origem -> $count_dst destino"
[ "$count_src" = "$count_dst" ] || { echo "FALHA na cópia"; exit 1; }

# context.db: só copiar se destino não tiver, ou comparar conteúdo
if [ ! -f "$DST/context.db" ] || [ ! -s "$DST/context.db" ]; then
  cp "$SRC/context.db" "$DST/context.db"
fi
[ -f "$SRC/ACTIVE_CONTEXT.md" ] && cp "$SRC/ACTIVE_CONTEXT.md" "$DST/ACTIVE_CONTEXT.md"
[ -f "$SRC/PROJECT_REGISTRY.md" ] && cp "$SRC/PROJECT_REGISTRY.md" "$DST/PROJECT_REGISTRY.md"
if [ -d "$SRC/archive" ] && [ -n "$(ls -A "$SRC/archive" 2>/dev/null)" ]; then
  cp -r "$SRC/archive/." "$DST/archive/"
fi
```

- [ ] **Step 4: Validar destino antes de tocar na origem**
```bash
cd C:/Projetos/Stout && python -m pytest tests/context_agent/test_migration.py -v
```
Se algo falhar, **PARAR**: origem ainda intacta, backup existe. Investigar antes de prosseguir.

- [ ] **Step 5: Substituir `data/` antigo por junction**
```powershell
Remove-Item -Recurse -Force C:\Projetos\Stout\antigravity\skills\context-agent\data
cmd /c "mklink /J `"C:\Projetos\Stout\antigravity\skills\context-agent\data`" `"C:\Projetos\Stout\memory\context-agent`""
```
Junction (`/J`) — não precisa admin. Qualquer código que ainda usa `CONTEXT_AGENT_ROOT/data/` chega no novo storage.

- [ ] **Step 6: Teste**
```python
# tests/context_agent/test_migration.py
import os
from pathlib import Path

UNIFIED = Path(r"C:\Projetos\Stout\memory\context-agent")

def test_at_least_one_session_migrated():
    sessions = list((UNIFIED / "sessions").glob("session-*-antigravity.md"))
    assert sessions, f"Nenhuma sessão -antigravity em {UNIFIED/'sessions'}"

def test_db_present_and_nonempty():
    db = UNIFIED / "context.db"
    assert db.exists() and db.stat().st_size > 0

def test_data_junction_resolves_to_unified():
    legacy = Path(r"C:\Projetos\Stout\antigravity\skills\context-agent\data")
    assert legacy.exists()
    # Junction: realpath resolve para o target
    assert os.path.realpath(str(legacy)) == os.path.realpath(str(UNIFIED))
```

- [ ] **Step 7: Validar via FTS5**
```bash
python C:/Projetos/Stout/antigravity/skills/context-agent/scripts/context_manager.py status
# Deve listar sessões migradas e DB no novo path
```

- [ ] **Step 8: Remover backup só após T8 (smoke test final) passar.**

---

## Task 6 — SKILL.md por motor

**Problema:** Antigravity/Gemini usam frontmatter `risk + source + date_added + author + tags + tools`. Claude Code usa só `name + description + allowed-tools`.

- [ ] **Step 1: Manter SKILL.md atual em `Stout/antigravity/skills/context-agent/SKILL.md`**
(formato Antigravity — não tocar campos extras).

- [ ] **Step 2: Atualizar seção "Localização" para apontar para o novo storage**
(já listado em Task 2 Step 2).

- [ ] **Step 3: Criar SKILL.md específico para Claude Code**

⚠️ **Frontmatter de skill no Claude Code é apenas `name` + `description`**.
`allowed-tools` é frontmatter de **slash command** (`.claude/commands/*.md`), não de skill.
Incluir `allowed-tools` num SKILL.md gera comportamento indefinido.

Em `~/.claude/skills/context-agent/SKILL.md`:
```markdown
---
name: context-agent
description: Salva e carrega contexto de sessão (decisões, tarefas pendentes, arquivos modificados). Storage unificado em C:\Projetos\Stout\memory\context-agent\, compartilhado com Antigravity, Gemini CLI e OpenCode. Sessões deste motor têm sufixo -claude.
---

# Context Agent (Claude Code)

Compartilha storage com Antigravity/Gemini CLI/OpenCode em `C:\Projetos\Stout\memory\context-agent\`.
Sessões deste motor são salvas com sufixo `-claude.md`.

## Quando usar
- Comandos: "salvar contexto", "carregar contexto", "próxima sessão"
- Hook Stop: salva automaticamente ao fim de cada sessão.

## Scripts
`python scripts/context_manager.py {load,save,status,search,maintain}`
```

- [ ] **Step 4: Teste — frontmatter parse (apenas campos válidos)**
```python
import yaml
from pathlib import Path
def test_claude_skill_frontmatter():
    txt = Path(r"C:\Users\victor.bernardi\.claude\skills\context-agent\SKILL.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(txt.split("---")[1])
    assert set(fm) == {"name", "description"}, (
        f"Frontmatter deve conter APENAS name+description (skills do Claude Code). Recebido: {set(fm)}"
    )
    assert fm["name"] == "context-agent"
```

---

## Task 7 — Auditoria de paridade de scripts

**Problema:** plano original "copiar todos os .py do OpenCode" assume paridade. Antigravity tem `governance.py`; OpenCode pode não ter.

- [ ] **Step 1: Diff de scripts entre instalações**
```bash
diff <(ls C:/Projetos/Stout/antigravity/skills/context-agent/scripts/*.py | xargs -n1 basename | sort) \
     <(ls C:/Projetos/Stout/.opencode/skills/context-agent/scripts/*.py | xargs -n1 basename | sort)
```

- [ ] **Step 2: Decisão por arquivo divergente**
Para cada arquivo presente só em um:
- Se for funcionalidade nova (ex.: `governance.py`) → portar pra outras instalações.
- Se for legado de uma instalação → remover.

- [ ] **Step 3: Para Claude Code, copiar do mais completo (Antigravity)**
```bash
SRC=C:/Projetos/Stout/antigravity/skills/context-agent/scripts
DST=C:/Users/victor.bernardi/.claude/skills/context-agent/scripts
mkdir -p "$DST"
cp "$SRC"/*.py "$DST/"
cp "$SRC"/requirements.txt "$DST/"
```

- [ ] **Step 4: Adaptar `config.py` do Claude Code**
- `SESSION_ORIGIN = "claude"`
- `DATA_DIR = Path(r"C:\Projetos\Stout\memory\context-agent")`
- `CLAUDE_SESSION_DIR`: **NÃO usar** `~/.claude/projects` direto — Claude Code grava em `~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl` (subdir por projeto). Usar:
  ```python
  # Subdir do projeto atual (Stout). Claude Code encoda o cwd substituindo / por -.
  CLAUDE_PROJECTS_ROOT = Path.home() / ".claude" / "projects"
  CLAUDE_SESSION_DIR = CLAUDE_PROJECTS_ROOT / "C--Projetos-Stout"
  # Para projetos diferentes, override via env var:
  #   CLAUDE_SESSION_DIR = Path(os.getenv("CLAUDE_SESSION_DIR", str(CLAUDE_SESSION_DIR)))
  ```
- Manter `DECISION_MARKERS`, `PENDING_MARKERS`, `KNOWN_PROJECTS`, `FILE_MODIFYING_TOOLS`, `FILE_READING_TOOLS` na íntegra (sem placeholder — copiar do config.py do Antigravity).

- [ ] **Step 5: Teste de paridade**
```python
def test_three_installs_have_same_script_set():
    paths = [
        Path(r"C:\Projetos\Stout\antigravity\skills\context-agent\scripts"),
        Path(r"C:\Projetos\Stout\.opencode\skills\context-agent\scripts"),
        Path.home() / r".claude\skills\context-agent\scripts",
    ]
    sets = [{p.name for p in d.glob("*.py") if p.name != "__init__.py"} for d in paths]
    assert sets[0] == sets[1] == sets[2], f"divergência: {sets}"
```

---

## Task 8 — Validar discovery em Antigravity/Gemini

**Problema:** Gemini/Antigravity carregam metadata e ativam via `activate_skill`. Cópia de arquivos não cadastra a skill.

- [ ] **Step 1: Verificar como Antigravity lista skills**
Rodar Antigravity/Gemini e usar `activate_skill(name="context-agent")`. Deve carregar SKILL.md atual.

- [ ] **Step 2: Confirmar que mudança em SKILL.md é refletida**
Adicionar linha de teste em SKILL.md, recarregar Antigravity, confirmar via `activate_skill`.

- [ ] **Step 3: Para Claude Code, validar Stop hook**

⚠️ **Path absoluto do Python obrigatório.** Hooks do Claude Code rodam em ambiente sem garantia de `python` no PATH. Resolver via:
```bash
where python   # ex.: C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe
```

Editar `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "C:\\Users\\victor.bernardi\\AppData\\Local\\anaconda3\\python.exe C:\\Users\\victor.bernardi\\.claude\\skills\\context-agent\\scripts\\context_manager.py save",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```
- `timeout: 60` evita travar a sessão se o save falhar.
- Preservar quaisquer outras chaves já existentes em `settings.json`.

- [ ] **Step 4: Smoke test cross-engine** (depende de T8.5 e T8.6)
```bash
# Cada motor escreve uma sessão
python Stout/antigravity/skills/context-agent/scripts/context_manager.py save  # via Antigravity
python Stout/.opencode/skills/context-agent/scripts/context_manager.py save     # via OpenCode
python ~/.claude/skills/context-agent/scripts/context_manager.py save           # via Claude

ls Stout/memory/context-agent/sessions/
# Esperado: arquivos com formato session-YYYYMMDD-HHMMSS-<origin>-<sid>.md
```

---

## Task 8.5 — SQLite WAL mode (pré-requisito do smoke test)

**Files:**
- Modify: `antigravity/skills/context-agent/scripts/context_manager.py` (ou `search.py` — onde DB é aberto)

- [ ] **Step 1: Localizar pontos de `sqlite3.connect`**
```bash
grep -rn "sqlite3.connect" Stout/antigravity/skills/context-agent/scripts/ \
                          Stout/.opencode/skills/context-agent/scripts/
```

- [ ] **Step 2: Adicionar PRAGMA WAL após cada connect**
```python
con = sqlite3.connect(DB_PATH, timeout=30)
con.execute("PRAGMA journal_mode=WAL")
con.execute("PRAGMA busy_timeout=30000")  # 30s
```
WAL é persistente: setado uma vez, fica no DB. `busy_timeout` é por conexão.

- [ ] **Step 3: Teste de concorrência**
```python
# tests/context_agent/test_db_concurrency.py
import sqlite3, threading
from pathlib import Path

DB = Path(r"C:\Projetos\Stout\memory\context-agent\context.db")

def test_wal_mode_active():
    con = sqlite3.connect(DB)
    mode = con.execute("PRAGMA journal_mode").fetchone()[0]
    con.close()
    assert mode.lower() == "wal", f"journal_mode={mode}, esperado wal"

def test_concurrent_reads_during_write():
    """Dois threads: um escreve longo, outro lê — não deve bloquear."""
    errors = []
    def writer():
        try:
            c = sqlite3.connect(DB, timeout=10)
            c.execute("PRAGMA busy_timeout=10000")
            c.execute("BEGIN")
            c.execute("CREATE TABLE IF NOT EXISTS _test_wal(x INTEGER)")
            c.execute("INSERT INTO _test_wal VALUES(1)")
            import time; time.sleep(0.5)
            c.commit(); c.close()
        except Exception as e: errors.append(("w", e))
    def reader():
        try:
            import time; time.sleep(0.1)
            c = sqlite3.connect(DB, timeout=2)
            c.execute("SELECT 1").fetchone()
            c.close()
        except Exception as e: errors.append(("r", e))
    tw = threading.Thread(target=writer); tr = threading.Thread(target=reader)
    tw.start(); tr.start(); tw.join(); tr.join()
    assert not errors, f"erros de concorrência: {errors}"
```

- [ ] **Step 4: Commit**

---

## Task 8.6 — Naming de sessão à prova de colisão

**Files:**
- Modify: `scripts/session_summary.py` (geração de nome)

- [ ] **Step 1: Localizar geração atual do nome**
```bash
grep -rn "session-" Stout/antigravity/skills/context-agent/scripts/session_summary.py
```

- [ ] **Step 2: Substituir contador `NNN` por timestamp + UUID curto**
```python
from datetime import datetime
import uuid
from config import SESSION_ORIGIN, SESSIONS_DIR

def generate_session_filename() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    sid = uuid.uuid4().hex[:8]
    return f"session-{ts}-{SESSION_ORIGIN}-{sid}.md"
```

- [ ] **Step 3: Atualizar `compressor.py` (archive) e `search.py` (FTS5 indexer) para reconhecer o novo padrão de nome**
Regex de reconhecimento: `r"session-\d{8}-\d{6}-(antigravity|opencode|claude)-[0-9a-f]{8}\.md"`.

- [ ] **Step 4: Migração de nomes legados (já tagged em T5)**
Sessões migradas em T5 têm formato `session-NNN-antigravity.md`. Decidir:
- (a) Manter como estão (compatibilidade com FTS5 existente) — regex deve aceitar ambos os formatos.
- (b) Renomear no Step 3 da T5 para o novo formato — mais consistente, mas exige reindex.

Recomendação: **(a)** — regex aceita os dois, evita reindex.

- [ ] **Step 5: Teste de unicidade sob concorrência**
```python
# tests/context_agent/test_session_naming.py
import re
from concurrent.futures import ThreadPoolExecutor
import sys; sys.path.insert(0, r"C:\Projetos\Stout\antigravity\skills\context-agent\scripts")
from session_summary import generate_session_filename

def test_no_collision_under_load():
    with ThreadPoolExecutor(max_workers=20) as pool:
        names = list(pool.map(lambda _: generate_session_filename(), range(200)))
    assert len(set(names)) == 200, f"colisão detectada: {len(set(names))}/200 únicos"

def test_format_matches_regex():
    pattern = re.compile(r"^session-\d{8}-\d{6}-(antigravity|opencode|claude)-[0-9a-f]{8}\.md$")
    for _ in range(10):
        assert pattern.match(generate_session_filename())
```

- [ ] **Step 6: Commit**

---

## Self-review

**Cobertura das 10 falhas originais:**
- [x] 1, 2, 5, 9 — T1+T5 (paths reais)
- [x] 3 — T3 (preservar CLAUDE_SESSION_DIR)
- [x] 4 — T4 (MEMORY.md migração)
- [x] 6, 7 — T6 (SKILL.md por motor)
- [x] 8 — T7 (paridade scripts)
- [x] 10 — T8 (discovery + hook correto)

**Falhas adicionais descobertas durante execução (revisão Opus, 2026-04-29):**
- [x] Junction `/J` em vez de SymbolicLink (T1, T5) — corrigido inline
- [x] Hardlink `/H` em vez de SymbolicLink para arquivos (T4) — corrigido inline
- [x] T2 cobre 4 chains (incluindo `Motores-LLM` wrapper) em vez de 3 — corrigido
- [x] T5 ordem destrutiva → cp + valida + rm (não mv direto) — corrigido
- [x] T5 SQLite locked check antes de copiar — adicionado
- [x] T6 Claude Code SKILL.md sem `allowed-tools` (frontmatter inválido) — corrigido
- [x] T7 `CLAUDE_SESSION_DIR` com subdir do projeto — corrigido
- [x] T8 Stop hook com path absoluto do Python + timeout — corrigido

**Sem placeholders:** todos os snippets têm código real.

**Riscos PROMOVIDOS para Fase 1 (não mais residuais — bloqueiam smoke test cross-engine):**

- **T8.5 (novo): SQLite WAL mode** — antes do smoke test cross-engine. Stop hook (Claude) + SessionEnd hook (Gemini) podem disparar simultaneamente:
  ```python
  # Em context_manager.py, ao abrir conexão:
  con = sqlite3.connect(DB_PATH, timeout=30)
  con.execute("PRAGMA journal_mode=WAL")
  con.execute("PRAGMA busy_timeout=30000")
  ```
  Sem WAL, locks bloqueiam writers; com WAL, leitores não bloqueiam writers.

- **T8.6 (novo): nome de sessão à prova de colisão** — abandonar contador `NNN` por motor.
  Usar `session-YYYYMMDD-HHMMSS-<origin>-<short-uuid>.md`:
  ```python
  from datetime import datetime
  import uuid
  ts = datetime.now().strftime("%Y%m%d-%H%M%S")
  sid = uuid.uuid4().hex[:8]
  filename = f"session-{ts}-{SESSION_ORIGIN}-{sid}.md"
  ```
  Sem isso, dois motores salvando ao mesmo tempo geram o mesmo nome (`session-001-claude.md` + `session-001-antigravity.md` ainda batem se cada um mantém contador local sem awareness do storage compartilhado).

**Riscos residuais reais:**
- `governance.py` ainda não auditado — T7 pode descobrir que precisa redesign.
- T8 Step 1-2 são manuais (rodar Antigravity, `activate_skill`) — sem automação.
- ~~Parser `.pb` para Antigravity é gap de Fase 2~~ — **resolvido em Fase 2** via `overview.txt` (NDJSON), ver `2026-04-29-fase2-antigravity-overview-parser.md`.

---

## ~~Gap de Fase 2~~ — RESOLVIDO (2026-04-29)

> Ver plano completo: `docs/superpowers/plans/2026-04-29-fase2-antigravity-overview-parser.md`

**Descoberto em T3 (2026-04-28):** o brain do Antigravity armazena sessões como `.pb` (protobuf)
— `session_parser.py` não conseguia ler, `get_latest_session_file()` retornava `None`.

**Resolução real (2026-04-29):** o brain também grava `<uuid>/.system_generated/logs/overview.txt`
em formato **NDJSON** (uma linha por step). `_parse_raw_entry()` já tratava `USER_INPUT`/`PLANNER_RESPONSE`.
Bastou reescrever o discovery para glob recursivo — parser `.pb` desnecessário.
`context_manager save` funcionando: 243 mensagens, 198 tool calls, session file gerado com sucesso.

**Solução investigada via Context7 (Gemini CLI docs):**

O Gemini CLI expõe dois mecanismos aproveitáveis:

1. **`/chat share file.json`** — exporta o histórico completo da sessão para JSON ou Markdown.
   Sessões ficam em `~/.gemini/tmp/<project_hash>/chats/`.

2. **Hook `SessionEnd`** — análogo ao `Stop` do Claude Code. Recebe via stdin:
   - `transcript_path` — path absoluto para o transcript JSON da sessão (chave do mecanismo)
   - `session_id`, `cwd`, `timestamp`

   O hook passa `transcript_path` para `context_manager.py save`, que lê o JSON diretamente —
   sem parsear `.pb`, sem dependência de protobuf.

**Plano para Fase 2 (Antigravity/Gemini session parser):**

- [ ] Localizar `settings.json` correto do Antigravity (`~/.gemini/settings.json`)
- [ ] Adicionar hook `SessionEnd`:
  ```json
  "SessionEnd": [{
    "matcher": "exit",
    "hooks": [{
      "type": "command",
      "command": "python C:\\Projetos\\Stout\\antigravity\\skills\\context-agent\\scripts\\context_manager.py save --transcript-path \"${transcript_path}\""
    }]
  }]
  ```
- [ ] Adaptar `context_manager.py save` para aceitar `--transcript-path <path>`
- [ ] Adaptar `session_parser.py` para ler o formato de transcript JSON do Gemini CLI
  (estrutura: `user`/`assistant` com `tool_calls`, `token_usage` — similar ao que o parser já trata)
- [ ] Teste: encerrar sessão Antigravity → confirmar `session-NNN-antigravity.md` aparece
  em `Stout/memory/context-agent/sessions/`

**Settings a modificar:** `~/.gemini/settings.json` (já identificado em `C:\Motores-LLM\gemini-cli\settings.json`)

---

**Pronto para execução task-a-task.**
