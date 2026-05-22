
# Criar documento final de entrega com passo a passo de instalação

entrega_final = """# 📦 ENTREGA FINAL — STOUT-INIT
## Ecossistema Plano Executivo: GEMINI.md + ANTIGRAVITY.md + MCPs

---

## 📋 O Que Foi Entregue

Esta entrega contém a skill **stout-init** e todos os templates necessários para inicializar projetos no ecossistema **Plano Executivo**, funcionando tanto no **Gemini CLI** quanto no **Antigravity**.

### Arquivos Gerados

| Arquivo | Propósito | Onde Instalar |
|---------|-----------|---------------|
| `GEMINI.md` | Contexto global do Plano Executivo | Pasta pai dos projetos (`C:\\Projetos\\Stout\\` ou `~/plano-executivo/`) |
| `ANTIGRAVITY.md` | Template do kernel operacional | Vai para cada projeto (a skill copia automaticamente) |
| `GEMINI_LOCAL_TEMPLATE.md` | Template de GEMINI.md local | Vai para cada projeto (a skill copia automaticamente) |
| `SKILL.md` | Skill stout-init | `~/.gemini/skills/stout-init/` e/ou `~/.antigravity/skills/stout-init/` |
| `install_stout_init.py` | Script de instalação automática | Executar uma vez |
| `README_STOUT_INIT.md` | Documentação completa | Referência manual |

---

## 🎯 Decisões Arquiteturais Tomadas

### 1. Separação de Responsabilidades

| Arquivo | Responsabilidade | Analogia |
|---------|-----------------|----------|
| **GEMINI.md** | Contexto de negócio, KPIs, stack, regras | "Mapa / Destino" |
| **ANTIGRAVITY.md** | Ferramentas, pipeline STOUT, state tracking | "Motor / Kernel" |
| `.gemini/settings.json` | MCPs configurados | "Extensões de capacidade" |

### 2. Dois Arquivos Sempre Criados

Todo projeto nasce com **GEMINI.md + ANTIGRAVITY.md**, sem perguntar. A detecção de ambiente serve apenas para escolher qual **ferramenta usar** (read_file vs view_file), não o que criar.

### 3. MCPs Obrigatórios

Três MCPs sempre configurados em todo projeto:
- **context7** — Documentação técnica
- **google-drive** — Arquivos e documentos
- **notebooklm** — Pesquisa e análise

### 4. Hierarquia de Contexto

```
Pasta Pai (Plano Executivo)
├── GEMINI.md          ← Global (regras universais)
│
└── Projeto A/
    ├── GEMINI.md      ← Local (contexto de negócio)
    ├── ANTIGRAVITY.md ← Kernel (ferramentas, STOUT, state)
    └── .gemini/
        └── settings.json  ← MCPs
```

---

## 🚀 PASSO A PASSO DE INSTALAÇÃO

### Passo 1: Baixar os Arquivos

Baixe todos os arquivos desta entrega para uma pasta temporária:
```
C:\\Temp\\stout-init\\
├── GEMINI.md
├── ANTIGRAVITY.md
├── GEMINI_LOCAL_TEMPLATE.md
├── SKILL.md
├── install_stout_init.py
└── README_STOUT_INIT.md
```

### Passo 2: Colocar GEMINI.md Global

Copie o arquivo `GEMINI.md` para a **pasta pai** onde ficarão todos os projetos:

**Windows:**
```cmd
copy GEMINI.md "C:\\Projetos\\Stout\\GEMINI.md"
```

**Linux/Mac:**
```bash
cp GEMINI.md ~/plano-executivo/GEMINI.md
```

> Este arquivo será herdado automaticamente por todos os projetos filhos.

### Passo 3: Executar Script de Instalação da Skill

No terminal, na pasta onde baixou os arquivos:

```bash
python install_stout_init.py
```

O script detecta automaticamente se você tem:
- **Gemini CLI** → instala em `~/.gemini/skills/stout-init/`
- **Antigravity** → instala em `~/.antigravity/skills/stout-init/`
- **Ambos** → instala nos dois

### Passo 4: Verificar Instalação

**Gemini CLI:**
```bash
ls ~/.gemini/skills/stout-init/
# Deve mostrar: SKILL.md, references/, scripts/
```

**Antigravity:**
```cmd
dir C:\\Users\\%USERNAME%\\.antigravity\\skills\\stout-init\\
# Deve mostrar: SKILL.md, references/, scripts/
```

### Passo 5: Configurar Variáveis de Ambiente dos MCPs

Crie ou edite o arquivo `.env` na pasta do projeto (ou no sistema):

```
# MCPs
CONTEXT7_API_KEY=sua_chave_aqui
GOOGLE_DRIVE_API_KEY=sua_chave_aqui
NOTEBOOKLM_API_KEY=sua_chave_aqui
```

> Obtenha as chaves em:
> - context7: https://context7.com/
> - google-drive: Google Cloud Console
> - notebooklm: Google AI Studio

### Passo 6: Testar a Skill

Abra o terminal e diga:

```
Iniciar novo projeto chamado meu-teste
```

O agente deve:
1. Perguntar os 6 itens (nome, domínio, objetivo, KPI, stack, tipo)
2. Criar a estrutura de pastas
3. Gerar GEMINI.md + ANTIGRAVITY.md
4. Criar `.gemini/settings.json` com MCPs
5. Inicializar Git

---

## 📁 Estrutura Final Após Instalação

### No Sistema

```
C:\\Users\\victor.bernardi\\
├── .gemini/
│   └── skills/
│       └── stout-init/
│           ├── SKILL.md
│           ├── references/
│           │   ├── gemini-local-template.md
│           │   └── antigravity-template.md
│           └── scripts/
│
├── .antigravity/
│   └── skills/
│       └── stout-init/
│           ├── SKILL.md
│           ├── references/
│           │   ├── gemini-local-template.md
│           │   └── antigravity-template.md
│           └── scripts/
│
└── .shared-ai-memory/
    └── context-agent/
        ├── sessions/
        └── projects/          ← Junction aponta para cá
```

### Em Cada Novo Projeto

```
C:\\Projetos\\Stout\\meu-projeto\\
├── GEMINI.md              ← Contexto de negócio
├── ANTIGRAVITY.md         ← Kernel operacional
├── README.md              ← Visão geral
├── .env.example           ← Variáveis de ambiente
├── .gitignore             ← Git ignore
├── .gemini/
│   └── settings.json      ← MCPs: context7, google-drive, notebooklm
├── docs/                  ← Junction → memory/context-agent/projects/meu-projeto/
│   ├── specs/
│   ├── plans/
│   └── adr/
├── src/                   ← Código-fonte
├── data/                  ← Dados e queries
├── tests/                 ← Testes
└── scripts/               ← Automações
```

---

## 🛠️ USO DA SKILL

### Comandos de Ativação

Diga qualquer um destes ao agente:
- "Iniciar novo projeto chamado [nome]"
- "Criar projeto [nome]"
- "Scaffoldar projeto [nome]"
- "Novo projeto [nome]"

### O Que a Skill Pergunta (6 itens)

1. **Nome do projeto:** (kebab-case, ex: analise-frota-jd)
2. **Domínio de negócio:** (Pós-Venda, Data Science, Automação, etc.)
3. **Objetivo principal:** (o que o projeto resolve)
4. **KPI principal:** (como medir sucesso)
5. **Stack tecnológica:** (Python, React, Node.js, etc.)
6. **Tipo de projeto:** (API, Dashboard, Automação, Análise, ML, Integração)

### O Que a Skill Cria Automaticamente

- ✅ GEMINI.md (contexto de negócio)
- ✅ ANTIGRAVITY.md (kernel operacional)
- ✅ `.gemini/settings.json` (MCPs configurados)
- ✅ README.md
- ✅ `.env.example` (inclui variáveis dos MCPs)
- ✅ `.gitignore`
- ✅ Estrutura de pastas (src, data, tests, scripts, docs)
- ✅ Junction de memória (se Antigravity + Windows)
- ✅ Git inicializado

---

## 🔧 TROUBLESHOOTING

### Problema: Skill não é reconhecida

**Solução:** Verifique se a pasta da skill está no local correto:
```bash
# Gemini CLI
ls ~/.gemini/skills/stout-init/SKILL.md

# Antigravity
ls ~/.antigravity/skills/stout-init/SKILL.md
```

### Problema: MCPs não conectam

**Solução:** Verifique se as variáveis de ambiente estão configuradas:
```bash
echo $CONTEXT7_API_KEY
echo $GOOGLE_DRIVE_API_KEY
echo $NOTEBOOKLM_API_KEY
```

### Problema: Junction não funciona no Windows

**Solução:** Execute o terminal como Administrador. O comando `mklink /J` requer privilégios elevados.

### Problema: GEMINI.md global não é herdado

**Solução:** Verifique se o arquivo está na pasta pai correta e se há um repositório Git inicializado (`git init`). O Gemini CLI busca até encontrar a raiz do repositório.

---

## 📚 REFERÊNCIAS

- **Gemini CLI Docs:** https://geminicli.com/docs/cli/gemini-md/
- **Gemini CLI Skills:** https://geminicli.com/docs/cli/creating-skills/
- **MCP Servers:** https://geminicli.com/docs/tools/mcp-server/
- **Context7 MCP:** https://mcp.directory/servers/context7
- **NotebookLM MCP:** https://mcpservers.org/servers/roomi-fields/notebooklm-mcp
- **Antigravity Tools:** `~/.antigravity/skills/process-superantigravity/references/gemini-tools.md`

---

**Versão:** 1.0  
**Data:** Maio 2026  
**Autor:** Perplexity AI para Victor Bernardi
"""

with open('output/ENTREGA_FINAL.md', 'w', encoding='utf-8') as f:
    f.write(entrega_final)

print("ENTREGA_FINAL.md criado com sucesso")
print(f"Tamanho: {len(entrega_final)} caracteres")
