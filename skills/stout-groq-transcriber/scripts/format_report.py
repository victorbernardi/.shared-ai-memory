#!/usr/bin/env python3
"""Compatibility CLI for the report ETL orchestrator in ``run.py``."""

import sys
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    Groq = None

_MODULE_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _MODULE_DIR.parent
if not __package__:
    if str(_SKILL_ROOT) in sys.path:
        sys.path.remove(str(_SKILL_ROOT))
    sys.path.insert(0, str(_SKILL_ROOT))

if __package__:
    from .run import (
        DEFAULT_CLEANUP_MODEL,
        parse_report_args,
        report_main,
        run_report_pipeline,
    )
    from .transform import render_report
else:
    from scripts.run import (
        DEFAULT_CLEANUP_MODEL,
        parse_report_args,
        report_main,
        run_report_pipeline,
    )
    from scripts.transform import render_report


def build_report(transcript_path, audio_path, output_path):
    """Preserve the historical function while routing through ``run.py``."""

    return run_report_pipeline(transcript_path, audio_path, output_path, client_factory=Groq)


def main(argv=None):
    return report_main(argv, client_factory=Groq)


if __name__ == "__main__":
    sys.exit(main())
