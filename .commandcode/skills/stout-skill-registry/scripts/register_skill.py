#!/usr/bin/env python3
"""
Registra ou atualiza uma skill no registry do ecossistema Stout.
Versão: 1.1.0 (Refatorada por stout-improve-skill v1.2.0)
"""

import argparse
import json
import sys
import threading
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

# Global Lock para evitar race conditions em ambiente concorrente
_registry_lock = threading.Lock()
REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"

def load_registry() -> Dict[str, Any]:
    """Carrega o banco de dados de metadados do ecossistema."""
    if not REGISTRY_PATH.exists():
        print(f"[ERRO] Registry não encontrado em {REGISTRY_PATH}")
        sys.exit(1)
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def save_registry(data: Dict[str, Any]):
    """Salva os dados de forma atômica no registry.json usando Lock."""
    with _registry_lock:
        temp_file = REGISTRY_PATH.with_suffix(".tmp")
        temp_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_file.replace(REGISTRY_PATH)

def validate_unique_role(registry: Dict[str, Any], role: str, current_name: Optional[str] = None) -> List[str]:
    """Garante que nenhuma outra skill ativa tem o mesmo papel (Role)."""
    role_clean = role.lower().strip()
    return [s["name"] for s in registry["skills"] 
            if s["status"] == "active" and s["name"] != current_name 
            and s["role"].lower().strip() == role_clean]

def bump_version(version_str: str, bump_type: str) -> str:
    """Realiza o incremento SemVer (major.minor.patch)."""
    major, minor, patch = map(int, version_str.split("."))
    if bump_type == "major":   
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor": 
        minor += 1; patch = 0
    elif bump_type == "patch": 
        patch += 1
    return f"{major}.{minor}.{patch}"

def handle_version_bump(existing: Dict[str, Any], registry: Dict[str, Any], args: argparse.Namespace):
    """Encapsula a lógica de atualização de versão."""
    existing["version"] = bump_version(existing["version"], args.bump_version)
    existing["updated_at"] = str(date.today())
    if args.notes: 
        existing["notes"] = args.notes
    save_registry(registry)
    print(f"[OK] '{args.name}' atualizado para v{existing['version']}")

def handle_new_registration(registry: Dict[str, Any], args: argparse.Namespace):
    """Encapsula a lógica de registro de uma nova skill."""
    # Validar campos obrigatórios
    if not all([args.path, args.tier, args.category, args.role, args.triggers]):
        print("[ERRO] Para nova skill, os campos --path, --tier, --category, --role e --triggers são obrigatórios.")
        sys.exit(1)

    # Validar papel único
    conflicts = validate_unique_role(registry, args.role)
    if conflicts:
        print(f"[ERRO] O papel '{args.role}' já pertence a: {conflicts}")
        sys.exit(1)

    today = str(date.today())
    triggers = [t.strip() for t in args.triggers.split(",") if t.strip()]
    deps = [d.strip() for d in args.dependencies.split(",") if d.strip()]

    entry = {
        "name": args.name,
        "path": args.path,
        "tier": args.tier,
        "category": args.category,
        "role": args.role,
        "triggers": triggers,
        "dependencies": deps,
        "version": "1.0.0",
        "status": "active",
        "created_at": today,
        "updated_at": today,
        "author": args.author,
        "notes": args.notes
    }

    registry["skills"].append(entry)
    registry["last_updated"] = today
    save_registry(registry)
    print(f"[OK] '{args.name}' registrado com sucesso como v1.0.0")

def main():
    parser = argparse.ArgumentParser(description="Registra ou atualiza skill no registry Stout")
    parser.add_argument("--name", required=True)
    parser.add_argument("--path")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4])
    parser.add_argument("--category")
    parser.add_argument("--role")
    parser.add_argument("--triggers", help="Separados por vírgula")
    parser.add_argument("--dependencies", default="", help="Separados por vírgula")
    parser.add_argument("--author", default="Victor")
    parser.add_argument("--notes", default="")
    parser.add_argument("--bump-version", choices=["patch", "minor", "major"])
    args = parser.parse_args()

    if not args.name.startswith("stout-"):
        print(f"[ERRO] Nome deve começar com 'stout-'. Recebido: '{args.name}'")
        sys.exit(1)

    registry = load_registry()
    existing = next((s for s in registry["skills"] if s["name"] == args.name), None)

    if existing and args.bump_version:
        handle_version_bump(existing, registry, args)
    elif existing:
        print(f"[AVISO] '{args.name}' já existe. Use --bump-version para atualizar.")
        sys.exit(1)
    else:
        handle_new_registration(registry, args)

if __name__ == "__main__":
    main()
