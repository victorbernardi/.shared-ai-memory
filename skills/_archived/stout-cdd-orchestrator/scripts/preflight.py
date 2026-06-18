import json
import sys
from pathlib import Path


def check_dependencies(skill_name: str, registry_path: Path, skills_dir: Path) -> list[str]:
    """Return list of missing first-level dependency names. Empty = all present."""
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    skill = next((s for s in data["skills"] if s["name"] == skill_name), None)
    if skill is None:
        return []
    missing = []
    for dep in skill.get("dependencies") or []:
        if not (skills_dir / dep).exists():
            missing.append(dep)
    return missing


def run_preflight(skill_name: str, registry_path: Path, skills_dir: Path) -> bool:
    """Print missing dependencies and return False if any are missing."""
    missing = check_dependencies(skill_name, registry_path, skills_dir)
    if not missing:
        return True
    print(f"\n[PREFLIGHT FAIL] Skill '{skill_name}' requer dependências não instaladas:")
    for dep in missing:
        print(f"  - {dep}  (instale em skills/{dep}/)")
    print("\nInstale as skills ausentes antes de continuar.")
    return False
