import sys
import json
import argparse
import io
from pathlib import Path

# Fix Windows encoding issues for printing emojis/utf-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup paths - Relativo ao arquivo launcher.py
SCRIPTS_DIR = Path(__file__).parent
STOUT_ORCHESTRATOR_DIR = SCRIPTS_DIR.parent
CDD_PROJECT_SKILLS_DIR = STOUT_ORCHESTRATOR_DIR.parent
REGISTRY_PATH = CDD_PROJECT_SKILLS_DIR / "stout-skill-registry" / "registry.json"

KARPATHY_LAWS = """
[LEI GLOBAL - KARPATHY LAWS]
1. Pense Antes de Codificar: Não assuma interpretações. Explicite trade-offs.
2. Simplicidade Primeiro: Código mínimo necessário. Sem overengineering.
3. Mudanças Cirúrgicas: Toque apenas no necessário. Match existing style.
4. Execução Orientada a Metas: Defina critérios de sucesso e loops (TDD).
"""

def load_registry():
    if not REGISTRY_PATH.exists():
        print(f"[ERRO] Registro CDD não encontrado em: {REGISTRY_PATH}")
        sys.exit(1)
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def launch_skill(skill_name):
    data = load_registry()
    skill = next((s for s in data["skills"] if s["name"] == skill_name), None)
    
    if not skill:
        print(f"[ERRO] Skill '{skill_name}' não registrada no registry.json.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  STOUT CDD ORCHESTRATOR V1.1.0 - Ativando: {skill['name']} (Tier {skill['tier']})")
    print(f"{'='*60}\n")
    
    print(f"[PAPEL] {skill['role']}")
    
    # Injeção Global de Karpathy Laws
    print(f"\n[GLOBAL_GUARDRAILS]")
    print(KARPATHY_LAWS)
    
    # Carregar instruções do SKILL.md da skill alvo
    skill_base_path = CDD_PROJECT_SKILLS_DIR.parent.parent # .gemini/skills
    skill_path = skill_base_path / skill['path'] / "SKILL.md"
    
    if skill_path.exists():
        print(f"\n[SKILL_INSTRUCTIONS] (from {skill['path']}/SKILL.md)")
        with open(skill_path, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print(f"\n[AVISO] SKILL.md não encontrado em: {skill_path}")
    
    if skill.get("triggers"):
        print(f"\n[TRIGGERS]")
        for trigger in skill["triggers"]:
            print(f"  - {trigger}")
    
    print(f"\n[OK] Skill '{skill_name}' orquestrada com sucesso.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Nome da skill a ser ativada")
    args = parser.parse_args()
    
    launch_skill(args.skill)
