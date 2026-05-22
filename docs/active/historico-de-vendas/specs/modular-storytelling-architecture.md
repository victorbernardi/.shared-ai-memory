---
title: >-
  Arquitetura Modular de Storytelling para Diagnóstico de Vendas (v7.3)
category: synthesis
tags: [data-storytelling, architecture, inventory-health, python]
sources:
  - conversation:2026-05-13
created: 2026-05-13T16:40:00Z
updated: 2026-05-13T16:40:00Z
summary: >-
  Arquitetura de diagnóstico que decompõe relatórios monolíticos em módulos independentes seguindo uma narrativa de 5 estágios: Macro, Conflito, Deep Dive, Geografia e Resolução.
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: 2026-05-13
---

# Arquitetura Modular de Storytelling (v7.3)

## Contexto
O pipeline original de diagnóstico de vendas sofria de rigidez arquitetural (monolítico) e falta de integridade nos dados (duplicidades de SKUs por filial), o que dificultava a manutenção e a confiança executiva nos números.

## Finding / Decision
A transição para uma arquitetura modular baseada em **Storytelling** permite que cada página do relatório opere como um motor independente, facilitando a "lupa" sobre indicadores específicos sem afetar o fluxo global.

### A Narrativa de 5 Estágios:
1.  **Macro Overview (Setup):** Diagnóstico do GAP total (R$ 45M) e vitalidade do portfólio.
2.  **Dead Capital (Conflito):** Identificação de onde o capital está "sangrando" (Dropout + Excedente).
3.  **Popularity Decay (Deep Dive):** Análise de "Estrelas Cadentes" (Itens de alto giro que colapsaram).
4.  **Geografia do Abandono (Regional):** Mapeamento de calor para identificar gargalos geográficos (Foco: Contagem-MG).
5.  **Matriz de Recuperação (Resolução):** Lista acionável de SKUs com sugestão de "Alerta Ruptura" ou "Revisão Comercial".

## Princípios de Integridade
A **Consolidação por SKU** é mandatória. O `data_loader.py` deve agregar tanto faturamento quanto estoque pelo código do item (`ITEM`) antes de qualquer cálculo de dropout, garantindo a visão "Total Inova" e eliminando registros duplicados causados pela granularidade regional.

## Implicações
- **Escalabilidade:** Novos módulos (ex: Lupa de Clientes) podem ser acoplados ao `report_orchestrator.py` sem reescrever o motor gráfico.
- **Filtros CLI:** O motor suporta filtros dinâmicos (ex: `--subgrupo`) que propagam a filtragem para todos os módulos mantendo a narrativa.
- **Validação Visual:** Todo deploy de relatório exige a exportação de PNGs de validação para auditoria de layout (prevenção de cortes e sobreposições).

## Related
- [[sales-dropout-metrics]]
- [[inventory-health-kpis]]
- [[stout-data-storytelling-patterns]]
