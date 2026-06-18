# Detalhamento de Peças — Especificação Técnica do Scraper de Devoluções (Power BI)

**Data:** 2026-06-17  
**Versão:** 1.2  
**Status:** Ready for Dev  
**Autor:** Antigravity (Stout AI Engineer)

---

## 1. Declaração de Escopo (SOW / Acceptance Criteria)

Abaixo estão definidos os critérios de aceitação acordados com o usuário comercial para a extração da tabela de devoluções:

* **AC-1:** O scraper de devoluções deve exportar a tabela "Detalhamento das Devoluções" do PBI e salvar os dados consolidados em `shared/data/detalhamento_devolucoes_2025-2026.parquet`.
* **AC-2:** O schema obrigatório e válido do parquet de devoluções deve ser idêntico ao de vendas, contendo as colunas: `Nota Fiscal`, `Data Emissão` e `CNPJ`.
* **AC-3:** O range de extração de devoluções é fixo e cobre de `01/01/2025` até a data atual, sempre full-load (sobrescrevendo o arquivo anterior).
* **AC-4:** Validar a integridade de dados usando threshold de 10% baseado na variação da soma da coluna `Valor Bruto` (mesma referência de vendas).
* **AC-5:** O scraper de devoluções deve residir em arquivo separado (`src/extract_devolucoes.py`) para isolamento de lógica, e rodar de forma isolada na arquitetura de estágios ICM (estágios 01 a 05).

---

## 2. Requisitos Técnicos e Funcionais

| ID | Requisito Funcional | Implements | Critério de Aceitação |
|----|---------------------|------------|-----------------------|
| **FR-001** | Script Scraper Separado | AC-1, AC-5 | Criar `src/extract_devolucoes.py` contendo a automação Playwright focada na tabela de devoluções, buscando o título do visual: `h3:has-text("Detalhamento das Devoluções")`. |
| **FR-002** | Filtro Fixo 2025-Hoje | AC-3 | Implementar lógica de data no novo scraper que aplica o filtro `01/01/2025` a `hoje` no slicer de data do Power BI. |
| **FR-003** | Transformação e Schema | AC-2 | Implementar limpeza de rodapés e validação das colunas `Nota Fiscal`, `Data Emissão`, `CNPJ` no DataFrame de devoluções bruto. |
| **FR-004** | Validação de Threshold Duplo | AC-4 | Calcular a soma de `Valor Bruto` no DataFrame de devoluções novo e no anterior; validar que a variação é <= 10% (a menos que `--forcar-validacao` seja passado). |
| **FR-005** | Persistência Física | AC-1 | Gravar arquivo parquet final em `shared/data/detalhamento_devolucoes_2025-2026.parquet`. |
| **FR-006** | Adaptação ICM Sequencial | AC-5 | Alterar os estágios ICM (`02_extrair`, `03_transformar`, `04_validar`, `05_persistir`) e `run.py` para processar ambas as entidades (Vendas e Devoluções) sequencialmente. |
| **FR-007** | Registro de Governança | AC-1 | Registrar `detalhamento_devolucoes_2025-2026.parquet` no validador `shared/generate_recency_report.py`. |

---

## 3. Requisitos Não-Funcionais

| ID | Requisito Não-Funcional | Validates | Rationale / Target |
|----|-------------------------|-----------|--------------------|
| **NFR-001** | Tempo de execução | AC-5 | A extração adicional com sessão isolada do Playwright não deve acrescer mais de 60s ao pipeline principal. |
| **NFR-002** | Governança Central | AC-1 | O parquet final gerado deve ser atualizado no arquivo de controle central `shared/recency_status.md` com marca verde de integridade. |

---

## 4. Cenários de Teste

| ID | Cenário de Teste | FR | Assertiva de Validação |
|----|------------------|----|-----------------------|
| **T-001** | Extração de Devoluções E2E | FR-001, FR-002 | Execução isolada do Playwright baixa arquivo xlsx contendo a tabela correta no range de datas correto. |
| **T-002** | Limpeza de Metadata e Schema | FR-003 | DataFrame final de devoluções não contém rodapés e tem todas as 3 colunas obrigatórias. |
| **T-003** | Validação de Gate Financeiro | FR-004 | O runner de validação de threshold emite `passed: false` caso a soma do `Valor Bruto` varie mais de 10% vs o histórico. |
| **T-004** | Persistência de Dados e Recência | FR-005, FR-007 | Execução completa grava o arquivo final e roda o script de recência atualizando o markdown central sem falhas. |

---

## 5. Matriz de Rastreabilidade

| SOW / AC | Requisito Funcional | Cenário de Teste | Requisito Não-Funcional |
|----------|---------------------|------------------|-------------------------|
| **AC-1** | FR-001, FR-005, FR-007 | T-001, T-004 | NFR-002 |
| **AC-2** | FR-003 | T-002 | - |
| **AC-3** | FR-002 | T-001 | - |
| **AC-4** | FR-004 | T-003 | - |
| **AC-5** | FR-001, FR-006 | T-001, T-004 | NFR-001 |

---

## 6. Arquitetura do Fluxo ICM Integrado

O pipeline será executado de forma síncrona e sequencial em cada estágio:

```
[01_autenticar]
      ↓ (Verifica sessão ativa em state.json)
[02_extrair]
      ├── 1. Executa extract.py (Vendas do ano solicitado) ──> data/output/vendas_bruto_{ano}.xlsx
      └── 2. Executa extract_devolucoes.py (Devoluções 2025-hoje) ──> data/output/devolucoes_bruto.xlsx
      ↓
[03_transformar]
      ├── 1. Transforma e limpa vendas (limpar_metadata_powerbi) ──> df_vendas_limpo
      └── 2. Transforma e limpa devoluções (limpar_metadata_powerbi) ──> df_devolucoes_limpo
      ↓
[04_validar] (GATE DUPLO)
      ├── 1. Valida threshold de Vendas (soma de Valor Bruto vs anterior <= 10%)
      ├── 2. Valida threshold de Devoluções (soma de Valor Bruto vs anterior <= 10%)
      └── 3. Se ambas passarem, escreve audit.json indicando liberação
      ↓
[05_persistir]
      ├── 1. Grava shared/data/detalhamento_vendas_{ano}.parquet
      ├── 2. Grava shared/data/detalhamento_devolucoes_2025-2026.parquet
      └── 3. Executa subprocess para generate_recency_report.py
```

---

## 7. Decision Log

| Decisão | Alternativas Consideradas | Razão da Escolha |
|---------|---------------------------|------------------|
| **Script `extract_devolucoes.py` separado** | Integrar tudo em `extract.py` | Separação de responsabilidades. Facilita testes isolados, manutenção de seletores do PBI e clareza na estrutura. |
| **Sessão Playwright Isolada** | Reutilizar a página aberta | Embora reutilizar a aba poupe ~30s, os seletores de filtros de data e cliques consecutivos em tabelas diferentes na mesma página do PBI são altamente propensos a glitches visuais. A sessão isolada garante 100% de estabilidade técnica. |
| **Consolidação em Parquet Único** | Parquet separado por ano | Volume de devoluções baixo simplifica o consumo se mantido em arquivo único. |

---

## 8. Riscos e Mitigações

* **R-1 (Mudança de layout no PBI):** Título ou botão de mais opções da tabela de devoluções mudarem.
  * *Mitigação:* Usar localizadores flexíveis no Playwright e salvar logs detalhados com screenshots de erro automáticos.
* **R-2 (Timeout de rede ou renderização):** O carregamento da página PBI para o segundo scraper falhar.
  * *Mitigação:* Implementar a mesma estratégia de retry automático (3 tentativas com backoff exponencial) usada para vendas.
