#!/usr/bin/env python3
"""
Orquestrador de refatoração com Auto-Healing V2.0.
Lê o laudo de elite e aplica correções automáticas em documentação.
"""
import argparse
import sys
import json
from pathlib import Path

def get_pending_actions(report_path: str):
    """Lê o laudo e extrai ações corretivas pendentes."""
    p = Path(report_path)
    if not p.exists():
        return []
    
    with open(p, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    actions = []
    for dim_name, dim_data in report.get("dimensions", {}).items():
        for finding in dim_data.get("findings", []):
            actions.append(finding)
            
    return actions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Nome da skill alvo")
    parser.add_argument("--report", default="elite_audit_report.json", help="Caminho do laudo")
    parser.add_argument("--auto", action="store_true", help="Aplica correções de doc automaticamente")
    args = parser.parse_args()

    actions = get_pending_actions(args.report)
    
    if not actions:
        print("[OK] Nenhuma ação pendente identificada no laudo.")
        return

    print(f"\n[DIAGNÓSTICO] Encontradas {len(actions)} oportunidades de melhoria na skill '{args.target}'.")
    
    # Filtra apenas documentação para o auto-healing
    doc_actions = [a for a in actions if a["dimension"] == "documentation"]

    if args.auto and doc_actions:
        print(f"\n[AUTO-HEALING] Corrigindo {len(doc_actions)} falhas de documentação...")
        
        target_path = Path(__file__).parent.parent.parent / args.target / "SKILL.md"
        if not target_path.exists():
            print(f"[ERRO] SKILL.md não encontrado em {target_path}")
            sys.exit(1)
            
        content = target_path.read_text(encoding="utf-8")
        
        for act in doc_actions:
            if act["category"].startswith("missing_section_"):
                section_name = act["category"].replace("missing_section_", "")
                title = section_name.capitalize()
                new_section = f"\n## {title}\nInformação gerada automaticamente pelo Auto-Healing Stout.\n"
                content += new_section
                print(f"  - Injetada seção: {title}")
        
        target_path.write_text(content, encoding="utf-8")
        print(f"\n[SUCESSO] Skill '{args.target}' curada. Re-execute o diagnóstico para validar.")
    else:
        for act in actions:
            print(f"  - [{act.get('severity', 'LOW').upper()}] {act['title']} -> {act['recommendation']}")
        print("\n[HITL] Use --auto para tentar correções automáticas em doc ou faça manualmente.")

if __name__ == "__main__":
    main()
