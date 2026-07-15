"""Promote CDD skills to global platform targets.

Usage:
    python scripts/promote_skills.py --dry-run   # preview only
    python scripts/promote_skills.py             # execute
"""
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import date

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"
STOUT_CREATE = SKILLS_ROOT / "stout-create-skill"
STOUT_MANAGER = SKILLS_ROOT / "stout-skill-manager"
RENDERER_SCRIPT = STOUT_CREATE / "scripts" / "platform_renderer.py"
INSTALLER_SCRIPT = STOUT_MANAGER / "scripts" / "global_installer.py"
VALIDATOR_SCRIPT = STOUT_CREATE / "scripts" / "hybrid_validator.py"
CATALOG_PATH = STOUT_CREATE / "config" / "platform_capabilities.yaml"

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
    "inova-pipeline-01":          [],
    "inova-motor-faturamento":    [],
}


def resolve_source(skill_name: str) -> Path | None:
    candidate = SKILLS_ROOT / skill_name
    return candidate if candidate.exists() else None


def validate_source(skill_name: str) -> bool:
    source_dir = SKILLS_ROOT / skill_name
    if not source_dir.exists():
        return False
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--source-path", str(source_dir)],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def render_skill(skill_name: str, output_dir: Path) -> bool:
    source_dir = SKILLS_ROOT / skill_name
    if not source_dir.exists():
        return False
    result = subprocess.run(
        [sys.executable, str(RENDERER_SCRIPT),
         "--source-path", str(source_dir),
         "--output-dir", str(output_dir),
         "--catalog", str(CATALOG_PATH)],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def install_skill(skill_name: str, artifacts_dir: Path, replace: bool) -> bool:
    source_dir = SKILLS_ROOT / skill_name
    if not source_dir.exists():
        return False
    cmd = [
        sys.executable, str(INSTALLER_SCRIPT),
        "--source-path", str(source_dir),
        "--artifacts-dir", str(artifacts_dir),
        "--replace" if replace else "",
    ]
    cmd = [c for c in cmd if c]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def promote_skill(skill_name: str, replaced: list, dry_run: bool) -> dict:
    source = resolve_source(skill_name)
    actions = []

    if source is None:
        return {"skill": skill_name, "status": "SOURCE_MISSING", "actions": []}

    if not validate_source(skill_name):
        actions.append(f"VALIDATION FAILED {skill_name}")
        return {"skill": skill_name, "status": "VALIDATION_FAILED", "actions": actions}

    if dry_run:
        actions.append(f"WOULD RENDER {skill_name}")
        actions.append(f"WOULD INSTALL {skill_name} to all targets")
        return {"skill": skill_name, "status": "DRY_RUN", "actions": actions}

    import tempfile
    artifacts_dir = Path(tempfile.mkdtemp(prefix="stout-promote-"))
    if not render_skill(skill_name, artifacts_dir):
        actions.append(f"RENDER FAILED {skill_name}")
        return {"skill": skill_name, "status": "RENDER_FAILED", "actions": actions}

    if not install_skill(skill_name, artifacts_dir, replace=False):
        actions.append(f"INSTALL FAILED {skill_name}")
        return {"skill": skill_name, "status": "INSTALL_FAILED", "actions": actions}

    actions.append(f"PROMOTED {skill_name} to all targets")
    return {"skill": skill_name, "status": "PROMOTED", "actions": actions}


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote CDD skills to global targets")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--skill", metavar="NAME", help="Promote only this skill")
    args = parser.parse_args()

    if args.skill and args.skill not in PROMOTION_MAP:
        print(f"ERROR: '{args.skill}' not found in PROMOTION_MAP.")
        return 1

    print(f"\n{'='*60}")
    mode = "DRY RUN" if args.dry_run else "EXECUTING"
    skill_filter = f" [skill: {args.skill}]" if args.skill else ""
    print(f"Skill Promotion -- {date.today()} [{mode}]{skill_filter}")
    print(f"{'='*60}\n")

    promotion_items = (
        [(args.skill, PROMOTION_MAP[args.skill])] if args.skill
        else PROMOTION_MAP.items()
    )

    results = []
    for skill_name, replaced in promotion_items:
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
