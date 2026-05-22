import filecmp
import os
import shutil
from datetime import datetime
from pathlib import Path

# Configurações do Stout
# Assume que o script está em src/tools/ ou scripts/
PROJECT_ROOT = Path(os.getcwd())
USER_HOME = Path.home()
# O brain do Antigravity agora reside em .shared-ai-memory/brain
SHARED_MEMORY_ROOT = USER_HOME / ".shared-ai-memory"
BRAIN_DIR = SHARED_MEMORY_ROOT / "brain"
# Pasta de temporários do Gemini CLI
GEMINI_TMP_ROOT = SHARED_MEMORY_ROOT / ".gemini" / "tmp" / "shared-ai-memory"


def get_project_name():
    """Tenta ler o nome do projeto do GEMINI.md ou usa o nome da pasta."""
    gemini_md = PROJECT_ROOT / "GEMINI.md"
    if gemini_md.exists():
        with open(gemini_md, "r", encoding="utf-8") as f:
            for line in f:
                if "PROJETO:" in line:
                    return line.split("PROJETO:")[1].strip().lower().replace(" ", "-")
    return PROJECT_ROOT.name

def is_session_for_current_project(session_dir):
    """Verifica se a sessà£o pertence ao projeto atual lendo o overview.txt."""
    overview_path = session_dir / ".system_generated" / "logs" / "overview.txt"
    project_name_str = PROJECT_ROOT.name.lower()

    if overview_path.exists():
        try:
            # Vacina: Encoding explícito UTF-8
            with open(overview_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if project_name_str in line.lower():
                        return True
        except Exception:
            pass

    plans_dir = session_dir / "plans"
    if plans_dir.exists():
        for f in plans_dir.iterdir():
            if project_name_str in f.name.lower():
                return True
            if (datetime.now().timestamp() - os.path.getmtime(f)) < 300:
                return True

    return False

def get_latest_brain_session():
    """Localiza a sessà£o de brain (Antigravity) mais recente."""
    if not BRAIN_DIR.exists():
        return None
    sessions = sorted([d for d in BRAIN_DIR.iterdir() if d.is_dir()], key=os.path.getmtime, reverse=True)
    for session in sessions:
        if (session / "artifacts").exists() and is_session_for_current_project(session):
            return session
    return None

def get_latest_gemini_tmp_session():
    """Localiza a sessà£o de tmp (Gemini CLI) mais recente."""
    if not GEMINI_TMP_ROOT.exists():
        return None
    sessions = sorted([d for d in GEMINI_TMP_ROOT.iterdir() if d.is_dir()], key=os.path.getmtime, reverse=True)
    for session in sessions:
        if (session / "plans").exists() and is_session_for_current_project(session):
            return session
    return None

def promote_artifacts():
    # Coletar de ambas as fontes
    sessions = []

    brain = get_latest_brain_session()
    if brain:
        sessions.append((brain, brain / "artifacts", "antigravity"))

    tmp = get_latest_gemini_tmp_session()
    if tmp:
        sessions.append((tmp, tmp / "plans", "gemini"))

    if not sessions:
        print(f"AVISO: Nenhuma sessà£o (Brain ou TMP) encontrada para o projeto {PROJECT_ROOT.name}")
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    project_name = get_project_name()
    promoted_count = 0

    for session_root, src_dir, origin in sessions:
        print(f"Verificando origem {origin}: {session_root.name}")

        if origin == "antigravity":
            targets = [
                ("implementation_plan.md.resolved", "docs/plans", "plan"),
                ("implementation_plan.md", "docs/plans", "plan"),
                ("walkthrough.md", "docs/walkthroughs", "walkthrough"),
            ]
        else: # gemini
            targets = []
            for f in src_dir.glob("plan_*.md"):
                targets.append((f.name, "docs/plans", "plan"))

        for src_name, dest_subfolder, type_prefix in targets:
            src_path = src_dir / src_name
            if src_path.exists():
                dest_dir = PROJECT_ROOT / dest_subfolder
                dest_dir.mkdir(parents=True, exist_ok=True)

                new_filename = f"{type_prefix}_{date_str}_{project_name}.md"
                dest_path = dest_dir / new_filename

                counter = 1
                while dest_path.exists():
                    if filecmp.cmp(src_path, dest_path, shallow=False):
                        print(f"  [SKIP] {new_filename} (sem mudanças)")
                        break
                    counter += 1
                    new_filename = f"{type_prefix}_{date_str}_{project_name}_v{counter}.md"
                    dest_path = dest_dir / new_filename

                if not dest_path.exists():
                    shutil.copy2(src_path, dest_path)
                    print(f"  [OK] PROMOVIDO: {src_name} -> {dest_subfolder}/{new_filename}")
                    promoted_count += 1

    print(f"\nResumo: {promoted_count} artefatos sincronizados.")

if __name__ == "__main__":
    print(f"--- Stout Artifact Promoter v2.0 ---")
    promote_artifacts()
