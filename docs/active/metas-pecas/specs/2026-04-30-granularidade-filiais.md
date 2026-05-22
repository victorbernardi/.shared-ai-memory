# Especificação Técnica: Granularidade de Filiais (Dashboard M6)

**Data:** 2026-04-30  
**Status:** Aprovado (v1.2)  
**Autor:** Antigravity (Stout Edition)

## 1. Objetivo
Restaurar a capacidade do Dashboard M6 de filtrar e exibir dados individuais por filial, eliminando a consolidação prematura que ocorre no pipeline de dados.

## 2. Rastreabilidade (Traceability Matrix)

| ID | Descrição | Origem (BRD) |
| :--- | :--- | :--- |
| **AC-01** | Acuracidade Financeira (0% divergência) | Business Goals: Meta 1 |
| **AC-02** | Gestão por Unidade de Negócio | Requisito Operacional (Dashboard) |

## 3. Requisitos Funcionais (FR)

| ID | Descrição | Implements |
| :--- | :--- | :--- |
| **FR-001** | Preservar dimensão `NOME_FILIAL` no `aggregator.py` | AC-02 |
| **FR-002** | Sincronizar filtros de Card KPI com a seleção de filial | AC-02 |
| **FR-003** | Habilitar reatividade no gráfico de Evolução por unidade | AC-02 |
| **FR-004** | Detalhamento de Status do Funil por filial no Donut Chart | AC-02 |
| **FR-005** | Filtragem Assimétrica: Grid de Filiais ignora seletor de unidade | AC-02 |
| **FR-006** | Luminescência de Status (Glow) baseada em DESIGN_RULES | UX Standard |
| **FR-007** | Exibição de Meta Nominal (R$) nos cards de filial | AC-01 |

## 4. Requisitos Não-Funcionais (NFR)

| ID | Descrição | Validates | Rationale |
| :--- | :--- | :--- | :--- |
| **NFR-001** | Soma dinâmica no Frontend | AC-01 | Evita "buracos" de conciliação entre o total do motor e a soma das partes. |
| **NFR-002** | TTI < 1.5s pós-processamento | UX Standard | Garante que a fluidez visual (GSAP/Tilt) não seja prejudicada pelo custo de cálculo. |

## 5. Arquitetura e Mudanças Propostas

### 5.1 Camada de Dados (aggregator.py)
Alteração das chaves de agregação (`defaultdict` keys) para evitar o colapso precoce dos dados.
- **De:** `(ANO, MES_NOME, SEGMENTO)`
- **Para:** `(NOME_FILIAL, ANO, MES_NOME, SEGMENTO)`

### 5.2 Camada de Visualização (index.html)
- A função `updateDashboard` operará com dois conjuntos de dados:
    - `perfFiltered`: Respeita todos os filtros (para KPIs Hero e Evolução).
    - `perfAllBranches`: Ignora filtro de filial (para o Bento Grid).
- Padronização total para `NOME_FILIAL`.
- Injeção de classes de CSS dinâmicas para os glows de status conforme atingimento.

## 6. Plano de Validação (Test Scenarios)

| ID | Descrição | References | Observable Signal |
| :--- | :--- | :--- | :--- |
| **T-001** | Teste de ordenação cronológica | FR-001 | Log de sucesso no `unittest`. |
| **T-002** | Verificação de paridade | NFR-001 | Total exibido em "TODOS" == Soma manual das unidades. |
| **T-003** | Teste de estresse visual | NFR-002 | Dashboard permanece a 60fps durante filtragem. |

---

## Log de Decisões
- **Decisão 1:** Soma dinâmica no Frontend em vez de registros "GRUPO" pré-calculados.  
- **Motivo:** Maior confiabilidade e eliminação de redundância/erros de conciliação no motor de cálculo.
