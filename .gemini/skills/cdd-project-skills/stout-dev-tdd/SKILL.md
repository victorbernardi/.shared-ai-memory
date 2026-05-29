---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-dev-tdd
description: "Motor de implementação técnica baseado em testes para o ecossistema Stout. Garante que nenhum código de produção nasça sem um teste que falhe primeiro. Triggers: implementar, build, bugfix, tdd, testes, pytest, red-green-refactor, iron law."
version: 1.3.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: engineering
---

# 🧪 Stout Dev TDD (Local Elite)

Esta skill é a autoridade técnica em desenvolvimento guiado por testes. Ela impõe a regra de que nenhum código de produção deve existir sem um teste que tenha falhado primeiro.

## 🚀 Quando Usar

- Em toda nova funcionalidade ou correção de bug.
- Durante a execução de planos via `stout-executing-plans`.
- Para garantir que o comportamento desejado seja validado deterministicamente.

---

## 🔄 Fluxo de Trabalho (Red-Green-Refactor)

Toda a inteligência técnica integral (350+ linhas), incluindo o ciclo Red-Green-Refactor, exemplos de testes, critérios de validação e anti-padrões, foi preservada e movida para o arquivo de referência técnica.

**CONSULTE OBRIGATORIAMENTE:** `@references/tdd-protocols.md` para guiar o desenvolvimento.

---

## 📦 Instalação

Skill integrada localmente ao projeto CDD. Requer `pytest` configurado no ambiente Python e acesso ao diretório `tests/`.

## 💻 Comandos

Para ativar esta skill via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-dev-tdd
```text

## 🛡️ Governanca

- **Iron Law:** Proibido código de produção sem teste falhando primeiro.
- **Simplicity First:** Implemente o código mínimo necessário para passar no teste. Evite abstrações especulativas.
- **Surgical Changes:** Toque apenas nos arquivos necessários para a tarefa. Não formate ou altere código adjacente.
- **Integridade:** Testes devem ser sistemáticos e não apenas "passagens acadêmicas".
- **Anti-padrões:** Consulte `@testing-anti-patterns.md` para evitar vícios de teste.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
