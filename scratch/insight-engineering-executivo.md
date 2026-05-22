---
title: Insight Engineering Executivo
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Framework para construcao de relatorios executivos diarios em texto puro com foco em acoes corretivas, leitura em 3 minutos e alta confiabilidade de dados.
base_confidence: 0.75
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.7
  inferred: 0.2
  ambiguous: 0.1
tags: [inova, dados, reporting, estrategia]
sources: [v2_insight_engineering.md]
---

## O que e

Framework operacional para construir relatorios executivos diarios (tipo Daily Executive Intelligence Report) enviados por email em texto puro/Markdown para diretoria de pos-venda. Foco em leitura em 3 minutos, acoes corretivas e confiabilidade de dados.

## Pilares do framework

### SCQA (McKinsey)

Estrutura narrativa top-down:
- **S**ituation: Onde estamos (baseline pacifico)
- **C**omplication: O que mudou (gatilho)
- **Q**uestion: O que resolver (tensao)
- **A**nswer: Acao recomendada

### So What Test (3 camadas)

Aplicar "E dai?" tres vezes a cada metrica. Se nao gerar acao sugerida, o dado nao entra no relatorio. Ex: acesso ao portal subiu 15% → campanha funcionou → conversao caiu → frete alto → **acao: nivelar tabela de frete**.

### Action Priority Matrix

| Quadrante | Acao |
|-----------|------|
| Quick Win (alto impacto, baixo esforco) | Executar hoje |
| Major Project (alto impacto, alto esforco) | Planejar no trimestre |
| Fill-in (baixo impacto, baixo esforco) | Delegar |
| Thankless Task (baixo impacto, alto esforco) | Suspender |

### Confidence Score

Cada insight recebe nivel de confianca explicito:
- Alta: dados diretos do ERP
- Media: anotacoes manuais
- Baixa: inferencia ou dados de campo

### Anchor Numbers

Nunca apresentar numero isolado. Ex: "12 falhas no modelo X, **3x maior** que a media historica para o periodo."

## KPIs criticos (pos-venda heavy equipment)

- **Parts Absorption Rate**: lucro bruto da oficina / despesas fixas (alvo > 85%)
- **Share of Wallet**: fatia do orcamento de manutencao do frotista dentro de casa
- **Parts Leakage**: frotistas que sumiram do balcao (mercado paralelo)

## Conceitos relacionados

[[pipeline-inova]], [[inova-sales-insight-agent]], [[data-science-governance-risks]], [[customer-profitability-analysis]]
