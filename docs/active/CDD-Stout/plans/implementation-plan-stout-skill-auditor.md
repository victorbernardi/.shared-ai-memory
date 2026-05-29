# Implementation Plan: stout-skill-auditor

> **Status:** Em Planejamento
> **Data:** 2026-05-15
> **Versão:** 1.0.0

## 1. Visão Geral

Construir a skill `stout-skill-auditor`, o "Porteiro" do ecossistema. Ele deve impedir a criação de habilidades redundantes analisando a intenção do usuário contra o `stout-skill-registry` antes de permitir o acesso à `stout-create-skill` (A Fábrica).

## 2. Estrutura de Arquivos

A skill seguirá o Tier 3 Platform Pattern:

```text
skills/stout-skill-auditor/
├── SKILL.md
├── config/
│   ├── similarity_threshold.yaml
│   └── role_definitions.yaml
├── scripts/
│   ├── semantic_overlap.py
│   └── role_conflict_checker.py
└── references/
    ├── decision_criteria.md
    └── overlap_examples.md
```text

## 3. Fases da Implementação

### Fase A: Estruturação Física e Governança

1. Criar as pastas `/config`, `/scripts` e `/references`.
2. Redigir os documentos de referência (`decision_criteria.md` e `overlap_examples.md`) detalhando como o cálculo de sobreposição funciona e exemplos práticos para balizar a IA.
3. Criar os arquivos YAML de configuração (`similarity_threshold.yaml` e `role_definitions.yaml`).
4. Escrever o `SKILL.md` com instruções rígidas (caixa alta) sobre a obrigatoriedade de emitir um arquivo `audit_result.json` e as opções de roteamento.

### Fase B: Desenvolvimento de Scripts Python

1. **`semantic_overlap.py`**:
   - Conectar-se ao `registry.json` da skill `stout-skill-registry`.
   - Comparar strings e metadados (`role`, `triggers`, `description` básica).
   - Gerar um score (heurístico) de similaridade.
   - Retornar o veredito sugerido.
2. **`role_conflict_checker.py`**:
   - Um check rápido e exato para evitar que a mesma frase de papel (`role`) seja submetida.

### Fase C: Testes Locais e Homologação

1. Simular uma intenção redundante ("criar uma skill que gerencia o ledger de skills"). O script deve retornar "REJECTED" e apontar para a `stout-skill-registry`.
2. Simular uma intenção nova ("skill de pipeline de dados com dbt"). O script deve retornar "APPROVED".
3. Verificar a correta emissão do artefato `audit_result.json`.

### Fase D: Registro

1. Executar o `register_skill.py` (da `stout-skill-registry`) para cadastrar o recém-criado `stout-skill-auditor` no ecossistema.

---
*Assinado: Arquiteto Stout Inova*