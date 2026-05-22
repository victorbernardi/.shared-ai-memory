# Spec v1.3: Segmentação Granular & Overlay Analytics (Stout Edition)

## 1. Matriz de Rastreabilidade (AC → FR)

| ID SOW | Critério de Aceitação (AC) | Requisito Funcional (FR) | Prioridade |
| :--- | :--- | :--- | :--- |
| AC-1 | Filtro de Segmentação Granular | FR-001: Seletor Dinâmico | P0 |
| AC-2 | Visão de Composição (Nested Bar) | FR-002: Bento Grid Bicolor | P0 |
| AC-3 | Análise de Tendência Comparativa | FR-003: Gráfico Triplo Eixo | P1 |
| AC-4 | Overlay de Dados no Hero | FR-004: Painel Verde JD | P0 |
| AC-5 | Representatividade (Share %) | FR-005: Cálculo de Share | P1 |

---

## 2. Requisitos Funcionais (FR)

### FR-001: Seletor de Segmento
- **SHALL:** Carregar valores únicos de `SEGMENTO` do snapshot.
- **SHALL:** Opção "Todos" reseta para visão global.
- **Implements:** AC-1.

### FR-002: Bento Grid Bicolor
- **SHALL:** Renderizar barra principal (Amarela) como Total da Filial.
- **SHALL:** Sobrepor barra interna (Verde JD) com o valor do segmento.
- **SHALL:** Exibir etiqueta com Realizado e Meta específicos do segmento.
- **Implements:** AC-2.

### FR-003: Gráfico Triplo Eixo (Evolução)
- **SHALL:** Plotar Linha Amarela (Total), Linha Verde Sólida (Real Segmento) e Linha Verde Tracejada (Meta Segmento).
- **Implements:** AC-3.

### FR-004: Painel Verde JD (KPI Hero)
- **SHALL:** Exibir métricas do segmento no canto inferior direito em destaque verde.
- **Implements:** AC-4.

### FR-005: Cálculo de Share
- **SHALL:** Calcular `(Realizado Segmento / Realizado Total Unidade)`.
- **Implements:** AC-5.

---

## 3. Cenários de Teste (T)

| ID | Título | Referência | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| T-001 | Validação de Filtro | FR-001 | KPIs Hero devem mudar, mas Grid Filiais deve manter todas as unidades. |
| T-002 | Proporção de Barras | FR-002 | A barra verde nunca deve ultrapassar a barra amarela em largura. |
| T-003 | Paridade Matemática | FR-005 | A soma do Share de todos os segmentos deve resultar em 100%. |
| T-004 | Scanner Gate | FR-002 | `onepage_scanner.py` deve retornar "Zero Diff" para o segmento filtrado. |

---

## 4. Auditoria e Governança
- **Scanner Gate:** Integrado.
- **YAGNI Check:** Aprovado (Métricas solicitadas pelo negócio).
