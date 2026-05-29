---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-finishing-a-development-branch
description: "Processo de finalização e integração de branches de desenvolvimento no ecossistema Stout. Garante a passagem de testes, detecção de ambiente e limpeza de worktrees. Triggers: finalizar branch, merge, pull request, fechar tarefa, concluir build."
version: 1.0.0
author: Arquiteto Stout
tier: 2
source: custom
date_added: "2026-05-16"
category: engineering
---

# 🏁 Stout Finishing a Development Branch

Esta skill guia a conclusão do trabalho de desenvolvimento, apresentando opções estruturadas para merge, PR ou descarte, garantindo a integridade do repositório.

## 🚀 Quando Usar

- Quando a implementação estiver completa e todos os testes passarem.
- Ao final de uma sessão de subagente ou sessão paralela de build.
- Para integrar o trabalho de volta à branch principal (`main`).

---

## 🔄 Fluxo de Trabalho

As diretrizes detalhadas de verificação de testes, detecção de ambiente (worktrees), opções de menu e protocolos de limpeza foram movidas para referências técnicas.

**CONSULTE OBRIGATORIAMENTE:** `@references/finishing-protocols.md` para guiar la integração.

---

## 📦 Instalação

Skill de engenharia local. Requer `git` instalado e configurado.

## 💻 Comandos

Para ativar via orquestrador local:

```bash
python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-finishing-a-development-branch
```text

## 🛡️ Governanca

- **Zero Failures:** Proibido prosseguir com merge ou PR se houver testes falhando.
- **Atomicidade:** Cada finalização deve corresponder a uma unidade lógica de trabalho.
- **Limpeza:** Worktrees de subagentes devem ser removidas após o merge bem-sucedido.

## When to Use

This skill is applicable to execute the workflow or actions described in the overview.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
