---
title: BUP Auto Extracao Orcamentos Fabric
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Plano para substituir exportacao manual do PowerBI por script Python que consulta VS1010 no Fabric e gera xlsx de orcamentos abertos e cancelados.
base_confidence: 0.92
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
tags: [bup, fabric, automacao, inova]
sources: [bup-auto-1-extrair-orcamentos-fabric.md]
---

## O que e

Script `extract_orcamentos.py` que consulta a tabela VS1010 no Microsoft Fabric e gera os arquivos `tabela_orcamentos_abertos.xlsx` e `tabela_orcamentos_cancelados.xlsx` em `shared/data/`, substituindo a exportacao manual do PowerBI. BUP e CEVAP continuam lendo os mesmos caminhos.

## Arquitetura

- **ETL puro**: conecta ao Fabric via `ConexaoFabric`, executa queries, salva xlsx
- **Sem logica de negocio**: apenas replica o schema que o PowerBI ja exportava
- **Join SA1010**: para nome do cliente e filial

### Schemas

**Abertos:** Num Orc, Filial, Cliente, Data Abertura, Data Validade, Reservado, Orc. em Aberto, Tempo Orc em Aberto

**Cancelados:** Codigo da Peca, Numero Orc, Cliente, Filial, Data Orc, Canceladas, Motivo Cancelado

## Tabelas Fabric envolvidas

| Tabela | Conteudo |
|--------|----------|
| VS1010 | Cabecalho de orcamentos Protheus |
| SA1010 | Cadastro de clientes (join VS1_CLIFAT / VS1_LOJA) |
| VS2010 | Itens do orcamento (possivel fonte de cancelados por peca) |

## Implementacao (TDD)

1. **Task 1**: Explorar VS1010 — mapear campos de status e motivo
2. **Task 2**: Implementar `extrair_abertos()` e `extrair_cancelados()` com testes
3. **Task 3**: Smoke test com dados reais + validacao contra BUP

## Conceitos relacionados

[[bup-recency-integration]], [[governanca-recencia]], [[pipeline-inova]], [[motores-inova]], [[microsoft-fabric]]
