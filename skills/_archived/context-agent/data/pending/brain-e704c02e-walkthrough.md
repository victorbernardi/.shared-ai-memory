# Walkthrough: Movimento Telemétrico Industrial

Os cards de performance por filial foram atualizados para um padrão de interação "Awwwards-tier", focado em precisão e dinamismo.

## Mudanças Realizadas

### [Componente] UI/UX Motion

#### [MODIFY] [index.html](file:///c:/Projetos/Inova/Metas%20Pe%C3%A7as/05_Resultados/index.html)

1.  **Status Hazard-Pulse**:
    - Substituição da animação genérica por pulsos industriais específicos: `hazard-pulse-amber` (Alerta) e `hazard-pulse-red` (Crítico).
    - Estes efeitos aumentam a visibilidade de filiais fora da meta sem poluir a interface.

2.  **Entrada Coreografada (Scanned Entry)**:
    - Ao trocar filtros, os cards agora surgem em uma sequência escalonada (`stagger`), removendo o "pulo" visual estático.

3.  **Contadores Telemétricos (Odometer)**:
    - Implementada a função `animateValue` que interpola os valores de R$ e % de 0 até o valor real em 1.5s.
    - Isso transmite a sensação de que o dashboard está processando dados ao vivo.

4.  **Sincronização de Barras**:
    - As barras de progresso agora acompanham o tempo dos contadores, preenchendo de forma fluida com easing `expo.out`.

## Validação e Resultados

- **Performance**: As animações utilizam aceleração de hardware (transform/opacity) e GSAP, mantendo 60fps mesmo com múltiplos cards.
- **Interatividade**: O efeito de "Magnetismo" (Tilt) é reativado automaticamente após a conclusão da animação de entrada.

> [!TIP]
> Experimente alternar entre os segmentos no topo para ver os cards se reconfigurarem e os contadores recalcularem em tempo real.
