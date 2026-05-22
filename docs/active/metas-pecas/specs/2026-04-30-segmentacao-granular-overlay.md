# Spec v1.3: Segmentação Granular & Overlay Analytics

Implementação de filtragem por segmento com visualização de "Parte sobre o Todo" (Share) e indicadores em Verde John Deere.

## 1. Requisitos Funcionais

### 1.1 Seletor de Segmento
- **Fonte:** Lista dinâmica baseada nos valores únicos do campo `SEGMENTO` no snapshot.
- **Opção Default:** "Todos os Segmentos".

### 1.2 Visão Sobreposta (KPI Hero)
- Quando um segmento é selecionado:
    - O card exibe o **Total (Amarelo)**.
    - Um novo painel em **Verde JD** (canto inferior direito) exibe:
        - Realizado do Segmento (R$).
        - % de Atingimento (Meta do Segmento).
        - % de Share (Representatividade sobre o faturamento total da unidade/grupo).
    - Acumulado do Ano (YTD) movido para a base do card.

### 1.3 Gráfico de Tendência (Triplo Eixo)
- Exibição de 3 linhas simultâneas ao filtrar segmento:
    - **Amarelo Sólido:** Realizado Total (Referência).
    - **Verde Sólido:** Realizado do Segmento.
    - **Verde Tracejado:** Meta do Segmento.

### 1.4 Bento Grid Bicolor
- **Barra de Progresso:**
    - Fundo: Dark Glass.
    - Preenchimento 1: Amarelo John Deere (Total da Filial).
    - Preenchimento 2 (Overlay): Verde John Deere (Valor do Segmento).
- **Metadados:** Exibição do "% Share" em cada card de filial.

## 2. Arquitetura de Dados (Frontend)

O `DataLoader` deve realizar a bifurcação dos dados:
- `perfContext`: Dados da unidade/filial selecionada (Respeita Filial, Ignora Segmento).
- `perfActive`: Dados específicos do filtro ativo (Respeita Filial e Segmento).

**Fórmula do Share:**
`Share % = (SUM(Realizado Segmento Selecionado) / SUM(Realizado Todos os Segmentos)) * 100`

## 3. Design Tokens (Update)
- **Primary Segment Color:** `#367C2B` (John Deere Green).
- **Secondary Segment Color:** `#2E5F23` (Darker Green for gradients).
- **Typography:** Uso de semibold para os valores de segmentação.

## 4. Plano de Validação
- **Scanner Gate:** O `onepage_scanner.py` deve validar se a soma dos segmentos individuais é igual ao total do consolidado.
- **UI Check:** Verificar se a barra verde nunca ultrapassa a amarela (Integridade lógica).
