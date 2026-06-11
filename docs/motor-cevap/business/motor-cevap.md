---
title: Motor CEVAP
category: business
tags:
  - business/projects
  - intelligence/engine
  - churn/prevention
sources:
  - docs/business/BRD-20260506-motor-cevap.md
updated: 2026-05-16
summary: Engine de inteligência comercial para reativação de clientes da base Inova inativos há mais de 90 dias.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: 2026-05-16
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
---

# Motor CEVAP

O **Motor CEVAP** é uma engine de inteligência comercial projetada para identificar e priorizar clientes da [[Base Inova]] que estão inativos há mais de 90 dias. O sistema visa a [[Reativação Inteligente]] de clientes, focando na redução do [[Churn]] e no aumento da eficiência comercial.

## Objetivos de Negócio
- **Redução do Churn:** Identificar precocemente clientes em risco de abandono.
- **Eficiência Comercial:** Priorizar leads de alto potencial.
- **Saneamento de Base:** Garantir qualidade nos dados de contato.

## Stakeholders
- **Accountable:** [[Filipe]] (Comercial)
- **Responsible:** [[Victor Bernardi]] (Dados)
- **Consulted:** [[Roberto]] (Estratégia)
- **Informed:** [[Time de Vendas]]

## Requisitos Técnicos
- Cálculo a nível de Grupo Econômico (CNPJ Raiz).
- Elegibilidade baseada na unidade com maior faturamento histórico.
- Exclusão de leads sem identificação e oportunidades em negociação.
- Enriquecimento de dados com [[Frota]], [[Seedz]], e [[Inovapay]].

## KPIs de Sucesso
- Taxa de Reativação
- Volume Recuperado (R$)
- Acurácia Identidade
- Eficiência Filtro
