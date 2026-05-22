#!/usr/bin/env python3
"""
Diagnóstico de Elite: Integrando Sentinel Core e Heurísticas de IA-Review.
Versão: 1.2.0 (Elite Upgrade)
"""
import argparse
import sys
import json
import yaml
import importlib.util
from pathlib import Path
from datetime import datetime

# Configuração de caminhos
SKILL_ROOT = Path(__file__).parent.parent
SENTINEL_CORE = SKILL_ROOT / "scripts" / "sentinel_core"
PROJECT_ROOT = SKILL_ROOT.parent.parent

# Importa o scanner da skill de sentinel (se disponível) ou local
GLOBAL_SENTINEL_SCRIPTS = Path.home() / ".shared-ai-memory" / "skills" / "skill-sentinel" / "scripts"
sys.path.append(str(GLOBAL_SENTINEL_SCRIPTS))
sys.path.append(str(SKILL_ROOT.parent / "skill-sentinel" / "scripts"))
try:
    from scanner import SkillScanner
except ImportError:
    # Fallback se não encontrar o scanner do sentinel
    class SkillScanner:
        def _analyze_skill(self, p): return {"name": p.name, "path": str(p), "description": "missing"}
    print("[AVISO] SkillScanner não encontrado. Usando mock.")

def load_analyzer(name: str):
    """Carrega dinamicamente um analyzer do Sentinel Core."""
    module_path = SENTINEL_CORE / f"{name}.py"
    if not module_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location(f"sentinel_{name}", str(module_path))
    module = importlib.util.module_from_spec(spec)
    # Mock do sys.modules para permitir imports relativos internos se necessário
    sys.path.append(str(SENTINEL_CORE))
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"[AVISO] Falha ao carregar analyzer '{name}': {e}")
        return None
    return module

def run_elite_diagnosis(target_name: str):
    skills_dir = SKILL_ROOT.parent
    target_path = skills_dir / target_name
    
    if not target_path.exists():
        print(f"[ERRO] A skill alvo '{target_name}' não foi encontrada.")
        sys.exit(1)
        
    print(f"\n{'='*60}")
    print(f"  STOUT ELITE DIAGNOSIS - {target_name} v1.2.0")
    print(f"{'='*60}\n")
    
    # Usa o scanner real para coletar dados (description, triggers, etc.)
    scanner = SkillScanner()
    skill_data = scanner._analyze_skill(target_path)
    
    if not skill_data:
        print(f"[ERRO] Falha ao analisar skill em {target_path}")
        sys.exit(1)

    results = {
        "target": target_name,
        "timestamp": datetime.now().isoformat(),
        "dimensions": {}
    }

    # Executar Analisadores do Sentinel
    analyzers = ["code_quality", "security", "performance", "documentation"]
    total_score = 0
    loaded_count = 0

    for a_name in analyzers:
        module = load_analyzer(a_name)
        if module and hasattr(module, "analyze"):
            score, findings = module.analyze(skill_data)
            results["dimensions"][a_name] = {"score": score, "findings": findings}
            total_score += score
            loaded_count += 1
            status = "[OK]" if score > 70 else "[ATENCAO]"
            print(f"{status} {a_name.replace('_', ' ').title()}: {score}/100")
        else:
            print(f"[?] {a_name.title()}: Não carregado.")

    # Alinhamento CDD (Stout Elite Check)
    catalog_path = PROJECT_ROOT / "data" / "config" / "skills_catalog.yaml"
    has_cdd = False
    if catalog_path.exists():
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = yaml.safe_load(f)
            has_cdd = any(s["id"] == target_name for s in catalog.get("skills", []))
    
    status_cdd = "[OK]" if has_cdd else "[ALERTA]"
    print(f"{status_cdd} Alinhamento CDD: {'Sim' if has_cdd else 'Não'}")
    if not has_cdd:
        results["dimensions"].setdefault("governance", {"score": 0, "findings": []})
        results["dimensions"]["governance"]["findings"].append({
            "skill_name": target_name,
            "dimension": "governance",
            "severity": "high",
            "category": "missing_cdd_alignment",
            "title": "Skill não alinhada ao catálogo CDD",
            "recommendation": "Registrar a skill no arquivo data/config/skills_catalog.yaml"
        })

    avg_score = total_score / loaded_count if loaded_count > 0 else 0
    print(f"\nSCORE GERAL: {avg_score:.1f}/100")
    
    # Salvar laudo para o orquestrador
    report_path = Path("elite_audit_report.json")
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[SUCESSO] Laudo de Elite gerado: {report_path}")
    print("Próximo passo: Use `apply_patch.py` para delegar as correções aos subagentes.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    
    run_elite_diagnosis(args.target)
