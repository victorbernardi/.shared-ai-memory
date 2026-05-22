#!/usr/bin/env python3
"""
Orquestrador Principal da stout-create-skill.
Valida o laudo do Auditor, exige HITL para o blueprint e orquestra subagentes.
"""
import argparse
import json
import sys
import subprocess
import os
from pathlib import Path

def get_audit_result():
    # Procura no diretório atual de execução
    audit_file = Path("audit_result.json")
    if not audit_file.exists():
        print("[ERRO FATAL] audit_result.json não encontrado.")
        print("Ação exigida: Execute stout-skill-auditor primeiro para obter aprovação.")
        sys.exit(1)
        
    try:
        data = json.loads(audit_file.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        print(f"[ERRO FATAL] Falha ao ler audit_result.json: {e}")
        sys.exit(1)

def run_blueprint_engine(audit_data):
    # Caminho absoluto para evitar erros dependendo de onde é chamado
    skill_dir = Path(__file__).parent.parent
    blueprint_script = skill_dir / "scripts" / "blueprint_engine.py"
    
    cmd = [
        sys.executable, str(blueprint_script),
        "--tier", str(audit_data.get("proposed_tier", 1)),
        "--name", audit_data.get("proposed_name", "stout-unknown"),
        "--description", audit_data.get("proposed_role", "Papel não definido")
    ]
    
    print("\n[STEP 1] Gerando Blueprint...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] Falha ao gerar blueprint:\n{result.stderr}")
        sys.exit(result.returncode)
    print(result.stdout.strip())

def register_skill(audit_data):
    registry_script = Path(__file__).parent.parent.parent / "stout-skill-registry" / "scripts" / "register_skill.py"
    if not registry_script.exists():
        print(f"[AVISO] Script de registro não encontrado em {registry_script}. Pulando registro.")
        return
        
    cmd = [
        sys.executable, str(registry_script),
        "--name", audit_data.get("proposed_name"),
        "--path", f"skills/{audit_data.get('proposed_name')}",
        "--tier", str(audit_data.get("proposed_tier", 1)),
        "--category", "pending-classification", # Será ajustado pelo governance agent
        "--role", audit_data.get("proposed_role"),
        "--triggers", "trigger-1,trigger-2" # Draft
    ]
    print("\n[STEP 4] Registrando no Ledger...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout.strip())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-audit", action="store_true", help="Apenas verifica se existe laudo aprovado")
    args = parser.parse_args()

    audit_data = get_audit_result()
    
    if audit_data.get("verdict") != "APPROVED":
        print(f"[ERRO FATAL] O Auditor não aprovou esta skill.")
        print(f"Veredito: {audit_data.get('verdict')}")
        print(f"Motivo: {audit_data.get('notes')}")
        sys.exit(1)
        
    print(f"[OK] Laudo Aprovado pelo Auditor ({audit_data.get('audited_at')}).")
    if args.check_audit:
        sys.exit(0)

    # 1. Gerar Blueprint
    run_blueprint_engine(audit_data)
    
    # 2. HITL (Human in the loop)
    print("\n[HITL] O blueprint.json foi gerado localmente. Revise-o.")
    try:
        confirm = input("Deseja aprovar o blueprint e iniciar a manufatura física? [y/N]: ").strip().lower()
    except EOFError:
        print("[ERRO] Console não interativo. Cancelando.")
        sys.exit(1)
        
    if confirm != 'y':
        print("[CANCELADO] Manufatura abortada pelo usuário.")
        sys.exit(0)
        
    # 3. Orientação para Agentes
    print("\n[STEP 2 & 3] Autorização concedida.")
    print("[ACA0_AGENTE] Invoque o 'scaffolder_agent' para ler o blueprint.json e criar pastas.")
    print("[ACA0_AGENTE] Depois, invoque o 'code_drafter_agent' para gerar os scripts Python.")
    
    # 4. Registro Oficial (Aviso ao agente)
    print("\n[FINAL] Após os agentes terminarem, certifique-se de invocar este pipeline ou o register_skill.py manualmente para finalizar o ciclo.")

if __name__ == "__main__":
    main()