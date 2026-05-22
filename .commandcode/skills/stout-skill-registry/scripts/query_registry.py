#!/usr/bin/env python3
"""Consulta skills no registry do ecossistema Stout."""

import argparse
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"

def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def print_skill(skill: dict):
    status_icon = {"active": "[ACTIVE]", "beta": "[BETA]", "deprecated": "[DEPRECATED]"}.get(skill["status"], "[?]")
    print(f"\n{status_icon} {skill['name']} (v{skill['version']}) - Tier {skill['tier']}")
    print(f"   Papel:      {skill['role']}")
    print(f"   Categoria:  {skill['category']}")
    print(f"   Triggers:   {', '.join(skill['triggers'])}")
    print(f"   Path:       {skill['path']}")
    if skill.get("dependencies"):
        print(f"   Depende de: {', '.join(skill['dependencies'])}")
    if skill.get("notes"):
        print(f"   Notas:      {skill['notes']}")

def main():
    parser = argparse.ArgumentParser(description="Consulta o registry de skills Stout")
    parser.add_argument("--name",     help="Filtrar por nome (suporta wildcard *)")
    parser.add_argument("--category", help="Filtrar por categoria")
    parser.add_argument("--trigger",  help="Filtrar por trigger semântico")
    parser.add_argument("--status",   choices=["active", "beta", "deprecated"], default="active")
    parser.add_argument("--tier",     type=int, choices=[1, 2, 3, 4])
    parser.add_argument("--impact",   help="Consulta dependentes da skill especificada")
    args = parser.parse_args()

    registry = load_registry()
    
    if args.impact:
        impacted_skills = [s for s in registry["skills"] if args.impact in s.get("dependencies", [])]
        if not impacted_skills:
            print(f"ℹ️  Nenhuma skill depende de '{args.impact}'.")
        else:
            print(f"⚠️  As seguintes skills dependem de '{args.impact}' (Impacto):")
            for s in impacted_skills:
                print(f"   - {s['name']} (v{s['version']})")
        return

    skills = [s for s in registry["skills"] if s["status"] == args.status]

    if args.name:
        pattern = args.name.replace("*", "")
        skills = [s for s in skills if pattern in s["name"]]
    if args.category:
        skills = [s for s in skills if s["category"] == args.category]
    if args.trigger:
        skills = [s for s in skills if any(args.trigger.lower() in t.lower() for t in s["triggers"])]
    if args.tier:
        skills = [s for s in skills if s["tier"] == args.tier]

    if not skills:
        print(f"ℹ️  Nenhuma skill encontrada com os filtros aplicados.")
        return

    print(f"\nRegistry Stout - {len(skills)} skill(s) encontrada(s):")
    for skill in skills:
        print_skill(skill)

if __name__ == "__main__":
    main()