"""Transform raw transcription inputs into cleaned text and reports."""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

DEFAULT_CLEANUP_MODEL = "openai/gpt-oss-120b"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
CORRECTIONS_FILE = SCRIPT_DIR / "config" / "corrections.json"

try:
    with CORRECTIONS_FILE.open(encoding="utf-8") as handle:
        WORD_CORRECTIONS = json.load(handle)
except FileNotFoundError:
    WORD_CORRECTIONS = {}
    print(f"[AVISO] Arquivo de correcoes nao encontrado: {CORRECTIONS_FILE}")


def configured_model(env_name: str, default: str) -> str:
    return os.environ.get(env_name, default).strip() or default


def apply_corrections(text: str) -> str:
    """Apply the configured correction dictionary to extracted speech."""

    for wrong, right in WORD_CORRECTIONS.items():
        text = text.replace(wrong, right)
    if WORD_CORRECTIONS:
        print(f"[OK] Aplicadas {len(WORD_CORRECTIONS)} regras de correcao")
    return text


def _chunk_text(text: str, max_chars: int = 8000) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    sentences = text.replace(". ", ".\n").split("\n")
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current += (" " if current else "") + sentence
    if current:
        chunks.append(current.strip())
    print(f"[INFO] Transcricao dividida em {len(chunks)} chunks (max {max_chars} chars cada)")
    return chunks


def _clean_chunk(chunk_text: str, chunk_idx: int, total_chunks: int, client, model: str) -> str:
    is_first = chunk_idx == 0
    is_last = chunk_idx == total_chunks - 1
    instructions = []
    if is_first:
        instructions.append(
            '4. Adicione um "Meeting Summary" no topo deste chunk (2-3 linhas resumindo os temas)'
        )
    if is_last:
        instructions.append(
            '5. Adicione "Key Action Items" no final com topicos de acao mencionados neste chunk'
        )
    extra = "\n".join(instructions)
    if extra:
        extra = "\n" + extra
    prompt = (
        f"Voce e um especialista em transcricao de reunioes.\n"
        f"Estou enviando a parte {chunk_idx + 1} de {total_chunks} de uma transcricao de audio. Precisa:\n\n"
        "1. Corrija gramatica e pontuacao (mantendo o tom natural)\n"
        '2. Identifique diferentes falantes (use "Speaker 1:", "Speaker 2:", etc)\n'
        f"3. Quebre em paragrafos quando a ideia muda{extra}\n"
        "6. Preserve toda fala importante -- nao corte nada essencial\n"
        "7. Mantenha o portugues natural e coloquial\n\n"
        f"Parte {chunk_idx + 1}/{total_chunks}:\n\n---\n{chunk_text}\n---\n\n"
        "Entregue apenas o texto formatado deste chunk, sem introducao."
    )
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def cleanup_with_groq(raw_text: str, client) -> str:
    """Transform raw speech into cleaned, structured transcript text."""

    model = configured_model("GROQ_CLEANUP_MODEL", DEFAULT_CLEANUP_MODEL)
    chunks = _chunk_text(raw_text, max_chars=7000)
    print(f"[LIMPANDO] Processando {len(chunks)} chunks via {model}...")
    cleaned_chunks = []
    for index, chunk in enumerate(chunks):
        print(f"[LIMPANDO] Chunk {index + 1}/{len(chunks)} ({len(chunk):,} chars)...")
        cleaned_chunks.append(_clean_chunk(chunk, index, len(chunks), client, model))
        if index < len(chunks) - 1:
            time.sleep(2)
    if len(cleaned_chunks) == 1:
        return cleaned_chunks[0]
    full = [cleaned_chunks[0]]
    for chunk_text in cleaned_chunks[1:]:
        lines = chunk_text.split("\n")
        filtered = []
        in_summary = False
        for line in lines:
            if line.strip().lower().startswith("meeting summary"):
                in_summary = True
                continue
            if in_summary and line.strip() == "":
                in_summary = False
                continue
            if not in_summary:
                filtered.append(line)
        full.append("\n".join(filtered))
    return "\n\n".join(full)


def count_speakers(transcript_text: str) -> int:
    speakers = set(re.findall(r"Speaker (\d+):", transcript_text))
    return len(speakers) if speakers else 1


def structure_minutes(transcript_text: str, client, model: str) -> str:
    """Transform the beginning of a transcript into structured minutes."""

    context = transcript_text[:6000]
    prompt = (
        "Documente esta transcricao de reuniao.\n\n"
        f"Transcricao (inicio):\n---\n{context}\n---\n\n"
        "Extraia em Markdown:\n"
        "- Participants: quem fala (Speaker X). Outras pessoas mencionadas: listar apos.\n"
        "- Topics Discussed: temas numerados com sub-pontos.\n"
        '- Decisions Made: decisoes formais. Se nenhuma, escreva: "Nenhuma decisao formal registrada."\n'
        "- Action Items: checkbox com responsavel se identificavel.\n"
        "Nao invente. Retorne APENAS as 4 secoes."
    )
    response = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def render_report(
    *,
    audio_path: str | Path,
    metadata: dict[str, str],
    speakers: int,
    minutes_md: str,
    transcript_text: str,
    model: str,
    process_date: datetime | None = None,
) -> str:
    """Transform extracted metadata and minutes into report Markdown."""

    process_date = process_date or datetime.now()
    filename = Path(audio_path).name
    return f"""# Audio Transcription Report

## Metadata

| Field | Value |
|-------|-------|
| **File Name** | {filename} |
| **File Size** | {metadata['size']} |
| **Duration** | {metadata['duration']} |
| **Language** | Portugues (pt-BR) |
| **Processed Date** | {process_date.strftime('%Y-%m-%d %H:%M')} |
| **Speakers Identified** | {speakers} |
| **Transcription Engine** | Groq Whisper Large v3 + {model} (stout-groq-transcriber) |

## Meeting Minutes

{minutes_md}

## Transcricao Completa

{transcript_text}

---

*Generated by stout-groq-transcriber (format_report.py) -- template: audio-transcriber v1.0.0*
"""
