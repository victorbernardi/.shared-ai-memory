# SYNC_WIRE Protocol v2.0 — Especificação

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
