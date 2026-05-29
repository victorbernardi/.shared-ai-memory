#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
import yaml
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_PLATFORMS = ["claude-code", "antigravity", "commandcode"]

PLATFORM_OUTPUTS = {
    "claude-code":   ".claude/skills",
    "antigravity":   ".gemini/antigravity-cli/skills",
    "commandcode":   ".commandcode/skills",
    "gemini-cli":    ".gemini/skills",
}


def build_skill_config(name: str, description: str, platforms: list[str]) -> dict:
    enabled_platforms = {
        p: {"enabled": True, "output": PLATFORM_OUTPUTS.get(p, f".{p}/skills")}
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--description", type=str, required=True)
    parser.add_argument(
        "--platforms",
        type=str,
        default=",".join(DEFAULT_PLATFORMS),
        help="Plataformas alvo separadas por virgula (default: claude-code,antigravity,commandcode)",
    )
    args = parser.parse_args()

    config_path = Path(__file__).parent.parent / "config" / "tier_definitions.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        tiers = yaml.safe_load(f)["tiers"]

    tier_info = next((t for t in tiers if t["id"] == args.tier), None)
    if not tier_info:
        print(f"[ERRO] Tier {args.tier} nao encontrado.")
        sys.exit(1)

    target_platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    blueprint = {
        "name": args.name,
        "tier": args.tier,
        "description": args.description,
        "target_platforms": target_platforms,
        "structure": tier_info["scaffold"],
    }

    skill_config = build_skill_config(args.name, args.description, target_platforms)

    with open("blueprint.json", "w", encoding="utf-8") as f:
        json.dump(blueprint, f, indent=2, ensure_ascii=False)

    with open("skill.config.json", "w", encoding="utf-8") as f:
        json.dump(skill_config, f, indent=2, ensure_ascii=False)

    print(f"[OK] blueprint.json gerado para '{args.name}' (Tier {args.tier})")
    print(f"[OK] skill.config.json gerado — plataformas: {', '.join(target_platforms)}")


if __name__ == "__main__":
    main()
