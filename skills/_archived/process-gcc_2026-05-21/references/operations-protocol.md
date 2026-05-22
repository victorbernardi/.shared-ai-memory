---
description: >-
  Protocolo detalhado de operações do GCC. Consultar quando houver
  dúvida sobre o comportamento esperado de cada comando.
metadata:
  tags: [gcc, operations, protocol, reference]
---

# Protocolo de Operações GCC

## Fluxo Visual

```
[Tarefa arriscada identificada]
         │
         ▼
    gcc branch "nome" --reason "hipótese"
         │
         ├─── Snapshot salvo (ACTIVE_CONTEXT + MEMORY)
         ├─── Indicator injetado no MEMORY.md
         └─── Experimentação inicia
                    │
         ┌─────────┴──────────┐
         │                    │
    [FALHOU]             [FUNCIONOU]
         │                    │
         ▼                    ▼
  gcc discard "nome"    Preencher learnings.md
         │                    │
         ├── Restaura state   ▼
         ├── Briefing      gcc merge "nome"
         └── NULO+INVÁLIDO    │
                              ├── Learnings → ACTIVE_CONTEXT
                              └── Branch arquivado
```

## Estrutura de Diretórios

```
~/.shared-ai-memory/context-agent/gcc/
├── gcc.json                    # Estado global
├── branches/
│   ├── <nome-branch>/
│   │   ├── ACTIVE_CONTEXT.md   # Snapshot
│   │   ├── MEMORY.md           # Snapshot
│   │   ├── metadata.json       # Timestamp, motivo, status
│   │   └── learnings.md        # Preenchido antes do merge
│   ├── _discarded/             # Branches descartados (arquivo)
│   └── _merged/                # Branches mergeados (arquivo)
└── logs/
    └── gcc-YYYY-MM-DD.log      # Audit trail diário
```

## Formato: metadata.json

```json
{
  "name": "tese-api-v3",
  "reason": "Testar se a API v3 resolve o rate limit",
  "created_at": "2026-05-09T02:30:00",
  "status": "active",
  "source_files": {
    "ACTIVE_CONTEXT.md": "~/.shared-ai-memory/context-agent/ACTIVE_CONTEXT.md",
    "MEMORY.md": "~/.shared-ai-memory/memory/MEMORY.md"
  }
}
```

## Formato: gcc.json (Estado Global)

```json
{
  "active_branch": "tese-api-v3",
  "history": [
    {
      "operation": "branch",
      "name": "tese-api-v3",
      "reason": "Testar se a API v3 resolve o rate limit",
      "timestamp": "2026-05-09T02:30:00"
    }
  ]
}
```

## Formato: learnings.md (Template)

```markdown
# Learnings: <nome-do-branch>

> Preencha ANTES de executar `gcc merge`.
> O merge será RECUSADO se este arquivo estiver vazio.

## O que funcionou e por quê


## Decisões técnicas validadas


## Padrões descobertos

```

## Regras de Integridade

1. **Máximo 1 branch ativo:** Branches aninhados são PROIBIDOS
2. **Learnings obrigatório:** Merge recusa se learnings.md estiver vazio
3. **Backup automático:** Antes de restaurar, o estado atual é salvo em `.pre-restore`
4. **Audit trail:** Toda operação é logada com timestamp
5. **Idempotência:** Criar branch com nome duplicado é erro (não sobrescreve)

## Testes Manuais (sem sandbox)

Para testar, crie cópias dos arquivos originais antes:

```bash
# Backup
copy "%USERPROFILE%\.shared-ai-memory\context-agent\ACTIVE_CONTEXT.md" "%USERPROFILE%\.shared-ai-memory\context-agent\ACTIVE_CONTEXT.md.backup"
copy "%USERPROFILE%\.shared-ai-memory\memory\MEMORY.md" "%USERPROFILE%\.shared-ai-memory\memory\MEMORY.md.backup"

# Testar
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" branch "teste-1" --reason "Teste inicial"
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" status
python "%USERPROFILE%\.shared-ai-memory\skills\process-gcc\scripts\gcc_controller.py" discard "teste-1"

# Restaurar originais se necessário
copy "%USERPROFILE%\.shared-ai-memory\context-agent\ACTIVE_CONTEXT.md.backup" "%USERPROFILE%\.shared-ai-memory\context-agent\ACTIVE_CONTEXT.md"
copy "%USERPROFILE%\.shared-ai-memory\memory\MEMORY.md.backup" "%USERPROFILE%\.shared-ai-memory\memory\MEMORY.md"
```
