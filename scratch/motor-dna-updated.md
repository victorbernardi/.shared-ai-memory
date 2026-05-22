---
title: Motor DNA (Engenharia de Identidades)
created_at: 2026-04-17
updated_at: 2026-05-21
summary: Sistema de engenharia de identidades usando chassi como elo do grafo. Alinhado ao padrao de governanca M0 com fail-fast e validacao de schema.
base_confidence: 1.0
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
sources: [session_audit_20260519.md]
tags: [inova, motor-dna, identity, graph]
---

## O que e
O Motor DNA e o sistema de engenharia de identidades e compressao de cadastro do projeto Inova. Sua inovacao tecnica e utilizar o **Chassi do equipamento como elo do Grafo**, cruzando o CNPJ da nota fiscal de venda original com o CNPJ que de fato abre as ordens de servico.

## Como uso no meu trabalho
- **Correcao Potencial Zero (D1/D2)**: Padronizacao das labels D1_LEAD_POPS e D2_ORFAO_TOTAL no motor DNA para evitar colisao na raiz 00000000.
- **Compressao Societaria**: Aglutinacao de CNPJs em Grupos Economicos (Conta Pai), eliminando fragmentacao de filiais homonimas.
- **Identificacao de Frotas**: Mapeamento de proprietarios reais atraves da telemetria e historico de manutencao.
- **Deteccao de Maquinas Cegas**: Equipamentos com menos de 10 horas anuais recebem a tag "ESTIMADA" e sao tratados com potencial proporcional.
---
- **Auditoria M1→M0 [2026-05-19]**: Motor DNA alinhado ao padrao de governanca do Motor Identidade (M0). Implementado `seo_dna_ingest_fabric.py` com fail-fast (validacao de schema e payload). Orquestracao `seo_dna_update_pipeline.ps1` com log de auditoria. Bugs de importacao corrigidos com ajuste dinamico de `sys.path`.

## KPIs Tecnicos
- **Match Rate**: 95,66% (2.934 chassis atrelados aos donos na base ativa).
- **Eficiencia de Compressao**: 98,7% (719.044 linhas brutas compactadas em 1 linha por Conta Pai).

## Licoes da Auditoria (2026-05-19)

- Nao assumir isolamento de projetos — sempre auditar Motor de Referencia (M0) antes de implementar em motores derivados (M1)
- Orquestracao deve validar `recency_status.md` antes de prosseguir; fail-fast comeca na orquestracao
- TDD nao e opcional — bateria de testes salvou o pipeline de deployar com erros de importacao

## Conceitos relacionados
[[motor-identidade-m0]], [[auditoria-granularidade-societaria]], [[dicionario-dados-inova]], [[governanca-recencia]], [[seo-ge-scanner]]
