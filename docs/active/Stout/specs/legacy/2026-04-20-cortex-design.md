# Spec: Córtex — Agente de Evolução do Ecossistema Inova AI

**Data:** 2026-04-20
**Autor:** Victor Bernardi
**Status:** Aprovado

---

## Propósito

O Córtex é o agente de inteligência do ecossistema — responsável por auditar a qualidade do conhecimento, pesquisar formas de melhoria via especialistas externos (NotebookLM) e gerar recomendações acionáveis. Ele libera o Wiki Compiler para ser um compilador puro, sem lógica de análise.

---

## Separação de Responsabilidades

| Agente | Responsabilidade |
|---|---|
| **Wiki Compiler** | Ingestão, merge, escrita de notas, atualização do INDEX. Fases 0–3 do SCHEMA apenas. |
| **Córtex** | Linting de qualidade, pesquisa em especialistas NLM, sugestões de evolução, retroalimentação do ecossistema. |

**Mudança no SCHEMA.md:** Remover Fase 4a (linting) e Fase 4b (sugestões proativas). O Wiki Compiler deixa de ter responsabilidade de análise — apenas compila.

---

## Taxonomia de NotebookLMs

O Córtex distingue dois tipos de notebook:

| Prefixo | Domínio | Quando consultar |
|---|---|---|
| `Estudo - LLM *` | Especialista técnico em IA | Agentes, modelos, arquitetura, prompting, padrões de build |
| `Estudo - Negócio - *` | Especialista de mercado | Concessionárias, John Deere, linha amarela, estratégia comercial |
| `INOVA *` | Projeto (estado atual) | Contexto do ecossistema construído |

O prefixo "Estudo" é automaticamente ignorado pelo Wiki Compiler quando a fonte é um agente — a taxonomia já está protegida.

---

## Regra de Output por Tipo de Nota

A distinção não é sobre permissão de pesquisa — o Córtex pesquisa qualquer nota. A distinção é sobre **onde o resultado vai**:

| `tipo` da nota | Pesquisa? | Destino do output |
|---|---|---|
| `tipo: referencia` | ✅ Sim | Merge direto na nota wiki (enriquece conhecimento externo) |
| `tipo: projeto` | ✅ Sim | `SUGESTOES-HOJE.md` como sugestão — **nunca** escreve de volta na nota como fato consumado |
| Sem tipo (ausente) | ❌ Não pesquisa | Apenas linting estrutural |

**Novo campo de frontmatter:** `tipo: sugestao` — usado em handoffs gerados pelo Córtex para notas de projeto. O Wiki Compiler roteia arquivos com `tipo: sugestao` exclusivamente para `SUGESTOES-HOJE.md`, nunca para merge em nota existente.

**Propagação de `tipo:` nas notas compiladas:** O SCHEMA deve propagar o campo `tipo:` do arquivo `_pending/` para o frontmatter da nota compilada. Notas compiladas sem `tipo:` são tratadas como `projeto` pelo Córtex (default conservador).

---

## Estrutura da Skill

```
~/.gemini/antigravity/skills/cortex/
├── SKILL.md               ← comportamento, protocolo de execução, registry
├── notebook_registry.json ← índice de especialistas com domínio e "quando usar"
└── trigger.bat            ← Windows Task Scheduler (23h diário)
```

### notebook_registry.json

```json
{
  "specialists": [
    {
      "id": "8547b961-ce03-45b6-97eb-bfb097b6e121",
      "title": "Estudo - LLM",
      "domain": "llm",
      "when": "LLMs, arquitetura de agentes, prompting, padrões de build"
    },
    {
      "id": "62d0a21a-eb14-451c-9d31-0cdeea59ad7b",
      "title": "Estudo - LLM 2",
      "domain": "llm",
      "when": "LLMs, multi-agent systems, avaliação, otimização"
    },
    {
      "id": "4ed4e779-28b8-4bee-b178-fdbe17625d48",
      "title": "Estudo - LLM3",
      "domain": "llm",
      "when": "LLMs, knowledge graphs, wiki patterns, linting"
    },
    {
      "id": "732b512a-cc94-4f01-ad26-746475b2722e",
      "title": "Estudo - LLM4",
      "domain": "llm",
      "when": "LLMs, evaluation layers, observabilidade"
    }
  ],
  "projects": [
    {
      "id": "987bb91c-86a3-4a9a-a3db-4dbaa150bd18",
      "title": "INOVA",
      "domain": "inova",
      "when": "Estado atual do ecossistema Inova AI"
    }
  ]
}
```

Notebooks `Estudo - Negócio - *` serão adicionados conforme criados.

---

## Fluxo de Execução

```
Task Scheduler → trigger.bat (08h diário)
  ↓
gemini --approval-mode=yolo -p "@cortex"
```

**Configuração do Task Scheduler:**
- Horário: 08:00 diário
- Opção obrigatória: "Run task as soon as possible after a scheduled start is missed"
- Comportamento: se o computador estiver desligado às 8h, o Córtex roda assim que ligar — sem retry manual necessário

### Fase 1 — Linting de Qualidade

Varre todas as notas em `wiki/INDEX.md`:

1. **Links órfãos:** `[[referência]]` sem página correspondente → cria handoff em `_pending/` para nova nota
2. **Conteúdo raso:** nota com seção `## Como uso no meu trabalho` vazia ou `## O que e` com menos de 3 linhas → candidata à Fase 3
3. **Contradições:** dois arquivos com informações conflitantes sobre o mesmo conceito → adiciona flag na nota e entra em `SUGESTOES-HOJE.md`

### Fase 2 — Contexto de Sessão

Lê (nesta ordem):
- `wiki/hot.md` — o que foi feito na última sessão
- `context-agent/data/sessions/session-NNN.md` (últimas 3) — o que foi construído recentemente
- `antigravity/knowledge/global_context_memory/artifacts/MEMORY.md` — projetos ativos

Monta um resumo: "o que construímos recentemente + o que está em progresso".

### Fase 3 — Pesquisa Especialista (Orchestrator Pattern)

Para cada candidata da Fase 1 + tópicos do contexto de sessão:

1. **Classifica domínio** pelo conteúdo e tags da nota:
   - Tags `[ia, llm, agente, embedding, rag, prompt]` → domínio `llm`
   - Tags `[negócio, mercado, john-deere, concessionária]` → domínio `negocio`
   - Outros → pula pesquisa especialista

2. **Seleciona notebooks** via `notebook_registry.json` (Progressive Context Loading — lê apenas metadados primeiro)

3. **Loop iterativo por notebook** (máximo 5 turnos):
   - Injeta: conteúdo atual da nota + resumo da sessão recente
   - Pergunta: "Como podemos melhorar isso? O que está faltando? Qual próximo passo faz sentido?"
   - Avalia resposta:
     - **Acionável + novo** (não está no INDEX, não foi sugerido recentemente) → materializa
     - Caso contrário → aprofunda com pergunta de follow-up
   - Para ao atingir 5 turnos ou ao encontrar insight válido

### Fase 4 — Materialização

Para cada insight válido gerado:

**Se nota é `tipo: referencia`:**
- Cria handoff em `_pending/` com conteúdo enriquecido
- Wiki Compiler fará merge na nota existente

**Se nota é `tipo: projeto`:**
- Adiciona entrada em `SUGESTOES-HOJE.md`:
  ```
  - [Como poderíamos melhorar X] — [[nome-da-nota]] — fonte: Córtex
  ```
- **Nunca** gera handoff que modifique a nota de projeto diretamente

**Para lacunas (notas ausentes):**
- Cria handoff em `_pending/` com nova nota (sem `tipo:` = wiki compiler trata como projeto)

**Retroalimentação NLM:**
- Adiciona handoffs gerados como novas fontes nos notebooks relevantes via `source_add`
- Fecha o loop: NLM → análise → nota → NLM

**Ao final:**
- Sobrescreve `wiki/SUGESTOES-HOJE.md`
- Salva cópia datada em `wiki/historico/sugestoes-YYYY-MM-DD.md`

---

## Critério de Parada do Loop

Um insight é válido quando atende **ambos**:

1. **Acionável:** gera pelo menos uma de:
   - Recomendação concreta de melhoria de código/skill/agente
   - Conteúdo para enriquecer nota de referência
   - Nova nota para lacuna identificada

2. **Novo:** não está no `INDEX.md` nem aparece em `SUGESTOES-HOJE.md` recente (últimas 7 dias — verificar `historico/`)

Máximo por execução: **5 turnos por notebook**, **3 insights materializados**.

---

## Mudanças no SCHEMA.md (Wiki Compiler)

1. **Remover Fase 4a** — linting transferido ao Córtex
2. **Remover Fase 4b** — sugestões proativas transferidas ao Córtex
3. **Adicionar regra na Fase 3:** propagar campo `tipo:` do arquivo `_pending/` para o frontmatter da nota compilada
4. **Adicionar tratamento de `tipo: sugestao`:** arquivos com esse tipo em `_pending/` → apenas append em `SUGESTOES-HOJE.md`, nunca merge em nota existente

---

## Fora de Escopo

- O Córtex não modifica notas de projeto diretamente — apenas sugere
- O Córtex não cria agentes ou skills — apenas recomenda criação via `SUGESTOES-HOJE.md`
- O Córtex não acessa internet — apenas os NotebookLMs configurados
- Notebooks sem prefixo `Estudo` não são consultados como especialistas

---

## Relação com o Ecossistema

```
Antigravity session
  → Trigger Gamma → _pending/
    → Wiki Compiler (Fases 0-3) → notas wiki + INDEX.md

Task Scheduler (23h)
  → Córtex
    → Fase 1: linting de INDEX.md
    → Fase 2: contexto de sessão (hot.md + sessions)
    → Fase 3: pesquisa em Estudo - LLM / Estudo - Negócio
    → Fase 4: handoffs → _pending/ + SUGESTOES-HOJE.md + source_add NLM
      → Wiki Compiler (próximo ciclo) processa handoffs
        → notas enriquecidas + retroalimentação NLM
```
