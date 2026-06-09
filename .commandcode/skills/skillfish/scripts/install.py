#!/usr/bin/env python3
"""Instala uma skill via skillfish CLI usando sempre o path canonico Stout."""
import argparse
import subprocess
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Path canonico — NUNCA usar junctions como destino de escrita
CANONICAL_SKILLS_DIR = Path.home() / ".shared-ai-memory" / "skills"
JUNCTION_GUARD = Path(__file__).parent.parent.parent / "stout-skill-manager" / "scripts" / "junction_guard.py"
REQUIRED_FRONTMATTER = ["name", "version"]


def run_junction_guard() -> bool:
    if not JUNCTION_GUARD.exists():
        print("[AVISO] junction_guard nao encontrado — pulando verificacao")
        return True
    result = subprocess.run([sys.executable, str(JUNCTION_GUARD)], capture_output=False)
    return result.returncode == 0


def run_skillfish_add(package: str, output_dir: Path) -> bool:
    result = subprocess.run(
        ["skillfish", "add", package, "--output", str(output_dir)],
        capture_output=False
    )
    return result.returncode == 0


def validate_stout_structure(skill_path: Path) -> tuple[bool, list[str]]:
    errors = []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md ausente")
        return False, errors

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    import re
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append("Frontmatter YAML ausente no SKILL.md")
        return False, errors

    frontmatter_text = match.group(1)
    for field in REQUIRED_FRONTMATTER:
        if f"{field}:" not in frontmatter_text:
            errors.append(f"Campo obrigatorio ausente: '{field}'")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Instala skill via skillfish CLI")
    parser.add_argument("--package", required=True, help="Owner/repo ou owner/repo@skill")
    parser.add_argument("--skill-name", required=True, help="Nome da pasta destino (kebab-case)")
    parser.add_argument("--force", action="store_true", help="Sobrescreve skill existente")
    args = parser.parse_args()

    dest = CANONICAL_SKILLS_DIR / args.skill_name

    if dest.exists() and not args.force:
        print(f"[ERRO] Skill '{args.skill_name}' ja existe em {dest}")
        print("Use --force para sobrescrever (requer aprovacao explicita).")
        sys.exit(1)

    print(f"[INFO] Verificando junctions antes da instalacao...")
    if not run_junction_guard():
        print("[ERRO] junction_guard falhou — abortando instalacao")
        sys.exit(1)

    print(f"[INFO] Instalando '{args.package}' via skillfish...")
    print(f"[INFO] Destino canonico: {CANONICAL_SKILLS_DIR}")

    if not run_skillfish_add(args.package, CANONICAL_SKILLS_DIR):
        print(f"[ERRO] skillfish add falhou para '{args.package}'")
        sys.exit(1)

    if not dest.exists():
        print(f"[ERRO] Skill nao encontrada em {dest} apos instalacao")
        print("[INFO] Verifique se o nome da skill coincide com o nome da pasta gerada pelo skillfish")
        sys.exit(1)

    print(f"[INFO] Validando estrutura Stout...")
    ok, errors = validate_stout_structure(dest)
    for e in errors:
        print(f"[ERRO] {e}")

    if not ok:
        print("[ERRO] Estrutura Stout invalida — removendo instalacao corrompida")
        shutil.rmtree(dest, ignore_errors=True)
        sys.exit(1)

    print(f"[OK] Skill '{args.skill_name}' instalada em {dest}")
    print("[OK] Disponivel em todas as plataformas via junction")


if __name__ == "__main__":
    main()
