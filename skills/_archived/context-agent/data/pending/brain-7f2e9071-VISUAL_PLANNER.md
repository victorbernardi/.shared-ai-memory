# Visual Planner: Dashboard Executivo John Deere (M6)

Este documento define a identidade visual e a estrutura funcional de cada componente do dashboard.

## 🎨 Paleta de Cores (John Deere Construction)
| Elemento | Hex Code | Aplicação |
| :--- | :--- | :--- |
| **Primária (Destaque)** | `#FFDE00` | Botões ativos, Realizado (Linhas), Ícones. |
| **Secundária (Marca)** | `#367C2B` | Logotipo, Metas (Linhas tracejadas), Sucesso. |
| **Background Principal**| `#F5F5F7` | Fundo da página (Apple White). |
| **Glass Card** | `rgba(255, 255, 255, 0.7)` | Fundo dos cards com `backdrop-filter: blur(20px)`. |
| **Texto Primário** | `#1D1D1F` | Títulos e métricas principais (Jet Black). |
| **Texto Secundário** | `#86868B` | Legendas e rótulos de eixos. |

## 🏗️ Estrutura de Componentes

### 1. Header & Filtros (Navegação Superior)
*   **Logo**: SVG da John Deere no canto superior esquerdo.
*   **Filtros**: Pílulas interativas (estilo iOS Control Center).
    *   `Mês`: Dropdown segmentado.
    *   `Segmento`: Dropdown com seleção única.
    *   `Pirâmide`: (Apenas Visível na aba Funil) Seletor de Quadrante (Classe A, B, C...).

### 2. Cards de KPI (O topo do Dashboard)
Cada card terá 140px de altura, com bordas arredondadas (24px).
*   **Card 1: Faturamento**: Valor em R$ (Ex: R$ 1.2M) + indicador de crescimento % em relação ao mês anterior.
*   **Card 2: Atingimento**: Gráfico de "Donut" minimalista ocupando o fundo do card, mostrando o % (Ex: 85%).
*   **Card 3: Gap de Meta**: Valor absoluto faltante em vermelho suave (`#FF3B30`) se negativo, ou verde se superado.
*   **Card 4: Pipeline Ativo**: Valor em "Em Aberto" (< 60 dias) com ícone de ampulheta animado.

### 3. Gráficos (A Visualização de Dados)

#### A. Evolução Mensal (Gráfico Master)
*   **Tipo**: Gráfico de Área Suave (Spline).
*   **Linha Realizado**: Amarela sólida com sombra projetada.
*   **Linha Meta**: Verde tracejada (estilo "target line").
*   **Interação**: Tooltip Apple-style (fundo branco, bordas arredondadas, sem bordas pretas).

#### B. Performance por Filial (Small Multiples)
*   **Tipo**: Mini-gráficos de linha (Sparklines) em grade.
*   **Comportamento**: Cada card de filial terá um checkbox no canto. Ao selecionar 2 ou mais, o dashboard abre um modal de "Comparativo Lado a Lado".

#### C. Funil de Vendas (Aba Pipeline)
*   **Tipo**: Gráfico de Barras Horizontais Empilhadas (Stacked Bar).
*   **Categorias**: Faturado (Verde), Em Aberto (Amarelo), Cancelado (Cinza).
*   **Destaque**: Uma "Badge" (Etiqueta) flutuante sobre as barras de "Em Aberto" indicando a média de dias de aging.

## 📱 Interatividade & Feedback
*   **Hover**: Cards elevam-se levemente (`transform: translateY(-5px)`) e ganham brilho.
*   **Transição**: Troca de filtros usa o GSAP para fazer o "cross-fade" suave dos dados, sem recarregar a página.
*   **Responsividade**: Em telas menores, os Small Multiples viram um carrossel horizontal.
