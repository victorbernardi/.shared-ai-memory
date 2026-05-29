---
name: skillfish
version: 1.0.0
tier: 2
category: meta-governance
description: >
  Use quando o usuário quer buscar, pesquisar, encontrar ou instalar skills
  via skillfish CLI. Descobre skills compatíveis com o ecossistema Stout,
  gerencia instalação com validação de estrutura e usa sempre o path canônico.
tools:
  - claude-code
  - antigravity
  - commandcode
  - gemini-cli
triggers:
  - buscar skills npm
  - instalar skill
  - pesquisar skills
  - skillfish search
  - skillfish add
author: Victor
---

# skillfish

## Objetivo

Descobrir, avaliar e instalar Agent Skills via CLI `skillfish`. Abstrai a busca por skills
compatíveis com o ecossistema Stout Inova, garantindo que toda instalação use o path canônico
`.shared-ai-memory/skills/` — nunca os paths de junction diretamente.

<!-- @if platform=claude -->

## Fluxo Detalhado

### Busca

```bash
skillfish search <query>
```

Apresentar resultados com nome, fonte, descrição e contagem de installs.
Verificar qualidade antes de recomendar: preferir skills com 1K+ installs e fonte conhecida.

### Instalação

1. Confirmar com o usuário antes de prosseguir
2. Executar via `scripts/install.py` (garante path canônico e validação Stout):

```bash
python scripts/install.py --package <owner/repo> --skill-name <nome>
```
1. O script roda `junction_guard.py` antes de qualquer escrita
2. Valida presença de `SKILL.md` e frontmatter (`name`, `version`) pós-download
3. Informa sucesso ou falha com detalhes acionáveis

### Atualização e Listagem

```bash
skillfish update    # atualiza todas as skills instaladas
skillfish list      # lista skills instaladas
```

## Exemplos

**Busca:**
Input: `"pesquise skills de debugging"`
Ação: `skillfish search debugging`
Output: Lista de skills com nome, fonte e install count

**Instalação:**
Input: `"instale anthropics/skills@tdd"`
Ação: `python scripts/install.py --package anthropics/skills@tdd --skill-name tdd`
Output: Skill instalada em `.shared-ai-memory/skills/tdd/` — disponível nas 3 plataformas

<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->

## Fluxo

1. **Busca:** `skillfish search <query>` — apresenta resultados ao usuário
2. **HITL:** confirmar skill e aguardar aprovação do usuário
3. **Instalação:** `python scripts/install.py --package <repo> --skill-name <nome>`
4. **Resultado:** skill disponível em todas as plataformas via junction

<!-- @endif -->

## Constraints

- NUNCA instalar sem confirmação explícita do usuário
- NUNCA escrever via paths de junction — sempre usar path canônico `.shared-ai-memory/skills/`
- SEMPRE validar estrutura Stout (SKILL.md + frontmatter) pós-download
- NÃO sobrescrever skills existentes sem `--force` explícito
- NUNCA instalar skill com veredito `REJECTED` pelo `stout-skill-auditor`

## Scripts disponíveis

- `scripts/search.py` — busca no npm registry via API + filtra compatibilidade Stout
- `scripts/install.py` — instala via skillfish CLI com path canônico + validação Stout
