#!/usr/bin/env python3
"""
Avalia a sobreposição semântica entre uma intenção de nova skill
e as skills ativas no stout-skill-registry.
Gera o artefato audit_result.json com o veredito.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import yaml

AUDITOR_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = AUDITOR_ROOT.parent / "stout-skill-registry" / "registry.json"
THRESHOLDS_PATH = AUDITOR_ROOT / "config" / "similarity_threshold.yaml"

def load_registry():
    if not REGISTRY_PATH.exists():
        print(f"[ERRO] Registry não encontrado em {REGISTRY_PATH}")
        sys.exit(1)
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def load_thresholds():
    return yaml.safe_load(THRESHOLDS_PATH.read_text(encoding="utf-8"))

def calculate_overlap(proposed_role, proposed_triggers, registry_skills, config):
    scores = {}
    proposed_role_lower = proposed_role.lower().strip()
    proposed_triggers_set = set([t.lower().strip() for t in proposed_triggers.split(",")])

    for skill in registry_skills:
        if skill.get("status") != "active":
            continue
            
        score = 0
        existing_role_lower = skill.get("role", "").lower().strip()
        existing_triggers_set = set([t.lower().strip() for t in skill.get("triggers", [])])

        # Heurística 1: Match exato de Role
        if proposed_role_lower == existing_role_lower:
            score += config['heuristics']['identical_role']
        else:
            # Match parcial (palavras em comum, desconsiderando stopwords simples)
            prop_words = set(proposed_role_lower.split())
            exist_words = set(existing_role_lower.split())
            intersection = prop_words.intersection(exist_words)
            # Se mais de 50% das palavras do role proposto existem na skill atual (heuristic)
            if len(prop_words) > 0 and (len(intersection) / len(prop_words)) > 0.5:
                score += config['heuristics']['partial_role_overlap']

        # Heurística 2: Triggers
        if proposed_triggers_set and existing_triggers_set:
            trigger_intersection = proposed_triggers_set.intersection(existing_triggers_set)
            overlap_ratio = len(trigger_intersection) / len(proposed_triggers_set)
            
            if overlap_ratio >= 0.5: # Mais da metade dos triggers batem
                score += config['heuristics']['identical_triggers'] * overlap_ratio

        scores[skill["name"]] = min(int(score), 100) # Cap em 100%

    return scores

def determine_verdict(scores, config):
    if not scores:
        return "APPROVED", "Nenhuma skill ativa no registry."
        
    highest_score = max(scores.values())
    highest_skill = max(scores, key=scores.get)

    if highest_score >= config['thresholds']['rejection']:
        return "REJECTED", f"Sobreposição crítica ({highest_score}%) com '{highest_skill}'. Use stout-improve-skill."
    elif highest_score >= config['thresholds']['question']:
        return "QUESTIONED", f"Sobreposição moderada ({highest_score}%) com '{highest_skill}'. Avalie fronteiras."
    else:
        return "APPROVED", "Papel único confirmado. Pode prosseguir com stout-create-skill."

def main():
    parser = argparse.ArgumentParser(description="Audita a sobreposição semântica de skills")
    parser.add_argument("--proposed-name", required=True)
    parser.add_argument("--proposed-role", required=True)
    parser.add_argument("--proposed-triggers", required=True, help="Separados por vírgula")
    parser.add_argument("--proposed-tier", type=int, default=1)
    args = parser.parse_args()

    registry = load_registry()
    config = load_thresholds()

    scores = calculate_overlap(args.proposed_role, args.proposed_triggers, registry.get("skills", []), config)
    verdict, notes = determine_verdict(scores, config)

    result = {
        "verdict": verdict,
        "proposed_name": args.proposed_name,
        "proposed_role": args.proposed_role,
        "proposed_tier": args.proposed_tier,
        "audited_at": datetime.now().isoformat(),
        "audited_by": "stout-skill-auditor",
        "overlap_scores": scores,
        "notes": notes
    }

    # Salva o artefato na raiz do auditor (ou onde foi chamado)
    Path("audit_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n[{verdict}] {notes}")
    if verdict != "APPROVED":
        print(f"Scores detalhados: {json.dumps(scores, indent=2)}")
    print("Artefato gerado: audit_result.json")

if __name__ == "__main__":
    main()