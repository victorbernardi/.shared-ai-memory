#!/usr/bin/env python3
"""
Transcrição de Áudio Contextual v1.0 (Stout Edition)
Baseado no Motor v4.0, adaptado para uso em Skills Agênticas.
"""

import os
import sys
import json
import hashlib
import subprocess
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# Forçar UTF-8 no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# === CONFIGURAÇÕES DE INFRAESTRUTURA ===
FFMPEG_PATH = r"C:\Projetos\Stout\Projetos\Transcricoes\bin\ffmpeg.exe"
PANDOC_PATH = r"pandoc"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def file_hash(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def normalize_audio(input_path: str) -> str:
    output_wav = "temp_normalized.wav"
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        output_wav
    ]
    print(f"   [FFmpeg] Normalizando: {os.path.basename(input_path)}")
    subprocess.run(cmd, capture_output=True, check=True, shell=True)
    return output_wav

def transcribe_audio(wav_path: str, model_name: str, language: str, initial_prompt: str = None):
    from faster_whisper import WhisperModel
    print(f"   [Whisper] Transcrevendo com modelo '{model_name}'...")
    if initial_prompt:
        print(f"   [Context] Usando Initial Prompt: {initial_prompt[:100]}...")
        
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        wav_path, 
        beam_size=5, 
        language=language, 
        initial_prompt=initial_prompt
    )

    results = []
    for segment in segments:
        results.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
    return results, info

def generate_pdf(md_path: str, pdf_path: str):
    temp_html = md_path.with_suffix(".html")
    print(f"   [Pandoc] Gerando HTML intermediário...")
    try:
        subprocess.run([PANDOC_PATH, str(md_path), "-o", str(temp_html)], check=True, shell=True)
        print(f"   [Edge] Convertendo para PDF: {pdf_path.name}")
        edge_cmd = [
            EDGE_PATH, "--headless", "--disable-gpu",
            f"--print-to-pdf={pdf_path}", str(temp_html)
        ]
        subprocess.run(edge_cmd, check=True, shell=True)
        if temp_html.exists():
            os.remove(temp_html)
        return True
    except Exception as e:
        print(f"   [Error] Falha na geração do PDF: {e}")
        return False

def process_file(filepath: str, model_name, language, output_dir, initial_prompt):
    filename = os.path.basename(filepath)
    print(f"\n[Processing] {filename}")
    
    wav_path = None
    try:
        wav_path = normalize_audio(filepath)
        segments, info = transcribe_audio(wav_path, model_name, language, initial_prompt)

        timestamp_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = Path(filepath).stem.replace(" ", "-")
        
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        full_md_path = out_path / f"{timestamp_str}_{safe_name}_FULL.md"
        full_pdf_path = out_path / f"{timestamp_str}_{safe_name}_FULL.pdf"

        content = f"# Transcrição Contextual: {filename}\n\n"
        content += f"**Data:** {timestamp_str} | **Modelo:** {model_name}\n"
        if initial_prompt:
            content += f"**Contexto Injetado:** {initial_prompt}\n"
        content += "\n---\n\n"

        for s in segments:
            m_s, s_s = divmod(int(s['start']), 60)
            m_e, s_e = divmod(int(s['end']), 60)
            content += f"**[{m_s:02d}:{s_s:02d} - {m_e:02d}:{s_e:02d}]** {s['text']}\n\n"

        with open(full_md_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"   [Success] Markdown gerado em: {full_md_path}")
        
        # Tenta gerar PDF se as ferramentas estiverem disponíveis
        if shutil.which("pandoc"):
            generate_pdf(full_md_path, full_pdf_path)

        return True

    except Exception as e:
        print(f"❌ Falha: {filename} -> {e}")
        return False
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)

def main():
    parser = argparse.ArgumentParser(description="Motor de Transcrição Contextual Antigravity")
    parser.add_argument("file", help="Arquivo específico para transcrever")
    parser.add_argument("--model", default="base", help="Modelo Whisper (tiny, base, small, etc)")
    parser.add_argument("--lang", default="pt", help="Linguagem do áudio")
    parser.add_argument("--output_dir", default="./docs/transcricao", help="Diretório de saída")
    parser.add_argument("--initial_prompt", help="Dicionário de termos para guiar a transcrição")
    args = parser.parse_args()

    print(f"--- Contextual Transcriber v1.0 (Model: {args.model}) ---")

    if not os.path.exists(args.file):
        print(f"❌ Erro: Arquivo não encontrado: {args.file}")
        return

    process_file(args.file, args.model, args.lang, args.output_dir, args.initial_prompt)

if __name__ == "__main__":
    main()
