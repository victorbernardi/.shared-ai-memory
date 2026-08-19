"""Extract audio and transcript inputs for the transcription ETL."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


DEFAULT_WHISPER_MODEL = "whisper-large-v3"
GROQ_SUPPORTED = {
    ".flac",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
}


def configured_model(env_name: str, default: str) -> str:
    return os.environ.get(env_name, default).strip() or default


def transcribe_audio(input_path: str | Path, client, model: str | None = None) -> str:
    """Extract raw speech text from an audio file through Groq Whisper."""

    input_path = Path(input_path)
    print(f"[TRANSCREVENDO] {input_path}")
    with input_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=(input_path.name, audio_file.read()),
            model=model or configured_model("GROQ_WHISPER_MODEL", DEFAULT_WHISPER_MODEL),
            response_format="text",
        )
    raw_text = result.strip()
    print(f"[OK] Capturados {len(raw_text):,} caracteres de fala")
    return raw_text


def read_transcript(transcript_path: str | Path) -> str:
    """Extract a previously generated transcript from disk."""

    return Path(transcript_path).read_text(encoding="utf-8")


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "Desconhecida (instale mutagen para extrair automaticamente)"
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_audio_metadata(audio_path: str | Path) -> dict[str, str]:
    """Extract file size and duration metadata without transcribing again."""

    audio_path = Path(audio_path)
    duration = None
    if MutagenFile is not None:
        try:
            audio = MutagenFile(audio_path)
            if audio is not None and audio.info is not None:
                duration = audio.info.length
        except Exception:
            duration = None
    return {
        "size": human_size(audio_path.stat().st_size),
        "duration": format_duration(duration),
    }
