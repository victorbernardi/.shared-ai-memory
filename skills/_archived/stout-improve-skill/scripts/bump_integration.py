#!/usr/bin/env python3
"""
Integração com o registry para oficializar o bump de versão de uma skill após a melhoria.
"""
import argparse
import sys
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Nome da skill alvo")
    parser.add_argument("--type", choices=["patch", "minor", "major"], default="minor", help="Tipo de bump")
    args = parser.parse_args()

    registry_script = Path(__file__).parent.parent.parent / "stout-skill-registry" / "scripts" / "register_skill.py"
    
    if not registry_script.exists():
        print(f"[ERRO] Script de registro não encontrado em {registry_script}")
        sys.exit(1)

    print(f"\n[BUMP] Iniciando processo de bump ({args.type}) para a skill '{args.target}'...")
    
    # Chama o register_skill.py existente no ledger
    cmd = [sys.executable, str(registry_script), "--name", args.target, "--bump-version", args.type]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
        
    if result.returncode == 0:
        print("[SUCESSO] Atualização no Ledger concluída e versionamento atualizado.")
    else:
        print("[ERRO] Falha ao atualizar o Ledger.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()