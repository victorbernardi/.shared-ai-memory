#!/usr/bin/env python3
"""
Transcrição de Áudio Industrial v4.0
Foco: Motor de Transcrição Puro, Suporte a Argumentos e Orquestração Agêntica.
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

# === GOVERNANÇA DE PASTAS (STOUT) ===
BASE_DIR = Path(r"C:\Projetos\Stout\Projetos\Transcricoes")
AUDIO_INPUT = BASE_DIR / "audio_input"
TRANS_FULL = BASE_DIR / "transcriptions" / "full"
LOG_DIR = BASE_DIR / "transcriptions" / "logs"
LOG_FILE = LOG_DIR / "transcription_log.json"

def file_hash(filepath: str) -> str:
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_log():
    if not LOG_FILE.exists():
        return {"processed": {}, "stats": {"total": 0, "success": 0, "failed": 0}}
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"processed": {}, "stats": {"total": 0, "success": 0, "failed": 0}}

def save_log(log_data):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

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

def transcribe_audio(wav_path: str, model_name: str, language: str):
    from faster_whisper import WhisperModel
    print(f"   [Whisper] Transcrevendo com modelo '{model_name}'...")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(wav_path, beam_size=5, language=language)
    
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

def archive_to_flac(input_path: str):
    if input_path.lower().endswith('.flac'):
        return Path(input_path)
        
    base_name = Path(input_path).stem
    flac_path = AUDIO_INPUT / f"{base_name}.flac"
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:a", "flac", "-compression_level", "5",
        str(flac_path)
    ]
    print(f"   [FFmpeg] Arquivando em FLAC...")
    subprocess.run(cmd, capture_output=True, check=True, shell=True)
    return flac_path

def process_file(filepath: str, log_data, model_name, language):
    filename = os.path.basename(filepath)
    current_hash = file_hash(filepath)
    
    if filename in log_data["processed"]:
        entry = log_data["processed"][filename]
        if entry["hash"] == current_hash and entry["status"] == "success":
            print(f"SKIP: {filename} (Already audited)")
            return True

    print(f"\n[Processing] {filename}")
    wav_path = None
    try:
        wav_path = normalize_audio(filepath)
        segments, info = transcribe_audio(wav_path, model_name, language)
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = Path(filepath).stem.replace(" ", "-")
        full_md_path = TRANS_FULL / f"{timestamp_str}_{safe_name}_FULL.md"
        full_pdf_path = TRANS_FULL / f"{timestamp_str}_{safe_name}_FULL.pdf"
        
        content = f"# Transcrição Full: {filename}\n\n"
        content += f"**Data:** {timestamp_str} | **Modelo:** {model_name}\n\n---\n\n"
        
        for s in segments:
            m_s, s_s = divmod(int(s['start']), 60)
            m_e, s_e = divmod(int(s['end']), 60)
            content += f"**[{m_s:02d}:{s_s:02d} - {m_e:02d}:{s_e:02d}]** {s['text']}\n\n"
            
        TRANS_FULL.mkdir(parents=True, exist_ok=True)
        with open(full_md_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        generate_pdf(full_md_path, full_pdf_path)
        
        # 6. Arquivamento e Limpeza (Move para /archive/)
        final_audio_path = archive_to_flac(filepath)
        ARCHIVE_DIR = AUDIO_INPUT / "archive"
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        dest_path = ARCHIVE_DIR / final_audio_path.name
        if dest_path.exists():
            os.remove(dest_path)
        shutil.move(str(final_audio_path), str(dest_path))
        
        # Se o original era diferente do flac e ainda existe na raiz, remove
        if str(filepath) != str(final_audio_path) and os.path.exists(filepath):
            os.remove(filepath)
            
        log_data["processed"][filename] = {
            "hash": current_hash,
            "processed_at": datetime.now().isoformat(),
            "status": "success",
            "model_size": model_name,
            "duration_seconds": round(segments[-1]["end"], 2) if segments else 0,
            "segments": len(segments),
            "error": None
        }
        log_data["stats"]["success"] += 1
        print(f"SUCCESS: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Falha: {filename} -> {e}")
        log_data["processed"][filename] = {
            "hash": current_hash,
            "processed_at": datetime.now().isoformat(),
            "status": "failed",
            "error": str(e)
        }
        log_data["stats"]["failed"] += 1
        return False
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        save_log(log_data)

def main():
    parser = argparse.ArgumentParser(description="Motor de Transcrição Antigravity")
    parser.add_argument("file", nargs="?", help="Arquivo específico para transcrever")
    parser.add_argument("--model", default="base", help="Modelo Whisper (tiny, base, small, etc)")
    parser.add_argument("--lang", default="pt", help="Linguagem do áudio")
    parser.add_argument("--output_dir", help="Diretório de saída customizado")
    args = parser.parse_args()

    print(f"--- Antigravity Transcriber v4.0 (Model: {args.model}) ---")
    
    log_data = load_log()
    
    if args.file:
        files = [args.file]
    else:
        files = [str(AUDIO_INPUT / f) for f in os.listdir(AUDIO_INPUT) 
                 if f.lower().endswith(('.mp3', '.m4a', '.wav', '.ogg', '.aac', '.flac'))]
    
    if not files:
        print("📭 Nenhum arquivo para processar.")
        return

    for f in files:
        process_file(f, log_data, args.model, args.lang)

if __name__ == "__main__":
    main()
