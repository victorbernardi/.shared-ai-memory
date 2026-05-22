#!/usr/bin/env python3
import json
import argparse
import os
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=str, default="blueprint.json")
    args = parser.parse_args()

    if not os.path.exists(args.blueprint):
        print(f"Erro: Blueprint {args.blueprint} não encontrado.")
        exit(1)

    with open(args.blueprint, 'r') as f:
        blueprint = json.load(f)

    target_dir = Path("/tmp") / blueprint['name']
    target_dir.mkdir(parents=True, exist_ok=True)

    for item in blueprint['structure']:
        if item.endswith('/'):
            (target_dir / item).mkdir(parents=True, exist_ok=True)
        else:
            file_path = target_dir / item
            file_path.touch()

    print(f"[OK] Estrutura criada em {target_dir}")

if __name__ == "__main__":
    main()
