#!/usr/bin/env python3
"""Validates canonical sources, rendered packages, extension compatibility, and active legacy references."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from platform_contract import SUPPORTED_PLATFORMS, load_catalog

LEGACY_MARKERS = re.compile(
    r"antigravity|\.gemini/antigravity|@if\s+platform|@unless\s+platform|junction_guard|junction_map",
    re.IGNORECASE,
)

SCAN_ROOTS = (
    Path("skills/stout-create-skill"),
    Path("skills/stout-skill-manager"),
    Path("skills/stout-promote-skill"),
)

EXCLUDE_DIRS = {"tests", "fixtures", "_archived", "__pycache__", "node_modules"}


def validate_source(source_dir: Path, catalog: dict) -> list[str]:
    errors: list[str] = []
    skill_md = source_dir / "SKILL.md"

    if not skill_md.exists():
        errors.append("[ERRO] SKILL.md nao encontrado")
        return errors

    content = skill_md.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)

    if not frontmatter_match:
        errors.append("[ERRO] Frontmatter nao encontrado em SKILL.md")
        return errors

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    if not frontmatter:
        frontmatter = {}

    name = frontmatter.get("name", "")
    if not name:
        errors.append("[ERRO] Campo 'name' obrigatorio ausente no frontmatter")

    description = frontmatter.get("description", "")
    if not description:
        errors.append("[ERRO] Campo 'description' obrigatorio ausente no frontmatter")

    if name and source_dir.name != name:
        errors.append(f"[ERRO] Nome do diretorio '{source_dir.name}' nao corresponde ao frontmatter '{name}'")

    manifest_path = source_dir / "skill.platforms.yaml"
    if manifest_path.exists():
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if manifest:
            targets = manifest.get("targets", [])
            invalid_targets = set(targets) - set(SUPPORTED_PLATFORMS)
            if invalid_targets:
                errors.append(f"[ERRO] Targets invalidos no manifest: {', '.join(sorted(invalid_targets))}")

            extensions = manifest.get("extensions", [])
            extensions_catalog = catalog.get("extensions", {})
            for ext in extensions:
                ext_id = ext.get("id", "")
                if ext_id not in extensions_catalog:
                    errors.append(f"[ERRO] Extensao obrigatoria nao catalogada: {ext_id}")
                    continue

                ext_meta = extensions_catalog[ext_id]
                expected_type = ext_meta.get("value_type", "")
                value = ext.get("value", "")
                if expected_type == "string_list" and not isinstance(value, list):
                    errors.append(f"[ERRO] Extensao '{ext_id}' espera string_list, recebeu {type(value).__name__}")
                elif expected_type == "mapping" and not isinstance(value, dict):
                    errors.append(f"[ERRO] Extensao '{ext_id}' espera mapping, recebeu {type(value).__name__}")

                required = ext.get("required", False)
                if not isinstance(required, bool):
                    errors.append(f"[ERRO] Extensao '{ext_id}' campo 'required' deve ser booleano")

    return errors


def validate_rendered_package(platform: str, package_dir: Path, catalog: dict) -> list[str]:
    errors: list[str] = []

    if platform not in SUPPORTED_PLATFORMS:
        errors.append(f"[ERRO] Plataforma '{platform}' nao suportada")

    skill_md = package_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"[ERRO] SKILL.md ausente no pacote renderizado para {platform}")

    return errors


def validate_active_pipeline(roots: tuple[Path, ...] = SCAN_ROOTS) -> list[str]:
    errors: list[str] = []

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name == "hybrid_validator.py":
                continue
            if path.suffix not in {".py", ".md", ".json", ".yaml", ".yml"}:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if LEGACY_MARKERS.search(content):
                errors.append(f"[ERRO] Referencia legada ativa em: {path}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate platform compatibility")
    parser.add_argument("--source-path", type=str, help="Path to canonical skill source")
    parser.add_argument("--pipeline-root", type=str, help="Root directory for legacy scan")
    args = parser.parse_args()

    all_errors: list[str] = []

    if args.source_path:
        source_dir = Path(args.source_path)
        if not source_dir.exists():
            print(f"[ERRO] Source path does not exist: {source_dir}", file=sys.stderr)
            sys.exit(1)

        catalog_path = Path(__file__).parent.parent / "config" / "platform_capabilities.yaml"
        catalog = load_catalog(catalog_path)
        all_errors.extend(validate_source(source_dir, catalog))

    if args.pipeline_root:
        root = Path(args.pipeline_root)
        all_errors.extend(validate_active_pipeline((root,)))

    for error in all_errors:
        print(error, file=sys.stderr)

    if all_errors:
        sys.exit(1)

    print("[OK] Validacao concluida sem erros")


if __name__ == "__main__":
    main()
