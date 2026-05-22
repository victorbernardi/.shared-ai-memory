# STOUT-INIT — Skill Unificada (Gemini CLI + Antigravity)

## O Que E

Skill unificada que funciona em **AMBOS** os ambientes:
- **Gemini CLI** — usa ferramentas nativas (read_file, write_file, edit)
- **Antigravity** — usa ferramentas customizadas (view_file, write_to_file, replace_file_content)

A skill **detecta automaticamente** o ambiente e adapta o comportamento.

## Como Funciona a Deteccao

1. Verifica se `.antigravity/` existe → usa ferramentas do Antigravity
2. Verifica se `.gemini/skills/` existe → usa ferramentas do Gemini CLI
3. Pergunta ao usuario se ambiguo

## Arquivos Gerados por Ambiente

| Arquivo | Gemini CLI | Antigravity |
|---------|-----------|-------------|
| `GEMINI.md` | ✅ | ✅ |
| `ANTIGRAVITY.md` | ❌ | ✅ |
| `README.md` | ✅ | ✅ |
| `.env.example` | ✅ | ✅ |
| `.gitignore` | ✅ | ✅ |
| `docs/` | Pasta normal | Junction → memoria persistente |
| `src/`, `data/`, `tests/`, `scripts/` | ✅ | ✅ |

## Ferramentas por Ambiente

| Operacao | Gemini CLI | Antigravity |
|----------|-----------|-------------|
| Ler arquivo | `read_file` | `view_file` |
| Escrever arquivo | `write_file` | `write_to_file` |
| Editar arquivo | `edit` | `replace_file_content` |
| Buscar texto | `search_file_content` | `grep_search` |
| Shell | `run_shell_command` | `run_command` |

## Instalacao

### Opcao 1: Script Automatico

```bash
python install_stout_init.py
```

O script instala a skill em **todos os ambientes detectados** (Gemini CLI e/ou Antigravity).

### Opcao 2: Manual

**Antigravity:**
```
C:\Users\[usuario]\.antigravity\skills\stout-init\
├── SKILL.md
├── references/
│   ├── gemini-local-template.md
│   └── antigravity-template.md
└── scripts/
```

**Gemini CLI:**
```
~/.gemini/skills/stout-init/
├── SKILL.md
├── references/
│   └── gemini-local-template.md
└── scripts/
```

## Uso

### Comando de Ativacao (ambos os ambientes)

```
Iniciar novo projeto chamado [nome-do-projeto]
```

Ou:
```
Criar projeto [nome-do-projeto]
```

Ou:
```
Scaffoldar projeto [nome-do-projeto]
```

### O que a Skill Pergunta (7 itens)

1. **Nome do projeto:** (kebab-case)
2. **Dominio de negocio:** (Pos-Venda, Data Science, etc.)
3. **Objetivo principal:** (o que resolve)
4. **KPI principal:** (como medir sucesso)
5. **Stack tecnologica:** (Python, React, etc.)
6. **Tipo de projeto:** (API, Dashboard, Automacao, etc.)
7. **Prioridade:** (P0-Critico, P1-Alta, P2-Media, P3-Baixa)

### Exemplo de Conversa

**Usuario:** "Iniciar projeto chamado analise-frota-jd"

**Agente:**
- Qual o dominio de negocio? → "Pos-Venda John Deere"
- Qual o objetivo? → "Reduzir downtime de frota"
- Qual o KPI? → "Aumentar First Time Fix"
- Qual a stack? → "Python + Pandas + PostgreSQL"
- Tipo? → "Analise"
- Prioridade? → "P1-Alta"

**Agente detecta:** Antigravity (porque .antigravity existe)

**Agente cria:**
```
analise-frota-jd/
├── GEMINI.md              ← contexto de negocio
├── ANTIGRAVITY.md         ← kernel operacional
├── README.md
├── .env.example
├── .gitignore
├── docs/ → junction         ← memoria persistente
├── src/
├── data/
├── tests/
└── scripts/
```

## Pipeline de Inicializacao

```
Coleta de Contexto (7 perguntas)
       |
Deteccao de Ambiente (auto)
       |
Scaffolding de Pastas
       |
Geracao GEMINI.md
       |
Geracao ANTIGRAVITY.md (se Antigravity)
       |
Configuracao de Junction (se Antigravity)
       |
README.md + .env + .gitignore
       |
Validacao
```

## Diferenca entre Ambientes na Pratica

| Cenario | Gemini CLI | Antigravity |
|---------|-----------|-------------|
| Projeto simples | GEMINI.md + estrutura basica | GEMINI.md + ANTIGRAVITY.md + junction |
| State tracking | Manual / save_memory | Automatico via replace_file_content |
| Memoria persistente | Nao nativo | Via junction em memory/context-agent/ |
| Ferramentas de arquivo | read_file, write_file, edit | view_file, write_to_file, replace_file_content |

## Manutencao

A skill e a mesma para ambos os ambientes. Para atualizar:
1. Copie o novo SKILL.md para ambos os diretorios de skills
2. Ou reexecute o script de instalacao

## Referencias

- Gemini CLI Skills Docs
- Antigravity Kit
- Agent Skills Protocol
