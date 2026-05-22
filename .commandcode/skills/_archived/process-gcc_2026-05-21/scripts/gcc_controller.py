#!/usr/bin/env python3
"""
Git-Context-Controller (GCC) — Motor de Blindagem contra Memória Envenenada
Ecossistema Stout/Antigravity — REGRA 3 do GEMINI.md

Usage:
    python gcc_controller.py branch <name> [--reason "motivo"]
    python gcc_controller.py discard <name>
    python gcc_controller.py merge <name>
    python gcc_controller.py status
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding for emoji/unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ── Configuration ──────────────────────────────────────────────────────────

SHARED_MEMORY = Path(os.environ.get(
    "SHARED_AI_MEMORY",
    Path.home() / ".shared-ai-memory"
))

CONTEXT_AGENT_DIR = SHARED_MEMORY / "context-agent"
MEMORY_DIR = SHARED_MEMORY / "memory"

# Source files to snapshot
ACTIVE_CONTEXT = CONTEXT_AGENT_DIR / "ACTIVE_CONTEXT.md"
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"

# GCC storage
GCC_DIR = CONTEXT_AGENT_DIR / "gcc"
BRANCHES_DIR = GCC_DIR / "branches"
DISCARDED_DIR = GCC_DIR / "branches" / "_discarded"
MERGED_DIR = GCC_DIR / "branches" / "_merged"
LOGS_DIR = GCC_DIR / "logs"
GCC_STATE_FILE = GCC_DIR / "gcc.json"

# Indicator injected into MEMORY.md
INDICATOR_PREFIX = "🔀 GCC Branch Ativo:"


# ── Helpers ────────────────────────────────────────────────────────────────

def ensure_dirs():
    """Create GCC directory structure if not exists."""
    for d in [BRANCHES_DIR, DISCARDED_DIR, MERGED_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    """Load GCC global state."""
    if GCC_STATE_FILE.exists():
        return json.loads(GCC_STATE_FILE.read_text(encoding="utf-8"))
    return {"active_branch": None, "history": []}


def save_state(state: dict):
    """Persist GCC global state."""
    GCC_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def log_operation(operation: str, branch_name: str, details: str = ""):
    """Append operation to audit log."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    log_file = LOGS_DIR / f"gcc-{datetime.now().strftime('%Y-%m-%d')}.log"
    entry = f"[{timestamp}] {operation}: {branch_name}"
    if details:
        entry += f" | {details}"
    entry += "\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)


def inject_indicator(branch_name: str):
    """Inject GCC branch indicator into MEMORY.md."""
    if not MEMORY_FILE.exists():
        print(f"  ⚠ MEMORY.md not found at {MEMORY_FILE}. Skipping indicator.")
        return

    content = MEMORY_FILE.read_text(encoding="utf-8")
    indicator_line = f"{INDICATOR_PREFIX} {branch_name} (desde {datetime.now().strftime('%Y-%m-%d %H:%M')})\n"

    # Check if indicator already present
    if INDICATOR_PREFIX in content:
        print("  ⚠ Indicator already present. Updating...")
        lines = content.split("\n")
        lines = [l for l in lines if INDICATOR_PREFIX not in l]
        content = "\n".join(lines)

    # Inject at top (after first heading if exists)
    lines = content.split("\n")
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_pos = i + 1
            break

    lines.insert(insert_pos, "")
    lines.insert(insert_pos + 1, indicator_line)
    MEMORY_FILE.write_text("\n".join(lines), encoding="utf-8")


def remove_indicator():
    """Remove GCC branch indicator from MEMORY.md."""
    if not MEMORY_FILE.exists():
        return

    content = MEMORY_FILE.read_text(encoding="utf-8")
    if INDICATOR_PREFIX not in content:
        return

    lines = content.split("\n")
    lines = [l for l in lines if INDICATOR_PREFIX not in l]
    # Clean up any double blank lines left behind
    cleaned = "\n".join(lines)
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    MEMORY_FILE.write_text(cleaned, encoding="utf-8")


def copy_state_to_branch(branch_dir: Path):
    """Copy cognitive state files to branch directory."""
    for src in [ACTIVE_CONTEXT, MEMORY_FILE]:
        if src.exists():
            dest = branch_dir / src.name
            shutil.copy2(src, dest)
            print(f"  ✓ Copied {src.name}")
        else:
            print(f"  ⚠ {src.name} not found, skipping")


def restore_state_from_branch(branch_dir: Path):
    """Restore cognitive state files from branch snapshot."""
    for filename in ["ACTIVE_CONTEXT.md", "MEMORY.md"]:
        src = branch_dir / filename
        if filename == "ACTIVE_CONTEXT.md":
            dest = ACTIVE_CONTEXT
        else:
            dest = MEMORY_FILE

        if src.exists():
            # Create backup of current state before restoring
            if dest.exists():
                backup = dest.with_suffix(".md.pre-restore")
                shutil.copy2(dest, backup)
            shutil.copy2(src, dest)
            print(f"  ✓ Restored {filename}")
        else:
            print(f"  ⚠ {filename} not in branch snapshot, skipping")


# ── Commands ───────────────────────────────────────────────────────────────

def cmd_branch(name: str, reason: str = ""):
    """Create a new experimental branch."""
    ensure_dirs()
    state = load_state()

    # Guard: no nested branches
    if state["active_branch"]:
        print(f"  ✖ ERRO: Branch '{state['active_branch']}' já está ativo.")
        print("  → Faça 'gcc discard' ou 'gcc merge' antes de criar outro.")
        sys.exit(1)

    branch_dir = BRANCHES_DIR / name

    # Guard: idempotency
    if branch_dir.exists():
        print(f"  ✖ ERRO: Branch '{name}' já existe.")
        print("  → Use outro nome ou faça discard/merge do existente.")
        sys.exit(1)

    branch_dir.mkdir(parents=True)

    # 1. Copy state
    print(f"\n🔀 GCC BRANCH: Criando branch '{name}'...")
    copy_state_to_branch(branch_dir)

    # 2. Write metadata
    metadata = {
        "name": name,
        "reason": reason,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "source_files": {
            "ACTIVE_CONTEXT.md": str(ACTIVE_CONTEXT),
            "MEMORY.md": str(MEMORY_FILE)
        }
    }
    (branch_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # 3. Create empty learnings.md
    (branch_dir / "learnings.md").write_text(
        f"# Learnings: {name}\n\n"
        f"> Preencha este arquivo ANTES de executar `gcc merge`.\n"
        f"> O merge será RECUSADO se este arquivo estiver vazio.\n\n"
        f"## O que funcionou e por quê\n\n\n"
        f"## Decisões técnicas validadas\n\n\n"
        f"## Padrões descobertos\n\n",
        encoding="utf-8"
    )

    # 4. Inject indicator into MEMORY.md
    inject_indicator(name)

    # 5. Update state
    state["active_branch"] = name
    state["history"].append({
        "operation": "branch",
        "name": name,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })
    save_state(state)

    # 6. Log
    log_operation("BRANCH", name, reason)

    print(f"\n  ✅ Branch '{name}' criado com sucesso.")
    print(f"  📁 Snapshot em: {branch_dir}")
    print(f"  📝 Preencha learnings.md antes do merge.")
    print(f"\n  → Prossiga com a experimentação.")
    print(f"  → Se falhar: python gcc_controller.py discard \"{name}\"")
    print(f"  → Se funcionar: python gcc_controller.py merge \"{name}\"")


def cmd_discard(name: str):
    """Discard a failed branch and restore clean state."""
    ensure_dirs()
    state = load_state()

    branch_dir = BRANCHES_DIR / name
    if not branch_dir.exists():
        print(f"  ✖ ERRO: Branch '{name}' não encontrado.")
        sys.exit(1)

    print(f"\n🗑️ GCC DISCARD: Descartando branch '{name}'...")

    # 1. Restore state from snapshot
    restore_state_from_branch(branch_dir)

    # 2. Remove indicator from MEMORY.md
    remove_indicator()

    # 3. Generate transition briefing
    briefing = (
        f"\n\n---\n"
        f"## ⚠️ GCC DISCARD — Branch '{name}' Descartado\n\n"
        f"**ATENÇÃO:** Todo raciocínio e conclusões gerados durante o branch "
        f"'{name}' são NULOS E INVÁLIDOS. O estado cognitivo foi restaurado "
        f"para o ponto anterior ao branch.\n\n"
        f"**NÃO reutilize** nenhuma conclusão, código ou decisão do branch "
        f"descartado. Reinicie a abordagem do zero se necessário.\n"
        f"---\n"
    )

    # Append briefing to ACTIVE_CONTEXT for visibility
    if ACTIVE_CONTEXT.exists():
        with open(ACTIVE_CONTEXT, "a", encoding="utf-8") as f:
            f.write(briefing)
        print("  ✓ Briefing de transição injetado no ACTIVE_CONTEXT.md")

    # 4. Move branch to _discarded
    dest = DISCARDED_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.move(str(branch_dir), str(dest))
    print(f"  ✓ Branch movido para _discarded/")

    # 5. Update state
    state["active_branch"] = None
    state["history"].append({
        "operation": "discard",
        "name": name,
        "timestamp": datetime.now().isoformat()
    })
    save_state(state)

    # 6. Log
    log_operation("DISCARD", name)

    print(f"\n  ✅ Branch '{name}' descartado. Estado limpo restaurado.")
    print(f"  ⚠️ Todo raciocínio do branch é INVÁLIDO. Recomece do zero.")


def cmd_merge(name: str):
    """Merge validated learnings from a successful branch."""
    ensure_dirs()
    state = load_state()

    branch_dir = BRANCHES_DIR / name
    if not branch_dir.exists():
        print(f"  ✖ ERRO: Branch '{name}' não encontrado.")
        sys.exit(1)

    # Guard: learnings.md must exist and have content
    learnings_file = branch_dir / "learnings.md"
    if not learnings_file.exists():
        print(f"  ✖ ERRO: learnings.md não encontrado no branch '{name}'.")
        print(f"  → Preencha o arquivo antes de fazer merge.")
        sys.exit(1)

    learnings_content = learnings_file.read_text(encoding="utf-8").strip()
    # Check if learnings has actual content beyond the template
    template_markers = [
        "# Learnings:",
        "Preencha este arquivo",
        "O merge ser",
        "RECUSADO",
        "## O que funcionou",
        "## Decisões técnicas",
        "## Padrões descobertos",
    ]
    content_lines = [
        l.strip() for l in learnings_content.split("\n")
        if l.strip()
        and not l.strip().startswith("#")
        and not l.strip().startswith(">")
        and not any(t in l for t in template_markers)
    ]

    if len(content_lines) == 0:
        print(f"  ✖ ERRO: learnings.md está vazio (apenas template).")
        print(f"  → Documente os aprendizados antes de fazer merge.")
        print(f"  → O merge RECUSA conteúdo vazio para prevenir injeção de veneno.")
        sys.exit(1)

    print(f"\n🔀 GCC MERGE: Consolidando branch '{name}'...")

    # 1. Inject learnings into ACTIVE_CONTEXT.md
    if ACTIVE_CONTEXT.exists():
        merge_block = (
            f"\n\n---\n"
            f"## ✅ GCC MERGE — Branch '{name}' Consolidado "
            f"({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
            f"{learnings_content}\n"
            f"---\n"
        )
        with open(ACTIVE_CONTEXT, "a", encoding="utf-8") as f:
            f.write(merge_block)
        print("  ✓ Learnings injetados no ACTIVE_CONTEXT.md")

    # 2. Remove indicator from MEMORY.md
    remove_indicator()
    print("  ✓ Indicator removido do MEMORY.md")

    # 3. Move branch to _merged
    dest = MERGED_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.move(str(branch_dir), str(dest))
    print(f"  ✓ Branch arquivado em _merged/")

    # 4. Update state
    state["active_branch"] = None
    state["history"].append({
        "operation": "merge",
        "name": name,
        "timestamp": datetime.now().isoformat()
    })
    save_state(state)

    # 5. Log
    log_operation("MERGE", name)

    print(f"\n  ✅ Branch '{name}' mergeado com sucesso.")
    print(f"  📝 Learnings consolidados no ACTIVE_CONTEXT.md do trunk.")


def cmd_status():
    """Show current GCC state."""
    ensure_dirs()
    state = load_state()

    print("\n📊 GCC STATUS")
    print("=" * 50)

    # Active branch
    if state["active_branch"]:
        branch_dir = BRANCHES_DIR / state["active_branch"]
        meta_file = branch_dir / "metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            print(f"\n  🔀 Branch ativo: {state['active_branch']}")
            print(f"     Motivo: {meta.get('reason', 'N/A')}")
            print(f"     Criado: {meta.get('created_at', 'N/A')}")
        else:
            print(f"\n  🔀 Branch ativo: {state['active_branch']}")
    else:
        print("\n  ✅ Nenhum branch ativo (trunk limpo)")

    # List all branches
    branches = [
        d for d in BRANCHES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    ]
    if branches:
        print(f"\n  📁 Branches existentes ({len(branches)}):")
        for b in branches:
            meta_file = b / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                status_icon = "🟢" if meta.get("status") == "active" else "⚪"
                print(f"     {status_icon} {b.name} — {meta.get('reason', 'N/A')}")
            else:
                print(f"     ⚪ {b.name}")

    # Recent history
    history = state.get("history", [])
    if history:
        recent = history[-5:]
        print(f"\n  📜 Histórico recente ({len(recent)} de {len(history)}):")
        for h in reversed(recent):
            icon = {"branch": "🔀", "discard": "🗑️", "merge": "✅"}.get(
                h["operation"], "❓"
            )
            ts = h.get("timestamp", "N/A")[:16]
            print(f"     {icon} [{ts}] {h['operation']}: {h['name']}")

    print(f"\n  📂 Storage: {GCC_DIR}")
    print("=" * 50)


# ── CLI Entry Point ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Git-Context-Controller (GCC) — Blindagem contra Memória Envenenada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  gcc_controller.py branch "tese-api-v3" --reason "Testar se a API v3 resolve o rate limit"
  gcc_controller.py status
  gcc_controller.py merge "tese-api-v3"
  gcc_controller.py discard "tese-api-v3"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando GCC")

    # branch
    branch_parser = subparsers.add_parser("branch", help="Criar branch experimental")
    branch_parser.add_argument("name", help="Nome do branch (kebab-case)")
    branch_parser.add_argument("--reason", default="", help="Motivo da hipótese")

    # discard
    discard_parser = subparsers.add_parser("discard", help="Descartar branch envenenado")
    discard_parser.add_argument("name", help="Nome do branch a descartar")

    # merge
    merge_parser = subparsers.add_parser("merge", help="Consolidar branch validado")
    merge_parser.add_argument("name", help="Nome do branch a mergear")

    # status
    subparsers.add_parser("status", help="Verificar estado atual")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "branch":
        cmd_branch(args.name, args.reason)
    elif args.command == "discard":
        cmd_discard(args.name)
    elif args.command == "merge":
        cmd_merge(args.name)
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
