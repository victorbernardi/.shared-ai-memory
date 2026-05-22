# ESTRUTURA DE ARQUIVOS — Onde Cada Arquivo Vai

## Hierarquia Completa

### NIVEL 1: HOME DIRECTORY (Global — Todos os Projetos)

```
~/.gemini/
├── GEMINI.md              ← REGRAS GLOBAIS (aplica a TODOS os projetos)
│                            Perfil, mindset, stack padrao, seguranca
│
├── antigravity/
│   └── skills/
│       └── stout-init/
│           ├── SKILL.md
│           ├── references/
│           │   ├── gemini-local-template.md
│           │   └── antigravity-template.md
│           └── scripts/
│
└── skills/
    └── stout-init/        ← (alternativa Gemini CLI)
        ├── SKILL.md
        └── references/
            ├── gemini-local-template.md
            └── antigravity-template.md
```

> Nota: No Windows, ~ = C:\Users\victor.bernardi\

---

### NIVEL 2: PASTA PAI DO PLANO EXECUTIVO (Opcional — Heranca de Contexto)

```
C:\Projetos\Stout\
│   (ou ~/plano-executivo/)
│
├── GEMINI.md              ← HERANCA DE CONTEXTO (opcional)
│                            Se existir, todos os projetos filhos herdam
│                            antes de carregar o GEMINI.md global do home
│
└── [Projeto A]/           ← Cada projeto e uma subpasta
    ├── ...
```

> Regra do Gemini CLI: Busca GEMINI.md do diretorio atual ate a raiz do repositorio Git
> Se houver um GEMINI.md na pasta pai, ele e carregado antes do global do home.

---

### NIVEL 3: PROJETO INDIVIDUAL (Local — Cada Projeto)

```
C:\Projetos\Stout\meu-projeto\
│
├── GEMINI.md              ← CONTEXTO DE NEGOCIO (local)
│                            Objetivo, KPI, stack especifica, regras locais
│                            PREVALECE sobre o global em caso de conflito
│
├── ANTIGRAVITY.md         ← KERNEL OPERACIONAL (local)
│                            Ferramentas, STOUT, state tracking
│                            So existe se voce usa Antigravity
│
├── AGENTS.md              ← (opcional — padrao cross-tool)
│                            Funciona em Antigravity + Cursor + Claude Code
│                            Usado se nao houver GEMINI.md
│
├── .agent/
│   ├── rules/             ← Regras modulares por subdiretorio
│   │   ├── backend.md
│   │   └── frontend.md
│   └── workflows/         ← Workflows salvos (/comando)
│       └── deploy.md
│
├── .gemini/
│   └── settings.json      ← MCPs configurados
│
├── .env.example
├── .gitignore
├── README.md
├── docs/                  ← Junction → memory/context-agent/projects/[ID]/
│   ├── specs/
│   ├── plans/
│   └── adr/
├── src/
├── data/
├── tests/
└── scripts/
```

---

## Resumo: Onde Colocar Cada Arquivo que Voce Baixou

| Arquivo Baixado | Onde Colocar | Escopo |
|-----------------|--------------|--------|
| GEMINI.md (global) | ~/.gemini/GEMINI.md | Todos os projetos |
| GEMINI.md (heranca) | C:\Projetos\Stout\GEMINI.md | Projetos filhos do Plano Executivo |
| SKILL.md | ~/.gemini/antigravity/skills/stout-init/ | Disponivel em todos os projetos |
| GEMINI_LOCAL_TEMPLATE.md | ~/.gemini/antigravity/skills/stout-init/references/ | Template copiado para cada projeto |
| ANTIGRAVITY.md (template) | ~/.gemini/antigravity/skills/stout-init/references/ | Template copiado para cada projeto |

---

## Ordem de Carregamento do Contexto

Quando voce abre um projeto, o agente carrega as regras nesta ordem:

```
1. ~/.gemini/GEMINI.md              ← Global (home directory)
        |
2. ../../GEMINI.md                  ← Heranca (pasta pai, se existir)
        |
3. ./GEMINI.md                      ← Local (raiz do projeto)
        |
4. ./ANTIGRAVITY.md                 ← Kernel operacional
        |
5. ./.agent/rules/*.md              ← Regras modulares
```

Regra de Precedencia: O ultimo carregado prevalece sobre o anterior.
- ./GEMINI.md (local) sobrescreve ~/.gemini/GEMINI.md (global)
- ./ANTIGRAVITY.md e carregado separadamente como kernel tecnico

---

## Diferenca: GEMINI.md vs AGENTS.md vs ANTIGRAVITY.md

| Arquivo | Escopo | Formato | Prioridade | Quando Usar |
|---------|--------|---------|------------|-------------|
| ~/.gemini/GEMINI.md | Global | Markdown | Mais alta | Preferencias pessoais, perfil, seguranca |
| ./GEMINI.md | Projeto | Markdown | Mais alta | Contexto de negocio, stack, KPIs |
| ./AGENTS.md | Projeto | Markdown | Padrao | Cross-tool (Antigravity + Cursor + Claude) |
| ./ANTIGRAVITY.md | Projeto | Markdown | Tecnico | Kernel operacional, ferramentas, state |
| .agent/rules/*.md | Subdir | Markdown | Limitado | Regras especificas de subdiretorio |

---

## Locais no Windows vs Linux/Mac

| Tipo | Windows | Linux/Mac |
|------|---------|-----------|
| Home directory | C:\Users\victor.bernardi\ | /home/victor.bernardi/ ou ~/ |
| Gemini global | C:\Users\victor.bernardi\.gemini\GEMINI.md | ~/.gemini/GEMINI.md |
| Antigravity skills | C:\Users\victor.bernardi\.gemini\antigravity\skills\ | ~/.gemini/antigravity/skills/ |
| Gemini CLI skills | C:\Users\victor.bernardi\.gemini\skills\ | ~/.gemini/skills/ |
| Projetos | C:\Projetos\Stout\ | ~/projetos/stout/ |
