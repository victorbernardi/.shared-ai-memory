---
# [STOUT-IMMUTABLE] - Protegido por trava física. Use apenas replace.
name: stout-governance-orchestration-engine
description: "Motor de governança para pre-flight checks (recência, ambiente, higiene) em pipelines analíticos Stout."
version: 1.0.0
author: Victor
tier: 1
source: custom
date_added: "2026-05-19"
category: engineering-governance
role: "Orquestrador de governança, recência e higiene para motores analíticos"
triggers:
  - "governance"
  - "recency"
  - "pre-flight"
  - "hygiene"
  - "orchestration"
---

# Governance Orchestration Engine

## Visão Geral
Esta skill implementa o protocolo de "Checklist de Decolagem" (Pre-flight) para os motores analíticos do ecossistema Stout. Ela garante que o ambiente, as fontes de dados e a higiene de execução estejam em conformidade com o Padrão Elite antes do processamento pesado.

## 🚀 Funcionalidades (Stout Standard)

### 1. Sensor de Recência (Data Recency Check)
- Analisa o arquivo `shared/recency_status.md`.
- Emite alertas visuais no console para fontes desatualizadas (🔴) ou ausentes (🔴).
- **Modo Padrão:** Informativo (não bloqueia, mas registra a irregularidade).

### 2. Guardião de Ambiente (Environment Guard)
- Verifica a integridade da ponte JVM/JDBC (Fabric Connector).
- Valida permissões de escrita em pastas de `cache/` e `data/`.
- Confirma a presença de configurações obrigatórias em `data/config/`.

### 3. Higiene de Execução (Execution Hygiene)
- Garante que o `stdout` e `run.log` estejam configurados para UTF-8.
- Registra o início da sessão no GCC (Global Context Control).
- Limpa artefatos temporários remanescentes de execuções falhas.

## 📦 Como Usar
Esta skill é acionada automaticamente pelo `SkillRouter` no início do pipeline se configurada no `rules.yaml`.

### Exemplo de Configuração (rules.yaml)
```yaml
  - id: 'check_governance'
    priority: 100
    enabled: true
    action:
      type: 'activate_skill'
      target: 'stout-governance-orchestration-engine'
      params:
        recency_check: true
        fail_fast: false
```

## 🛠️ Recursos Técnicos
- `scripts/preflight_check.py` — Script principal de validação.

## [LEI GLOBAL - KARPATHY LAWS]
1. **Higiene Total:** Dados inconsistentes devem gerar alertas imediatos.
2. **Soberania do shared:** O `shared/recency_status.md` é a única fonte de verdade para recência.
3. **Simplicidade:** A validação deve ser leve e não obstrutiva.
