# 📑 SOW & Especificação Técnica: Patch de Qualidade (stout-create-skill)

> **Status:** Fase de Pesquisa (Patch)
> **Data:** 2026-05-15
> **Versão:** 1.2.0 (Foco em Quality Gate e Templates)

---

## 1. Statement of Work (SOW)

### 1.1 Visão Geral

Este patch visa fechar as lacunas físicas e de governança identificadas na Fábrica (`stout-create-skill`). O objetivo é garantir que a geração de novas skills não dependa apenas da inteligência do subagente (generativo), mas que utilize âncoras físicas (Templates) e um porteiro de qualidade automatizado (Validator) para assegurar o Selo Stout.

### 1.2 In Scope

| Target | Observable Outcome |
| :--- | :--- |
| **Templates Físicos** | Pasta `templates/` populada com arquivos .md para Tier 1, 2, 3, 4 e casos de uso Stout (Data, NotebookLM) |
| **Validator Subagent** | Arquivo `agents/validator-agent.md` criado com instruções de auditoria de 7 camadas |
| **Quality Gate Config** | Arquivo `config/quality_gate.yaml` com as regras duras de validação |
| **Cleanup Script** | Arquivo `scripts/cleanup_on_failure.py` para limpeza de diretórios temporários em caso de erro |
| **Validação TDD** | Scripts de teste em `tests/` validando o comportamento pós-deploy da Fábrica |

### 1.3 Out of Scope

- Alteração no `stout-skill-registry` ou `stout-skill-auditor`. *Why not:* O foco deste patch é a completude interna da Fábrica.

### 1.4 Acceptance Criteria (AC)

| ID | Critério de Aceite | Observable Signal |
| :--- | :--- | :--- |
| **AC-1** | O Scaffolder deve ter acesso a templates reais para não alucinar estruturas. | Arquivos `.md` existem na pasta `templates/`. |
| **AC-2** | A skill criada deve ser auditada automaticamente antes do registro. | Log mostra execução do `validator-agent` retornando "PASS" ou "FAIL". |
| **AC-3** | Falhas na validação não devem deixar rastro no disco. | Diretório em `/tmp` é removido se o validador falhar. |

---

## 2. Especificação Técnica (Spec)

### 2.1 Requisitos Funcionais (FR)

| ID | Requisito | Implements |
| :--- | :--- | :--- |
| **FR-001** | O `code_drafter_agent` deve usar obrigatoriamente os arquivos em `templates/` como base de texto. | AC-1 |
| **FR-002** | O `validator_agent` deve implementar 7 gates (Frontmatter, Name, Desc, Examples, Constraints, Chmod, Secrets). | AC-2 |
| **FR-003** | O script `cleanup_on_failure.py` deve aceitar o parâmetro `--target` e realizar `shutil.rmtree` de forma segura. | AC-3 |

### 2.2 Requisitos Não-Funcionais (NFR)

| ID | Requisito | Alvo (Métrica) | Rationale | Validates |
| :--- | :--- | :--- | :--- | :--- |
| **NFR-001** | **Segurança** | Regex de segredos | Impede vazamento acidental de tokens nas novas skills. | AC-2 |
| **NFR-002** | **Robustez** | Idempotência de Limpeza | O script de limpeza não deve falhar se o diretório já não existir. | AC-3 |

---

## 3. Cenários de Teste (Test)

| ID | Descrição do Teste | FR | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **T-001** | Validação de Skill Malformada | FR-002 | O Validador retorna "FAIL" listando a falta de Exemplos ou Constraints. |
| **T-002** | Teste de Limpeza Pós-Falha | FR-003 | Pasta temporária é excluída após simulação de erro no validador. |
| **T-003** | Presença de Templates | FR-001 | Subagente consegue ler e citar trechos dos templates físicos. |

---

## 4. Traceability Matrix

| SOW AC | Spec FR | Spec NFR | Spec Test |
| :--- | :--- | :--- | :--- |
| AC-1 | FR-001 | - | T-003 |
| AC-2 | FR-002 | NFR-001 | T-001 |
| AC-3 | FR-003 | NFR-002 | T-002 |

---
*Assinado: Arquiteto Stout Inova*