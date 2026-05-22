# SYNC_WIRE Protocol v2.0

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
