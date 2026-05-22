# Plano de Implementação - Wave 8.3 (Luxury Earth & Spec v1.3)

Este plano visa restaurar a identidade visual premium e implementar as funcionalidades de segmentação granular, seguindo estritamente o `DESIGN_RULES.md` e a `Spec v1.3`.

## 🎨 Fase 1: DNA Visual (CSS)
- **Background & Material:** Mudar para `#1E1B18` e aplicar o blur de `90px` no vidro.
- **Sistema de Semáforo (Luminescência):**
    - Criar `.status-success` (Verde), `.status-alert` (Âmbar) e `.status-critical` (Vermelho).
    - Implementar a animação `breathing` (opacidade 0.6 a 1.0) para o estado crítico.
- **Tipografia:** Integrar `Plus Jakarta Sans`, configurar `letter-spacing: 0.2em` para labels e `weight 800` para KPIs.
- **Correção da Island:** Ajustar o `transform` para usar variáveis CSS, evitando que ela desloque no hover.
- **Magnetismo:** Preparar a classe `.magnet-card` para interação 3D via GSAP.

## ⚙️ Fase 2: Lógica de Dados e Segmentação (JS)
- **Cálculo de Status:** Função `getStatusClass(atingimento)` baseada nas faixas (70% / 90%).
- **Bento Bicolor (Filiais):** 
    - Atualizar `renderBranches` para criar o container de barra dupla.
    - Barra Amarela (Fundo) -> Real Total.
    - Barra Verde JD (Sobreposta) -> Real Segmento.
    - Alinhamento da % no topo direito do card.
- **Painel Verde JD (Hero):** Injetar um overlay no canto do card Hero com o Realizado e Meta do segmento filtrado.
- **Gráfico de Evolução:** Implementar o Triplo Eixo (FR-003) no ApexCharts.

## 🛠️ Fase 3: Estabilização e Auditoria
- **Lottie Icons:** Substituir as URLs por fontes confiáveis (cerca de 5 links alternativos de CDN estável).
- **Formatadores:** Garantir `toFixed(0)` em todos os labels de gráfico para eliminar decimais.
- **Scanner Gate:** Execução final do `onepage_scanner.py`.

## Plano de Verificação
1. **Visual:** Abrir o dashboard e validar a cor do background e os glows de status.
2. **Interação:** Testar o hover na Island e o magnetismo dos cards.
3. **Dados:** Filtrar por "Peças" e verificar se as barras bicolores nas filiais refletem a proporção correta (Share %).
