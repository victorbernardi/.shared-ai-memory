"""post_approve.py — Promote artifacts after plan approval, then commit.

Usage:
    python src/tools/post_approve.py            # promote + git commit
    python src/tools/post_approve.py --dry-run  # list candidates, no copy, no commit
"""
import sys
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stout_promote import promote_artifacts, get_current_branch  # noqa: E402


def run(
    project_root: Path | None = None,
    session_dirs: list | None = None,
    dry_run: bool = False,
) -> int:
    """Promote artifacts and optionally commit. Returns exit code."""
    project_root = Path(project_root) if project_root else Path.cwd()
    branch = get_current_branch(project_root)

    count = promote_artifacts(project_root, branch, session_dirs, dry_run=dry_run)

    if dry_run:
        print(
            f"[dry-run] {count} artefato(s) seriam promovidos "
            f"(branch '{branch}'). Nada copiado, nada commitado."
        )
        return 0

    if count == 0:
        print("Nenhum artefato novo para promover.")
        return 0

    subprocess.run(["git", "add", "docs/"], cwd=project_root, check=True)
    msg = f"docs: Promote {count} artifact(s) [{branch}]"
    subprocess.run(["git", "commit", "-m", msg], cwd=project_root, check=True)
    print(f"OK: {count} artefato(s) promovido(s) e commitado(s). Branch: {branch}")
    return 0


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Promote artifacts after plan approval"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List candidates without copying or committing",
    )
    args = parser.parse_args()
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
