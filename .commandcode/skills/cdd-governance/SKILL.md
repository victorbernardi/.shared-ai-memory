---
id: cdd-governance
name: CDD Governance
description: Gerencia e moderniza o ecossistema Stout utilizando Configuration-Driven Development (CDD). Permite o retrofit de projetos legados e auditoria global de regras.
level: 2
tags: [governance, cdd, automation, stout]
---

# CDD Governance — Gestão de Ecossistema

Esta skill é responsável por garantir que todos os projetos do ecossistema Stout (novos e legados) sigam os padrões de Configuration-Driven Development e possuam rastreabilidade via GCC.

## Quando Usar
- Para modernizar um projeto antigo ("retrofit").
- Para auditar se os projetos estão seguindo as regras globais.
- Para verificar a integridade da memória episódica (GCC) em múltiplos repositórios.

## Comandos Disponíveis

### 1. Retrofit (Modernizar Legado)
Injeta a "Pegada CDD" em um projeto que ainda não possui GCC ou roteamento de regras.

`powershell
python "C:\Users\victor.bernardi\.shared-ai-memory\skills\cdd-governance\scripts\retrofit.py" --path "C:\Caminho\Para\Projeto\Legado"
`

O que este comando faz:
- Cria a estrutura .GCC/branches/.
- Cria um data/config/rules.yaml local inicial.
- Atualiza o GEMINI.md do projeto para apontar para o motor global cdd_core.

### 2. Audit (Auditoria Global)
Verifica o status de todos os projetos registrados.

`powershell
python "C:\Users\victor.bernardi\.shared-ai-memory\skills\cdd_core\tools\sentinel_agent.py" --all
`

## Estrutura de Regras (Hierarquia)
Lembre-se que agora o sistema opera em dois níveis:
1. **Global (rules.yaml na raiz do CDD)**: Regras universais da Stout.
2. **Local (data/config/rules.yaml no projeto)**: Regras específicas para o contexto atual.

O motor faz o merge automático, priorizando regras locais em caso de conflito de ID.

