# Design DNA & Visual Rules - Luxury Earth Edition

Este documento define os tokens de alta fidelidade para a interface Inova M6.

## 1. Pilar Estético: Luxury Earth (Deep Organic)

Abandona o estilo industrial tradicional por uma sofisticação tecnológica sobre base orgânica.

- **Substrato (Background):** `#1E1B18` (Terra Profunda).
- **Material:** Liquid Glass. `backdrop-filter: blur(90px)`.
- **Transparência:** `rgba(255, 255, 255, 0.03)` para superfícies de vidro.
- **Bordas:** `1px solid rgba(255, 255, 255, 0.08)`. Bordas do tipo *Squircle* (iOS Style).
- **Status Success:** `border: rgba(34, 197, 94, 0.5)`, Glow discreto (12px).
- **Status Alert:** `border: rgba(245, 158, 11, 0.6)`, Glow equilibrado (15px) + Fundo 2%.
- **Status Critical:** `border: rgba(255, 49, 49, 0.7)`, Glow focado + Sombra interna + Fundo 3% + **Animação Breathing (4s)**.

## 2. Paleta de Cores & Luminescência

- **Primária:** `#FFB800` (John Deere Yellow). Usado para dados de "Realizado".
- **Secundária:** `#F2F2F2` (Puro). Usado para "Metas" e labels.
- **Hazard Glow:** Sombra difusa `0 0 20px rgba(255, 184, 0, 0.3)`.
- **Status:**
  - *Sucesso (>=90%):* Glow Verde Esmeralda.
  - *Alerta (<90%):* Hazard Glow Âmbar.
  - *Crítico (<70%):* Hazard Glow Vermelho.

## 3. Tipografia Sleek

- **Primary:** `Plus Jakarta Sans` ou `Inter`.
- **Visual Contrast:**
  - Números KPI: `Weight 800`, `Trackig -0.04em`, `Uppercase`.
  - Labels: `Weight 300`, `Letter-spacing 0.2em`, `Text-transform uppercase`.
  - Secondary: `Weight 500`, `Italic` para metadados sutis.

## 4. Profundidade & Movimento

- **Magnetism:** Cards têm uma rotação 3D de ±2 graus baseada na posição do mouse.
- **Grain & Glow:** Uso de `feGaussianBlur` e `feColorMatrix` em SVGs para glows orgânicos.
- **Transitions:** `duration: 0.8s`, `ease: "expo.out"`.
- **Interaction:** Hover nos cards deve intensificar o glow de status em 50%.

## 5. Regras de Comportamento & Dados

Para garantir a integridade analítica, o dashboard segue uma lógica de filtragem assimétrica:

- **Bento Grid (Filiais):** 
    - **Soberania Visual:** Deve exibir permanentemente todas as filiais mapeadas.
    - **Filtro:** IGNORA o seletor global de Filial. RESPEITA os seletores de Ano e Mês.
    - **Conteúdo:** Exibição obrigatória do valor Realizado e Meta Nominal (R$).
- **KPIs Hero & Evolução:**
    - **Filtro:** RESPEITA integralmente todos os seletores (Ano, Mês e Filial).
    - **Consolidação:** Quando "Todas" (ALL) estiver selecionado, deve exibir a soma de todas as unidades (Equivalente ao GRUPO).
- **Gráfico de Funil (Pipeline):**
    - **Dinâmica Central:** Ao interagir ou selecionar um status, o centro da rosca deve exibir o valor monetário (R$) do status em foco.
- **Formatação de Dados:**
    - Números em Cards: Padrão `fmtK` (Ex: 1.2M).
    - Tooltips e Detalhes: Padrão `fmtFull` (Ex: R$ 1.234.567,89).

## 6. Protocolo de Auditoria (Scanner First)

Para garantir a confiabilidade executiva do Dashboard M6, o seguinte protocolo é MANDATÓRIO:

- **Scanner Gate:** Nenhuma alteração de lógica ou deploy de dados é considerada "Finalizada" sem a execução do `onepage_scanner.py`.
- **Critério de Aceite:** O Scanner deve retornar `✅ OK` para todas as metas. Qualquer `❌ ERRO` bloqueia o deploy.
- **Evidência:** O log do Scanner deve ser anexado (ou reportado) como evidência de validação matemática, substituindo a necessidade de validação manual via browser.
- **Soberania do Código:** O código do Scanner reflete as regras de negócio oficiais. Em caso de divergência entre o Scanner e o Dashboard, o Dashboard deve ser ajustado para refletir o Scanner.
