from __future__ import annotations

import sys
from pathlib import Path


def fixture_script() -> str:
    """Return the small child fixture used by process-supervisor tests."""

    return (
        "import sys, time\n"
        "print('out-one', flush=True)\n"
        "print('err-one', file=sys.stderr, flush=True)\n"
        "if '--wait' in sys.argv:\n"
        "    time.sleep(float(sys.argv[sys.argv.index('--wait') + 1]))\n"
    )


def fixture_command(*args: str) -> tuple[str, ...]:
    """Build an argument-array command for the deterministic child fixture."""

    return (sys.executable, "-c", fixture_script(), *args)


def descendant_fixture_command(marker: Path) -> tuple[str, ...]:
    """Build a child/grandchild fixture for native cleanup tests."""

    script = (
        "import json, os, subprocess, sys, time\n"
        "marker = sys.argv[1]\n"
        "grandchild = subprocess.Popen([sys.executable, '-c', "
        "'import time; time.sleep(60)'])\n"
        "with open(marker, 'w', encoding='utf-8') as handle:\n"
        "    json.dump({'bootstrap': os.getppid(), 'child': os.getpid(), "
        "'grandchild': grandchild.pid}, handle)\n"
        "    handle.flush()\n"
        "print('grandchild-ready', flush=True)\n"
        "time.sleep(60)\n"
    )
    return (sys.executable, "-c", script, str(marker))
