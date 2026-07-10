#!/usr/bin/env python3
"""
Stout Groq Transcriber -- Main Script

Transcricao de audio via Groq Whisper v3 + LLaMA 3.3-70b com:
- Correcao automatica de termos (dicionario customizavel)
- Limpeza semantica (gramatica, pontuacao, estrutura)
- Extracao automatica de action items
- Output contract controlado (clean, debug, archive)

Uso:
  python transcribe.py audio.m4a
  python transcribe.py audio.mp3 --mode debug
  python transcribe.py audio.mp3 --mode archive --keep-source-copy
  python transcribe.py audio.mp3 --out-dir custom --session-name reuniao
"""

import sys
import os
import json
import argparse
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

from scripts.output_contract import (
    build_output_plan,
    copy_source_if_requested,
    render_markdown,
    resolve_mode,
)

# Forcar UTF-8 no output do Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Carregar .env de localizacao canonica
ENV_PATH = Path.home() / ".shared-ai-memory" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # Fallback para .env local

# Carregar dicionario de correcoes
SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_DIR = SCRIPT_DIR / "config"
CORRECTIONS_FILE = CONFIG_DIR / "corrections.json"

try:
    with open(CORRECTIONS_FILE) as f:
        WORD_CORRECTIONS = json.load(f)
except FileNotFoundError:
    WORD_CORRECTIONS = {}
    print(f"[AVISO] Arquivo de correcoes nao encontrado: {CORRECTIONS_FILE}")

# Formatos suportados nativamente pelo Groq
GROQ_SUPPORTED = {".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm"}


def apply_corrections(text):
    """Aplicar correcoes do dicionario customizado."""
    for wrong, right in WORD_CORRECTIONS.items():
        text = text.replace(wrong, right)

    if WORD_CORRECTIONS:
        print(f"[OK] Aplicadas {len(WORD_CORRECTIONS)} regras de correcao")
    return text


def transcribe_audio(input_path, client):
    """Transcrever audio via Groq Whisper v3."""
    print(f"[TRANSCREVENDO] {input_path}")

    with open(input_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=(os.path.basename(input_path), audio_file.read()),
            model="whisper-large-v3",
            response_format="text",
        )

    raw_text = result.strip()
    chars = len(raw_text)
    print(f"[OK] Capturados {chars:,} caracteres de fala")
    return raw_text


def cleanup_with_groq(raw_text, client):
    """Limpeza e estruturacao via Groq LLaMA."""
    print("[LIMPANDO] Estruturando transcricao via LLaMA 3.3-70b...")

    prompt = f"""Voce e um especialista em transcricao de reunioes.
Estou enviando uma transcricao bruta de audio e preciso que voce:

1. Corrija gramatica e pontuacao (mantendo o tom natural)
2. Identifique diferentes falantes (use "Speaker 1:", "Speaker 2:", etc)
3. Quebre em paragrafos quando a ideia muda
4. Adicione um "Meeting Summary" no topo (2-3 linhas resumindo temas principais)
5. Adicione "Key Action Items" no final com topicos de acao mencionados
6. Preservem toda fala importante -- nao corte nada essencial
7. Mantenha o portugues natural e coloquial

Aqui esta a transcricao bruta:

\"\"\"
{raw_text}
\"\"\"

Por favor, entregue apenas a transcricao formatada, sem introducao."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def parse_args(argv=None):
    """Parse CLI arguments, returning a namespace with the new output-contract flags."""
    parser = argparse.ArgumentParser(
        description="Transcrever audio com Groq Whisper + LLaMA"
    )
    parser.add_argument("input_file", help="Arquivo de audio para transcrever")
    parser.add_argument(
        "--mode",
        choices=["clean", "debug", "archive"],
        default="clean",
        help="Modo de saida (clean, debug, archive). Padrao: clean",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Diretorio base de saida (substitui resolucao automatica)",
    )
    parser.add_argument(
        "--session-name",
        default=None,
        help="Nome da sessao (substitui o nome derivado do arquivo)",
    )
    parser.add_argument(
        "--keep-source-copy",
        action="store_true",
        default=False,
        help="Manter copia do arquivo de audio original na saida",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Run the transcription pipeline with the new output contract.

    Returns an exit code (0 for success, 1 for error).
    """
    args = parse_args(argv)

    # Validar arquivo de entrada
    input_path = Path(args.input_file)
    if not input_path.is_file():
        print(f"[ERRO] input file not found: {args.input_file}", file=sys.stderr)
        return 1

    # Validar API key (suporta ambos os nomes)
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("Groq_API_Key")
    if not api_key:
        print("[ERRO] GROQ_API_KEY not set", file=sys.stderr)
        print("   Set GROQ_API_KEY in ~/.shared-ai-memory/.env or as environment variable", file=sys.stderr)
        return 1

    # Resolver plano de saida
    mode = resolve_mode(args.mode)
    out_dir_override = Path(args.out_dir) if args.out_dir else None
    cwd = Path.cwd()

    plan = build_output_plan(
        input_path=input_path,
        cwd=cwd,
        mode=mode,
        out_dir_override=out_dir_override,
        session_name_override=args.session_name,
        keep_source_copy=args.keep_source_copy,
    )

    # Emitir warnings
    for warning in plan.warnings:
        print(warning, file=sys.stderr)

    # Garantir que os diretorios de saida existam
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

    # Inicializar cliente Groq
    client = Groq(api_key=api_key)

    # Pipeline
    print("\n" + "=" * 60)
    print("Stout Groq Transcriber v1.0.0")
    print("=" * 60 + "\n")

    raw_transcript = transcribe_audio(str(input_path), client)

    if not raw_transcript:
        print("[ERRO] Transcricao vazia -- audio pode estar inaudivel ou corrompido", file=sys.stderr)
        return 1

    raw_transcript = apply_corrections(raw_transcript)
    final_transcript = cleanup_with_groq(raw_transcript, client)

    # Construir markdown final
    session_name = plan.session_name
    markdown = render_markdown(
        title=session_name,
        metadata_lines=[f"- File: {input_path.name}", f"- Mode: {mode}"],
        summary="",  # LLM ja inclui summary no corpo da transcricao formatada
        action_items=[],  # LLM ja inclui action items no corpo
        transcript=final_transcript,
    )

    # Escrever artefatos
    try:
        plan.final_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        print(
            f"[ERRO] final file cannot be written: {plan.final_path} ({exc})",
            file=sys.stderr,
        )
        return 1
    print(f"[OK] Final: {plan.final_path}")

    if plan.source_copy_path is not None:
        copy_source_if_requested(plan, input_path)

    if plan.artifact_dir is not None and plan.mode != "clean":
        print(f"[OK] Artifacts in: {plan.artifact_dir}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

