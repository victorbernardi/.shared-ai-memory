---
name: brd-generator
version: 1.0.0
description: Use when you need to generate a Business Requirements Document (BRD). Guia a criação de documentos de requisitos de negócio, focando em objetivos, stakeholders e KPIs.
when_to_use: criar BRD, requisitos de negócio, escopo de projeto, business goals, KPIs, stakeholders mapping, product discovery
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

# brd-generator

Esta habilidade automatiza o processo de descoberta e documentação de requisitos de negócio para projetos de dados e software.

## Fluxo de Trabalho

### 1. Descoberta (AskUserQuestion)
Se as informações não estiverem disponíveis no contexto atual, pergunte ao usuário:
- **Objetivo Principal:** Qual problema estamos resolvendo?
- **Stakeholders:** Quem são os donos do processo e os usuários finais?
- **KPIs de Sucesso:** Como mediremos o sucesso (ex: redução de 10% no churn)?

### 2. Geração do Documento
Crie o arquivo `docs/business/BRD-YYYYMMDD-[slug].md` seguindo o template:

| Seção | Conteúdo Necessário |
|-------|---------------------|
| Executive Summary | Visão de 30 segundos do projeto. |
| Business Goals | Objetivos SMART. |
| Stakeholders | Matriz de responsabilidades (RACI simplificado). |
| Requirements | Lista priorizada de necessidades de negócio. |
| Success Metrics | KPIs técnicos e de negócio. |

## Regras de Excelência (Anti-Rationalization)
- **Não pule a validação:** Nunca gere um BRD sem confirmar os KPIs com o usuário.
- **Brevidade:** Mantenha o documento focado em resultados, não em implementação técnica (isso fica para a `spec-validation`).

## Related Skills
- **user-story-expert**: Use após o BRD para quebrar requisitos em tarefas executáveis.
- **doc-workflow-orchestrator**: Guia mestre do ciclo de vida.

## Instalação
```bash
# Instalado manualmente via writing-skills no ambiente Stout
```

## Comandos
| Comando | Descrição |
|---------|-----------|
| `/brd-generator` | Inicia o rito de criação do BRD |

## Governança e Segurança
- **Nível de Governança:** 1 (Logging).
- **Segurança:** Apenas escrita de arquivos de documentação.
