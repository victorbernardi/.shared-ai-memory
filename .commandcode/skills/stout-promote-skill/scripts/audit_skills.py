"""Audit CDD skills against Stout governance checklist.

Usage:
    python scripts/audit_skills.py

Output:
    docs/audits/skill-audit-YYYY-MM-DD.json
    Console summary table
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "docs" / "audits"

MAIN_FILENAMES = ["SKILL.md", "main.md", "README.md", "skill.md"]

CHECKLIST = {
    "has_trigger": ["trigger", "quando usar", "when to use", "use when"],
    "has_scope": ["scope", "escopo", "objetivo", "goal"],
    "has_exit_criteria": ["done", "concluído", "exit", "saída", "criteria", "critério"],
}
MIN_LENGTH = 200
# Match placeholder markers in uppercase only; avoids Portuguese "todo/todos"
_BANNED_RE = re.compile(r"\bTODO\b|\bTBD\b")


def find_main_file(skill_dir: Path) -> Path | None:
    """Find the primary Markdown file for a skill."""
    for name in MAIN_FILENAMES:
        candidate = skill_dir / name
        if candidate.exists():
            return candidate
    md_files = list(skill_dir.glob("*.md"))
    return md_files[0] if md_files else None


def audit_skill(skill_dir: Path) -> dict:
    """Evaluate one skill directory against the governance checklist."""
    main_file = find_main_file(skill_dir)
    if main_file is None:
        return {
            "skill": skill_dir.name,
            "file": None,
            "status": "NO_FILE",
            "checks": {},
            "fail_reasons": ["No Markdown file found"],
        }

    content = main_file.read_text(encoding="utf-8", errors="ignore")
    content_lower = content.lower()

    checks = {}
    fail_reasons = []

    checks["has_trigger"] = any(kw in content_lower for kw in CHECKLIST["has_trigger"])
    if not checks["has_trigger"]:
        fail_reasons.append("Missing trigger definition")

    checks["has_description"] = len(content) >= MIN_LENGTH
    if not checks["has_description"]:
        fail_reasons.append(f"File too short ({len(content)} chars, min {MIN_LENGTH})")

    checks["has_scope"] = any(kw in content_lower for kw in CHECKLIST["has_scope"])
    if not checks["has_scope"]:
        fail_reasons.append("Missing scope/objective section")

    checks["has_exit_criteria"] = any(
        kw in content_lower for kw in CHECKLIST["has_exit_criteria"]
    )
    if not checks["has_exit_criteria"]:
        fail_reasons.append("Missing exit criteria / done definition")

    checks["no_todos"] = _BANNED_RE.search(content) is None
    if not checks["no_todos"]:
        fail_reasons.append("Contains TODO/TBD placeholders")

    passed = all(checks.values())
    try:
        rel_file = str(main_file.relative_to(SKILLS_ROOT.parent))
    except ValueError:
        rel_file = str(main_file)
    return {
        "skill": skill_dir.name,
        "file": rel_file,
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "fail_reasons": fail_reasons,
    }


def main() -> int:
    if not SKILLS_ROOT.exists():
        print(f"ERROR: Skills root not found: {SKILLS_ROOT}")
        return 1

    skill_dirs = sorted(
        [d for d in SKILLS_ROOT.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    results = [audit_skill(d) for d in skill_dirs]
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] != "PASS"]

    print(f"\n{'='*60}")
    print(f"Stout Skill Audit — {date.today()}")
    print(f"{'='*60}")
    print(f"Total: {len(results)}  |  PASS: {len(passed)}  |  FAIL: {len(failed)}\n")

    print("PASS:")
    for r in passed:
        print(f"  [OK] {r['skill']}")

    print("\nFAIL:")
    for r in failed:
        reasons = ", ".join(r["fail_reasons"]) if r["fail_reasons"] else r["status"]
        print(f"  [FAIL] {r['skill']} — {reasons}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"skill-audit-{date.today()}.json"
    report = {
        "date": str(date.today()),
        "summary": {
            "total": len(results),
            "passed": len(passed),
            "failed": len(failed),
        },
        "results": results,
    }
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nReport saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
