# Implementation Plan: Upgrade de Elite (stout-improve-skill)

> **Status:** STANDBY - Aguardando Aprovação
> **Data:** 2026-05-15
> **Versão:** 1.2.0

## 1. Estratégia de Transição
O upgrade será focado na integração profunda dos motores analíticos do Sentinel e do Reviewer externo no coração do Melhorador.

## 2. Fases de Execução (Ciclo Build)

| Fase | Descrição | Depends |
| :--- | :--- | :--- |
| **Fase A** | Integração do Sentinel Core em `diag_runner.py`. | - |
| **Fase B** | Atualização dos Subagentes com Heurísticas de Elite. | Fase A |
| **Fase C** | Implementação de Padrões de Refatoração (Lock, Packaging, O(1)). | Fase B |
| **Fase D** | Validação TDD: Auto-refatoração do Melhorador para V1.2.0. | Fase C |

### Detalhamento:

**Fase A (Diagnóstico de Elite):**
- Modificar `diag_runner.py` para carregar dinamicamente os analisadores na pasta `scripts/sentinel_core/`.
- Gerar relatório consolidado com categorias: Qualidade, Segurança, Performance, Arquitetura.

**Fase B (Treinamento de Agentes):**
- Injetar no `code_optimizer_agent.md` as "Melhores Práticas de 2025" (Base AI-Review).
- Ensinar o agente a identificar e propor correções para O(n) e Race Conditions.

**Fase C (Assets):**
- Criar a pasta `references/refactoring_patterns.md` com trechos de código de exemplo para Lock de Arquivos e SemVer Robusto.

**Fase D (O Teste de Fogo):**
- Usar a própria `stout-improve-skill` para se auto-diagnosticar e aplicar as melhorias, subindo sua própria versão no Ledger.

## 3. Human-in-the-Loop
O ponto de interrupção HITL em `apply_patch.py` permanece obrigatório.

---
*Aguardando autorização para iniciar a Fase de Execução (Build).*