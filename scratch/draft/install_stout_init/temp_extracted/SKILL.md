---
name: stout-init
description: Inicializa novos projetos no ecossistema Plano Executivo, priorizando a criação da estrutura física (código) antes da reflexão. Cria sempre GEMINI.md (Manual do Engenheiro) e ANTIGRAVITY.md (Manual do Cientista). Detecta o ambiente, configura MCPs e dispara automaticamente a skill de brainstorming para refinamento.
---

# 🚀 SKILL: STOUT-INIT — Scaffolding de Alta Maturidade

## Propósito

Garantir que todo novo projeto no ecossistema **Plano Executivo** nasça com uma base técnica sólida e uma governança clara, seguindo a separação de responsabilidades entre o **Gemini CLI (Engenheiro/Dev)** e o **Antigravity (Analista/Cientista)**.

Todo projeto nasce com:
- **GEMINI.md** — Manual de Operações (Engenheiro)
- **ANTIGRAVITY.md** — Kernel Operacional (Cientista)
- **MCPs configurados** — context7, google-drive, notebooklm sempre inicializados

## 🛠️ Detecção de Ambiente (Apenas para Ferramentas)

A skill detecta o ambiente verificando:

1. **Presença de `.antigravity/`** no home directory → Usa ferramentas do **Antigravity**
2. **Presença de `.gemini/skills/`** no home directory → Usa ferramentas do **Gemini CLI**
3. **Variáveis de ambiente** (`ANTIGRAVITY_HOME`, `GEMINI_CLI_HOME`)
4. **Pergunta ao usuário** se ambiguidade persistir

### Ferramentas por Ambiente

| Operação | Gemini CLI | Antigravity |
|----------|-----------|-------------|
| Ler arquivo | `read_file` | `view_file` |
| Escrever arquivo | `write_file` | `write_to_file` |
| Editar arquivo | `edit` | `replace_file_content` |
| Buscar texto | `search_file_content` | `grep_search` |
| Listar diretório | `list_directory` | `list_directory` |
| Shell | `run_shell_command` | `run_command` |
| Memória | `save_memory` | `replace_file_content` no próprio arquivo |

## Pipeline de Execução

### Fase 1: Coleta de Contexto (6 perguntas)

1. **Nome do projeto:** [kebab-case, ex: analise-frota-jd]
2. **Domínio de negócio:** [Ex: Pós-Venda John Deere, Data Science, Automação]
3. **Objetivo principal:** [Uma frase do que o projeto resolve]
4. **KPI principal:** [Como mediremos sucesso]
5. **Stack tecnológica:** [Python, React, etc.]
6. **Tipo de projeto:** [API, Dashboard, ML, etc.]

### Fase 2: Scaffolding Físico (Execução Imediata)
O agente deve criar a estrutura física **antes** de qualquer reflexão profunda para evitar falhas de inicialização:
```
[NomeProjeto]/
├── GEMINI.md              # Manual de Operações (Engenheiro)
├── ANTIGRAVITY.md         # Kernel Operacional (Cientista)
├── README.md              # Visão Geral
├── .env.example           # Variáveis de ambiente (incluindo MCPs)
├── .gitignore             # Padrão do stack
├── .gemini/
│   └── settings.json      # MCPs: context7, google-drive, notebooklm
├── docs/                  # Documentação (Junction para memória se Antigravity)
├── src/                   # Código-fonte
├── data/                  # Dados e queries
├── tests/                 # Testes automatizados
└── scripts/               # Scripts de automação e deploy
```

### Fase 3: Configuração de MCPs (Obrigatória)

Criar `.gemini/settings.json` com os 3 MCPs padrão:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp@latest"],
      "env": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-drive@latest"],
      "env": {
        "GOOGLE_DRIVE_API_KEY": "${GOOGLE_DRIVE_API_KEY}"
      }
    },
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"],
      "env": {
        "NOTEBOOKLM_API_KEY": "${NOTEBOOKLM_API_KEY}"
      }
    }
  }
}
```

**Instruções para o Agente:**
- Sempre inicializar os 3 MCPs no início de cada sessão
- Verificar se as variáveis de ambiente estão configuradas em `.env`
- Se MCPs falharem, fallback para ferramentas nativas + busca web

### Fase 4: Geração de GEMINI.md Local

```markdown
# 📂 GEMINI.md — PROJETO: [Nome do Projeto]

> **Herança:** Plano Executivo Global
> **Ambiente:** [Gemini CLI / Antigravity — auto-detectado]
> **Inicializado em:** [DATA]

---

## 1. CONTEXTO DE NEGÓCIO

**Objetivo de Negócio:** [Preenchido na coleta]
**KPI Principal:** [Preenchido na coleta]
**Leitura Executiva:** [Gerar com base no objetivo]
**Stakeholders:** [Perguntar ou inferir do domínio]

---

## 2. CONTEXTO TÉCNICO

### Stack
- **Linguagem/Framework:** [Preenchido]
- **Banco de Dados:** [Perguntar se não informado]
- **Dependências Críticas:** [Listar padrões do stack]

### Integrações
- [ ] APIs externas: [A definir]
- [ ] Serviços internos: [A definir]
- [ ] Autenticação: [A definir]

### MCPs Configurados
- [ ] **context7** — Documentação técnica
- [ ] **google-drive** — Arquivos e documentos
- [ ] **notebooklm** — Pesquisa e análise

---

## 3. REGRAS LOCAIS

### Padrões Específicos
- [Gerar com base no stack e domínio]

### Diretrizes de Análise
- Toda análise conecta achados técnicos ao KPI principal.
- Outputs estruturados com impacto financeiro/operacional primeiro.

---

## 4. ESTADO ATUAL

### Fase Atual: Research ⏳

#### Progresso STOUT
- [ ] **Research:** Pendente — mapear dados e dependências
- [ ] **Strategy:** Pendente — definir plano de ação
- [ ] **Execution:** Pendente — implementar solução
- [ ] **Validation:** Pendente — testar e validar

#### Decisões Pendentes
- [ ] Definir formato de dados de entrada
- [ ] Confirmar acesso a APIs externas

#### Bloqueios
- Nenhum identificado

---

## 5. NOTAS DE CONTEXTO

- *Projeto inicializado em [DATA] via skill stout-init*
- *Ambiente detectado: [Gemini CLI / Antigravity]*
- *MCPs configurados: context7, google-drive, notebooklm*

---

## 6. PRÓXIMAS AÇÕES

1. Mapear arquivos e dados disponíveis (Research)
2. Definir arquitetura técnica inicial (Strategy)
3. Configurar ambiente de desenvolvimento (Execution)

---

## 7. REFERÊNCIAS

- **GEMINI.md Global:** `../../GEMINI.md`
- **ANTIGRAVITY.md:** `./ANTIGRAVITY.md`
- **MCPs:** `.gemini/settings.json`
- **Skill de Inicialização:** `stout-init`
```

### Fase 5: Geração de ANTIGRAVITY.md

```markdown
# 🧠 ANTIGRAVITY.md — Kernel Agêntico

> **Ambiente:** [Gemini CLI / Antigravity — auto-detectado]
> **Projeto:** [Nome]
> **Skill:** stout-init
> **Inicializado:** [DATA]

---

## 1. ARQUITETURA DE MEMÓRIA

### Hierarquia
```
C:\Projetos\Stout\
├── antigravity\skills\          # Skills técnicas
├── memory\context-agent\
│   ├── sessions\                 # Sessões ativas
│   └── projects\[ID]\           # Memória persistente ← docs/ junction
└── [Projeto]\
    ├── ANTIGRAVITY.md             # Este arquivo
    └── docs/ → junction           # Link para memory/context-agent/projects/[ID]/
```

### Junction Configurado
- `docs/` → `C:\Projetos\Stout\memory\context-agent\projects\[nome-projeto]\`

---

## 2. FERRAMENTAS DISPONÍVEIS

| Ferramenta | Uso Principal |
|-----------|---------------|
| `view_file` | Leitura de arquivos |
| `write_to_file` | Criação de arquivos |
| `replace_file_content` | Edição precisa |
| `grep_search` | Busca em arquivos |
| `run_command` | Execução shell |

**Referência completa:**
`C:\Users\victor.bernardi\.antigravity\skills\process-superantigravity\references\gemini-tools.md`

---

## 3. MCPs (Model Context Protocol)

### MCPs Configurados
- **context7** — Busca documentação técnica atualizada
- **google-drive** — Acesso a arquivos e documentos
- **notebooklm** — Pesquisa e análise de documentos

### Uso dos MCPs
- Sempre inicializar no início da sessão
- Usar context7 para validar documentação de bibliotecas
- Usar google-drive para ler/salvar arquivos de referência
- Usar notebooklm para criar notebooks de pesquisa

---

## 4. FRAMEWORK STOUT

1. **Research:** `grep_search` + `view_file` + **MCPs** → mapear contexto
2. **Strategy:** Documentar plano no GEMINI.md local
3. **Execution:** `write_to_file` / `replace_file_content`
4. **Validation:** `view_file` + testes via `run_command`

---

## 5. STATE TRACKING

> Atualizar via `replace_file_content` ao final de cada ciclo.

### 🛠️ Status STOUT
- [ ] **Research:** [Pendente]
- [ ] **Strategy:** [Pendente]
- [ ] **Execution:** [Pendente]
- [ ] **Validation:** [Pendente]

### 📝 Notas Recentes
- *Projeto inicializado em [DATA]*
- *MCPs: context7, google-drive, notebooklm*

---

## 6. SEGURANÇA

- Confirmar caminhos absolutos antes de `write_to_file`
- Nunca executar comandos destrutivos sem validação
- Credenciais via `.env`, nunca hardcoded
- API keys dos MCPs em `.env`, não em settings.json

---

## 7. INTEGRAÇÃO

- **ANTIGRAVITY.md** = Kernel técnico (COMO operar)
- **GEMINI.md** = Contexto de negócio (O QUE construir)
- **MCPs** = Extensões de capacidade (documentação, arquivos, pesquisa)
- Nunca misturar responsabilidades entre os arquivos
```

### Fase 6: Configuração de Junction (Antigravity + Windows)

Se ambiente = Antigravity e OS = Windows:

```cmd
mklink /J "C:\Projetos\Inova\[projeto]\docs"   "C:\Projetos\Stout\memory\context-agent\projects\[projeto]\"
```

Criar subpastas no destino do junction:
```
C:\Projetos\Stout\memory\context-agent\projects\[projeto]\
├── specs/
├── plans/
└── adr/
```

### Fase 7: README.md e Governança

Gerar README.md mínimo:
```markdown
# [Nome do Projeto]

**Objetivo:** [Objetivo de negócio]
**Status:** 🟡 Inicialização
**KPI:** [KPI principal]
**Ambiente:** [Gemini CLI / Antigravity]

## Stack
- [Stack listado]

## Setup
1. Copiar `.env.example` para `.env` e preencher
2. Configurar MCPs: `npx @context7/mcp@latest` etc.
3. [Instruções específicas do stack]

## Documentação
- Especificações: `docs/specs/`
- Planos de ação: `docs/plans/`
- Decisões: `docs/adr/`

## Contexto IA
- `GEMINI.md` — Contexto de negócio
- `ANTIGRAVITY.md` — Kernel operacional
- `.gemini/settings.json` — MCPs configurados
```

Gerar `.env.example` com variáveis típicas do stack + MCPs:
```
# Stack
DATABASE_URL=
API_KEY=
SECRET_KEY=

# MCPs
CONTEXT7_API_KEY=
GOOGLE_DRIVE_API_KEY=
NOTEBOOKLM_API_KEY=
```

Gerar `.gitignore` padrão para o stack.

### Fase 8: Validação

Verificar via ferramenta de leitura do ambiente:
- [ ] GEMINI.md criado e preenchido
- [ ] ANTIGRAVITY.md criado e preenchido
- [ ] `.gemini/settings.json` com MCPs configurados
- [ ] Estrutura de pastas completa
- [ ] Junction configurado (se Antigravity)
- [ ] README.md gerado
- [ ] Git inicializado (via ferramenta de shell do ambiente)

## Regras de Ouro

1. **Sempre criar ambos:** GEMINI.md + ANTIGRAVITY.md em todo projeto.
2. **Sempre configurar MCPs:** context7, google-drive, notebooklm em todo projeto.
3. **Nunca sobrescrever** arquivos existentes sem confirmação do usuário.
4. **Sempre perguntar** os 6 itens da Fase 1 — não inventar dados.
5. **Junctions só no Windows** — em Linux/Mac usar symlinks (`ln -s`).
6. **GEMINI.md ≠ ANTIGRAVITY.md** — manter separação de responsabilidades.
7. **Adaptar ferramentas** ao ambiente detectado — nunca usar `replace_file_content` no Gemini CLI nem `edit` no Antigravity.
8. **Documentar ambiente** no GEMINI.md local para referência futura.

## Referências
- **Identidade Global:** `C:\Motores-LLM\gemini-cli\draft\plano_executivo_kpis_ia_pos_venda_v2_consolidado.md`
- **Orquestrador de Skills:** `using-superantigravity`
- **Skill de Gestão:** `skill-manager`
