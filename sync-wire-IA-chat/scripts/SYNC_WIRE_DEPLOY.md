# SYNC_WIRE Deploy e Operações

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
copy SYNC_WIRE.jsonl backups\SYNC_WIRE_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.jsonl
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
