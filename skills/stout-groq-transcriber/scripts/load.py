"""Load transformed transcription artifacts to their planned destinations."""

from __future__ import annotations

from pathlib import Path

try:
    from scripts.output_contract import OutputPlan, copy_source_if_requested
except ModuleNotFoundError:
    from output_contract import OutputPlan, copy_source_if_requested


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
