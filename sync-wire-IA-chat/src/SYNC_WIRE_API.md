# SYNC_WIRE API — Referência Python

## sync_wire_client.py

### Classe `SyncWireClient`

```python
from scripts.sync_wire_client import SyncWireClient

client = SyncWireClient(agent_name: str)
```

#### `__init__(agent_name: str)`

Inicializa o cliente para um agente. Cria arquivos do protocolo se não existirem.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `agent_name` | str | Identificador do agente (`gemini_cli`, `antigravity`) |

---

#### `send(to: str, msg_type: str, payload: str, reply_to: str | None = None, thread_id: str | None = None) -> str`

Envia uma mensagem para outro agente.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `to` | str | — | Destinatário ou `broadcast` |
| `msg_type` | str | — | Tipo da mensagem (ver enum) |
| `payload` | str | — | Conteúdo |
| `reply_to` | str | `None` | UUID da mensagem sendo respondida |
| `thread_id` | str | `None` | UUID da thread (auto-gerado se omitido) |

**Retorno:** `str` — UUID da mensagem enviada.

**Exemplo:**
```python
msg_id = client.send(
    to="antigravity",
    msg_type="query",
    payload="Status da extração?"
)
```

---

#### `poll(timeout: int = 30) -> list[dict]`

Lê novas mensagens destinadas ao agente.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `timeout` | int | `30` | Segundos máximos de espera (polling) |

**Retorno:** `list[dict]` — Lista de mensagens JSON.

**Exemplo:**
```python
msgs = client.poll(timeout=10)
for msg in msgs:
    print(f"[{msg['from']}] {msg['payload']}")
```

---

#### `ack(message_id: str) -> str`

Envia uma confirmação de recebimento.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `message_id` | str | UUID da mensagem sendo confirmada |

**Retorno:** `str` — UUID do ACK.

**Exemplo:**
```python
client.ack("550e8400-e29b-41d4-a716-446655440000")
```

---

#### `heartbeat() -> str`

Envia um sinal de vida. Chamado automaticamente pelo monitor, mas pode ser usado manualmente.

**Retorno:** `str` — UUID do heartbeat.

---

#### `get_pending() -> dict`

Retorna mensagens pendentes de ACK enviadas por este agente.

**Retorno:** `dict` — Subconjunto de `SYNC_WIRE_STATE.json["pending"]`.

---

#### `get_agent_status(agent_name: str) -> dict`

Verifica se um agente está online com base no último heartbeat.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `agent_name` | str | Nome do agente a verificar |

**Retorno:** `dict` com campos `online` (bool), `last_seen` (str), `seconds_ago` (int).

**Exemplo:**
```python
status = client.get_agent_status("antigravity")
if not status["online"]:
    print("Antigravity offline por", status["seconds_ago"], "segundos")
```

---

## sync_wire_monitor.py

### Uso

```bash
python scripts/sync_wire_monitor.py --agent <nome> [--poll-interval <segundos>]
```

#### Argumentos

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `--agent` | — | Nome do agente local |
| `--poll-interval` | `2` | Intervalo de fallback polling (segundos) |
| `--heartbeat-interval` | `60` | Intervalo entre heartbeats (segundos) |
| `--timeout-check` | `60` | Intervalo de verificação de timeouts (segundos) |

#### Comportamento

1. Inicializa watchdog no arquivo `SYNC_WIRE.jsonl`.
2. Em caso de falha do watchdog, ativa polling de fallback.
3. Processa novas mensagens usando `SYNC_WIRE.idx`.
4. Emite notificações via trigger file.
5. Envia heartbeat periódico.
6. Verifica timeouts e reenvia se necessário.

---

## sync_wire_archiver.py

### Uso

```bash
python scripts/sync_wire_archiver.py [--max-messages 1000] [--max-days 7]
```

#### Argumentos

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| `--max-messages` | `1000` | Limite de mensagens antes da rotação |
| `--max-days` | `7` | Idade máxima das mensagens no arquivo ativo |
| `--dry-run` | `False` | Simula rotação sem executar |

---

## Constantes do Protocolo

```python
# sync_wire_client.py (valores padrão)
LOCK_TIMEOUT = 5.0          # segundos
HEARTBEAT_INTERVAL = 60     # segundos
TIMEOUT_DEFAULT = 300       # segundos para query/command
MAX_RETRIES = 3
TRIGGER_DIR = "."           # diretório dos arquivos trigger
ARCHIVE_MAX_MSG = 1000
ARCHIVE_MAX_DAYS = 7
```
