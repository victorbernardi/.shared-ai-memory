# Design: Canary Deployment Universal — Ecossistema Antigravity

**Data:** 2026-04-17  
**Escopo:** Fase 1 — file-based (Antigravity, Stout, Inova, novos projetos)  
**Fase 2 (fora do escopo):** n8n automations — protocolo diferente, spec separado

---

## Objetivo

Proteger qualquer modificação significativa no ecossistema do Victor com um padrão de canary deployment: a versão nova só substitui a stable após comparação explícita e aprovação manual.

Invisível quando desnecessário. Automático quando crítico.

---

## Domínios Monitorados

```
C:\Users\victor.bernardi\.gemini\antigravity\**   → sempre canary (ecossistema completo)
C:\Users\victor.bernardi\.gemini\GEMINI.md        → sempre canary (config global)
C:\Projetos\Stout\**\*.py, *.sh, *.md            → canary
C:\Projetos\Inova\**\*.py, *.sql                 → sempre canary
C:\Projetos\*\**\*.py, *.sh                      → canary (novos projetos)
```

**Não dispara canary:**
- Arquivos de log, outputs temporários, `.gitignore`
- Arquivos dentro de `docs/`, `raw/`, `diary/` (exceto `diary/canary-log.md`)
- Edições triviais: typos, formatação, comentários (avaliado pelo agente)

**Novos projetos:** O primeiro arquivo substantivo vai direto para stable — sem versão anterior para comparar. Canary entra na segunda modificação em diante.

---

## Arquitetura

**Componentes:**

1. **`skills/canary-deployment/SKILL.md`** — nova skill no Antigravity que define o protocolo completo
2. **`diary/canary-log.md`** — log de todas as promoções e reversões (novo arquivo)
3. **Convenção de arquivos:**
   - `<nome>.stable.<ext>` — backup automático da versão aprovada
   - Presença do `.stable.*` = arquivo em estado canary ativo

**Sem infraestrutura nova.** Tudo roda no Gemini CLI via leitura/escrita de arquivos e execução Python.

---

## Protocolo de Trigger

O agente ativa o canary **antes** de salvar qualquer modificação significativa em um domínio monitorado:

```
Agente detecta modificação significativa em domínio monitorado
     ↓
Backup: copiar arquivo atual → <nome>.stable.<ext>
     ↓
Salvar nova versão no arquivo original
     ↓
Apresentar comparação ao Victor (modo texto ou execução)
     ↓
"Promover canary para stable? (S/N)"
     S → deletar .stable.* → mudança permanente → registrar em canary-log.md
     N → restaurar .stable.* → arquivo volta ao estado anterior → registrar em canary-log.md
```

---

## Modos de Comparação

### Modo Texto
Aplicado a: skills, workflows, agentes, KIs, GEMINI.md, arquivos `.md`

```
═══════════════════════════════════════════════
CANARY ATIVO: skills/task-intelligence/SKILL.md
═══════════════════════════════════════════════
STABLE (atual)          │ CANARY (nova versão)
────────────────────────┼────────────────────────
- Linha removida        │
                        │ + Linha adicionada
  Linha igual           │   Linha igual
────────────────────────┴────────────────────────
Promover canary para stable? (S/N)
```

### Modo Execução
Aplicado a: engines Python (M0-M4), scripts bash, arquivos `.sql`

```
═══════════════════════════════════════════════
CANARY ATIVO: Inova/engines/engine_M1.py
═══════════════════════════════════════════════
[diff de código apresentado primeiro]

Executar ambas as versões no dataset de amostra para comparar outputs? (S/N)
  S → roda <nome>.stable.py + <nome>.py no mesmo input → mostra diff de output
  N → apresentar só o diff de código

Promover canary para stable? (S/N)
```

---

## Rollback Posterior

Se Victor promover e depois identificar um problema:

```
/canary rollback <arquivo>
```

O agente consulta `diary/canary-log.md` para localizar o backup mais recente e restaura.

---

## Log de Canary

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md`

Formato por entrada:
```
DATA | ARQUIVO | AÇÃO: [promovido|revertido] | RESUMO DA MUDANÇA
```

Exemplo:
```
2026-04-17 | skills/task-intelligence/SKILL.md | AÇÃO: promovido | Adicionado critério de classificação Crítica para tasks de produção
```

---

## Critérios de Sucesso

- Nenhuma modificação significativa nos domínios monitorados é aplicada sem passar pelo canary
- O overhead de tokens é zero fora do momento da modificação
- Rollback sempre disponível via canary-log.md
- Funciona para qualquer novo projeto criado em `C:\Projetos\*`
