# ⚡ SKILL: SYNC_WIRE — Comunicação Inter-Agente v2.0

## Propósito
Permitir a troca de mensagens estruturadas, comandos e sincronização de contexto em tempo real entre o **Gemini CLI (Engenheiro)** e o **Antigravity (Cientista)** operando no mesmo host.

## Quando usar
- Quando houver **Assimetria de Contexto** (um agente não sabe o que o outro fez).
- Para **Delegar Tarefas** entre as personas (ex: Engenheiro pede validação de dados ao Cientista).
- Para **Sincronizar Credenciais** ou estados transitórios.
- Quando o usuário solicitar "conversa direta" ou "chat entre as IAs".

## 🛠️ Ferramentas Necessárias
- Python 3.10+
- Biblioteca `filelock` (`pip install filelock`)
- Scripts em `scripts/sync_wire_*.py`

## Protocolo de Operação (Fluxo v2.0)

### 1. Inicialização de Sessão
Sempre verifique se os arquivos de transporte existem. Se não, inicialize via script:
```bash
python scripts/sync_wire_client.py --init
```

### 2. Envio de Mensagem
**NUNCA** escreva diretamente no arquivo `SYNC_WIRE.jsonl`. Utilize sempre a API Python para garantir o travamento (lock) e integridade:

```python
from scripts.sync_wire_client import SyncWireClient
client = SyncWireClient("seu_nome_de_agente")
client.send(to="destinatario", msg_type="query", payload="Sua mensagem aqui")
```

**Tipos de Mensagem (Enum `type`):**
- `ping`: Teste de conexão.
- `query`: Pergunta que exige resposta.
- `command`: Instrução de ação direta.
- `response`: Resposta a uma query/command anterior.
- `ack`: Confirmação de recebimento.

### 3. Escuta e Resposta
O monitor `scripts/sync_wire_monitor.py` deve estar rodando em background. 
- **SEMPRE** verifique o log do monitor antes de assumir que não há mensagens.
- **SEMPRE** envie um `ack(msg_id)` ao processar uma mensagem recebida.

### 4. Sincronização de Estado
- O SYNC_WIRE é para diálogos **transitórios**.
- **SEMPRE** promova decisões permanentes ou mudanças de estado global para o `ACTIVE_CONTEXT.md` ao final da interação.

## Regras de Ouro (Stout Standard)

1. **SEMPRE** use `filelock` (via SyncWireClient) para evitar corrupção.
2. **NUNCA** edite mensagens passadas. O protocolo é **Append-Only**.
3. **SEMPRE** inclua o `thread_id` se a mensagem for parte de uma conversa contínua.
4. **SEMPRE** mantenha o heartbeat ativo (60s) se estiver em uma tarefa longa.

## Referências
- Especificação Completa: `references/v2_protocol.md`
- Guia de API: `references/v2_api.md`
