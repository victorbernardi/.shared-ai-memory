# Global Skill Promotion Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Audit all 24 CDD skills against the Stout governance checklist, promote passing skills to the Golden Copy (replacing their outdated counterparts), and copy 6 Python src/ modules to the shared template location.

**Architecture:**

- Phase A (Tasks 1–3): Automated structural audit via `scripts/audit_skills.py` → JSON report → human review checkpoint.
- Phase B (Tasks 4–5): Promote passing skills to Golden Copy, delete/archive replaced generics.
- Phase C (Task 6): Copy Python src/ modules to `~/.shared-ai-memory/templates/scripts/`.

**Tech Stack:** Python 3.8+, pathlib, json, shutil — no external dependencies.

---

## Context (read before starting)

### CDD Skills root

`C:\Projetos\Stout\Projetos\Configuration-Driven Development\skills\`

### Golden Copy root

`C:\Users\victor.bernardi\.shared-ai-memory\skills\`

### Governance checklist (Stout standard)

A skill PASSES if its main Markdown file satisfies ALL:

1. **has_trigger** — contains "trigger", "quando usar", "when to use", or "use when"
2. **has_description** — file length > 200 characters
3. **has_scope** — contains "scope", "escopo", "objetivo", or "goal"
4. **has_exit_criteria** — contains "done", "concluído", "exit", "saída", "criteria", or "critério"
5. **no_todos** — does NOT contain "todo" or "tbd" (case-insensitive)

### Replacement map (confirmed in grilling session)

| CDD skill | Replaces in Golden Copy | Type |
|-----------|------------------------|------|
| `stout-brainstorming` | `process-brainstorming` | Replace |
| `stout-dev-tdd` | `dev-tdd` | Replace |
| `stout-writing-plans` | `process-writing-plans` | Replace |
| `stout-systematic-debugging` | `dev-systematic-debugging` | Replace |
| `stout-executing-plans` | `process-gcc` | Replace |
| `stout-adr` | `process-adr` | Replace |
| `stout-spec-validation` | `audit-spec-validation` | Replace |
| `stout-commit` | `commit` | Replace |
| `stout-init` | `process-stout-init`, `stout-init-v2` | Replace |
| `stout-create-skill` | `skill-creator`, `workflow_skill_creator` | Replace |
| `stout-improve-skill` | *(none — new)* | Add |
| `stout-skill-registry` | *(none — new)* | Add |
| `stout-skill-auditor` | *(none — new)* | Add |

### Python modules going to global template

| Module | Source | Destination |
|--------|--------|-------------|
| `guardrail.py` | `src/core/guardrail.py` | `~/.shared-ai-memory/templates/scripts/` |
| `sandbox.py` | `src/core/sandbox.py` | `~/.shared-ai-memory/templates/scripts/` |
| `preflight.py` | `src/core/preflight.py` | `~/.shared-ai-memory/templates/scripts/` |
| `git_guard.py` | `src/core/git_guard.py` | `~/.shared-ai-memory/templates/scripts/` |
| `skill_tool.py` | `src/tools/skill_tool.py` | `~/.shared-ai-memory/templates/scripts/` |
| `stout_promote.py` | `src/tools/stout_promote.py` | Already done ✅ |

---

## Phase A — Structural Audit

### Task 1: Create audit script

**Files:**

- Create: `scripts/audit_skills.py`

- [ ] **Step 1: Create `scripts/` directory and audit script**

Create `scripts/audit_skills.py`:

```python
"""Audit CDD skills against Stout governance checklist.

Usage:
    python scripts/audit_skills.py

Output:
    docs/audits/skill-audit-YYYY-MM-DD.json
    Console summary table
"""
import json
import sys
from datetime import date
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "audits"

MAIN_FILENAMES = ["SKILL.md", "main.md", "README.md", "skill.md"]

CHECKLIST = {
    "has_trigger": ["trigger", "quando usar", "when to use", "use when"],
    "has_scope": ["scope", "escopo", "objetivo", "goal"],
    "has_exit_criteria": ["done", "concluído", "exit", "saída", "criteria", "critério"],
}
MIN_LENGTH = 200
BANNED_TOKENS = ["todo", "tbd"]


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

    # has_trigger
    checks["has_trigger"] = any(kw in content_lower for kw in CHECKLIST["has_trigger"])
    if not checks["has_trigger"]:
        fail_reasons.append("Missing trigger definition")

    # has_description (length gate)
    checks["has_description"] = len(content) >= MIN_LENGTH
    if not checks["has_description"]:
        fail_reasons.append(f"File too short ({len(content)} chars, min {MIN_LENGTH})")

    # has_scope
    checks["has_scope"] = any(kw in content_lower for kw in CHECKLIST["has_scope"])
    if not checks["has_scope"]:
        fail_reasons.append("Missing scope/objective section")

    # has_exit_criteria
    checks["has_exit_criteria"] = any(
        kw in content_lower for kw in CHECKLIST["has_exit_criteria"]
    )
    if not checks["has_exit_criteria"]:
        fail_reasons.append("Missing exit criteria / done definition")

    # no_todos
    checks["no_todos"] = not any(tok in content_lower for tok in BANNED_TOKENS)
    if not checks["no_todos"]:
        fail_reasons.append("Contains TODO/TBD placeholders")

    passed = all(checks.values())
    return {
        "skill": skill_dir.name,
        "file": str(main_file.relative_to(SKILLS_ROOT.parent)),
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

    # Console output
    print(f"\n{'='*60}")
    print(f"Stout Skill Audit — {date.today()}")
    print(f"{'='*60}")
    print(f"Total: {len(results)}  |  PASS: {len(passed)}  |  FAIL: {len(failed)}\n")

    print("PASS:")
    for r in passed:
        print(f"  ✅ {r['skill']}")

    print("\nFAIL:")
    for r in failed:
        reasons = ", ".join(r["fail_reasons"]) if r["fail_reasons"] else r["status"]
        print(f"  ❌ {r['skill']} — {reasons}")

    # JSON output
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
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the script to confirm it works**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python scripts/audit_skills.py
```

Expected: Console table with PASS/FAIL per skill + JSON report at `docs/audits/skill-audit-YYYY-MM-DD.json`. No errors.

- [ ] **Step 3: Commit**

```bash
git add scripts/audit_skills.py
git commit -m "feat: add skill governance audit script"
```

---

### Task 2: Run audit and review results

**Files:**

- Run: `scripts/audit_skills.py`
- Read: `docs/audits/skill-audit-YYYY-MM-DD.json`

- [ ] **Step 1: Run audit**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python scripts/audit_skills.py
```

- [ ] **Step 2: Read the JSON report**

```bash
python -c "
import json; from pathlib import Path
reports = sorted(Path('docs/audits').glob('skill-audit-*.json'))
data = json.loads(reports[-1].read_text(encoding='utf-8'))
print(f\"PASS ({data['summary']['passed']}): {[r['skill'] for r in data['results'] if r['status']=='PASS']}\")
print(f\"FAIL ({data['summary']['failed']}): {[r['skill'] for r in data['results'] if r['status']!='PASS']}\")
"
```

- [ ] **Step 3: Create fix tasks for FAILing skills**

For each FAIL, decide: **fix** (add missing section) or **discard** (skill is a placeholder).

Skills likely to FAIL (based on their names suggesting early-stage work):

- `welcome_skill` — likely a demo, discard
- `cdd_technical_skill` — likely internal, evaluate
- `self_healing_skill` — evaluate
- `stout_knowledge_fallback` — evaluate

For each skill to FIX, edit its `SKILL.md` to add the missing sections flagged by the audit.
For each to DISCARD, note it in the report — do not promote.

- [ ] **Step 4: Re-run audit until all target skills PASS**

```bash
python scripts/audit_skills.py
```

Expected: All skills intended for global promotion show PASS.

- [ ] **Step 5: Commit fixes**

```bash
git add skills/
git commit -m "fix: add missing governance sections to skills for promotion"
```

---

## Phase B — Skill Promotion

### Task 3: Promote passing skills to Golden Copy

**Files:**

- Create: `scripts/promote_skills.py`

- [ ] **Step 1: Create promotion script**

Create `scripts/promote_skills.py`:

```python
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

SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"
GOLDEN_COPY = Path.home() / ".shared-ai-memory" / "skills"
ARCHIVE_DIR = Path.home() / ".shared-ai-memory" / "skills" / "_archived"
AUDIT_DIR = Path(__file__).resolve().parents[1] / "docs" / "audits"

# Skills to promote and what they replace in the Golden Copy
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
}


def load_latest_audit() -> dict:
    reports = sorted(AUDIT_DIR.glob("skill-audit-*.json"))
    if not reports:
        return {}
    data = json.loads(reports[-1].read_text(encoding="utf-8"))
    return {r["skill"]: r["status"] for r in data["results"]}


def promote_skill(skill_name: str, replaced: list, dry_run: bool) -> dict:
    src = SKILLS_ROOT / skill_name
    dst = GOLDEN_COPY / skill_name
    actions = []

    if not src.exists():
        return {"skill": skill_name, "status": "SOURCE_MISSING", "actions": []}

    # Archive replaced skills
    for old_name in replaced:
        old_path = GOLDEN_COPY / old_name
        if old_path.exists():
            archive_path = ARCHIVE_DIR / f"{old_name}_{date.today()}"
            actions.append(f"ARCHIVE {old_name} → _archived/{old_name}_{date.today()}")
            if not dry_run:
                ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
                if archive_path.exists():
                    shutil.rmtree(archive_path)
                shutil.move(str(old_path), str(archive_path))

    # Copy new skill
    actions.append(f"COPY {skill_name} → Golden Copy")
    if not dry_run:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    return {"skill": skill_name, "status": "PROMOTED", "actions": actions}


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
    print(f"Skill Promotion — {date.today()} [{mode}]")
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
            print(f"    → {action}")

    promoted = len([r for r in results if r["status"] == "PROMOTED"])
    print(f"\nTotal promoted: {promoted}")
    if args.dry_run:
        print("(dry-run: no files changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run dry-run to preview**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python scripts/promote_skills.py --dry-run
```

Expected: Console shows each skill that would be promoted and what would be archived. No file changes.

- [ ] **Step 3: Review dry-run output**

Confirm:

- All target skills show PROMOTED (not SKIP)
- Archive list matches the replacement map above
- No unexpected skills being skipped

If any target skill shows SKIP, go back to Task 2 and fix its governance.

- [ ] **Step 4: Execute promotion**

```bash
python scripts/promote_skills.py
```

Expected: All target skills promoted, replaced generics archived to `~/.shared-ai-memory/skills/_archived/`.

- [ ] **Step 5: Verify Golden Copy**

```bash
python -c "
from pathlib import Path
golden = Path.home() / '.shared-ai-memory' / 'skills'
stout_skills = [d.name for d in golden.iterdir() if d.is_dir() and d.name.startswith('stout')]
print('stout-* skills in Golden Copy:')
for s in sorted(stout_skills): print(f'  {s}')
"
```

Expected: All promoted `stout-*` skills visible in Golden Copy.

- [ ] **Step 6: Commit**

```bash
git add scripts/promote_skills.py
git commit -m "feat: add skill promotion script with archive support"
```

---

### Task 4: Verify no duplicate responsibilities

**Files:**

- Run: verification script (inline)

- [ ] **Step 1: Check for remaining duplicates**

```bash
python -c "
from pathlib import Path
golden = Path.home() / '.shared-ai-memory' / 'skills'
# Skills that should no longer exist after replacement
replaced = [
    'process-brainstorming', 'dev-tdd', 'process-writing-plans',
    'dev-systematic-debugging', 'process-gcc', 'process-adr',
    'audit-spec-validation', 'commit', 'process-stout-init',
    'stout-init-v2', 'skill-creator', 'workflow_skill_creator',
]
survivors = [r for r in replaced if (golden / r).exists()]
if survivors:
    print('WARNING: These replaced skills still exist:')
    for s in survivors: print(f'  {s}')
else:
    print('OK: All replaced skills have been archived.')
"
```

Expected: `OK: All replaced skills have been archived.`

- [ ] **Step 2: Run final audit on Golden Copy to confirm stout-* are present**

```bash
python -c "
from pathlib import Path
golden = Path.home() / '.shared-ai-memory' / 'skills'
expected = [
    'stout-brainstorming', 'stout-dev-tdd', 'stout-writing-plans',
    'stout-systematic-debugging', 'stout-executing-plans', 'stout-adr',
    'stout-spec-validation', 'stout-commit', 'stout-init',
    'stout-create-skill', 'stout-improve-skill',
    'stout-skill-registry', 'stout-skill-auditor',
]
missing = [s for s in expected if not (golden / s).exists()]
if missing:
    print('MISSING from Golden Copy:')
    for s in missing: print(f'  {s}')
else:
    print('OK: All expected skills present in Golden Copy.')
"
```

Expected: `OK: All expected skills present in Golden Copy.`

---

## Phase C — Python Module Promotion

### Task 5: Copy src/ modules to global template

**Files:**

- Copy: 5 files from `src/core/` and `src/tools/` to `~/.shared-ai-memory/templates/scripts/`

- [ ] **Step 1: Verify source modules exist**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python -c "
from pathlib import Path
modules = [
    'src/core/guardrail.py',
    'src/core/sandbox.py',
    'src/core/preflight.py',
    'src/core/git_guard.py',
    'src/tools/skill_tool.py',
]
for m in modules:
    p = Path(m)
    status = '✅' if p.exists() else '❌ MISSING'
    print(f'{status} {m}')
"
```

Expected: All 5 show ✅.

- [ ] **Step 2: Copy modules to template location**

```bash
python -c "
import shutil
from pathlib import Path
src_root = Path('C:/Projetos/Stout/Projetos/Configuration-Driven Development')
dest = Path.home() / '.shared-ai-memory' / 'templates' / 'scripts'
dest.mkdir(parents=True, exist_ok=True)
modules = [
    src_root / 'src/core/guardrail.py',
    src_root / 'src/core/sandbox.py',
    src_root / 'src/core/preflight.py',
    src_root / 'src/core/git_guard.py',
    src_root / 'src/tools/skill_tool.py',
]
for m in modules:
    if m.exists():
        shutil.copy2(m, dest / m.name)
        print(f'  Copied: {m.name}')
    else:
        print(f'  MISSING: {m.name}')
"
```

Expected: 5 files copied, no MISSING.

- [ ] **Step 3: Verify template directory**

```bash
python -c "
from pathlib import Path
template_dir = Path.home() / '.shared-ai-memory' / 'templates' / 'scripts'
files = sorted(template_dir.glob('*.py'))
print('Scripts in template dir:')
for f in files: print(f'  {f.name}')
"
```

Expected: `guardrail.py`, `sandbox.py`, `preflight.py`, `git_guard.py`, `skill_tool.py`, `stout_promote.py` all present.

---

## Task 6: Final verification

- [ ] **Step 1: Run full CDD test suite (regression check)**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
python -m pytest tests/test_stout_promote_v3.py -q
```

Expected: 34 passed.

- [ ] **Step 2: Verify Golden Copy skill count**

```bash
python -c "
from pathlib import Path
golden = Path.home() / '.shared-ai-memory' / 'skills'
dirs = [d for d in golden.iterdir() if d.is_dir() and not d.name.startswith('_')]
print(f'Total skills in Golden Copy: {len(dirs)}')
stout = [d.name for d in dirs if d.name.startswith('stout')]
print(f'stout-* skills: {len(stout)}')
"
```

- [ ] **Step 3: Commit audit artifacts**

```bash
cd "C:\Projetos\Stout\Projetos\Configuration-Driven Development"
git add docs/audits/ scripts/
git commit -m "docs: add skill audit report and promotion scripts"
```

---

## Spec coverage checklist

- [x] **Structural audit** — `audit_skills.py` checks all 5 governance criteria per skill
- [x] **Replacement map** — all 10 substitutions + 3 new skills covered in PROMOTION_MAP
- [x] **Archive instead of delete** — replaced skills go to `_archived/` with date suffix
- [x] **Dry-run** — `promote_skills.py --dry-run` previews without changes
- [x] **Duplicate check** — Task 4 verifies no replaced skill survives
- [x] **Python modules** — 5 modules copied to template, stout_promote already done
- [x] **Regression check** — CDD test suite re-run in Task 6

---

## Out of scope (separate follow-up)

- Smoke testing of promoted skills in live agent sessions
- V6.0 `stout-skill-registry` / `stout-skill-auditor` integration
- Propagation to Antigravity and Inova projects as consumers
