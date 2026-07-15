#!/usr/bin/env python3
"""Renders a canonical source into one artifact per platform and applies registered extensions."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

from platform_contract import (
    SUPPORTED_PLATFORMS,
    CompatibilityItem,
    load_catalog,
    load_manifest,
)

SKIP_PATTERNS = {".stout-install.json", "skill.platforms.yaml", "platform-overrides"}


def _extract_skill_name(source_dir: Path) -> str:
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        return source_dir.name
    content = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^---\s*\n.*?name:\s*(.+?)\s*\n.*?---", content, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return source_dir.name


def render_source(source_dir: Path, output_dir: Path, catalog: dict) -> list[CompatibilityItem]:
    items: list[CompatibilityItem] = []
    extensions_catalog = catalog.get("extensions", {})
    skill_name = _extract_skill_name(source_dir)

    manifest_path = source_dir / "skill.platforms.yaml"
    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        target_platforms = manifest.targets
        requested_extensions = manifest.extensions
    else:
        target_platforms = SUPPORTED_PLATFORMS
        requested_extensions = ()

    for ext in requested_extensions:
        ext_meta = extensions_catalog.get(ext.id)
        if not ext_meta:
            items.append(CompatibilityItem(
                extension_id=ext.id,
                platform="all",
                status="error",
                reason="extensao nao catalogada",
            ))
            continue

        expected_type = ext_meta.get("value_type", "")
        if expected_type == "string_list" and not isinstance(ext.value, list):
            items.append(CompatibilityItem(
                extension_id=ext.id,
                platform="all",
                status="error",
                reason=f"tipo incorreto: espera {expected_type}",
            ))
            continue
        if expected_type == "mapping" and not isinstance(ext.value, dict):
            items.append(CompatibilityItem(
                extension_id=ext.id,
                platform="all",
                status="error",
                reason=f"tipo incorreto: espera {expected_type}",
            ))
            continue

        ext_platforms = set(ext_meta.get("platforms", []))
        compatible = ext_platforms & set(target_platforms)
        if not compatible and ext.required:
            items.append(CompatibilityItem(
                extension_id=ext.id,
                platform="all",
                status="error",
                reason="extensao obrigatoria sem plataforma compativel nos targets",
            ))
            continue

        for platform in target_platforms:
            if platform in ext_platforms:
                items.append(CompatibilityItem(
                    extension_id=ext.id,
                    platform=platform,
                    status="included",
                    reason="plataforma suportada",
                ))
            else:
                items.append(CompatibilityItem(
                    extension_id=ext.id,
                    platform=platform,
                    status="skipped",
                    reason="extensao nao suportada nesta plataforma",
                ))

    for platform in target_platforms:
        artifact_dir = output_dir / "rendered" / platform / skill_name
        artifact_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if item.name in SKIP_PATTERNS or item.name == "platform-overrides":
                continue
            if item.is_dir():
                dest = artifact_dir / item.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, artifact_dir / item.name)

        for ext in requested_extensions:
            ext_meta = extensions_catalog.get(ext.id, {})
            ext_platforms = set(ext_meta.get("platforms", []))
            if platform not in ext_platforms:
                continue

            kind = ext_meta.get("kind", "")
            output_spec = ext_meta.get("output", "")

            if kind == "frontmatter":
                _apply_frontmatter_extension(artifact_dir / "SKILL.md", ext.id, ext.value)
            elif kind == "file":
                out_path = artifact_dir / output_spec
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(
                    yaml.dump({ext.id: ext.value}, default_flow_style=False, allow_unicode=True),
                    encoding="utf-8",
                )

    return items


def _apply_frontmatter_extension(skill_md_path: Path, ext_id: str, value) -> None:
    if not skill_md_path.exists():
        return
    content = skill_md_path.read_text(encoding="utf-8")
    match = re.match(r"^(---\s*\n)(.*?)(\n---)", content, re.DOTALL)
    if not match:
        return
    header = match.group(1)
    body = match.group(2)
    footer = match.group(3)
    rest = content[match.end():]

    key = ext_id.split(".")[-1]
    if isinstance(value, list):
        val_str = yaml.dump(value, default_flow_style=False).strip()
    elif isinstance(value, dict):
        val_str = yaml.dump(value, default_flow_style=False).strip()
    else:
        val_str = str(value)

    if f"{key}:" in body:
        return

    new_fm = f"{body}\n{key}:\n{val_str}\n"
    skill_md_path.write_text(f"{header}{new_fm}{footer}{rest}", encoding="utf-8")


def write_compatibility_reports(output_dir: Path, items: list[CompatibilityItem]) -> None:
    payload = sorted(
        [asdict(item) for item in items],
        key=lambda item: (item["extension_id"], item["platform"]),
    )
    (output_dir / "compatibility-report.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    rows = [
        "| Extensao | Plataforma | Status | Motivo |",
        "| --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {item['extension_id']} | {item['platform']} | {item['status']} | {item['reason']} |"
        for item in payload
    )
    (output_dir / "compatibility-report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render platform packages from canonical source")
    parser.add_argument("--source-path", type=str, required=True, help="Path to canonical skill source")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for rendered packages")
    parser.add_argument("--catalog", type=str, default=None, help="Path to platform_capabilities.yaml")
    args = parser.parse_args()

    source_dir = Path(args.source_path)
    output_dir = Path(args.output_dir)

    if not source_dir.exists():
        print(f"[ERRO] Source path does not exist: {source_dir}", file=sys.stderr)
        sys.exit(1)

    catalog_path = Path(args.catalog) if args.catalog else (
        Path(__file__).parent.parent / "config" / "platform_capabilities.yaml"
    )
    catalog = load_catalog(catalog_path)

    items = render_source(source_dir, output_dir, catalog)
    write_compatibility_reports(output_dir, items)

    errors = [item for item in items if item.status == "error"]
    if errors:
        print(f"[ERRO] {len(errors)} extension(s) have errors", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Rendered packages to {output_dir / 'rendered'}")
    print(f"[OK] Compatibility reports written to {output_dir}")


if __name__ == "__main__":
    main()
