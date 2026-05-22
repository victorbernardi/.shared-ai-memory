"""Runner interativo para promoção de skills CDD ao golden copy."""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PROJECT_ROOT / "skills" / "stout-skill-registry" / "registry.json"
AUDIT_SCRIPT = Path(__file__).resolve().parent / "audit_skills.py"
PROMOTE_SCRIPT = Path(__file__).resolve().parent / "promote_skills.py"


def get_pending_promotions(registry_path: Path) -> list[str]:
    """Return names of active skills with promoted_at == null."""
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    return [
        s["name"]
        for s in data["skills"]
        if s.get("status") == "active" and s.get("promoted_at") is None
    ]


def run_audit() -> dict[str, str]:
    """Run audit_skills.py and return {skill_name: status} from latest report."""
    result = subprocess.run(
        [sys.executable, str(AUDIT_SCRIPT)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[ERRO] Falha ao rodar audit_skills.py:")
        print(result.stderr)
        sys.exit(1)

    audit_dir = PROJECT_ROOT / "docs" / "audits"
    reports = sorted(audit_dir.glob("skill-audit-*.json"))
    if not reports:
        print("[ERRO] Nenhum relatório de auditoria encontrado.")
        sys.exit(1)
    data = json.loads(reports[-1].read_text(encoding="utf-8"))
    return {r["skill"]: r["status"] for r in data["results"]}


def main() -> None:
    print("\n=== STOUT PROMOTE SKILL ===\n")

    if not AUDIT_SCRIPT.exists():
        print(f"[ERRO] audit_skills.py não encontrado em: {AUDIT_SCRIPT}")
        sys.exit(1)
    if not PROMOTE_SCRIPT.exists():
        print(f"[ERRO] promote_skills.py não encontrado em: {PROMOTE_SCRIPT}")
        sys.exit(1)

    print("[1/4] Rodando auditoria de skills...")
    audit = run_audit()

    pending = get_pending_promotions(REGISTRY_PATH)
    ready = [s for s in pending if audit.get(s) == "PASS"]
    not_ready = [s for s in pending if audit.get(s) != "PASS"]

    print(f"\nSkills pendentes de promoção: {len(pending)}")
    if ready:
        print(f"\n  PRONTAS (audit PASS):")
        for s in ready:
            print(f"    [OK] {s}")
    if not_ready:
        print(f"\n  NÃO PRONTAS (audit FAIL/ausente):")
        for s in not_ready:
            print(f"    [--] {s}  (status: {audit.get(s, 'não auditada')})")

    if not ready:
        print("\nNenhuma skill pronta para promoção.")
        sys.exit(0)

    print("\nDigite o nome da skill a promover (ou 'todas' para promover todas prontas):")
    choice = input("> ").strip()

    if choice == "todas":
        to_promote = ready
    elif choice in ready:
        to_promote = [choice]
    else:
        print(f"[ERRO] '{choice}' não está na lista de skills prontas.")
        sys.exit(1)

    print(f"\n[2/4] Dry-run para: {', '.join(to_promote)}")
    result = subprocess.run(
        [sys.executable, str(PROMOTE_SCRIPT), "--dry-run"],
        capture_output=True, text=True
    )
    print(result.stdout)

    print("\n[3/4] Confirmar promoção? (s/N)")
    confirm = input("> ").strip().lower()
    if confirm != "s":
        print("Promoção cancelada.")
        sys.exit(0)

    print("\n[4/4] Promovendo skills...")
    result = subprocess.run(
        [sys.executable, str(PROMOTE_SCRIPT)],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("[ERRO]", result.stderr)
        sys.exit(1)

    print("\n[OK] Promoção concluída. Campo promoted_at atualizado no registry.")

    # Verificar se ainda há outras skills pendentes
    remaining = [s for s in get_pending_promotions(REGISTRY_PATH) if s not in to_promote]
    if remaining:
        print(f"\nAinda há {len(remaining)} skill(s) pendente(s) de promoção:")
        for s in remaining:
            status = audit.get(s, "não auditada")
            marker = "[OK]" if status == "PASS" else "[--]"
            print(f"  {marker} {s}  (audit: {status})")
        print("\nDeseja promover alguma delas agora? (s/N)")
        again = input("> ").strip().lower()
        if again == "s":
            main()


if __name__ == "__main__":
    main()
