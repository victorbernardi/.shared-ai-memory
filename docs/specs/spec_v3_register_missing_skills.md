# Especificação Técnica: Registro de Skills Ausentes no Ledger (v3)

> **ID da Spec:** SPEC-003
> **Título:** Registro de Skills Ausentes no registry.json
> **Autor:** Gemini CLI / Antigravity Agent
> **Data:** 2026-06-18
> **Status:** Elaborada

## 1. Contexto e Motivação
O ledger `registry.json` (em `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`) serve como a Fonte Única de Verdade (Single Source of Truth) para catalogar, auditar e orquestrar as skills do ecossistema Stout. 
No entanto, descobriu-se um gap significativo entre as pastas de skills fisicamente presentes no diretório `C:\Users\victor.bernardi\.shared-ai-memory\skills` (65 diretórios) e as registradas no ledger (33 ativas/deprecadas). Um total de 50 skills físicas não constavam no arquivo `registry.json`.

O objetivo desta especificação é mapear e realizar o registro em lote dessas 50 skills ausentes para alinhar o ledger com o estado físico atual do sistema.

## 2. Análise e Mapeamento
Executou-se um script de preflight (`analyze_missing_skills.py`) que varreu os diretórios de skills e realizou o parse automático do bloco YAML Frontmatter dos arquivos `SKILL.md` de cada pasta física.
Foram encontradas 50 skills não registradas, detalhadas no arquivo temporário `missing_skills.json`.

Entre as skills ausentes e mapeadas estão:
- `audio-transcriber`
- `brainstorming`
- `deep-research`
- `dispatching-parallel-agents`
- `executing-plans`
- `find-skills`
- `finishing-a-development-branch`
- `grill-me`
- `grill-with-docs`
- `handoff`
- `inova-bi-faturamento`
- `process-writing-skills` (como `writing-skills` no frontmatter)
- E outras skills da wiki e utilitários gerais.

## 3. Escopo das Modificações
As seguintes ações lógicas são exigidas:

### 3.1. Mesclagem de Registros no Ledger
* **Arquivo Alvo:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`
* **Operação:** 
  1. Carregar o arquivo `registry.json` existente.
  2. Ler a lista de novas entradas mapeadas em `missing_skills.json`.
  3. Acrescentar (append) as novas 50 entradas de skills no array `skills`.
  4. Atualizar o campo de cabeçalho `"last_updated": "2026-06-18"`.
  5. Gravar o JSON atualizado com formatação idêntica (indentação de 2 espaços).

## 4. Critérios de Aceitação (AC)
- [ ] O arquivo `registry.json` deve conter todas as 50 novas skills cadastradas e ativas.
- [ ] O arquivo `registry.json` deve ser um JSON válido que passe em validadores de sintaxe.
- [ ] O campo `last_updated` do ledger deve ser `"2026-06-18"`.
- [ ] Nenhuma skill existente deve ser removida ou ter seus metadados originais corrompidos/alterados incorretamente (preservar as marcas antigas de inativas/deprecated).
