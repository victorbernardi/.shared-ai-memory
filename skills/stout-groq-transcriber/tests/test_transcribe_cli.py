#!/usr/bin/env python3
"""CLI-facing tests for the new output-contract flags in transcribe.py."""

from pathlib import Path

from scripts import transcribe


def test_parse_args_defaults_to_clean_mode() -> None:
    args = transcribe.parse_args(["meeting.mp4"])

    assert args.input_file == "meeting.mp4"
    assert args.mode == "clean"
    assert args.out_dir is None
    assert args.session_name is None
    assert args.keep_source_copy is False


def test_parse_args_with_all_flags() -> None:
    args = transcribe.parse_args(
        [
            "meeting.mp4",
            "--mode",
            "archive",
            "--out-dir",
            "custom",
            "--session-name",
            "standup-2026",
            "--keep-source-copy",
        ]
    )

    assert args.mode == "archive"
    assert args.out_dir == "custom"
    assert args.session_name == "standup-2026"
    assert args.keep_source_copy is True


def test_main_errors_when_input_missing(capsys) -> None:
    exit_code = transcribe.main(["missing.mp4"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "[ERRO] input file not found: missing.mp4" in captured.err


def test_main_errors_when_api_key_missing(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("Groq_API_Key", raising=False)
    audio_path = tmp_path / "audio.mp3"
    audio_path.write_bytes(b"audio")

    exit_code = transcribe.main([str(audio_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "GROQ_API_KEY" in captured.err


class DummyGroq:
    def __init__(self, **_: object) -> None:
        pass

    class audio:
        class transcriptions:
            @staticmethod
            def create(**_: object) -> str:
                return "fala crua"

    class chat:
        class completions:
            @staticmethod
            def create(**_: object):
                class Choice:
                    class Message:
                        content = "Resumo curto\n\nSpeaker 1: Fala organizada"

                    message = Message()

                class Response:
                    choices = [Choice()]

                return Response()


def test_clean_writes_single_markdown_in_research(
    monkeypatch, tmp_path: Path
) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    (project_root / "research").mkdir()
    audio_path = project_root / "meeting.mp4"
    audio_path.write_bytes(b"audio")

    monkeypatch.chdir(project_root)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "Groq", DummyGroq)

    exit_code = transcribe.main([str(audio_path)])

    assert exit_code == 0
    assert (project_root / "research" / "meeting.md").is_file()
    assert not (project_root / "meeting_transcript.txt").exists()
    assert not list(project_root.glob("phx_*"))


def test_clean_without_research_falls_back_to_transcriptions(
    monkeypatch, tmp_path: Path
) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    audio_path = project_root / "standup.m4a"
    audio_path.write_bytes(b"audio")

    monkeypatch.chdir(project_root)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "Groq", DummyGroq)

    exit_code = transcribe.main([str(audio_path)])

    assert exit_code == 0
    assert (project_root / "transcriptions" / "standup.md").is_file()


def test_debug_writes_inside_session_directory(
    monkeypatch, tmp_path: Path
) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    audio_path = project_root / "meeting.mp4"
    audio_path.write_bytes(b"audio")

    monkeypatch.chdir(project_root)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "Groq", DummyGroq)

    exit_code = transcribe.main(
        [str(audio_path), "--mode", "debug", "--keep-source-copy"]
    )

    assert exit_code == 0
    assert (
        project_root / "transcriptions" / "meeting" / "debug" / "meeting.md"
    ).is_file()
    assert (
        project_root / "transcriptions" / "meeting" / "debug" / "meeting.mp4"
    ).is_file()


def test_main_errors_when_out_dir_points_to_existing_file(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    audio_path = project_root / "meeting.mp4"
    audio_path.write_bytes(b"audio")
    out_dir_file = project_root / "SKILL.md"
    out_dir_file.write_text("occupied", encoding="utf-8")

    monkeypatch.chdir(project_root)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    exit_code = transcribe.main(
        [str(audio_path), "--out-dir", str(out_dir_file)]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "[ERRO] output directory cannot be created:" in captured.err
    assert str(out_dir_file) in captured.err


def test_main_errors_when_final_markdown_path_is_directory(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    project_root = tmp_path / "repo"
    (project_root / ".git").mkdir(parents=True)
    research_dir = project_root / "research"
    research_dir.mkdir()
    audio_path = project_root / "meeting.mp4"
    audio_path.write_bytes(b"audio")
    final_path_dir = research_dir / "meeting.md"
    final_path_dir.mkdir()

    monkeypatch.chdir(project_root)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(transcribe, "Groq", DummyGroq)

    exit_code = transcribe.main([str(audio_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "[ERRO] final file cannot be written:" in captured.err
    assert str(final_path_dir) in captured.err

