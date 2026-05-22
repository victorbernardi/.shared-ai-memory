# Arquitetura LLM Wiki — Topologia Real

**Data:** 2026-05-08
**Status:** Aprovado (versão corrigida após auditoria física exaustiva)

## TL;DR

A infraestrutura foi unificada em `C:\Users\victor.bernardi\.shared-ai-memory`. O diretório legado `C:\Motores-LLM` foi desativado. Tudo o que antes era espalhado agora converge para este hub central, que atua como o sistema nervoso central do ecossistema.

## Topologia real

### Camada 1 — Hub Central `.shared-ai-memory` (Source of Truth)

```
C:\Users\victor.bernardi\.shared-ai-memory\
├── brain\               (Sessões Agentic — Real)
├── memory\              (Contexto Global e Metadados — Real)
├── conversations\       (Logs de Conversa — Real)
├── implicit\            (Memória Implícita — Real)
├── knowledge\           (Base de Conhecimento — Real)
├── extensions\          (Extensões VS Code e MCP — Real)
├── skills\              (Golden Copy das Skills — Real)
└── context-agent\       (Storage unificado do agente — Real)
```

Este diretório contém os **arquivos físicos reais**. Não são junctions.

### Camada 2 — Home dirs dos motores (Projeções)

```
C:\Users\victor.bernardi\
├── .claude\                         (Instalação Real)
│   ├── settings.json
│   ├── skills\                      (Local Skills)
│   └── projects\                    (Session Logs)
│
├── .antigravity\                    (Instalação Real — Projeção de .shared-ai-memory)
│   ├── brain      ──► .shared-ai-memory\brain         (Junction)
│   ├── conversations ──► .shared-ai-memory\conversations (Junction)
│   ├── implicit   ──► .shared-ai-memory\implicit       (Junction)
│   ├── knowledge  ──► .shared-ai-memory\knowledge      (Junction)
│   ├── skills     ──► .shared-ai-memory\skills         (Junction)
│   └── docs       ──► .shared-ai-memory\docs           (Junction)
│
└── .gemini\                         (Instalação Real)
    ├── settings.json
    └── antigravity ──► .shared-ai-memory              (Junction Completa)
```

### Camada 3 — Laboratório Stout (Desenvolvimento)

```
C:\Projetos\Stout\
├── Plugins\                    (Skills em incubação)
├── wiki-compiler\              (Ferramental de Build)
└── memory\
    └── ARCHITECTURE.md         (Este arquivo — Original em .shared-ai-memory\memory)
```

## Regras de Governança

1. **Soberania do Hub:** `C:\Users\victor.bernardi\.shared-ai-memory` é a única Golden Copy.
2. **Imutabilidade Documental:** NUNCA utilize `write_file` em arquivos existentes. O uso de `replace` é obrigatório para preservar histórico.
3. **Validação Física:** Toda alteração estrutural deve ser precedida por um `dir /a` para validar junctions.
4. **Promoção:** Desenvolvimento (Stout/Plugins) -> Validação -> Promoção para `.shared-ai-memory/skills` via `canary-deployment`.

---
*Assinado: Arquiteto de Design Agêntico*
