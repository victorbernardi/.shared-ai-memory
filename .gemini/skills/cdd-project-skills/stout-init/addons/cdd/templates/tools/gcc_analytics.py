import os
import re
import sys
import io
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Reconfigura o output para UTF-8 (Corta o mal pela raiz no Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class GCCAnalytics:
    """
    Engine analítica para processar checkpoints do Git-Context-Controller (GCC).
    Extrai métricas de performance e ativação de regras/skills.
    """
    def __init__(self, branches_dir: str = '.GCC/branches'):
        self.branches_dir = Path(branches_dir)
        self.checkpoints = []

    def parse_all(self):
        """Lê e processa todos os arquivos markdown no diretório de branches."""
        if not self.branches_dir.exists():
            print(f"[-] Erro: Diretorio {self.branches_dir} nao encontrado.")
            return

        self.checkpoints = []
        for file_path in self.branches_dir.glob('checkpoint_*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    data = self._parse_checkpoint(content)
                    if data:
                        data['file'] = file_path.name
                        self.checkpoints.append(data)
            except Exception as e:
                print(f"[-] Erro ao processar {file_path.name}: {e}")
        
        # Ordena por data (mais recente primeiro)
        self.checkpoints.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    def _parse_checkpoint(self, content: str) -> dict:
        """Extrai campos-chave do markdown de checkpoint via Regex."""
        data = {}
        
        # 1. Action (Título)
        action_match = re.search(r'# 📍 Checkpoint: (.*)', content)
        data['action'] = action_match.group(1).strip() if action_match else "N/A"

        # 2. Timestamp
        date_match = re.search(r'- \*\*Data:\*\* (.*)', content)
        data['timestamp'] = date_match.group(1).strip() if date_match else "N/A"

        # 3. Status
        status_match = re.search(r'- \*\*Status:\*\* (.*)', content)
        data['status'] = status_match.group(1).strip() if status_match else "N/A"

        # 4. Intent (extraído do bloco Situation JSON)
        situation_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if situation_match:
            try:
                sit_json = json.loads(situation_match.group(1))
                data['intent'] = sit_json.get('intent', 'N/A')
            except:
                data['intent'] = 'PARSE_ERROR'
        else:
            data['intent'] = 'N/A'

        return data

    def generate_report(self):
        """Exibe um relatório resumido de métricas no terminal."""
        if not self.checkpoints:
            print("[!] Nenhum checkpoint encontrado para analise.")
            return

        total = len(self.checkpoints)
        statuses = Counter([c['status'] for c in self.checkpoints])
        actions = Counter([c['action'] for c in self.checkpoints])
        intents = Counter([c['intent'] for c in self.checkpoints])

        print("\n" + "="*50)
        print(" 📊 RELATÓRIO TÁTICO: GCC ANALYTICS ENGINE")
        print("="*50)
        print(f"Total de Checkpoints: {total}")
        print(f"Última Atividade:   {self.checkpoints[0]['timestamp']}")
        
        print("\n--- [STATUS] ---")
        for status, count in statuses.items():
            pct = (count/total)*100
            icon = "✅" if status == "SUCCESS" else "⚠️"
            print(f"{icon} {status:<10}: {count} ({pct:.1f}%)")

        print("\n--- [DISTRIBUIÇÃO POR AÇÃO] ---")
        for action, count in actions.most_common(5):
            print(f"-> {action:<40}: {count}")

        print("\n--- [TOP INTENTS DO USUÁRIO] ---")
        for intent, count in intents.most_common(5):
            print(f"-> {intent:<40}: {count}")
        print("="*50 + "\n")

    def run_telemetry_ui(self):
        """Simula um painel tático monitorando os últimos 10 eventos."""
        self.parse_all()
        print("\n" + "!"*10 + " PAINEL TÁTICO: TELEMETRY UI (Real-Time View) " + "!"*10)
        print(f"{'DATA':<25} {'STATUS':<10} {'AÇÃO':<40}")
        print("-" * 80)
        
        for cp in self.checkpoints[:10]:
            ts = cp['timestamp'].split('.')[0].replace('T', ' ')
            st = cp['status']
            ac = cp['action'][:38] + "..." if len(cp['action']) > 38 else cp['action']
            print(f"{ts:<25} {st:<10} {ac:<40}")
        print("-" * 80)

if __name__ == "__main__":
    engine = GCCAnalytics()
    engine.parse_all()
    engine.generate_report()
    engine.run_telemetry_ui()
