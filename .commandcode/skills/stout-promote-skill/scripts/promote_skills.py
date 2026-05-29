"""Promote CDD skills to Golden Copy and archive replaced generics.

Usage:
    python scripts/promote_skills.py --dry-run   # preview only
    python scripts/promote_skills.py             # execute
"""
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import date

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"
GOLDEN_COPY = Path.home() / ".shared-ai-memory" / "skills"
ARCHIVE_DIR = Path.home() / ".shared-ai-memory" / "skills" / "_archived"
AUDIT_DIR = Path(__file__).resolve().parents[3] / "docs" / "audits"

# Fallback: skills que ainda vivem no projeto CDD (não foram migradas para SKILLS_ROOT)
CDD_SKILLS_ROOT = Path(r"C:\Projetos\Stout\Projetos\Configuration-Driven Development\skills")

PROMOTION_MAP = {
    "stout-brainstorming":        ["process-brainstorming"],
    "stout-dev-tdd":              ["dev-tdd"],
    "stout-writing-plans":        ["process-writing-plans"],
    "stout-systematic-debugging": ["dev-systematic-debugging"],
    "stout-executing-plans":      ["process-gcc"],
    "stout-adr":                  ["process-adr"],
    "stout-spec-validation":      ["audit-spec-validation"],
    "stout-commit":               ["commit"],
    "stout-init":                 ["process-stout-init", "stout-init-v2"],
    "stout-create-skill":         ["skill-creator", "workflow_skill_creator"],
    "stout-improve-skill":        [],
    "stout-skill-registry":       [],
    "stout-skill-auditor":        [],
    "stout-subagent-driven-development": [],
    "stout-finishing-a-development-branch": [],
    "stout-immunity-gate":        [],
    "stout-cdd-orchestrator":     ["stout-cdd-orchestrator"],
    "stout-data-analyze":         ["data-analyze"],
    "stout-data-sql-queries":     ["data-sql-queries"],
    "stout-data-write-query":     ["data-write-query"],
    "stout-promote-skill":        [],
    "stout-session-learning":     [],
    "stout-retrofit":             [],
    "stout-skill-manager":        [],
    "skillfish":                  [],
}


def load_latest_audit() -> dict:
    reports = sorted(AUDIT_DIR.glob("skill-audit-*.json"))
    if not reports:
        return {}
    data = json.loads(reports[-1].read_text(encoding="utf-8"))
    return {r["skill"]: r["status"] for r in data["results"]}


def resolve_source(skill_name: str) -> Path | None:
    """Retorna o path fonte da skill: SKILLS_ROOT primeiro, depois CDD_SKILLS_ROOT."""
    candidate = SKILLS_ROOT / skill_name
    if candidate.exists():
        return candidate
    fallback = CDD_SKILLS_ROOT / skill_name
    if fallback.exists():
        return fallback
    return None


def promote_skill(skill_name: str, replaced: list, dry_run: bool) -> dict:
    src = resolve_source(skill_name)
    dst = GOLDEN_COPY / skill_name
    actions = []

    if src is None:
        return {"skill": skill_name, "status": "SOURCE_MISSING", "actions": []}

    for old_name in replaced:
        old_path = GOLDEN_COPY / old_name
        if old_path.exists():
            archive_path = ARCHIVE_DIR / f"{old_name}_{date.today()}"
            actions.append(f"ARCHIVE {old_name} -> _archived/{old_name}_{date.today()}")
            if not dry_run:
                ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
                if archive_path.exists():
                    shutil.rmtree(archive_path)
                shutil.move(str(old_path), str(archive_path))

    if src.resolve() == dst.resolve():
        # Skill já está no golden copy (source of truth unificada)
        actions.append(f"ALREADY IN PLACE {skill_name} (source == golden copy)")
    else:
        actions.append(f"COPY {skill_name} -> Golden Copy")
        if not dry_run:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    if not dry_run:
        registry_path = SKILLS_ROOT / "stout-skill-registry" / "registry.json"
        update_promoted_at(skill_name, registry_path)

    return {"skill": skill_name, "status": "PROMOTED", "actions": actions}


def update_promoted_at(skill_name: str, registry_path: Path) -> None:
    """Set promoted_at to today in the project registry after a successful promotion."""
    if not registry_path.exists():
        return
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    for skill in data["skills"]:
        if skill["name"] == skill_name:
            skill["promoted_at"] = str(date.today())
            break
    registry_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote CDD skills to Golden Copy")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    args = parser.parse_args()

    audit = load_latest_audit()
    if not audit:
        print("ERROR: No audit report found. Run audit_skills.py first.")
        return 1

    print(f"\n{'='*60}")
    mode = "DRY RUN" if args.dry_run else "EXECUTING"
    print(f"Skill Promotion -- {date.today()} [{mode}]")
    print(f"{'='*60}\n")

    results = []
    for skill_name, replaced in PROMOTION_MAP.items():
        status = audit.get(skill_name)
        if status != "PASS":
            print(f"  SKIP {skill_name} (audit status: {status or 'not audited'})")
            continue
        result = promote_skill(skill_name, replaced, args.dry_run)
        results.append(result)
        print(f"  {result['status']} {skill_name}")
        for action in result["actions"]:
            print(f"    -> {action}")

    promoted = len([r for r in results if r["status"] == "PROMOTED"])
    print(f"\nTotal promoted: {promoted}")
    if args.dry_run:
        print("(dry-run: no files changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
