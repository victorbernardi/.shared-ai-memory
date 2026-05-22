#!/usr/bin/env python3
"""Depreca uma skill no registry. NUNCA deleta — apenas marca como deprecated."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"

def main():
    parser = argparse.ArgumentParser(description="Depreca uma skill do registry Stout")
    parser.add_argument("--name", required=True)
    parser.add_argument("--reason", required=True, help="Motivo da depreciação")
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    skill = next((s for s in registry["skills"] if s["name"] == args.name), None)

    if not skill:
        print(f"[ERRO] Skill '{args.name}' não encontrada no registry.")
        sys.exit(1)

    if skill["status"] == "deprecated":
        print(f"[AVISO] '{args.name}' já está depreciada.")
        sys.exit(0)

    # Move para deprecated com histórico
    skill["status"] = "deprecated"
    skill["updated_at"] = str(date.today())
    skill["notes"] = f"[DEPRECATED {date.today()}] {args.reason}"

    if "deprecated" not in registry:
        registry["deprecated"] = []

    registry["deprecated"].append({"name": args.name, "deprecated_at": str(date.today()), "reason": args.reason})
    registry["last_updated"] = str(date.today())

    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] '{args.name}' depreciada. Historico preservado no registry.")

if __name__ == "__main__":
    main()