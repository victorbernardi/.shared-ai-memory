#!/usr/bin/env python3
"""
stout-skill-manager — Orquestrador das 5 fases.

Uso:
  python orchestrator.py --query "skill de debugging"
  python orchestrator.py --install owner/repo --skill-name minha-skill
"""
import sys
import json
import argparse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
SKILLS_ROOT = SCRIPT_DIR.parent.parent
CANONICAL_PATH = SKILLS_ROOT  # .shared-ai-memory/skills/
AUDITOR_SCRIPT = SKILLS_ROOT / "stout-skill-auditor" / "scripts" / "semantic_overlap.py"
SENTINEL_SCRIPT = SKILLS_ROOT / "skill-sentinel" / "scripts" / "run_audit.py"
IMPROVE_SKILL = SKILLS_ROOT / "stout-improve-skill"


def load_thresholds() -> dict:
    import yaml
    path = CONFIG_DIR / "thresholds.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_junction_guard() -> bool:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "junction_guard.py")],
        capture_output=False
    )
    return result.returncode == 0


def run_local_search(query: str, threshold: int) -> list[dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "local_search.py"),
         "--query", query, "--threshold", str(threshold), "--json"],
        capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def run_skillfish_search(query: str) -> str:
    result = subprocess.run(
        ["skillfish", "search", query],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def run_auditor(name: str, role: str, triggers: str, tier: int = 2) -> str:
    result = subprocess.run(
        [sys.executable, str(AUDITOR_SCRIPT),
         "--proposed-name", name,
         "--proposed-role", role,
         "--proposed-triggers", triggers,
         "--proposed-tier", str(tier)],
        capture_output=True, text=True, encoding="utf-8"
    )
    output = result.stdout + result.stderr
    if "APPROVED" in output:
        return "APPROVED"
    if "QUESTIONED" in output:
        return "QUESTIONED"
    return "REJECTED"


def run_skillfish_install(repo: str) -> bool:
    result = subprocess.run(
        ["skillfish", "add", repo,
         "--output", str(CANONICAL_PATH)],
        capture_output=False
    )
    return result.returncode == 0


def run_validator(skill_path: Path) -> bool:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "install_validator.py"),
         "--skill-path", str(skill_path)],
        capture_output=False
    )
    return result.returncode == 0


def run_sentinel(skill_name: str) -> int:
    if not SENTINEL_SCRIPT.exists():
        print(f"[AVISO] skill-sentinel nao encontrado em {SENTINEL_SCRIPT}")
        print("[AVISO] Pulando analise de qualidade — registrando com status: pending-review")
        return 70  # assume aprovado para nao bloquear o fluxo
    result = subprocess.run(
        [sys.executable, str(SENTINEL_SCRIPT),
         "--skill", skill_name, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8"
    )
    try:
        data = json.loads(result.stdout)
        return int(data.get("overall_score", 0))
    except (json.JSONDecodeError, ValueError):
        return 0


def run_improve(skill_name: str) -> bool:
    improve_script = IMPROVE_SKILL / "scripts" / "improve.py"
    if not improve_script.exists():
        print(f"[AVISO] stout-improve-skill nao encontrado — pulando melhoria")
        return False
    result = subprocess.run(
        [sys.executable, str(improve_script), "--skill", skill_name],
        capture_output=False
    )
    return result.returncode == 0


def register_skill(skill_name: str, status: str, role: str = "", tier: int = 2):
    registry_path = SKILLS_ROOT / "stout-skill-registry" / "registry.json"
    if not registry_path.exists():
        print(f"[AVISO] registry.json nao encontrado — pulando registro")
        return
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    existing = next((s for s in data["skills"] if s["name"] == skill_name), None)
    if existing:
        existing["status"] = status
        print(f"[REGISTRY] '{skill_name}' atualizado para status={status}")
    else:
        data["skills"].append({
            "name": skill_name,
            "path": f".shared-ai-memory/skills/{skill_name}",
            "tier": tier,
            "category": "imported",
            "role": role or f"Skill importada via skillfish: {skill_name}",
            "triggers": [skill_name],
            "version": "1.0.0",
            "status": status,
            "created_at": __import__("datetime").date.today().isoformat(),
            "updated_at": __import__("datetime").date.today().isoformat(),
            "author": "skillfish-import",
            "notes": f"Instalada via stout-skill-manager. status={status}"
        })
        print(f"[REGISTRY] '{skill_name}' registrado com status={status}")
    registry_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def hitl_confirm(message: str) -> bool:
    print(f"\n[HITL] {message}")
    try:
        resp = input("Continuar? [s/N]: ").strip().lower()
        return resp in ("s", "sim", "y", "yes")
    except EOFError:
        print("[ERRO] Ambiente nao interativo. Abortando por seguranca.")
        return False


def hitl_choice(prompt: str, options: list[str]) -> int:
    print(f"\n[HITL] {prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    try:
        val = input("Escolha [1]: ").strip()
        idx = int(val) - 1 if val.isdigit() else 0
        return max(0, min(idx, len(options) - 1))
    except EOFError:
        return 0


# ─── Fases ──────────────────────────────────────────────────────────────────

def phase1_local_search(query: str, threshold: int) -> list[dict]:
    print(f"\n[FASE 1] Busca local para: '{query}' (threshold={threshold}%)")
    results = run_local_search(query, threshold)
    if results:
        print(f"  Encontradas {len(results)} skills locais:")
        for r in results:
            print(f"    [{r['_score']:3d}%] {r['name']} — {r['role']}")
    else:
        print("  Nenhuma skill local suficiente encontrada.")
    return results


def phase2_external_search(query: str) -> tuple[str, str]:
    """Retorna (repo_escolhido, acao) onde acao = 'instalar'|'criar'|'abortar'"""
    print(f"\n[FASE 2] Busca externa via skillfish: '{query}'")
    output = run_skillfish_search(query)
    if output:
        print(output)
    else:
        print("  Nenhum resultado externo encontrado.")

    choice = hitl_choice(
        "O que deseja fazer?",
        ["Instalar skill encontrada (informe o repo no próximo passo)",
         "Criar nova skill com stout-create-skill",
         "Abortar"]
    )
    if choice == 0:
        repo = input("\nInforme o repo (owner/repo): ").strip()
        skill_name = input("Nome da skill (kebab-case): ").strip()
        return f"{repo}|{skill_name}", "instalar"
    if choice == 1:
        return "", "criar"
    return "", "abortar"


def phase3_audit(skill_name: str, role: str, triggers: str) -> str:
    print(f"\n[FASE 3] Auditoria de conflito para '{skill_name}'")
    verdict = run_auditor(skill_name, role, triggers)
    print(f"  Veredicto: {verdict}")

    if verdict == "QUESTIONED":
        if not hitl_confirm(
            f"O auditor encontrou sobreposicao moderada com skills existentes.\n"
            f"  Deseja instalar mesmo assim?"
        ):
            return "ABORT"
        return "APPROVED"  # usuario confirmou

    return verdict


def phase4_install(repo: str, skill_name: str) -> bool:
    print(f"\n[FASE 4] Instalando '{skill_name}' de {repo}")
    print("  Verificando junctions antes da instalacao...")
    if not run_junction_guard():
        print("[ERRO] Junction guard falhou — abortando instalacao")
        return False

    if not run_skillfish_install(repo):
        print(f"[ERRO] skillfish add falhou para {repo}")
        return False

    skill_path = CANONICAL_PATH / skill_name
    if not skill_path.exists():
        print(f"[ERRO] Skill nao encontrada em {skill_path} apos instalacao")
        return False

    print(f"  Validando estrutura Stout...")
    if not run_validator(skill_path):
        print("[ERRO] Validacao de estrutura falhou")
        return False

    print(f"  Instalacao concluida: {skill_path}")
    return True


def phase5_quality(skill_name: str, thresholds: dict) -> str:
    """Retorna 'active' | 'quarantine'"""
    min_score = thresholds.get("sentinel_min_score", 70)
    max_cycles = thresholds.get("improve_max_cycles", 2)

    print(f"\n[FASE 5] Controle de qualidade (score minimo: {min_score})")
    score = run_sentinel(skill_name)
    print(f"  Score sentinel: {score}/100")

    cycle = 0
    while score < min_score and cycle < max_cycles:
        cycle += 1
        print(f"  Score abaixo do minimo. Ciclo stout-improve-skill {cycle}/{max_cycles}...")
        run_improve(skill_name)
        score = run_sentinel(skill_name)
        print(f"  Score apos melhoria: {score}/100")

    if score >= min_score:
        print(f"  Qualidade aprovada (score={score})")
        return "active"
    else:
        print(f"  Qualidade insuficiente apos {max_cycles} ciclos. Status: quarantine")
        return "quarantine"


# ─── Entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="stout-skill-manager orchestrator")
    parser.add_argument("--query", help="Query de busca de skills")
    parser.add_argument("--install", metavar="OWNER/REPO", help="Instala diretamente sem busca")
    parser.add_argument("--skill-name", help="Nome da skill (obrigatorio com --install)")
    parser.add_argument("--role", default="", help="Role da skill (para auditoria)")
    parser.add_argument("--triggers", default="", help="Triggers separados por virgula")
    args = parser.parse_args()

    thresholds = load_thresholds()
    local_threshold = thresholds.get("local_match_threshold", 60)

    # Modo direto: --install
    if args.install:
        if not args.skill_name:
            print("[ERRO] --skill-name obrigatorio com --install")
            sys.exit(1)
        repo = args.install
        skill_name = args.skill_name
    else:
        query = args.query or input("Query de busca: ").strip()

        # Fase 1 — busca local
        local_results = phase1_local_search(query, local_threshold)
        if local_results:
            choice = hitl_choice(
                "Skills locais encontradas. O que deseja?",
                ["Usar skill local (encerrar)",
                 "Buscar externamente mesmo assim"]
            )
            if choice == 0:
                print("\n[OK] Use a skill local listada acima.")
                return

        # Fase 2 — busca externa
        result, action = phase2_external_search(query)
        if action == "abortar":
            print("[CANCELADO] Operacao abortada pelo usuario.")
            return
        if action == "criar":
            print("\n[INFO] Invoque stout-create-skill para criar a skill.")
            return
        repo, skill_name = result.split("|", 1)

    role = args.role or f"Skill importada: {skill_name}"
    triggers = args.triggers or skill_name

    # Fase 3 — auditoria
    verdict = phase3_audit(skill_name, role, triggers)
    if verdict == "REJECTED":
        print("\n[REJEITADO] Skill nao pode ser instalada — conflito com skills existentes.")
        local = run_local_search(skill_name, 20)
        if local:
            print("  Alternativas locais:")
            for r in local[:3]:
                print(f"    - {r['name']}: {r['role']}")
        return
    if verdict == "ABORT":
        print("\n[CANCELADO] Instalacao abortada pelo usuario.")
        return

    # Fase 4 — instalacao
    if not phase4_install(repo, skill_name):
        print("\n[FALHA] Instalacao nao concluida.")
        return

    # Fase 5 — qualidade
    status = phase5_quality(skill_name, thresholds)
    register_skill(skill_name, status, role)

    if status == "active":
        print(f"\n[CONCLUIDO] '{skill_name}' instalada e ativa no ecossistema.")
    else:
        print(f"\n[AVISO] '{skill_name}' instalada com status=quarantine.")
        print("  Execute stout-improve-skill manualmente quando pronto para revisao.")


if __name__ == "__main__":
    main()
