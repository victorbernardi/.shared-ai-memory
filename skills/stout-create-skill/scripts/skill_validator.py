#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
import yaml
import io

# Reconfigura o output para UTF-8 no Windows
if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def validate_quality(skill_path: str, config_path: str) -> bool:
    print(f"Auditando skill em: {skill_path}")
    print(f"Usando Quality Gate: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        gates = yaml.safe_load(f)['checklists']
    
    skill_dir = Path(skill_path)
    all_passed = True

    # Gate 1: Mandatory Files
    if not (skill_dir / "SKILL.md").exists():
        print("[FALHA] SKILL.md nao encontrado.")
        all_passed = False
    
    # Gate 2: Technical Integrity (Scripts)
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            # Check basic executable status (simulated cross-platform check)
            if not os.access(script, os.X_OK):
                print(f"[AVISO] O script {script.name} pode nao ter permissao de execucao.")
    
    # Gate 3: Security Leak (Basic Check)
    for ext in ["*.py", "*.md", "*.json", "*.yaml"]:
        for file in skill_dir.rglob(ext):
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "sk-" in content or "password=" in content:
                    print(f"[FALHA DE SEGURANCA] Possivel secret hardcoded em {file.name}.")
                    all_passed = False

    return all_passed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    config_path = Path(__file__).parent.parent / 'config' / 'quality_gate.yaml'
    
    if validate_quality(args.path, str(config_path)):
        print("\n[SUCESSO] Skill aprovada no Quality Gate Stout Inova.")
        sys.exit(0)
    else:
        print("\n[REPROVADA] A skill nao atende aos criterios do Quality Gate.")
        sys.exit(1)

if __name__ == "__main__":
    main()
