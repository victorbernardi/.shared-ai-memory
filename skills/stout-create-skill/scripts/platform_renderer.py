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

    for ext_id, ext_meta in extensions_catalog.items():
        ext_platforms = set(ext_meta.get("platforms", []))
        for platform in SUPPORTED_PLATFORMS:
            if platform in ext_platforms:
                items.append(CompatibilityItem(
                    extension_id=ext_id,
                    platform=platform,
                    status="included",
                    reason="plataforma suportada",
                ))
            else:
                items.append(CompatibilityItem(
                    extension_id=ext_id,
                    platform=platform,
                    status="skipped",
                    reason="extensao nao suportada nesta plataforma",
                ))

    for platform in SUPPORTED_PLATFORMS:
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

    return items


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
