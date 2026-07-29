#!/usr/bin/env python3
"""
Valida estrutura Stout de uma skill recém-instalada.
Verifica SKILL.md, frontmatter obrigatório e campos esperados.
"""
import sys
import re
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - installation fallback
    yaml = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_FIELDS = ["name", "version"]
RECOMMENDED_FIELDS = ["description", "tools", "tier"]


def extract_frontmatter(skill_md: Path) -> dict:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    if yaml is not None:
        parsed = yaml.safe_load(match.group(1))
        if isinstance(parsed, dict):
            fields = dict(parsed)
            metadata = fields.get("metadata")
            if isinstance(metadata, dict):
                # Stout historically expected version/tools/tier at the top
                # level. Keep aliases while preserving the common nested
                # metadata contract used by Codex and CommandCode.
                for key, value in metadata.items():
                    fields.setdefault(key, value)
            return fields

    fields = {}
    metadata = {}
    section = None
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, val = line.partition(":")
        if not separator:
            continue
        indentation = len(line) - len(line.lstrip())
        if indentation == 0:
            section = key.strip()
            fields[section] = val.strip()
        elif section == "metadata":
            metadata[key.strip()] = val.strip().strip("'\"")
    if metadata:
        fields["metadata"] = metadata
        for key, value in metadata.items():
            fields.setdefault(key, value)
    return fields


def validate(skill_path: Path) -> tuple[bool, list[str], list[str]]:
    errors = []
    warnings = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md ausente")
        return False, errors, warnings

    frontmatter = extract_frontmatter(skill_md)
    if not frontmatter:
        errors.append("Frontmatter YAML ausente ou malformado no SKILL.md")
        return False, errors, warnings

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"Campo obrigatório ausente: '{field}'")

    for field in RECOMMENDED_FIELDS:
        if field not in frontmatter:
            warnings.append(f"Campo recomendado ausente: '{field}'")

    return len(errors) == 0, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Valida estrutura Stout de uma skill")
    parser.add_argument("--skill-path", required=True, help="Path da skill instalada")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"[ERRO] Path não encontrado: {skill_path}")
        sys.exit(1)

    ok, errors, warnings = validate(skill_path)

    for e in errors:
        print(f"[ERRO] {e}")
    for w in warnings:
        print(f"[AVISO] {w}")

    if ok:
        print(f"[OK] Skill '{skill_path.name}' valida para instalacao Stout")
    else:
        print(f"[FALHA] Skill '{skill_path.name}' nao passou na validacao")
        sys.exit(1)


if __name__ == "__main__":
    main()
