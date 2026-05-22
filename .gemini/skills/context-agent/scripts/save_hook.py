#!/usr/bin/env python3
"""
Stop hook wrapper para Claude Code.
Lê transcript_path do stdin JSON e chama context_manager save --session <path>.

Uso pelo hook: python save_hook.py
Uso para teste: python save_hook.py --dry-run  (imprime comando, não executa)
"""
import json
import sys
import subprocess
from pathlib import Path


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}

    transcript_path = data.get("transcript_path", "")

    script = Path(__file__).parent / "context_manager.py"
    cmd = [sys.executable, str(script), "save"]

    if transcript_path:
        cmd += ["--session", transcript_path]
        print(f"[save_hook] transcript_path: {transcript_path}")
    else:
        print("WARNING: transcript_path ausente no stdin — usando sessão mais recente por mtime.", file=sys.stderr)

    print(f"[save_hook] cmd: {' '.join(cmd)}")

    if not dry_run:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
