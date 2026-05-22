# 📑 SOW & Especificação Técnica: stout-improve-skill (V1.2.0 - Elite Upgrade)

> **Status:** Fase de Pesquisa (Upgrade)
> **Data:** 2026-05-15
> **Versão:** 1.2.0 (Integração Sentinel + AI-Review)

---

## 1. Statement of Work (SOW)

### 1.1 Visão Geral
Este upgrade transforma o `stout-improve-skill` em um **Melhorador de Elite**. Ele deixa de realizar apenas diagnósticos estruturais básicos e passa a incorporar as 7 dimensões da `skill-sentinel` e a profundidade arquitetural da `code-review-ai-ai-review`. O objetivo é que o Melhorador consiga identificar e corrigir falhas de concorrência, performance e padrões de código avançados de forma autônoma.

### 1.2 In Scope

| Target | Observable Outcome |
| :--- | :--- |
| **Diagnóstico Multi-Dimensional** | `diag_runner.py` invoca analisadores de Performance, Segurança e Qualidade (Base Sentinel) |
| **Deep Code Analysis** | Subagentes treinados com heurísticas de SOLID, DRY e Segurança (Base AI-Review) |
| **Fixes Complexos** | Capacidade de implementar Locks de arquivo, migração de bibliotecas e otimização de busca O(1) |
| **Integração de Laudos** | Consolidação de achados internos e externos em um plano de refatoração único |

### 1.3 Out of Scope
- Auditoria de custos (Token ROI). *Why not:* Manter foco em integridade técnica e governança.

### 1.4 Acceptance Criteria (AC)

| ID | Critério de Aceite | Observable Signal |
| :--- | :--- | :--- |
| **AC-1** | O diagnóstico identifica riscos de concorrência e falhas de SemVer. | Relatório de diagnóstico exibe seções de "Performance" e "Arquitetura". |
| **AC-2** | O orquestrador propõe a inclusão de bibliotecas ou travas de segurança. | Plano de refatoração (HITL) inclui código de `threading.Lock` ou `packaging.version`. |
| **AC-3** | O registro no Ledger reflete a melhoria de elite. | `notes` no `registry.json` indicam "Refatoração de Elite V1.2.0 aplicada". |

---

## 2. Especificação Técnica (Spec)

### 2.1 Requisitos Funcionais (FR)

| ID | Requisito | Implements |
| :--- | :--- | :--- |
| **FR-001** | O `diag_runner.py` deve importar e executar as classes da pasta `sentinel_core/`. | AC-1 |
| **FR-002** | O orquestrador deve enviar um "Context Briefing" para o subagente incluindo as melhores práticas de IA-Review. | AC-2 |
| **FR-003** | O subagente `code_optimizer` deve suportar a escrita de blocos de código multi-threaded e gestão de estado. | AC-2 |

### 2.2 Requisitos Não-Funcionais (NFR)

| ID | Requisito | Alvo (Métrica) | Rationale | Validates |
| :--- | :--- | :--- | :--- | :--- |
| **NFR-001** | **Exatidão** | Falso Positivo < 10% | O diagnóstico deve ser preciso para não sugerir refatorações inúteis. | AC-1 |
| **NFR-002** | **Segurança** | Sanidade de Patches | O código sugerido não deve quebrar a compatibilidade Windows (encoding). | AC-3 |

---

## 3. Cenários de Teste (Test)

| ID | Descrição do Teste | FR | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **T-001** | Diagnóstico de Concorrência | FR-001 | O Melhorador aponta falta de Lock no `registry.json`. |
| **T-002** | Sugestão de Refatoração de Classe | FR-002 | O subagente sugere transformar lógica procedural em POO para conformidade SOLID. |
| **T-003** | Validação de SemVer Robusto | FR-003 | O código gerado utiliza `packaging.version` em vez de split de strings. |

---

## 4. Traceability Matrix

| SOW AC | Spec FR | Spec NFR | Spec Test |
| :--- | :--- | :--- | :--- |
| AC-1 | FR-001 | NFR-001 | T-001 |
| AC-2 | FR-002, FR-003 | NFR-002 | T-002, T-003 |
| AC-3 | - | - | - |

---
*Assinado: Arquiteto Stout Inova*