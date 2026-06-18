# Especificação Técnica: Restauração da Skill stout-spec-validation

> **ID da Spec:** SPEC-001
> **Título:** Restauração da Skill stout-spec-validation como oficial
> **Autor:** Gemini CLI / Antigravity Agent
> **Data:** 2026-06-18
> **Status:** Elaborada

## 1. Contexto e Motivação
A skill `stout-spec-validation` (localizada em `C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived\stout-spec-validation`) foi arquivada anteriormente em um lote de deprecaciação em 2026-06-18. 
O usuário solicitou explicitamente a restauração dessa skill para que ela volte a ser uma skill oficial ativa do ecossistema.

## 2. Objetivo
Restaurar fisicamente e logicamente a skill `stout-spec-validation` no repositório de memória global `C:\Users\victor.bernardi\.shared-ai-memory`, garantindo que:
1. Os arquivos da skill sejam movidos da pasta de arquivamento para a pasta ativa de skills.
2. O registro global de skills (`registry.json`) seja atualizado para refletir o status `"active"`.

## 3. Escopo e Alterações
As seguintes ações físicas e lógicas são necessárias:

### 3.1. Movimentação Física de Diretório
* **Origem:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived\stout-spec-validation`
* **Destino:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation`
* A pasta restaurada deve conter os seguintes arquivos originais:
  * `SKILL.md`
  * `references/check-list.md`
  * `references/id-system.md`

### 3.2. Atualização do Ledger (stout-skill-registry)
* **Arquivo:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`
* **Modificação:**
  * Localizar a entrada com `"name": "stout-spec-validation"`.
  * Alterar o campo `"status"` de `"deprecated"` para `"active"`.
  * Atualizar o campo `"updated_at"` para `"2026-06-18"`.
  * Atualizar o campo `"notes"` para `"Restaurada a pedido do usuário em 2026-06-18."`.

## 4. Critérios de Aceitação (AC)
- **AC-1:** A pasta `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-spec-validation` deve conter a estrutura original completa: `SKILL.md`, `references/check-list.md` e `references/id-system.md`.
- **AC-2:** A pasta de origem em `_archived\stout-spec-validation` não deve mais existir no local original (ou seja, deve ser completamente movida).
- **AC-3:** O arquivo `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json` deve conter a skill com `"status": "active"`, `"updated_at": "2026-06-18"` e nota condizente.
- **AC-4:** Validação sintática do JSON `registry.json` para garantir que continua válido após a edição.
