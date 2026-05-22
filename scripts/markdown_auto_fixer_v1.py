#!/usr/bin/env python3
"""
Stout Markdown Auto Fixer Watcher
Fica em background corrigindo automaticamente arquivos .md usando o markdownlint oficial.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("[ERRO] Pacote 'watchdog' nao encontrado. Por favor, instale com: pip install watchdog")
    sys.exit(1)

RECENTLY_MODIFIED = {}

def process_file(file_path):
    path = Path(file_path)
    if path.name == "watcher.py" or path.name.startswith("."):
        return

    current_time = time.time()
    # Evita loop infinito: se alteramos o arquivo nos ultimos 2 segundos, ignora
    if file_path in RECENTLY_MODIFIED:
        if current_time - RECENTLY_MODIFIED[file_path] < 2:
            return

    try:
        # Roda o npx markdownlint-cli silenciosamente
        # Usamos shell=True no Windows para que o npx seja resolvido corretamente
        result = subprocess.run(
            ["npx", "markdownlint-cli", "--fix", str(file_path)],
            capture_output=True,
            text=True,
            shell=os.name == 'nt'
        )

        # Se houveram modificacoes (ou mesmo se ja estava certo), atualizamos o timer
        RECENTLY_MODIFIED[file_path] = time.time()

        # O markdownlint-cli normalmente avisa no stderr quando arruma coisas ou quando restam erros inarrumaveis
        if "Fixed" in result.stderr or "Fixed" in result.stdout:
            print(f"[{time.strftime('%H:%M:%S')}] Sanitizado pelo markdownlint: {path.name}")
        elif result.returncode != 0:
            # Mostra se houveram erros que não puderam ser corrigidos automaticamente
            print(f"[{time.strftime('%H:%M:%S')}] Erros restantes em {path.name}: (Pressione F8 no editor)")
            
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Erro ao processar {path.name}: {e}")

class MarkdownHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            # Ignora pastas de ambiente e controle
            if any(x in event.src_path for x in ['.git', 'node_modules', '.venv', 'venv']):
                return
            process_file(event.src_path)

if __name__ == "__main__":
    path_to_watch = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Verifica se o npx e markdownlint-cli estao acessiveis
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True, shell=os.name == 'nt')
    except Exception:
        print("[ERRO] 'npx' não encontrado no sistema. Por favor, instale o Node.js.")
        sys.exit(1)

    event_handler = MarkdownHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    
    print(f"Markdown Auto Fixer (Motor Oficial) ativo em: {Path(path_to_watch).absolute()}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
