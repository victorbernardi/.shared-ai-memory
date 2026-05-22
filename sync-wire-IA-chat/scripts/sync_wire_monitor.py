import os
import time
import argparse
import json
from datetime import datetime, timezone
from sync_wire_client import SyncWireClient, HEARTBEAT_INTERVAL

class SyncWireMonitor:
    def __init__(self, agent_name, poll_interval=2):
        self.client = SyncWireClient(agent_name)
        self.agent_name = agent_name
        self.poll_interval = poll_interval
        self.last_heartbeat = 0
        self.last_timeout_check = 0

    def run(self):
        print(f"[*] Iniciando monitor SYNC_WIRE v2.0 para o agente: {self.agent_name}")
        print(f"[*] Caminho: {self.client.jsonl_path}")
        
        while True:
            try:
                # 1. Poll para novas mensagens
                new_msgs = self.client._read_new_messages()
                if new_msgs:
                    self._process_messages(new_msgs)
                    self._regenerate_md_view()

                # 2. Heartbeat periódico
                now = time.time()
                if now - self.last_heartbeat > HEARTBEAT_INTERVAL:
                    self.client.heartbeat()
                    self.last_heartbeat = now
                    print(f"[DEBUG] Heartbeat enviado em {datetime.now().strftime('%H:%M:%S')}")

                # 3. Verificação de timeout (placeholder para v2.0 completa)
                if now - self.last_timeout_check > 60:
                    self._check_timeouts()
                    self.last_timeout_check = now

                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                print("\n[!] Monitoramento encerrado pelo usuário.")
                break
            except Exception as e:
                print(f"[!] Erro no monitor: {e}")
                time.sleep(5)

    def _process_messages(self, messages):
        for msg in messages:
            ts_short = datetime.fromisoformat(msg["ts"]).strftime("%H:%M:%S")
            print(f"\n[SYNC_WIRE] [{ts_short}] {msg['from']} -> {msg['to']} ({msg['type']})")
            print(f"  > {msg['payload']}")

    def _check_timeouts(self):
        # Implementação básica de detecção
        pass

    def _regenerate_md_view(self):
        """Gera uma visão Markdown amigável para humanos."""
        messages = []
        try:
            if not os.path.exists(self.client.jsonl_path):
                return
                
            with open(self.client.jsonl_path, 'r', encoding='utf-8') as f:
                # Pega as últimas 50 mensagens
                lines = f.readlines()[-50:]
                for line in lines:
                    try:
                        messages.append(json.loads(line))
                    except: pass

            with open(self.client.md_path, 'w', encoding='utf-8') as f:
                f.write(f"# SYNC_WIRE Live Log (View v2.0)\n")
                f.write(f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                for msg in messages:
                    ts = datetime.fromisoformat(msg["ts"]).strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"### [{ts}] [{msg['from']}]\n")
                    f.write(f"**Tipo:** `{msg['type']}` | **Para:** `{msg['to']}`\n\n")
                    f.write(f"{msg['payload']}\n\n")
                    f.write("---\n\n")
        except Exception as e:
            print(f"[!] Falha ao regenerar MD view: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor SYNC_WIRE v2.0")
    parser.add_argument("--agent", required=True, help="Nome do agente local")
    parser.add_argument("--poll", type=int, default=2, help="Intervalo de polling (segundos)")
    
    args = parser.parse_args()
    
    monitor = SyncWireMonitor(args.agent, args.poll)
    monitor.run()
