# Especificação Técnica: Arquivamento de Skills Específicas (v2)

> **ID da Spec:** SPEC-002
> **Título:** Arquivamento das Skills find-skills, subagent-driven-development e process-writing-skills
> **Autor:** Gemini CLI / Antigravity Agent
> **Data:** 2026-06-18
> **Status:** Elaborada

## 1. Contexto e Motivação
O usuário solicitou o arquivamento de três skills específicas localizadas no diretório do usuário:
- `C:\Users\victor.bernardi\.gemini\skills\find-skills`
- `C:\Users\victor.bernardi\.gemini\skills\subagent-driven-development`
- `C:\Users\victor.bernardi\.gemini\skills\process-writing-skills`

Para manter a conformidade com as regras de governança e organização do ecossistema Stout, em vez de deletar fisicamente, essas skills serão movidas para a subpasta `_archived/` sob o diretório principal de skills.

## 2. Escopo e Alterações
As seguintes ações físicas são necessárias:

### 2.1. Movimentação Física de Diretórios
Os diretórios de origem abaixo serão movidos de forma atômica para o diretório de arquivo:
* **Skill 1:**
  * **Origem:** `C:\Users\victor.bernardi\.gemini\skills\find-skills`
  * **Destino:** `C:\Users\victor.bernardi\.gemini\skills\_archived\find-skills`
* **Skill 2:**
  * **Origem:** `C:\Users\victor.bernardi\.gemini\skills\subagent-driven-development`
  * **Destino:** `C:\Users\victor.bernardi\.gemini\skills\_archived\subagent-driven-development`
* **Skill 3:**
  * **Origem:** `C:\Users\victor.bernardi\.gemini\skills\process-writing-skills`
  * **Destino:** `C:\Users\victor.bernardi\.gemini\skills\_archived\process-writing-skills`

Se a pasta correspondente de destino já existir dentro de `_archived/`, ela será removida ou substituída para evitar conflitos de arquivos.

### 2.2. Atualização do Ledger (stout-skill-registry)
A entrada de `stout-subagent-driven-development` no ledger `registry.json` já está marcada como `"deprecated"`. As outras duas skills (`find-skills` e `process-writing-skills`) não estão explicitamente registradas no `registry.json`. Desta forma, não há necessidade de atualização do ledger nesta operação de arquivamento além de registrar a movimentação e a data.

## 3. Critérios de Aceitação (AC)
- [ ] Os diretórios das três skills especificadas devem ser movidos fisicamente para o diretório `_archived`.
- [ ] O diretório principal de skills (`C:\Users\victor.bernardi\.gemini\skills\`) não deve mais conter os diretórios originais das três skills listadas.
- [ ] Nenhum arquivo deve ser excluído de forma irrecuperável; todos os subarquivos e referências das pastas arquivadas devem estar presentes nas respectivas pastas de destino sob `_archived`.
