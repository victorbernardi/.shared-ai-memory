---
name: user-story-expert
version: 1.0.0
description: Use when you need to write or refine User Stories and Acceptance Criteria. Especialista em criar e refinar histórias de usuário, garantindo critérios de aceitação claros e conformidade com o padrão INVEST.
when_to_use: criar histórias de usuário, critérios de aceitação, backlog refinement, user stories, acceptance criteria, INVEST, agile, grooming
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

# user-story-expert

Esta habilidade refina o backlog técnico transformando requisitos abstratos em histórias de usuário prontas para desenvolvimento.

## Padrão de Escrita

### Formato Base
> **Como** [papel/persona]
> **Eu quero** [ação/funcionalidade]
> **Para que** [valor de negócio/benefício]

### Critérios de Aceitação (Gherkin ou Checklist)
- **Dado que** [contexto inicial]
- **Quando** [ação executada]
- **Então** [resultado esperado]

## Checklist de Qualidade (INVEST)
- **I**ndependent: Pode ser desenvolvida isoladamente?
- **N**egotiable: Deixa espaço para discussão técnica?
- **V**aluable: Agrega valor claro ao usuário?
- **E**stimable: O esforço é previsível?
- **S**mall: Pode ser concluída em um sprint?
- **T**estable: O critério de aceitação é verificável?

## Related Skills
- **brd-generator**: As histórias devem derivar do BRD.
- **spec-validation**: Valida se a implementação final atende aos critérios de aceitação.

## Comandos
| Comando | Descrição |
|---------|-----------|
| `/user-story` | Cria ou refina uma história de usuário |

## Governança e Segurança
- **Nível de Governança:** 1 (Logging).
- **Segurança:** Apenas leitura/escrita de arquivos Markdown.
