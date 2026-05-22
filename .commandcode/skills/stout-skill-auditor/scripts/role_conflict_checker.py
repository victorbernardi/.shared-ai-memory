#!/usr/bin/env python3
"""
Checagem rápida e determinística para impedir papéis idênticos
antes mesmo da análise heurística profunda.
"""

import argparse
import json
import sys
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent.parent / "stout-skill-registry" / "registry.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposed-role", required=True)
    args = parser.parse_args()

    if not REGISTRY_PATH.exists():
        print(f"❌ ERRO: Registry não encontrado.")
        sys.exit(1)

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    proposed_role_clean = args.proposed_role.lower().strip()

    conflicts = []
    for skill in registry.get("skills", []):
        if skill.get("status") == "active":
            if skill.get("role", "").lower().strip() == proposed_role_clean:
                conflicts.append(skill["name"])

    if conflicts:
        print(f"[REJEICAO IMEDIATA] O papel '{args.proposed_role}' ja e exercido por {conflicts}.")
        print("   Ação: Use stout-improve-skill para evoluir a skill existente.")
        sys.exit(1)
    
    print(f"[OK] Passou no pre-check de conflito direto.")
    sys.exit(0)

if __name__ == "__main__":
    main()