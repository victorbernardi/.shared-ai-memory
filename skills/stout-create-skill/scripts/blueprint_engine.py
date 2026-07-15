#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
import yaml
import sys

from platform_contract import SUPPORTED_PLATFORMS, create_default_manifest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def build_skill_config(name: str, description: str, platforms: list[str]) -> dict:
    enabled_platforms = {
        p: {"enabled": True, "output": f".{p}/skills"}
        for p in platforms
    }
    short_desc = description[:120] + "..." if len(description) > 120 else description
    return {
        "name": name,
        "version": "1.0.0",
        "author": "Victor",
        "platforms": enabled_platforms,
        "description": {
            "full": description,
            "short": short_desc,
        },
        "body": {
            "source": "SKILL.md",
            "sections": {
                "claude": ["all"],
                **{p.replace("-", ""): ["Objetivo", "Fluxo", "Constraints"]
                   for p in platforms if p != "claude-code"},
            },
        },
    }


def write_artifacts(output_dir: Path, blueprint: dict, skill_config: dict, manifest: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "blueprint.json").write_text(
        json.dumps(blueprint, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "skill.config.json").write_text(
        json.dumps(skill_config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "skill.platforms.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--description", type=str, required=True)
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Diretorio de saida para os artefatos gerados",
    )
    parser.add_argument(
        "--platforms",
        type=str,
        default=None,
        help="Plataformas alvo separadas por virgula (default: todas)",
    )
    args = parser.parse_args()

    config_path = Path(__file__).parent.parent / "config" / "tier_definitions.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        tiers = yaml.safe_load(f)["tiers"]

    tier_info = next((t for t in tiers if t["id"] == args.tier), None)
    if not tier_info:
        print(f"[ERRO] Tier {args.tier} nao encontrado.", file=sys.stderr)
        sys.exit(1)

    from platform_contract import parse_targets
    try:
        target_platforms = list(parse_targets(args.platforms))
    except ValueError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        sys.exit(1)

    blueprint = {
        "name": args.name,
        "tier": args.tier,
        "description": args.description,
        "target_platforms": target_platforms,
        "structure": tier_info["scaffold"],
    }

    skill_config = build_skill_config(args.name, args.description, target_platforms)
    manifest = create_default_manifest(tuple(target_platforms))

    output_dir = Path(args.output_dir)
    write_artifacts(output_dir, blueprint, skill_config, manifest)

    print(f"[OK] Blueprint gerado em {output_dir}")
    print(f"[OK] Plataformas: {', '.join(target_platforms)}")


if __name__ == "__main__":
    main()
