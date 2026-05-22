# Spec: Geração de Relatórios Multi-Output e Visão Total (FR-001 a FR-003)

**Data:** 2026-05-13
**Versão:** 1.1
**Status:** Validada

## 1. Objetivo
Modernizar o motor de geração de PDF para suportar a exportação simultânea de dois relatórios (Consolidado e Página 1) e expandir a visão de subgrupos para 100% do portfólio, garantindo a integridade visual da página.

## 2. Requisitos Funcionais (FR)

| ID | Descrição | Implements |
|---|---|---|
| **FR-001** | O script `report_orchestrator.py` deve gerar dois arquivos PDF por execução: `Relatorio_Consolidado_[Timestamp].pdf` e `Relatorio_Pagina1_[Timestamp].pdf`. | AC-2 |
| **FR-002** | A renderização da Página 1 (Macro Overview) deve exibir todos os 20 subgrupos existentes, sem filtros de limite (Top 5) ou cortes por volume histórico. | AC-1 |
| **FR-003** | O sistema deve gerar um arquivo de preview visual em formato PNG (`docs/previews/preview_P1.png`) da Página 1 para QA visual antes do envio final. | AC-3 |

## 3. Requisitos Não-Funcionais (NFR)

| ID | Descrição | Validates | Rationale |
|---|---|---|---|
| **NFR-001** | A geração do relatório e do preview deve concluir em menos de 10 segundos. | AC-2 | Garantir performance da pipeline. |
| **NFR-002** | O layout da Página 1 deve ajustar dinamicamente o `GridSpec` (ex: `fontsize=7`, `width=0.2`) para que os 20 subgrupos caibam sem sobreposição e permaneçam legíveis. | AC-3 | Evitar quebra visual com o aumento de densidade. |
| **NFR-003** | A lógica de renderização da Página 1 não deve ser duplicada (DRY). O mesmo objeto/dado gerado deve ser salvo no PDF Consolidado, no PDF Página 1 e no PNG. | AC-2 | Prevenir inconsistências de dados entre as versões. |

## 4. Test Scenarios (T)

| ID | Descrição | FR |
|---|---|---|
| **T-001** | **Verificação de Geração Dupla:** Rodar o orquestrador e confirmar a criação de `Relatorio_Consolidado_...pdf` (5 pág) e `Relatorio_Pagina1_...pdf` (1 pág). | FR-001 |
| **T-002** | **Contagem de Subgrupos:** Inspecionar os dados renderizados e confirmar que o gráfico no eixo Y possui exatamente 20 barras (subgrupos). | FR-002 |
| **T-003** | **QA Visual (Anti-Quebra):** Abrir `docs/previews/preview_P1.png`. Validar visualmente se: 1) Nenhuma barra se sobrepõe; 2) Os textos dos 20 subgrupos estão perfeitamente legíveis; 3) O gráfico cabe dentro das margens da página. | FR-003, NFR-002 |

## 5. Implementação (Fases)

| Fase | Descrição | Depends |
|---|---|---|
| Fase 1 | Ajustar `macro_overview.py` (Remover filtros e ajustar layout + PNG) | - |
| Fase 2 | Ajustar `report_orchestrator.py` (Geração Dual) | Fase 1 |
| Fase 3 | Validação QA Visual | Fase 2 |
