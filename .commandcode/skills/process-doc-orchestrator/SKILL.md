---
name: doc-workflow-orchestrator
version: 1.0.0
description: Use when you need to manage the end-to-end documentation lifecycle of a project. Gerencia o ciclo de vida completo da documentação (Negócio -> Técnica -> Implementação), orquestrando o uso de skills complementares.
when_to_use: fluxo de documentação, ciclo de vida do projeto, documentação de ponta a ponta, orchestrate documentation, project lifecycle, documentation flow, master guide
allowed-tools: [Read, AskUserQuestion]
---

# doc-workflow-orchestrator

Esta habilidade rege a ordem de execução e a integridade do ecossistema de documentação no Stout.

## O Ciclo de Vida da Documentação (Stout Edition)

| Fase | Atividade | Skill Primária | Gatilho de Saída |
|------|-----------|----------------|-------------------|
| 1. Descoberta | Definição de Requisitos | `brd-generator` | BRD assinado/validado |
| 2. Refinamento | Quebra em User Stories | `user-story-expert` | Backlog INVEST pronto |
| 3. Arquitetura | Decisões Técnicas | `adr` | ADR aceito no repo |
| 4. Especificação | Detalhamento Técnico | `spec-validation` | Spec consistente com SOW |
| 5. Exploração | Onboarding/Navegação | `explore` | Estrutura de código mapeada |
| 6. Entrega | Relato de Impacto | `data-insight-reporter` | Insight acionável gerado |

## Regras de Orquestração (Anti-Rationalization)

1. **Não inverta a ordem:** Não comece um ADR ou Spec sem um BRD ou User Story validada. O negócio guia a técnica.
2. **Consistência é Lei:** Use a `spec-validation` sempre que o BRD ou ADR sofrer alterações significativas.
3. **Traceability:** Cada documento deve citar seu predecessor (ex: o ADR deve citar o ID do requisito no BRD).

## Como utilizar

Sempre que um novo projeto for iniciado ou uma funcionalidade grande for solicitada, invoque esta skill para mapear o status atual da documentação e planejar os próximos passos seguindo o ciclo de vida acima.

## Comandos
| Comando | Descrição |
|---------|-----------|
| `/doc-flow` | Exibe o status do workflow e recomenda a próxima skill |

## Governança e Segurança
- **Nível de Governança:** 2 (Review).
- **Segurança:** Apenas coordenação intelectual. Não executa alterações automáticas.
