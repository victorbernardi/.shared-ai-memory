# Spec v1.4 - Refinamento Segmentação Analytics (Wave 8.1)

## 1. Objetivo
Refinar a implementação da Wave 8 para garantir hierarquia visual premium, legibilidade de dados em escalas díspares e consistência cromática industrial no Dashboard Inova M6.

## 2. Requisitos de Interface (Antigravity & High-End Design)

### 2.1. Arquitetura de Cards (Double-Bezel)
- **Estrutura:** Todo card deve possuir um `div.card-shell` (borda externa sutil) e um `div.card-core` (container interno com sombreamento de profundidade).
- **Radii:** Shell: `rounded-2xl` (16px) | Core: `rounded-xl` (12px).

### 2.2. Hero KPI & Share (Floating Badges)
- **Remoção:** Eliminar o `div` retangular verde de performance de segmento.
- **Nova Implementação:** Adicionar um `span.badge-floating` posicionado acima do valor principal do Faturamento Realizado.
- **Estética:** Fundo translúcido (`backdrop-filter: blur(8px)`), borda neon verde e texto com brilho suave (glow).

### 2.3. Geometria das Barras de Progresso
- **Altura (Height):** Aumentar de 8px para **16px** em todos os componentes de barra (Hero e Bento Grid).
- **Double-Stack:** Barra do Segmento (Verde) deve ser renderizada como uma camada aninhada sobre a barra do Total (Amarelo), com uma textura sutil (ex: listras diagonais 5% de opacidade) para diferenciar os materiais.
- **Rótulos:** Adicionar a porcentagem de atingimento (Ex: "105%") em um `div.island-label` fixado no final da trilha da barra.

## 3. Requisitos de Dados & Gráficos (KPI Dashboard Design)

### 3.1. Evolução Estratégica (Eixo Duplo)
- **Eixo Y1 (Esquerdo):** Escala linear para Faturamento Total (Milhões).
- **Eixo Y2 (Direito):** Escala linear para Faturamento Segmento (Milhares).
- **Legenda:** Identificar claramente qual linha pertence a qual eixo.

### 3.2. Acumulado do Ano (YTD Context)
- **Injeção de Dados:** Adicionar campos `Realizado Segmento YTD` e `Meta Segmento YTD` no card de acumulado.
- **Layout:** Manter o Total como KPI primário e o Segmento como secundário (fonte menor, logo abaixo).

### 3.3. Bento Grid (Filiais)
- **Nesting:** Abaixo da barra de progresso da filial, exibir o nome dinâmico do segmento selecionado.
- **Proporção:** O atingimento (%) da filial deve ficar à esquerda e o atingimento do segmento à direita, mantendo equilíbrio visual.

## 4. Consistência Cromática (Stout Standard)
- **Realizado Total:** `#FFB800` (John Deere Yellow) - Opacidade 100%.
- **Realizado Segmento:** `#367C2B` (John Deere Green) - Opacidade 100%.
- **Meta:** `#444` ou similar (Fundo neutro industrial).

## 5. Validação (Quality Gate)
1. **Scanner Gate:** Execução obrigatória do `onepage_scanner.py`. Diferença aceitável: **R$ 0,00**.
2. **Visual Check:** Verificação de brilho e alinhamento em resolução 1920x1080.

---
**Documento Gerado em:** 2026-04-30
**Status:** Aguardando Aprovação para Build.
