"""Orchestrate the transcription ETL pipelines."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        """Keep non-network tests importable without python-dotenv."""

        return False


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
    from .extract import (
        DEFAULT_WHISPER_MODEL,
        get_audio_metadata,
        read_transcript,
        transcribe_audio,
    )
    from .load import load_report, load_transcription
    from .output_contract import build_output_plan, render_markdown, resolve_mode
    from .transform import (
        DEFAULT_CLEANUP_MODEL,
        apply_corrections,
        configured_model,
        count_speakers,
        cleanup_with_groq,
        render_report,
        structure_minutes,
    )
else:
    from scripts.extract import (
        DEFAULT_WHISPER_MODEL,
        get_audio_metadata,
        read_transcript,
        transcribe_audio,
    )
    from scripts.load import load_report, load_transcription
    from scripts.output_contract import build_output_plan, render_markdown, resolve_mode
    from scripts.transform import (
        DEFAULT_CLEANUP_MODEL,
        apply_corrections,
        configured_model,
        count_speakers,
        cleanup_with_groq,
        render_report,
        structure_minutes,
    )


ENV_PATH = Path.home() / ".shared-ai-memory" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Transcrever audio com Groq Whisper + modelo configuravel")
    parser.add_argument("input_file", help="Arquivo de audio para transcrever")
    parser.add_argument("--mode", choices=["clean", "debug", "archive"], default="clean")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--session-name", default=None)
    parser.add_argument("--keep-source-copy", action="store_true", default=False)
    return parser.parse_args(argv)


def run_transcription_pipeline(
    input_path: str | Path,
    *,
    mode: str = "clean",
    out_dir_override: Path | None = None,
    session_name_override: str | None = None,
    keep_source_copy: bool = False,
    cwd: Path | None = None,
    client_factory=None,
) -> int:
    """Run ``extract -> transform -> load`` for one audio file."""

    input_path = Path(input_path)
    if not input_path.is_file():
        print(f"[ERRO] input file not found: {input_path}", file=sys.stderr)
        return 1

    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("Groq_API_Key")
    if not api_key:
        print("[ERRO] GROQ_API_KEY not set", file=sys.stderr)
        print(
            "   Set GROQ_API_KEY in ~/.shared-ai-memory/.env or as environment variable",
            file=sys.stderr,
        )
        return 1

    effective_mode = resolve_mode(mode)
    plan = build_output_plan(
        input_path=input_path,
        cwd=cwd or Path.cwd(),
        mode=effective_mode,
        out_dir_override=out_dir_override,
        session_name_override=session_name_override,
        keep_source_copy=keep_source_copy,
    )
    for warning in plan.warnings:
        print(warning, file=sys.stderr)

    try:
        plan.final_path.parent.mkdir(parents=True, exist_ok=True)
        if plan.artifact_dir is not None:
            plan.artifact_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(
            f"[ERRO] output directory cannot be created: {plan.final_path.parent} ({exc})",
            file=sys.stderr,
        )
        return 1

    client_factory = client_factory or Groq
    if client_factory is None:
        print(
            "[ERRO] dependencia groq nao instalada; execute: python -m pip install 'groq>=1.5.0'",
            file=sys.stderr,
        )
        return 1

    client = client_factory(api_key=api_key)
    print("\n" + "=" * 60)
    print("Stout Groq Transcriber v1.0.0")
    print("=" * 60 + "\n")

    raw_transcript = transcribe_audio(input_path, client)
    if not raw_transcript:
        print("[ERRO] Transcricao vazia -- audio pode estar inaudivel ou corrompido", file=sys.stderr)
        return 1
    corrected_transcript = apply_corrections(raw_transcript)
    final_transcript = cleanup_with_groq(corrected_transcript, client)
    markdown = render_markdown(
        title=plan.session_name,
        metadata_lines=[f"- File: {input_path.name}", f"- Mode: {effective_mode}"],
        summary="",
        action_items=[],
        transcript=final_transcript,
    )
    try:
        load_transcription(plan, markdown, input_path)
    except OSError as exc:
        print(f"[ERRO] final file cannot be written: {plan.final_path} ({exc})", file=sys.stderr)
        return 1
    print(f"[OK] Final: {plan.final_path}")
    if plan.artifact_dir is not None and plan.mode != "clean":
        print(f"[OK] Artifacts in: {plan.artifact_dir}")
    print()
    return 0


def parse_report_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Reformatar transcricao de transcribe.py no template Audio Transcription Report"
    )
    parser.add_argument("transcript_txt")
    parser.add_argument("audio_file")
    parser.add_argument("output_md", nargs="?")
    return parser.parse_args(argv)


def run_report_pipeline(
    transcript_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    *,
    client_factory=None,
) -> int:
    """Run ``extract -> transform -> load`` for a formatted report."""

    transcript_path = Path(transcript_path)
    audio_path = Path(audio_path)
    transcript_text = read_transcript(transcript_path)
    metadata = get_audio_metadata(audio_path)
    speakers = count_speakers(transcript_text)
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("Groq_API_Key")
    if not api_key:
        print("[ERRO] GROQ_API_KEY nao configurada")
        print("   Verificar em: ~/.shared-ai-memory/.env")
        return 1
    client_factory = client_factory or Groq
    if client_factory is None:
        print(
            "[ERRO] dependencia groq nao instalada; execute: python -m pip install 'groq>=1.5.0'",
        )
        return 1

    client = client_factory(api_key=api_key)
    model = configured_model("GROQ_CLEANUP_MODEL", DEFAULT_CLEANUP_MODEL)
    print("[ESTRUTURANDO] Meeting Minutes (participantes, topicos, decisoes, action items)...")
    minutes_md = structure_minutes(transcript_text, client, model)
    report = render_report(
        audio_path=audio_path,
        metadata=metadata,
        speakers=speakers,
        minutes_md=minutes_md,
        transcript_text=transcript_text,
        model=model,
    )
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        load_report(report, output_path)
    except OSError as exc:
        print(f"[ERRO] relatorio nao pode ser gravado: {output_path} ({exc})")
        return 1
    print(f"\n[OK] Relatorio salvo em: {output_path}\n")
    return 0


def transcribe_main(argv=None, client_factory=None) -> int:
    args = parse_args(argv)
    return run_transcription_pipeline(
        args.input_file,
        mode=args.mode,
        out_dir_override=Path(args.out_dir) if args.out_dir else None,
        session_name_override=args.session_name,
        keep_source_copy=args.keep_source_copy,
        client_factory=client_factory,
    )


def report_main(argv=None, client_factory=None) -> int:
    args = parse_report_args(argv)
    if not Path(args.transcript_txt).is_file():
        print(f"[ERRO] Transcricao nao encontrada: {args.transcript_txt}")
        return 1
    if not Path(args.audio_file).is_file():
        print(f"[ERRO] Audio nao encontrado: {args.audio_file}")
        return 1
    output_path = args.output_md or f"{Path(args.transcript_txt).with_suffix('')}_report.md"
    return run_report_pipeline(args.transcript_txt, args.audio_file, output_path, client_factory=client_factory)


def main(argv=None) -> int:
    """Official CLI entrypoint for transcription and report ETL."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0].casefold() == "report":
        return report_main(arguments[1:])
    return transcribe_main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
