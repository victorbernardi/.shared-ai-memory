import os
import json
import uuid
import time
import hashlib
from datetime import datetime, timezone
from filelock import FileLock

# Configurações padrão
LOCK_TIMEOUT = 5.0
HEARTBEAT_INTERVAL = 60
TIMEOUT_DEFAULT = 300
MAX_RETRIES = 3
ARCHIVE_MAX_MSG = 1000
ARCHIVE_MAX_DAYS = 7

class SyncWireClient:
    def __init__(self, agent_name: str, base_path: str = "."):
        self.agent_name = agent_name
        self.base_path = base_path
        self.jsonl_path = os.path.join(base_path, "SYNC_WIRE.jsonl")
        self.idx_path = os.path.join(base_path, "SYNC_WIRE.idx")
        self.state_path = os.path.join(base_path, "SYNC_WIRE_STATE.json")
        self.md_path = os.path.join(base_path, "SYNC_WIRE.md")
        self.lock_path = self.jsonl_path + ".lock"
        
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Inicializa os arquivos do protocolo se não existirem."""
        for path in [self.jsonl_path, self.idx_path]:
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    pass
        
        if not os.path.exists(self.state_path):
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump({"pending": {}, "acknowledged": [], "last_seen": {}}, f)

    def _get_timestamp(self):
        return datetime.now(timezone.utc).isoformat()

    def _generate_checksum(self, payload, ts):
        data = f"{payload}{ts}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def send(self, to: str, msg_type: str, payload: str, reply_to: str = None, thread_id: str = None) -> str:
        """Envia uma mensagem para outro agente."""
        msg_id = str(uuid.uuid4())
        ts = self._get_timestamp()
        
        message = {
            "id": msg_id,
            "ts": ts,
            "from": self.agent_name,
            "to": to,
            "type": msg_type,
            "payload": payload,
            "reply_to": reply_to,
            "thread_id": thread_id or msg_id,
            "status": "pending",
            "checksum": self._generate_checksum(payload, ts),
            "resent": False
        }

        lock = FileLock(self.lock_path, timeout=LOCK_TIMEOUT)
        with lock:
            # Escreve no JSONL
            with open(self.jsonl_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message) + '\n')
                f.flush()
                os.fsync(f.fileno())
            
            # Atualiza STATE se for query ou command
            if msg_type in ["query", "command"]:
                self._update_state_pending(msg_id, ts)
            
            # Atualiza last_seen
            self._update_last_seen()

        return msg_id

    def _update_state_pending(self, msg_id, ts):
        with open(self.state_path, 'r+', encoding='utf-8') as f:
            state = json.load(f)
            state["pending"][msg_id] = {
                "ts": ts,
                "retries": 0,
                "timeout_sec": TIMEOUT_DEFAULT
            }
            f.seek(0)
            json.dump(state, f, indent=2)
            f.truncate()

    def _update_last_seen(self):
        with open(self.state_path, 'r+', encoding='utf-8') as f:
            state = json.load(f)
            state["last_seen"][self.agent_name] = self._get_timestamp()
            f.seek(0)
            json.dump(state, f, indent=2)
            f.truncate()

    def ack(self, message_id: str) -> str:
        """Confirma recebimento de uma mensagem."""
        return self.send(to="broadcast", msg_type="ack", payload=f"ACK for {message_id}", reply_to=message_id)

    def heartbeat(self) -> str:
        """Envia um sinal de vida."""
        return self.send(to="broadcast", msg_type="heartbeat", payload="I am alive")

    def poll(self, timeout: int = 30) -> list[dict]:
        """Lê novas mensagens destinadas ao agente."""
        start_time = time.time()
        messages = []
        
        # Simples polling para esta implementação inicial
        # Em produção, usaria o .idx para ler apenas o delta
        while time.time() - start_time < timeout:
            new_msgs = self._read_new_messages()
            if new_msgs:
                return new_msgs
            time.sleep(1)
        return []

    def _read_new_messages(self) -> list[dict]:
        messages = []
        last_offset = 0
        
        # Lê offset do índice
        if os.path.exists(self.idx_path) and os.path.getsize(self.idx_path) > 0:
            try:
                with open(self.idx_path, 'r') as f:
                    idx = json.load(f)
                    last_offset = idx.get("last_offset", 0)
            except: pass

        if os.path.getsize(self.jsonl_path) > last_offset:
            with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                f.seek(last_offset)
                for line in f:
                    try:
                        msg = json.loads(line)
                        if msg["to"] in [self.agent_name, "broadcast"] and msg["from"] != self.agent_name:
                            messages.append(msg)
                    except: pass
                new_offset = f.tell()
            
            # Atualiza índice
            with open(self.idx_path, 'w') as f:
                json.dump({"last_offset": new_offset}, f)
        
        return messages

    def get_agent_status(self, agent_name: str) -> dict:
        """Verifica se um agente está online."""
        if not os.path.exists(self.state_path):
            return {"online": False, "last_seen": None, "seconds_ago": -1}
        
        with open(self.state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
            last_ts_str = state["last_seen"].get(agent_name)
            if not last_ts_str:
                return {"online": False, "last_seen": None, "seconds_ago": -1}
            
            last_ts = datetime.fromisoformat(last_ts_str)
            now = datetime.now(timezone.utc)
            diff = (now - last_ts).total_seconds()
            
            return {
                "online": diff < (HEARTBEAT_INTERVAL * 2),
                "last_seen": last_ts_str,
                "seconds_ago": int(diff)
            }
