# Spec: stout-skill-manager — Orquestrador Universal de Skills

**Data:** 2026-05-29  
**Status:** Aprovado  
**Autor:** Victor Bernardi  

---

## 1. Contexto e Motivação

O ecossistema Stout possui skills distribuídas em múltiplas plataformas (Claude Code, CommandCode, Gemini/Antigravity) sem um ponto de entrada unificado. Hoje:

- `audit-skill-manager` gerencia instalação via CLI `skillfish`, mas sem auditoria de conflito nem controle de qualidade automatizado.
- `stout-create-skill` fabrica skills novas sem verificar se já existe equivalente externo.
- `stout-skill-auditor` é chamado antes de criar, mas não antes de instalar.
- Não existe fluxo que conecte: busca local → busca externa → auditoria → instalação → qualidade.

**Decisão arquitetural concluída:** fonte da verdade única em `C:\Users\victor.bernardi\.shared-ai-memory\skills`, com junctions das 3 plataformas apontando para esse diretório. Setup já executado.

---

## 2. Objetivo

Criar `stout-skill-manager` (Tier 1 — Orchestrator) como **portão único de entrada** para qualquer adição ao ecossistema de skills, seja por instalação de skill externa ou criação de skill nova.

---

## 3. Escopo

### Incluso

- Skill `stout-skill-manager` com SKILL.md e scripts Python
- Script de busca local no registry
- Integração com `skillfish` CLI para busca e instalação externa
- Pipeline de auditoria via `stout-skill-auditor`
- Pipeline de qualidade via `skill-sentinel`
- Ciclo de auto-reparo via `stout-improve-skill`
- Atualização do `stout-create-skill` para chamar `stout-skill-manager` antes de fabricar
- Deprecação do `audit-skill-manager`
- Registro da skill `skillfish` no `stout-skill-registry`
- Validação e atualização do SKILL.md da skill `skillfish` para padrão multi-plataforma

### Fora do Escopo

- Modificação interna do `stout-skill-auditor` ou `skill-sentinel`
- Interface gráfica ou web
- Publicação de skills no npm/GitHub

---

## 4. Arquitetura

### 4.1 Fonte da Verdade

```
C:\Users\victor.bernardi\.shared-ai-memory\skills\   ← diretório real
  ↑ junction
C:\Users\victor.bernardi\.claude\skills
C:\Users\victor.bernardi\.commandcode\skills
C:\Users\victor.bernardi\.gemini\config\skills  (via .antigravity\skills)
```

### 4.2 Fluxo Completo

```
INTENÇÃO DO USUÁRIO
        │
        ├── "busque/instale skill X"  ─────────────────────────────────┐
        └── "crie skill X"                                              │
                  │                                                     │
                  ▼                                                     │
     stout-skill-manager (FASE 1 — Busca Local)                        │
       └── consulta registry.json, filtra status=active                │
           match semântico: role + triggers (threshold ≥ 60%)          │
           │                                                            │
           ├── skill local suficiente → apresenta ao usuário, FIM      │
           └── insuficiente ou ausente                                  │
                  │                                                     │
                  ▼                                                     │
     stout-skill-manager (FASE 2 — Busca Externa)          ←───────────┘
       └── skillfish search <query>
           apresenta resultados com nome, fonte, descrição
           HITL: usuário escolhe skill ou decide criar
           │
           ├── "criar mesmo assim" → stout-create-skill (ver 4.3)
           └── skill escolhida
                  │
                  ▼
     stout-skill-manager (FASE 3 — Auditoria de Conflito)
       └── stout-skill-auditor semantic_overlap.py
           │
           ├── APPROVED  ──────────────────────────────────────────────┐
           ├── QUESTIONED → PARA, pergunta usuário                     │
           │     ├── continuar → FASE 4                                │
           │     └── abortar → FIM                                     │
           └── REJECTED → abort + sugere alternativa local             │
                                                                       ▼
     stout-skill-manager (FASE 4 — Instalação)
       └── skillfish add <owner/repo> --project
           valida: SKILL.md presente + frontmatter (name, version, tools)
           copia para .shared-ai-memory\skills\<nome>
           │
           ▼
     stout-skill-manager (FASE 5 — Controle de Qualidade)
       └── skill-sentinel run_audit.py --skill <nome>
           │
           ├── score ≥ 70 → registra em registry.json (status: active), FIM
           └── score < 70 → stout-improve-skill
                 └── re-avalia (máx 2 ciclos)
                       ├── score ≥ 70 → registra, FIM
                       └── falha → instala com status: quarantine, avisa usuário
```

### 4.3 Integração com stout-create-skill

`stout-create-skill` passa a exigir que `stout-skill-manager` seja consultado primeiro:

```
stout-create-skill recebe intenção
  └── chama stout-skill-manager (Fases 1 e 2)
        ├── skill externa encontrada → HITL: instalar ou criar mesmo assim?
        │     └── instalar → pipeline de instalação (Fases 3-5)
        └── nada encontrado → continua pipeline de criação original
              └── stout-skill-auditor (conflito local?)
                    ├── APPROVED → manufatura
                    └── REJECTED/QUESTIONED → abort/HITL
```

### 4.4 stout-skill-auditor como Serviço Compartilhado

O `stout-skill-auditor` é chamado por dois caminhos sem duplicação de lógica:

| Caller | Propósito |
|--------|-----------|
| `stout-skill-manager` (Fase 3) | Conflito ao instalar skill externa |
| `stout-create-skill` | Conflito ao fabricar skill nova |

Ambos leem o mesmo `registry.json` e geram `audit_result.json` com a mesma estrutura.

---

## 5. Skill skillfish — Padronização Multi-plataforma

### 5.1 Estado atual

A skill `skillfish` foi criada nesta sessão em `.shared-ai-memory\skills\skillfish\` com scripts `search.py` e `install.py`. O SKILL.md precisa ser atualizado para o padrão universal.

### 5.2 Frontmatter universal

```yaml
---
name: skillfish
version: 1.0.0
tier: 2
category: meta-governance
tools:
  - claude-code
  - antigravity
  - commandcode
  - gemini-cli
---
```

O campo `tools` declara compatibilidade. Como as 3 plataformas apontam para a mesma pasta via junction, o SKILL.md é lido nativamente por todas.

### 5.3 Atualização dos scripts

Os scripts `search.py` e `install.py` atuais chamam a API do npm diretamente. Devem ser atualizados para envolver o CLI `skillfish` (instalado via `npm i -g skillfish`) como camada primária, com fallback para API npm apenas quando o CLI não estiver disponível.

---

## 6. Estrutura de Arquivos

```
.shared-ai-memory\skills\
  stout-skill-manager\
    SKILL.md
    scripts\
      local_search.py        ← busca no registry.json por semântica
      orchestrator.py        ← orquestra as 5 fases
      install_validator.py   ← valida SKILL.md pós-download
    config\
      thresholds.yaml        ← score mínimo sentinel (default: 70)
  skillfish\
    SKILL.md                 ← atualizado para frontmatter universal
    scripts\
      search.py              ← wraps skillfish CLI + fallback API npm
      install.py             ← wraps skillfish add + validação Stout
```

---

## 7. Deprecação do audit-skill-manager

Após `stout-skill-manager` estar ativo:

1. `audit-skill-manager/SKILL.md` recebe header `[DEPRECADO]` e ponteiro para `stout-skill-manager`
2. Status no `registry.json` atualizado para `deprecated`
3. Arquivo físico mantido por 30 dias, depois removido

---

## 8. Critérios de Aceitação

- [ ] `stout-skill-manager` invocado por "busque skills para esse projeto" executa as 5 fases
- [ ] Skill externa instalada aparece no `.claude\skills`, `.commandcode\skills` e `.gemini\config\skills` sem ação adicional
- [ ] `stout-create-skill` invoca `stout-skill-manager` antes de fabricar
- [ ] QUESTIONED dispara HITL e aguarda decisão antes de prosseguir
- [ ] REJECTED aborta com sugestão de alternativa local
- [ ] Score < 70 no sentinel aciona `stout-improve-skill` (máx 2 ciclos)
- [ ] `skillfish/SKILL.md` contém `tools: [claude-code, antigravity, commandcode, gemini-cli]`
- [ ] `audit-skill-manager` marcado como deprecated no registry
