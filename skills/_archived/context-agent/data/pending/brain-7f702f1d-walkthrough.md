# Walkthrough - Dashboard Executivo M6 (Industrial Stout Edition)

O dashboard foi totalmente refatorado para atender aos padrões de design "Linha Amarela" da Inova, focando em contraste OLED, autoridade visual e interatividade fluida.

## 🎨 Transformação Visual (Antes vs Depois)

````carousel
![Versão Industrial Stout](file:///C:/Users/victor.bernardi/.gemini/antigravity/brain/7f702f1d-083b-4616-b6f3-365bc73bed4d/.tempmediaStorage/media_7f702f1d-083b-4616-b6f3-365bc73bed4d_1777517515463.png)
<!-- slide -->
![Status de Atenção (Glow Amarelo)](file:///C:/Users/victor.bernardi/.gemini/antigravity/brain/7f702f1d-083b-4616-b6f3-365bc73bed4d/.tempmediaStorage/media_7f702f1d-083b-4616-b6f3-365bc73bed4d_1777517508464.png)
````

## 🛠️ Principais Implementações

### 1. Sistema de Alerta "Hazard Glow"
*   **Crítico (<85%):** Glow pulsante em **Hazard Red (#FF3B30)** para ação imediata.
*   **Atenção (<95%):** Glow estático em **Construction Yellow (#FFB800)**.
*   **Sucesso (>95%):** Visual limpo com bordas douradas sutis.

### 2. Grid de Performance Panorâmico
*   Restauração do grid de filiais (Contagem, Uberlândia, etc).
*   Cada filial possui seu próprio **Sparkline Industrial** e sinalização de status independente.

### 3. Interatividade Stout
*   **Zoom no Hover:** A barra de ferramentas do ApexCharts agora é invisível por padrão, aparecendo apenas quando o executivo interage com o gráfico.
*   **Pipeline Focus:** Ao realizar o scroll, o gráfico de "Composição Estratégica" sofre uma ampliação (scale) de 5% via GSAP, focando a atenção na estrutura do funil.

## 📊 Validação de Paridade Financeira
*   Mantida a função `formatExecInt` para garantir o "Diff Zero".
*   Os thresholds de metas foram elevados para o padrão executivo (Crítico abaixo de 85%).

> [!TIP]
> Para testar o **Hazard Red Glow**, basta selecionar o mês de **Abril** no filtro (no mock data, Abril está com 60% de atingimento).
