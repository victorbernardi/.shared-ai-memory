"""
Configuração centralizada do Context Agent.
Suporta múltiplos motores via env vars: Antigravity, Gemini CLI, Claude Code, OpenCode.

Env vars de override:
  CONTEXT_AGENT_DATA     — path para o storage unificado
  CONTEXT_AGENT_ORIGIN   — origem da sessão (antigravity | claude | opencode | gemini)
  CLAUDE_SESSION_DIR     — path para os arquivos JSONL do motor ativo
"""

from pathlib import Path
import os


def _env_path(name: str, default: Path) -> Path:
    val = os.getenv(name)
    return Path(val) if val else default


# ── Raízes ──────────────────────────────────────────────────────────
USER_PROFILE = Path(os.getenv("USERPROFILE", str(Path.home())))
STOUT_ROOT = _env_path("STOUT_ROOT", Path(r"C:\Projetos\Stout"))

# Source of truth: ~/.shared-ai-memory/context-agent (compartilhado entre todos os motores)
DATA_DIR = _env_path("CONTEXT_AGENT_DATA", USER_PROFILE / ".shared-ai-memory" / "context-agent")

# ── Dados do agente (storage unificado) ─────────────────────────────
SESSIONS_DIR = DATA_DIR / "sessions"
ARCHIVE_DIR  = DATA_DIR / "archive"
LOGS_DIR     = DATA_DIR / "logs"
CLEANED_DIR  = DATA_DIR / "cleaned"
ACTIVE_CONTEXT_PATH   = DATA_DIR / "ACTIVE_CONTEXT.md"
PROJECT_REGISTRY_PATH = DATA_DIR / "PROJECT_REGISTRY.md"
DB_PATH               = DATA_DIR / "context.db"

# ── Origem da sessão ─────────────────────────────────────────────────
# Padrão: antigravity. Claude Code define CONTEXT_AGENT_ORIGIN=claude via settings.json.
SESSION_ORIGIN = os.getenv("CONTEXT_AGENT_ORIGIN", "antigravity")

# ── Fontes de leitura ────────────────────────────────────────────────
AGENT_ROOT = USER_PROFILE / ".gemini" / "antigravity"
BRAIN_DIR  = AGENT_ROOT / "brain"

COMMANDCODE_SESSION_DIR = _env_path(
    "COMMANDCODE_SESSION_DIR",
    USER_PROFILE / ".commandcode" / "projects",
)

if SESSION_ORIGIN == "commandcode":
    CLAUDE_SESSION_DIR = _env_path("CLAUDE_SESSION_DIR", COMMANDCODE_SESSION_DIR)
elif SESSION_ORIGIN == "claude":
    CLAUDE_SESSION_DIR = _env_path("CLAUDE_SESSION_DIR", USER_PROFILE / ".claude" / "projects")
else:
    CLAUDE_SESSION_DIR = _env_path("CLAUDE_SESSION_DIR", BRAIN_DIR)

MEMORY_DIR     = USER_PROFILE / ".shared-ai-memory" / "memory"
MEMORY_MD_PATH = MEMORY_DIR / "MEMORY.md"

# Compatibilidade com código que ainda usa CONTEXT_AGENT_ROOT / "data"
SKILLS_ROOT        = USER_PROFILE / ".shared-ai-memory" / "skills"
CONTEXT_AGENT_ROOT = SKILLS_ROOT / "process-context-agent"

# ── Limites ─────────────────────────────────────────────────────────
MAX_ACTIVE_CONTEXT_LINES = 150
MAX_RECENT_SESSIONS = 5
ARCHIVE_AFTER_SESSIONS = 20
MAX_DECISIONS_AGE_DAYS = 30
MAX_SEARCH_RESULTS = 10

# ── Padrões de detecção ────────────────────────────────────────────
DECISION_MARKERS = [
    "decidimos", "vamos usar", "optamos por", "escolhemos",
    "a decisão foi", "ficou decidido", "definimos que",
    "a abordagem será", "seguiremos com",
    "we decided", "let's use", "we'll go with", "the decision is",
    "we chose", "going with", "the approach will be", "decided to",
]

PENDING_MARKERS = [
    "falta", "ainda precisa", "pendente", "todo:", "TODO:",
    "depois vamos", "próximo passo", "faltando",
    "still need", "pending", "next step",
    "remaining", "left to do", "needs to be done",
]

# Ferramentas que modificam arquivos
FILE_MODIFYING_TOOLS = {"Edit", "Write", "NotebookEdit", "write_to_file", "replace_file_content", "multi_replace_file_content", "create_or_update_file", "push_files"}
FILE_READING_TOOLS = {"Read", "Glob", "Grep", "view_file", "list_dir", "grep_search", "get_file_contents"}

# ── Projetos conhecidos ────────────────────────────────────────────
KNOWN_PROJECTS = {
    "antigravity": "Antigravity Framework",
    "inova": "Projeto Inova",
    "stout": "Stout Edition",
    "context-agent": "Context Agent",
}

# ── Governança ─────────────────────────────────────────────────────
AUTO_GIT_SYNC = True  # Realiza commit e push automático ao salvar

# ── Docs archiver ────────────────────────────────────────────────────
SHARED_AI_MEMORY_ROOT = USER_PROFILE / ".shared-ai-memory"
DOCS_ROOT = SHARED_AI_MEMORY_ROOT / "docs"
DOCS_ACTIVE_DIR = DOCS_ROOT / "active"
DOCS_LEGACY_DIR = DOCS_ROOT / "legacy"
DOCS_BYPASS_DIRS: frozenset[str] = frozenset({"decisions", "walkthroughs", "business"})
# Root-level folders in docs/ that are never treated as projects
DOCS_ROOT_EXEMPT_DIRS: frozenset[str] = DOCS_BYPASS_DIRS | frozenset({"plans", "specs", "active", "legacy"})
DOCS_INACTIVE_DAYS: int = 7
