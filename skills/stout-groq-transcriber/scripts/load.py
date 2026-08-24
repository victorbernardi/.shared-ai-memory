"""Load transformed transcription artifacts to their planned destinations."""

from __future__ import annotations

import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _MODULE_DIR.parent
if not __package__:
    if str(_SKILL_ROOT) in sys.path:
        sys.path.remove(str(_SKILL_ROOT))
    sys.path.insert(0, str(_SKILL_ROOT))

if __package__:
    from .output_contract import OutputPlan, copy_source_if_requested
else:
    from scripts.output_contract import OutputPlan, copy_source_if_requested


def load_transcription(plan: OutputPlan, markdown: str, input_path: str | Path) -> Path:
    """Persist the canonical transcript and optional source copy."""

    plan.final_path.write_text(markdown, encoding="utf-8")
    if plan.source_copy_path is not None:
        copy_source_if_requested(plan, Path(input_path))
    return plan.final_path


def load_report(report: str, output_path: str | Path) -> Path:
    """Persist a formatted report Markdown artifact."""

    output_path = Path(output_path)
    output_path.write_text(report, encoding="utf-8")
    return output_path
