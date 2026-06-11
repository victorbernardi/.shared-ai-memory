---
name: adr-data-contracts-schema-sensor
description: "Decision record for adopting active schema validation (Data Contracts) to prevent downstream pipeline breaks."
version: 1.0.0
author: Antigravity AI
date: 2026-06-08
category: architecture
status: accepted
---

# 🏗️ ADR — Governança Ativa de Schemas (Data Contracts)

## 1. Contexto e Problema
Durante a refatoração do motor M3 (03_Potencial), identificou-se que a coluna Horimetro_Final gerava ambiguidade (parecendo ser um valor absoluto em vez de uma taxa anual). Ao renomear esta coluna para Horimetro_Anual_Final e adicionar a nova coluna Horimetro_Total_Acumulado, surgiu um risco sistêmico: quebrar o contrato de dados esperado pelos motores consumidores a jusante (downstream), como o M4 (Estratégia) e M5 (Segmentação).

Até o momento, a esteira analítica não possuía um catálogo centralizado para garantir a estabilidade das colunas, dependendo inteiramente de busca textual (grep) no repositório para mapear dependências (blast radius). Isso tornava o pipeline vulnerável a falhas silenciosas.

## 2. Decisão Arquitetural
Adotamos uma abordagem de **Validação Ativa (Active Schema Governance)** via a implementação de um schema_sensor.py na camada compartilhada (/shared).

1. **Dicionário de Contratos:** O módulo schema_sensor.py centraliza a definição das colunas "Ouro" obrigatórias para os principais artefatos exportados (ex: m3_potencial_chassi e m3_potencial_clientes).
2. **Execução Strict (Fail-Fast):** Os runners de cada estágio (ex: un.py no M3) devem instanciar o schema_sensor.validate_schema em modo strict=True **antes** de gravar qualquer Parquet ou Excel em disco.
3. **Bloqueio de Propagação:** Se um desenvolvedor alterar as rotinas de transformação e acidentalmente remover ou renomear uma coluna que faz parte do contrato, o pipeline abortará a gravação lançando a exceção SchemaViolationError.

## 3. Consequências

### Positivas (Benefícios)
- **Segurança M2M (Machine-to-Machine):** Quebras de integridade são detectadas na origem (M3) antes de poluírem o shared/data e derrubarem os motores consumidores (M4/M5).
- **Auto-documentação:** O dicionário CONTRACTS em schema_sensor.py serve como a fonte de verdade viva para o Data Lineage da esteira.
- **Auditoria Instantânea:** Facilita a manutenção do código, garantindo que refatorações não alterem o output esperado pelas demais áreas do negócio.

### Negativas (Trade-offs)
- **Atrito Adicional (Friction):** Qualquer nova coluna obrigatória exigirá uma atualização dupla (na rotina de exportação do motor e no dicionário do schema_sensor).

## 4. Rastreabilidade ICM (Stout Edition)
*   Esta decisão afeta diretamente as saídas documentadas no CONTEXT.md do M3.
*   Cumpre o princípio de anti-fragilidade e fail-fast da arquitetura Inova.
