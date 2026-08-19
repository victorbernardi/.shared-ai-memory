#!/usr/bin/env python3
"""Compatibility CLI for the transcription ETL orchestrator in ``run.py``."""

import sys

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from scripts.extract import DEFAULT_WHISPER_MODEL, transcribe_audio
    from scripts.run import (
        DEFAULT_CLEANUP_MODEL,
        main as _run_main,
        parse_args,
        run_transcription_pipeline,
        transcribe_main,
    )
    from scripts.transform import apply_corrections, cleanup_with_groq, configured_model
except ModuleNotFoundError:
    from extract import DEFAULT_WHISPER_MODEL, transcribe_audio
    from run import (
        DEFAULT_CLEANUP_MODEL,
        main as _run_main,
        parse_args,
        run_transcription_pipeline,
        transcribe_main,
    )
    from transform import apply_corrections, cleanup_with_groq, configured_model


def main(argv=None):
    """Preserve the historical ``transcribe.py`` command and test seam."""

    return transcribe_main(argv, client_factory=Groq)


if __name__ == "__main__":
    sys.exit(main())
