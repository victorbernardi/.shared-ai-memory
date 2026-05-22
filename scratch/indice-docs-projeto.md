---
title: Indice de Documentos de Projeto
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Indice de specs, plans e walkthroughs dos repositorios Stout e Inova processados pelo superpowers_cleaner e ingeridos no vault.
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
tags: [indice, stout, inova, documentacao]
sources: [_raw/ (117 docs)]
---

## Sobre

Este indice referencia documentos de projeto processados pelo pipeline `superpowers_cleaner -> _raw/ -> wiki-ingest`. Os originais completos estao nos repositorios `C:/Projetos/Stout/` e `C:/Projetos/Inova/`.

## ADRs e Decisoes Tecnicas

- **0001-resilient-date-conversion-historical-sync**: Conversao resiliente de datas SQL com COALESCE+TRY_CONVERT para integracao de base historica. Resgate de R$ 13.3M em dados com 67% NaT.

## Motor Identidade (M0)

- **ecossistema-maestro-v10**: Arquitetura do ecossistema Maestro v10
- **implementacao-m0-v9-pops**: Implementacao M0 v9 com POPS
- **reativacao-c2-pops**: Reativacao da C2 POPS
- **shared-sync-v11-7**: Sincronizacao shared v11.7
- **correcao-bridges-laboratorio-m0**: Correcao de bridges no laboratorio M0
- **delta-qsa-scanner**: Scanner delta QSA paragrupos economicos

## Segmentacao e Potencial (M3)

- **segmentacao-granular-overlay**: Overlay de segmentacao granular
- **v1_segmentacao_hero**: Segmentacao Hero v1
- **v2_evolucao_segmentacao**: Evolucao da segmentacao v2
- **v1_ligar_m3**: Ativacao do Motor M3
- **v1_governanca_recencia_m3**: Governanca de recencia M3
- **v1_migracao_arquitetura_src_m3**: Migracao de arquitetura src/ M3
- **v1_validacao_granularidade_m3_m0**: Validacao de granularidade M3 vs M0
- **v2_ajuste_m3_feedback**: Ajuste M3 com feedback do M0
- **2026-05-20_03_potencial**: Consolidado Potencial Maio/2026

## Faturamento (M2)

- **m2-faturamento-elite**: Motor Faturamento Elite
- **m2-recency-governance**: Governanca de recencia M2
- **elite-migration-m2-sandbox**: Migracao Elite M2 sandbox

## DNA (M1)

- **dna_recency_v1**: Recencia DNA v1
- **v1_correcao_governanca_dna**: Correcao de governanca DNA

## Recencia e Governanca (M5)

- **m5-recency-governance**: Governanca de recencia M5
- **v1_governanca_recencia_m5**: Governanca de recencia M5 v1
- **validacao-recencia-cevap**: Validacao de recencia CEVAP

## BUP (Pos-Venda)

- **transicao-identidade-bup**: Transicao de identidade para BUP
- **filtro_bi_orcamentos_abertos**: Filtro BI de orcamentos abertos
- **vendedores_ativos_2026**: Vendedores ativos 2026

## Infraestrutura Stout

- **elite-migration-cdd**: Migracao Elite para CDD
- **otimizacao-performance-superantigravity**: Otimizacao de performance SuperAntigravity
- **2026-05-20_fix-stout-promote-antigravity-brain-path**: Fix do stout-promote para path do Antigravity Brain
- **v1_stout_init_retrofit**: Retrofit do stout-init

## Dashboard e Insights (M6)

- **v1_filtro_consultores**: Filtro de consultores
- **v6_consultant_filter**: Filtro de consultores v6
- **design-capa-executiva**: Design de capa executiva
- **v1_mineracao_insights**: Mineracao de insights
- **insight_log**: Log de insights

## Relatorios e Emails

- **relatorio-roberto-executivo**: Relatorio executivo Roberto
- **relatorio-roberto-semana-1**: Relatorio Roberto Semana 1
- **roberto-summary-email**: Email sumario Roberto
- **EMAIL_ENTREGA_CAMPANHA_UBERLANDIA**: Email campanha Uberlandia
- **RELATO_IMPACTO_UBERLANDIA**: Relato de impacto Uberlandia
- **WALKTHROUGH_UBERLANDIA_2026**: Walkthrough Uberlandia 2026

## Walkthroughs e Consolidados

- **2026-05-11-walkthrough-shared-sync**: Walkthrough shared sync
- **2026-05-12_05-motor-identidade**: Motor Identidade Maio/2026
- **2026-05-12_Inova**: Consolidado Inova Maio/2026
- **2026-05-13-walkthrough-consolidacao-infra-stout**: Consolidacao infra Stout
- **2026-05-13-walkthrough-otimizacao-performance-superantigravity**: Otimizacao SuperAntigravity
- **2026-05-13-walkthrough-transicao-bup**: Walkthrough transicao BUP
- **2026-05-13_Stout**: Consolidado Stout Maio/2026
- **walkthrough_2026-05-20_03_potencial**: Walkthrough Potencial Maio/2026
- **walkthrough_20260520_regras_status_consultor**: Walkthrough regras status consultor
- **walkthrough_v4_validacao_datas_motores**: Walkthrough validacao datas motores

## Conceitos e Feedback (Claude)

- **concept_claude_feedback_antigravity_context_agent_paths**: Feedback paths context-agent
- **concept_claude_feedback_baseline_vs_schema**: Baseline vs Schema
- **concept_claude_feedback_credentials_pattern**: Padrao de credenciais
- **concept_claude_MEMORY**: Conceito MEMORY.md
- **concept_claude_project_antigravity_reset**: Reset Antigravity
- **concept_claude_project_context_agent**: Projeto context-agent
- **concept_claude_project_docs_centralizados**: Docs centralizados
- **concept_claude_project_fabric_connector**: Fabric connector
- **concept_claude_project_faturamento_schema_slim**: Schema slim faturamento
- **concept_claude_project_knowledge_graph_pending**: Knowledge graph pendente
- **concept_claude_project_llm_wiki_reforma**: Reforma LLM wiki
- **concept_claude_project_opencode_transition**: Transicao OpenCode
- **concept_claude_project_pendencias_paths**: Pendencias e paths
- **concept_claude_project_quarentena_pre_migration**: Quarentena pre-migration
- **concept_claude_project_shared_modules_location**: Localizacao shared modules
- **concept_claude_project_token_rotation_pending**: Token rotation pendente
- **concept_claude_project_tracking_agent_pending**: Tracking agent pendente
- **concept_claude_project_validate_pipeline**: Validacao pipeline

## Dicionarios e Schemas

- **DICIONARIO_OUTPUT**: Dicionario de output
- **granularidade-filiais**: Granularidade de filiais
- **performance-filial-motion**: Performance filial motion
- **PLANO_VALIDACAO_LAB**: Plano de validacao laboratorio
- **lista-clientes-integral**: Lista de clientes integral
- **v2_lista_clientes_integral**: Lista clientes v2
- **v3_lista_clientes_detalhada**: Lista clientes v3 detalhada
- **v4_refinamento_filiais**: Refinamento de filiais v4
- **v5_unificacao_pipeline**: Unificacao pipeline v5
- **v4_validacao_datas_motores**: Validacao datas motores v4
- **auditoria-reparo-encoding**: Auditoria reparo encoding
- **mcp_test_report**: Relatorio de teste MCP

## Conceitos relacionados

[[motores-inova]], [[motor-identidade]], [[motor-dna]], [[motor-faturamento]], [[pipeline-inova]], [[bup-auto-orcamentos-fabric]], [[governanca-recencia]], [[insight-engineering-executivo]], [[journal-abril-maio-2026]], [[wiki-compiler]]
