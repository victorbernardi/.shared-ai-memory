"""Regression tests for the skill's explicit ETL module seams."""

from scripts import extract, load, run, transform


def test_skill_exposes_the_four_etl_modules() -> None:
    assert callable(extract.transcribe_audio)
    assert callable(transform.cleanup_with_groq)
    assert callable(load.load_transcription)
    assert callable(run.run_transcription_pipeline)


def test_run_module_keeps_the_etl_stage_order() -> None:
    source = run.run_transcription_pipeline
    source_text = source.__code__.co_names

    assert source_text.index("transcribe_audio") < source_text.index("apply_corrections")
    assert source_text.index("apply_corrections") < source_text.index("cleanup_with_groq")
    assert source_text.index("cleanup_with_groq") < source_text.index("load_transcription")
