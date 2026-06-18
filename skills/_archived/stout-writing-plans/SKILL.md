---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-writing-plans
description: "Transformação de especificações técnicas em planos de execução atômicos e rastreáveis para o ecossistema Stout. Triggers: planejar execução, implementar plano, roteiro de tarefas, atomicidade, plano de execução, roadmap técnico."
version: 1.2.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: design
---

# 🧠 Stout Writing Plans (Local Elite)

Esta skill é responsável por transformar uma especificação técnica (Spec) em um plano de execução detalhado, seguro e atômico.

## 📋 Diretrizes de Execução (Stout Edition)

- **Pré-requisito:** Só inicie o plano se localizar uma **Spec aprovada** na pasta `./docs/specs/`. Se não existir, use `/stout-brainstorming`.
- **Modo Nativo (Plan Mode):** É OBRIGATÓRIO invocar a ferramenta `enter_plan_mode` do Gemini CLI para formular o plano de forma segura e não destrutiva.
- **Alinhamento Nativo (Task List):** Após gerar o arquivo Markdown do plano, você DEVE invocar a ferramenta `write_todos` para registrar cada tarefa atômica na lista visual do CLI (`Ctrl+T`).
- **Goal-Driven Execution:** Cada tarefa do plano deve incluir um critério de sucesso verificável (Ex: "Rodar teste X e obter Pass").
- **Atomicidade:** Decomponha em tarefas de 2-5 minutos.
- **Rastreabilidade:** Cite caminhos exatos dos arquivos.

---

## 🔄 Fluxo de Trabalho
As diretrizes detalhadas de cabeçalho, estrutura de tarefas e modo de espera foram movidas para o arquivo de referência técnica para otimização de contexto.

**CONSULTE OBRIGATORIAMENTE:** `@references/plan-format.md` para gerar o plano.

---

## 📦 Instalação
Skill integrada localmente ao projeto CDD.

## 💻 Comandos
Para ativar via orquestrador local:
```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-writing-plans
```

## 🛡️ Governanca
- Nenhum plano deve ser gerado sem Spec prévia aprovada.
- Exige o "Modo de Espera" (Standby) após a geração do plano.

## When to Use
This skill is applicable to execute the workflow or actions described in the overview.
