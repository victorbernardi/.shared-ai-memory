#!/usr/bin/env python3
"""Compatibility CLI for the transcription ETL orchestrator in ``run.py``."""

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
    from .extract import DEFAULT_WHISPER_MODEL, transcribe_audio
    from .run import (
        DEFAULT_CLEANUP_MODEL,
        main as _run_main,
        parse_args,
        run_transcription_pipeline,
        transcribe_main,
    )
    from .transform import apply_corrections, cleanup_with_groq, configured_model
else:
    from scripts.extract import DEFAULT_WHISPER_MODEL, transcribe_audio
    from scripts.run import (
        DEFAULT_CLEANUP_MODEL,
        main as _run_main,
        parse_args,
        run_transcription_pipeline,
        transcribe_main,
    )
    from scripts.transform import apply_corrections, cleanup_with_groq, configured_model


def main(argv=None):
    """Preserve the historical ``transcribe.py`` command and test seam."""

    return transcribe_main(argv, client_factory=Groq)


if __name__ == "__main__":
    sys.exit(main())
