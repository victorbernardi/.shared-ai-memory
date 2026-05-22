#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
import yaml
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--description", type=str, required=True)
    args = parser.parse_args()

    # Load tier definitions
    config_path = Path(__file__).parent.parent / 'config' / 'tier_definitions.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        tiers = yaml.safe_load(f)['tiers']
    
    tier_info = next((t for t in tiers if t['id'] == args.tier), None)
    if not tier_info:
        print(f"Tier {args.tier} não encontrado.")
        sys.exit(1)

    blueprint = {
        "name": args.name,
        "tier": args.tier,
        "description": args.description,
        "structure": tier_info['scaffold']
    }

    with open('blueprint.json', 'w', encoding='utf-8') as f:
        json.dump(blueprint, f, indent=2)
    
    print(f"[OK] blueprint.json gerado para {args.name} (Tier {args.tier})")

if __name__ == "__main__":
    main()
