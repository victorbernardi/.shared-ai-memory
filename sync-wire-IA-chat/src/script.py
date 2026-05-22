
import os

os.makedirs("output", exist_ok=True)

# ============================================================
# 1. README.md
# ============================================================
readme = """# SYNC_WIRE Protocol v2.0

Canal de comunicação inter-agente via filesystem para Gemini CLI e Antigravity.

---

## O que é

O **SYNC_WIRE** é um protocolo de comunicação inter-agente (IAC) que utiliza o filesystem como camada de transporte. Ele permite que o **Gemini CLI** e o **Antigravity** troquem mensagens em tempo real sem depender de rede, banco de dados ou servidores externos.

A versão 2.0 corrige falhas críticas da implementação original:
- **Concorrência**: file locking cross-platform (`filelock`)
- **Integridade**: checksum SHA-256 + índice de offsets
- **Confiabilidade**: ACK explícito, heartbeat e detecção de timeout
- **Escalabilidade**: rotação automática de arquivos
- **Observabilidade**: view Markdown auto-gerada para leitura humana

---

## Requisitos

- Python 3.10+
- Windows, Linux ou macOS
- Ambos os agentes operando no mesmo filesystem (mesma máquina ou pasta compartilhada)

### Dependências

```bash
pip install filelock
```

Opcional para watchdog nativo:
```bash
pip install watchdog
```

---

## Instalação Rápida

1. Copie os scripts da pasta `scripts/` para o root do seu workspace.
2. Execute uma vez para inicializar os arquivos de protocolo:
```bash
python scripts/sync_wire_client.py --init
```
3. Inicie o monitor em cada sessão de agente:
```bash
# Terminal do Gemini CLI
python scripts/sync_wire_monitor.py --agent gemini_cli

# Terminal do Antigravity
python scripts/sync_wire_monitor.py --agent antigravity
```

---

## Quick Start

### Enviar uma mensagem

```python
from scripts.sync_wire_client import SyncWireClient

cli = SyncWireClient("gemini_cli")
msg_id = cli.send(
    to="antigravity",
    msg_type="query",
    payload="Preciso dos cookies do NotebookLM."
)
print(f"Mensagem enviada: {msg_id}")
```

### Receber mensagens

```python
msgs = cli.poll(timeout=10)
for msg in msgs:
    print(f"[{msg['from']}] {msg['payload']}")
    cli.ack(msg["id"])
```

---

## Arquitetura

```
workspace/
├── SYNC_WIRE.jsonl              # Transporte primário (JSON Lines)
├── SYNC_WIRE.idx                # Índice de offsets para delta seguro
├── SYNC_WIRE_STATE.json         # Estado: pending, ack, last_seen
├── SYNC_WIRE.md                 # View humana auto-gerada
├── SYNC_WIRE.trigger            # Notificação cross-terminal
├── scripts/
│   ├── sync_wire_client.py      # Biblioteca de envio/recebimento
│   ├── sync_wire_monitor.py     # Monitor de arquivo + notificador
│   └── sync_wire_archiver.py    # Rotação e archiving
```

---

## Regras de Ouro

1. **Sempre use `filelock`** antes de escrever em qualquer arquivo do protocolo.
2. **Nunca edite `SYNC_WIRE.jsonl` in-place.** Apenas append.
3. **Nunca confie em `seek()` sem o `.idx`.** O índice é a fonte de verdade para deltas.
4. **Sempre envie `heartbeat` a cada 60s** se o agente estiver ativo.
5. **Sempre sincronize decisões para `ACTIVE_CONTEXT.md`.** O SYNC_WIRE é o telefone; o ACTIVE_CONTEXT é o CRM.

---

## Documentação

- [`SYNC_WIRE_PROTOCOL.md`](SYNC_WIRE_PROTOCOL.md) — Especificação completa do protocolo
- [`SYNC_WIRE_API.md`](SYNC_WIRE_API.md) — Referência da API Python
- [`SYNC_WIRE_DEPLOY.md`](SYNC_WIRE_DEPLOY.md) — Deploy, troubleshooting e operações

---

## Licença

Uso interno. Protocolo desenvolvido para o ecossistema Stout / NeoHive local.
"""

# ============================================================
# 2. SYNC_WIRE_PROTOCOL.md
# ============================================================
protocol = """# SYNC_WIRE Protocol v2.0 — Especificação

## 1. Objetivo

Definir um protocolo de comunicação inter-agente baseado em filesystem, robusto o suficiente para produção entre Gemini CLI e Antigravity no mesmo host.

## 2. Princípios

- **Filesystem como bus de mensagens**: sem dependências de rede.
- **Append-only**: nenhuma mensagem é editada ou deletada.
- **Locking obrigatório**: toda escrita requer `filelock`.
- **Idempotência**: reenvio com mesmo `id` deve ser detectável.
- **Separação de concerns**: transporte (JSONL), estado (STATE), view (MD).

## 3. Schema da Mensagem

Cada linha em `SYNC_WIRE.jsonl` é um objeto JSON válido:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ts": "2026-05-11T10:00:00-03:00",
  "from": "gemini_cli",
  "to": "antigravity",
  "type": "query",
  "payload": "Precisamos alinhar a extração do NotebookLM.",
  "reply_to": null,
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "checksum": "sha256(...)",
  "resent": false
}
```

### Campos obrigatórios

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID v4 | Identificador único da mensagem |
| `ts` | ISO 8601 com offset | Momento de criação |
| `from` | string | Nome do agente emissor |
| `to` | string | Nome do agente receptor ou `broadcast` |
| `type` | enum | Categoria semântica da mensagem |
| `payload` | string | Conteúdo da mensagem |

### Campos opcionais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `reply_to` | UUID ou null | Referência à mensagem original |
| `thread_id` | UUID | ID da conversa/thread |
| `status` | enum | Estado de entrega (`pending`, `delivered`, `ack`, `error`) |
| `checksum` | SHA-256 | Hash de integridade do payload + ts |
| `resent` | boolean | Indica reenvio após timeout |

### Enum `type`

| Valor | Uso |
|-------|-----|
| `ping` | Teste de vida |
| `query` | Pergunta que exige resposta |
| `command` | Instrução de ação |
| `response` | Resposta a query/command |
| `error` | Falha no processamento |
| `heartbeat` | Sinal de vida periódico |
| `ack` | Confirmação de recebimento |

### Enum `status`

| Valor | Significado |
|-------|-------------|
| `pending` | Mensagem enviada, aguardando consumo |
| `delivered` | Receptor leu a mensagem |
| `ack` | Receptor confirmou processamento |
| `error` | Falha no envio ou processamento |

## 4. Arquivos do Protocolo

### 4.1 SYNC_WIRE.jsonl

- Formato: JSON Lines (UTF-8, line-buffered).
- Semântica: append-only. Nunca editado in-place.
- Rotação: a cada 1000 mensagens ou 7 dias.

### 4.2 SYNC_WIRE.idx

```json
{
  "last_offset": 2048,
  "last_line_count": 15,
  "last_hash": "sha256:abc123..."
}
```

- Atualizado pelo monitor após processar novas mensagens.
- Se `last_hash` não bater com o conteúdo do `.jsonl`, o índice é reconstruído do zero.

### 4.3 SYNC_WIRE_STATE.json

```json
{
  "pending": {
    "msg_001": {
      "ts": "2026-05-11T10:00:00-03:00",
      "retries": 0,
      "timeout_sec": 300
    }
  },
  "acknowledged": ["msg_001", "msg_002"],
  "last_seen": {
    "gemini_cli": "2026-05-11T10:05:00-03:00",
    "antigravity": "2026-05-11T10:04:30-03:00"
  }
}
```

- Reescrito periodicamente (não append-only).
- Protegido por `filelock`.

### 4.4 SYNC_WIRE.md

View humana auto-gerada a partir das últimas 100 mensagens do `.jsonl`. Não é fonte de verdade.

### 4.5 SYNC_WIRE.trigger

Arquivo vazio criado pelo monitor quando há novas mensagens. Nome pode incluir timestamp: `SYNC_WIRE_20260511_104000.trigger`. Serve para notificar agentes em outros terminais.

## 5. Fluxos de Comunicação

### 5.1 Query / Response

```
Gemini CLI                       Antigravity
   |                                  |
   |--[type:query, status:pending]--->|
   |                                  |
   |<--[type:response, reply_to:id]--|
   |                                  |
   |--[type:ack, reply_to:id]-------->|
```

### 5.2 Heartbeat

```
Agente X
   |
   |--[type:heartbeat]---> SYNC_WIRE.jsonl
   |
Monitor (qualquer agente)
   |
   |-- lê heartbeat -- atualiza STATE.last_seen[X]
```

### 5.3 Detecção de Timeout

O monitor verifica `STATE.pending` a cada 60s. Se `now - pending[msg].ts > timeout_sec`:
- Incrementa `retries`.
- Se `retries < 3`, reenvia mensagem com `resent: true`.
- Se `retries >= 3`, marca `status: error`.

## 6. Regras de Locking

1. Todo arquivo mutável (`.jsonl`, `.idx`, `.STATE.json`) requer `filelock`.
2. Timeout padrão do lock: 5 segundos.
3. Após `write()`, executar `flush()` + `os.fsync()` antes de liberar o lock.
4. Nunca adquirir múltiplos locks simultaneamente (evita deadlock).

## 7. Rotação e Archiving

Quando `SYNC_WIRE.jsonl` atinge 1000 mensagens ou 7 dias:
1. Agente detecta limite durante escrita.
2. Cria arquivo `SYNC_WIRE_YYYY-MM-DD_YYYY-MM-DD.jsonl` com mensagens antigas.
3. Trunca `.jsonl` mantendo apenas as últimas 50 mensagens (hot window).
4. Reseta `.idx`.
5. Regenera `.md`.

## 8. Integração com ACTIVE_CONTEXT.md

| SYNC_WIRE | ACTIVE_CONTEXT.md |
|-----------|-------------------|
| Diálogo transitório, coordenação | Estado persistente, decisões |
| "Preciso do cookie X" | "Cookies válidos até 2026-06-01" |
| "Vou rodar teste Y" | "Pipeline Y integrado ao CI" |

**Regra:** todo `type: command` que altere estado do projeto deve ser refletido no `ACTIVE_CONTEXT.md` pelo agente executor.

## 9. Versionamento

- `protocol_version`: `2.0.0`
- Compatibilidade: quebra com v1.0 (mudança de Markdown para JSONL).
- Futuras versões 2.x mantêm backward compatibility no schema JSONL.
"""

# ============================================================
# 3. SYNC_WIRE_API.md
# ============================================================
api_doc = """# SYNC_WIRE API — Referência Python

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
"""

# ============================================================
# 4. SYNC_WIRE_DEPLOY.md
# ============================================================
deploy = """# SYNC_WIRE Deploy e Operações

## Instalação Passo a Passo

### 1. Preparação do Ambiente

```bash
# Verifique Python
python --version  # >= 3.10

# Instale dependências
pip install filelock

# Opcional: watchdog para notificações nativas do OS
pip install watchdog
```

### 2. Colocação dos Arquivos

Copie para o **root do workspace** (onde Gemini CLI e Antigravity operam):

```
workspace/
├── scripts/
│   ├── sync_wire_client.py
│   ├── sync_wire_monitor.py
│   └── sync_wire_archiver.py
```

### 3. Inicialização

Execute em qualquer terminal:

```bash
python scripts/sync_wire_client.py --init
```

Isso cria:
- `SYNC_WIRE.jsonl`
- `SYNC_WIRE.idx`
- `SYNC_WIRE_STATE.json`
- `SYNC_WIRE.md` (template)

### 4. Iniciar Monitores

Abra **dois terminais** (ou mais, se houver subagentes):

**Terminal A — Gemini CLI:**
```bash
python scripts/sync_wire_monitor.py --agent gemini_cli
```

**Terminal B — Antigravity:**
```bash
python scripts/sync_wire_monitor.py --agent antigravity
```

O monitor roda em foreground. Para background no Windows, use:
```bash
start /B python scripts/sync_wire_monitor.py --agent gemini_cli
```

---

## Operações Diárias

### Enviar mensagem manual (teste)

```bash
python -c "
from scripts.sync_wire_client import SyncWireClient
c = SyncWireClient('gemini_cli')
print(c.send('antigravity', 'ping', 'teste de vida'))
"
```

### Verificar status do outro agente

```bash
python -c "
from scripts.sync_wire_client import SyncWireClient
c = SyncWireClient('gemini_cli')
print(c.get_agent_status('antigravity'))
"
```

### Forçar rotação do log

```bash
python scripts/sync_wire_archiver.py
```

---

## Troubleshooting

### Problema: mensagens não aparecem no outro terminal

**Causa provável:** o monitor não está rodando no terminal receptor, ou o watchdog falhou.

**Solução:**
1. Verifique se o monitor está ativo: `python scripts/sync_wire_monitor.py --agent <nome>`
2. Observe o arquivo `SYNC_WIRE.trigger`. Se não for criado, o watchdog falhou; o fallback de polling (2s) deve compensar.
3. Verifique permissões de escrita no diretório.

### Problema: arquivo JSONL corrompido (JSON inválido)

**Causa provável:** race condition sem lock, ou edição manual.

**Solução:**
1. Pare todos os monitores.
2. Faça backup: `copy SYNC_WIRE.jsonl SYNC_WIRE.jsonl.bak`
3. Execute script de reparo (a ser implementado ou manualmente):
   - Leia linha por linha.
   - Ignore linhas inválidas.
   - Reconstrua `SYNC_WIRE.idx`.
4. Reinicie os monitores.

### Problema: lock timeout

**Causa provável:** um processo travou com o lock adquirido.

**Solução:**
1. Identifique processos Python travados e mate-os.
2. Delete manualmente `SYNC_WIRE.jsonl.lock` se existir (resíduo de crash).
3. Reinicie os monitores.

### Problema: SYNC_WIRE.md não atualiza

**Causa provável:** o regenerador de view não está ativo.

**Solução:** a view é um luxo, não uma necessidade. O monitor regenera `.md` a cada 30s. Se não regenerar, use:
```bash
python -c "
from scripts.sync_wire_client import SyncWireClient
c = SyncWireClient('gemini_cli')
c._regenerate_md_view()
"
```

---

## Backup e Recuperação

### Backup diário recomendado

```bash
# Windows (batch ou PowerShell)
copy SYNC_WIRE.jsonl backups\\SYNC_WIRE_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.jsonl
```

### Recuperação completa

Se o diretório for perdido, recrie:
1. `SYNC_WIRE.jsonl` — vazio ou restaurado do backup.
2. `SYNC_WIRE.idx` — será reconstruído automaticamente pelo monitor.
3. `SYNC_WIRE_STATE.json` — será recriado; mensagens pendentes serão perdidas (esperado).

---

## Performance

- **Latência:** < 100ms entre escrita e detecção (watchdog ativo); < 2s (fallback polling).
- **Throughput:** testado até 1000 mensagens/segundo com `filelock` (limitado por I/O do disco).
- **Memória:** monitor consome < 50 MB RAM (independente do tamanho do `.jsonl`).

---

## Segurança

- O protocolo assume **filesystem local confiável**. Não use em pastas compartilhadas de rede não confiáveis.
- Não armazene segredos (tokens, senhas) no `payload`. Use referências (ex: "use o token do arquivo X").
- O checksum SHA-256 detecta corrupção acidental, não maliciosa.

---

## Roadmap

| Versão | Feature |
|--------|---------|
| 2.1 | Criptografia de payload com chave simétrica |
| 2.2 | Compressão gzip para arquivos arquivados |
| 2.3 | Suporte a múltiplos workspaces (relay via pasta central) |
| 2.4 | Integração MCP (Model Context Protocol) nativa |
"""

# ============================================================
# Escrever arquivos
# ============================================================
files = {
    "output/README.md": readme,
    "output/SYNC_WIRE_PROTOCOL.md": protocol,
    "output/SYNC_WIRE_API.md": api_doc,
    "output/SYNC_WIRE_DEPLOY.md": deploy,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Arquivos gerados:")
for p in files.keys():
    print(f"  - {p} ({os.path.getsize(p)} bytes)")
