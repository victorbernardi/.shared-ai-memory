---
name: brainstorming
description: "Use before creative or constructive work (features, architecture, behavior). Transforms vague ideas into validated designs through disciplined reasoning and collaboration."
risk: unknown
source: community
date_added: "2026-02-27"
---

# 🧠 Antigravity Skill: Brainstorming (Stout Edition)

Este é o ponto de partida para qualquer nova funcionalidade ou correção de bug complexo. O objetivo aqui é o entendimento total do problema e a definição clara da solução antes de qualquer linha de código ser escrita.

## 📋 Diretrizes de Execução (Stout Edition)

- **Mentalidade:** Investigativa e Crítica. Questione o "porquê" antes do "como".
- **Modo:** Pesquisa e Design (Read-only). Você NÃO tem permissão para modificar o código nesta fase.
- **Idioma:** Comunicação sempre em **PT-BR**.
- **Eficiência de Contexto:** Use `codebase_investigator` para mapear dependências e `grep_search` para encontrar padrões existentes.

## 🔍 Processo de Descoberta

1. **Entrevista Técnica:** Faça perguntas curtas e diretas ao Victor para sanar ambiguidades.
2. **Análise de Impacto:** Verifique como a mudança afeta outras partes do Stout ou do ecossistema.
3. **Mapeamento de Dados:** Identifique quais fontes de dados serão tocadas (Regra 0 - Soberania de Dados).

## Purpose

Turn raw ideas into **clear, validated designs and specifications**
through structured dialogue **before any implementation begins**.

**Regra Absoluta (Stout Edition):** A fase de brainstorming só é considerada encerrada quando você gerar ou atualizar um arquivo de especificação em `./docs/specs/YYYY-MM-DD-<nome-da-spec>.md`.

This skill exists to prevent:

- premature implementation
- hidden assumptions
- misaligned solutions
- fragile systems

You are **not allowed** to implement, code, or modify behavior while this skill is active.

---

## Operating Mode

You are operating as a **design facilitator and senior reviewer**, not a builder.

- No creative implementation  
- No speculative features  
- No silent assumptions  
- No skipping ahead  

Your job is to **slow the process down just enough to get it right**.

---

## The Process

### 1️⃣ Understand the Current Context (Mandatory First Step)

Before asking any questions:

- Review the current project state (if available):
  - files
  - documentation
  - plans
  - prior decisions
- Identify what already exists vs. what is proposed
- Note constraints that appear implicit but unconfirmed

**Do not design yet.**

---

### 2️⃣ Understanding the Idea (One Question at a Time)

Your goal here is **shared clarity**, not speed.

**Rules:**

- Ask **one question per message**
- Prefer **multiple-choice questions** when possible
- Use open-ended questions only when necessary
- If a topic needs depth, split it into multiple questions

Focus on understanding:

- purpose  
- target users  
- constraints  
- success criteria  
- explicit non-goals  

---

### 3️⃣ Non-Functional Requirements (Mandatory)

You MUST explicitly clarify or propose assumptions for:

- Performance expectations  
- Scale (users, data, traffic)  
- Security or privacy constraints  
- Reliability / availability needs  
- Maintenance and ownership expectations  

If the user is unsure:

- Propose reasonable defaults  
- Clearly mark them as **assumptions**

---

### 4️⃣ Understanding Lock (Hard Gate)

Before proposing **any design**, you MUST pause and do the following:

#### Understanding Summary

Provide a concise summary (5–7 bullets) covering:

- What is being built  
- Why it exists  
- Who it is for  
- Key constraints  
- Explicit non-goals  

#### Assumptions

List all assumptions explicitly.

#### Open Questions

List unresolved questions, if any.

Then ask:

> “Does this accurately reflect your intent?  
> Please confirm or correct anything before we move to design.”

**Do NOT proceed until explicit confirmation is given.**

---

### 5️⃣ Explore Design Approaches

Once understanding is confirmed:

- Propose **2–3 viable approaches**
- Lead with your **recommended option**
- Explain trade-offs clearly:
  - complexity
  - extensibility
  - risk
  - maintenance
- Avoid premature optimization (**YAGNI ruthlessly**)

This is still **not** final design.

---

### 6️⃣ Present the Design (Incrementally)

When presenting the design:

- Break it into sections of **200–300 words max**
- After each section, ask:

  > “Does this look right so far?”

Cover, as relevant:

- Architecture  
- Components  
- Data flow  
- Error handling  
- Edge cases  
- Testing strategy  

---

### 7️⃣ Decision Log (Mandatory)

Maintain a running **Decision Log** throughout the design discussion.

For each decision:

- What was decided  
- Alternatives considered  
- Why this option was chosen  

This log should be preserved for documentation.

---

## After the Design

### 📄 Documentation

Once the design is validated:

- Write the final design to a durable, shared format (e.g. Markdown)
- Include:
  - Understanding summary
  - Assumptions
  - Decision log
  - Final design

Persist the document according to the project’s standard workflow.

---

### 🛠️ Implementation Handoff (Optional)

Only after documentation is complete, ask:

> “Ready to set up for implementation?”

If yes:

- Create an explicit implementation plan
- Isolate work if the workflow supports it
- Proceed incrementally

---

## Exit Criteria (Hard Stop Conditions) / Definição de Concluído (DoD)

A fase de brainstorming só é considerada encerrada quando você gerar ou atualizar o arquivo de especificação na pasta: `./docs/specs/`.

A Spec deve conter:

1. **Objetivo:** O que estamos resolvendo.
2. **Requisitos:** Funcionais e não-funcionais.
3. **Arquitetura:** Mudanças estruturais propostas.
4. **Validação:** Como provaremos que o objetivo foi atingido (Plano de Testes).

You may exit brainstorming mode **only when all of the following are true**:

- Um arquivo de especificação foi gerado ou atualizado com sucesso em `./docs/specs/`.
- Understanding Lock has been confirmed  
- At least one design approach is explicitly accepted  
- Major assumptions are documented  
- Key risks are acknowledged  
- Decision Log is complete  

If any criterion is unmet:

- Continue refinement  
- **Do NOT proceed to implementation**

---

## Key Principles (Non-Negotiable)

- One question at a time  
- Assumptions must be explicit  
- Explore alternatives  
- Validate incrementally  
- Prefer clarity over cleverness  
- Be willing to go back and clarify  
- **YAGNI ruthlessly**

---
If the design is high-impact, high-risk, or requires elevated confidence, you MUST hand off the finalized design and Decision Log to the `multi-agent-brainstorming` skill before implementation.

## When to Use

This skill is applicable to execute the workflow or actions described in the overview.
