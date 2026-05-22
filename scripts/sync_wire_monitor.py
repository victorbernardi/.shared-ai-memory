import os
import time
import sys
from datetime import datetime

class SyncWireMonitor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.should_exit = False

    def watch(self):
        print(f"[*] Monitorando {self.file_path} para novas mensagens...")
        while True:
            try:
                if not os.path.exists(self.file_path):
                    time.sleep(1)
                    continue

                current_size = os.path.getsize(self.file_path)
                if current_size > self.last_size:
                    with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(self.last_size)
                        new_content = f.read()
                        self.process_new_content(new_content)
                    self.last_size = current_size
                elif current_size < self.last_size:
                    # Arquivo foi truncado ou resetado
                    self.last_size = current_size
                
                if self.should_exit:
                    print("\n[SYNC_WIRE] CLOSE_SESSION detectado. Encerrando monitor e limpando canal.")
                    template = (
                        "# SYNC_WIRE Protocol v1.0\n"
                        "Este arquivo é o canal de comunicação em tempo real entre o Gemini CLI (Engenheiro) e o Antigravity (Cientista).\n"
                        "Apenas adicione novas mensagens ao final do arquivo seguindo o padrão de cabeçalho abaixo.\n\n"
                        "---\n"
                    )
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        f.write(template)
                    break
                
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n[!] Monitoramento interrompido.")
                break
            except Exception as e:
                print(f"[!] Erro no monitor: {e}")
                time.sleep(5)

    def process_new_content(self, content):
        lines = content.strip().split('\n')
        for line in lines:
            if "CLOSE_SESSION" in line:
                self.should_exit = True
            
            if line.startswith('### ['):
                print(f"\n[SYNC_WIRE] {line}")
            elif line.strip() and not line.startswith('---'):
                print(f"  > {line.strip()}")

if __name__ == "__main__":
    path = os.path.join(os.getcwd(), "SYNC_WIRE.md")
    monitor = SyncWireMonitor(path)
    monitor.watch()
