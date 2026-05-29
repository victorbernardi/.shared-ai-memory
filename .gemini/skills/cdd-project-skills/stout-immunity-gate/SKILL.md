---

# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.

name: stout-immunity-gate
description: "Autoridade Máxima de Governança Técnica e Protocolo de Imunidade. Monitora erros de execução, falhas de preflight e violações de integridade de arquivos."
version: 1.2.0
author: Victor
tier: 1
source: custom
date_added: "2026-05-14"
category: governance
---

<EXTREMELY-IMPORTANT>
O stout-immunity-gate é a Autoridade Máxima de Governança Técnica.
Sua função é APENAS garantir que o sistema não viole o Protocolo de Imunidade a Erros.
NÃO execute comandos de build, design ou especificação. Delegue essas tarefas ao cdd-builder.
</EXTREMELY-IMPORTANT>

## 🛡️ Protocolo de Imunidade (Stout Standard)

Sempre que um comando falhar ou um comportamento inesperado ocorrer, este protocolo é ativado automaticamente:

1. **Trava Física (Audit Gate):** Criação do `.audit_gate`. Nenhuma modificação permitida enquanto o gate existir.
2. **Modo de Auditoria:** Bloqueio total de escritas (`write/replace`) para proteção do estado do projeto.
3. **Delegação (Context Wall):** Ativação obrigatória da skill `systematic-debugging` para gerenciar a crise.

### 🛡️ Guardrail de Imutabilidade (Antigravity Guard)

O sistema detecta e bloqueia preventivamente:

- Uso de `write_file` em arquivos que já existem (ID: `guardrail_governance_rule`).
- Se o validador `src/core/guardrail.py` falhar, o sistema entra em **Lockdown** imediato.
- **Resolução:** O agente deve analisar o `failure-log.md`, remover o `.audit_gate` e realizar a edição usando a ferramenta `replace`.

## 🚀 Quando Usar

- Quando ocorrer um erro de execução (Exit Code != 0).
- Quando houver falha de integridade ou violação de imutabilidade.
- Quando o sistema entrar em lockdown via audit-gate.
- Para gerenciar travamentos e falhas críticas de governança.

## 🔗 Arquitetura de Delegação (O QUE NÃO FAZER)

- **NÃO FAÇA:** Planejamento, Brainstorming, Spec, Build, Deploy.
- **FAÇA:** Delegue todas as atividades de ciclo de vida acima para o `cdd-builder`.
- **Validação:** Consulte obrigatoriamente a MCP `context7` para documentação de libs.
- **Registro:** Escreva em `notes/failure-log.md` qualquer falha técnica.

## 🛠️ Regras de Execução (CLI Protocol)

O Orquestrador impõe as diretrizes do `docs/governance/protocolo_ferramentas_cli.md`:

- **Imutabilidade:** Proibido `write_file` em arquivos existentes. Use apenas `replace`.
- **Atomicidade:** Toda alteração estrutural deve ser precedida por um ADR.
- **Bypass Seguro:** A flag `--bypass-gate` é permitida exclusivamente para correções no núcleo do sistema (pasta `src/core/`).

## 📦 Instalação

Skill integrada nativamente ao motor CDD. Requer `src/core/guardrail.py` e `src/core/write_guard.ps1`.

## 📚 Referências

- [Protocolo de Ferramentas CLI](docs/governance/protocolo_ferramentas_cli.md)
- [ADR-0006: Protocolo de Imunidade](docs/decisions/ADR-0006-protocolo-imunidade.md)

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todas as camadas de documentação e interação.

## Escopo

Esta skill se aplica a sessões de desenvolvimento no ecossistema Stout.
