---
title: Visão por Centro de Custos - Inova Daily
updated: 2026-05-22
category: business/inova-daily
tags:
  - business
  - inova-daily
  - centro-custos
  - faturamento
sources:
  - "docs/active/inova-daily/plano-visao-centro-custos.md"
summary: Visão gerencial pioneira do Inova Daily por Centro de Custo, agregando dados entre filial e cliente para melhor controle de carteiras e operações.
provenance:
  extracted: 1.0
  inferred: 0.0
  ambiguous: 0.0
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: "2026-05-22"
visibility: internal
---

# Visão por Centro de Custos

Esta é uma visão gerencial pioneira no Inova Daily, agregando faturamento por Centro de Custo (`DESCRICAO_CC`). O objetivo é preencher a lacuna entre a visão geográfica (filial) e a visão por cliente individual (CNPJ).

## Fonte de Dados
A fonte é o M2 (`cache_vendas_rfm.parquet`) via `faturamento.py`, garantindo reconciliação total com o faturamento consolidado.

## Estrutura da Classificação
O campo `DESCRICAO_CC` é normalizado considerando:
- **Eixos:** Operação (Peças, Serviço-MO, Contratos) + Carteira (CSN, CRC, WIRTGEN, etc.).
- **Tratamento de Nulos:** ~26% da receita está sem centro de custo no ERP. O relatório exibe obrigatoriamente a linha **"SEM CLASSIFICAÇÃO"** para garantir a reconciliação de 100% dos dados.

## Design do Bloco
O relatório exibe duas seções:
1. **Composição Peças × Serviços:** Saúde do core de negócio.
2. **Ranking de Carteiras:** Receita do dia, share e desvio vs. média diária do mês.

> [!NOTE]
> O e-mail do Inova Daily não utiliza emojis. A formatação segue o padrão textual (Markdown).
