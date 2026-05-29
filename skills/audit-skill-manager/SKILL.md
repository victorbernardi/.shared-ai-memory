---
name: skill-manager
description: Use when you need to install, update, or list Antigravity agent skills using skillfish.
metadata:
  category: operation
  version: 1.0.0
  triggers: install skill, update skills, list skills, add-habilidade, skillfish
---

# [DEPRECADO] Skill Manager

> **Esta skill foi substituída por `stout-skill-manager` em 2026-05-29.**
> Use `/stout-skill-manager` para buscar, instalar e gerenciar skills com pipeline completo
> de auditoria, validação e controle de qualidade.
> Este arquivo será removido em 30 dias (2026-06-28).

## Overview

Interface para gerenciamento do ecossistema de habilidades do agente Antigravity utilizando a ferramenta CLI skillfish.

## When to Use

- Quando o usuário solicita a adição de uma nova skill via repositório GitHub.
- Quando há necessidade de atualizar as habilidades instaladas para as versões mais recentes.
- Quando é necessário listar as capacidades atuais do agente.

**NÃO usar para:**

- Modificar o código interno de uma skill existente (use `writing-skills`).
- Deletar arquivos de sistema do Antigravity.

## Step-by-Step

1. **Adicionar Skill:**
   - Execute `skillfish add [usuario/repositorio] --project`.
   - Se os arquivos forem baixados para `.claude/skills`, mova-os para a pasta `./skills/` do seu workspace atual para mantê-los visíveis ao Antigravity.
2. **Atualizar Skills:** Execute `skillfish update`.
3. **Listar Skills:** Execute `skillfish list`.

## Disciplina e Auditoria (Anti-Rationalization)

**REGRA CRÍTICA:** Após qualquer instalação ou atualização de skills no diretório `./skills/`, você DEVE invocar a habilidade **`skill-sentinel`** imediatamente para auditar os novos arquivos antes do uso.

## Quick Reference

| Comando | Ação |
|---------|------|
| `add` | Instala uma nova skill do GitHub |
| `update` | Atualiza todas as skills locais |
| `list` | Mostra o que está instalado |

## Instalação

Esta habilidade depende do binário global `skillfish`.

```bash
npm i -g skillfish
```

## Governança e Segurança

- **Nível de Governança:** 1 (Logging).
- **Audit Log:** Toda instalação é registrada pelo Antigravity através do histórico de conversas.
- **Segurança:** O Skillfish baixa habilidades de repositórios públicos. O uso da `skill-sentinel` é obrigatório para mitigar riscos de injeção de código ou instruções maliciosas.
