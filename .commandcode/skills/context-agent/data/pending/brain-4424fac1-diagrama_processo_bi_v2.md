# Diagrama de Estrutura: BI Performance Inova (v2)

Este diagrama atualizado representa a arquitetura de dados extraída do quadro branco, com a hierarquia de detalhamento corrigida.

```mermaid
graph LR
    subgraph GESTAO["1. Gestão de Performance (Hierarquia)"]
        direction TB
        F1[FILIAL] --> CC[Centros de Custo]
        CC --> V1[Consultores]
        
        M1[Realizado] --- F1
        M2[Meta 2026] --- F1
        M3[Ano Anterior] --- F1
    end

    subgraph SEGMENTACAO["2. Quebras de Negócio (Segmentos)"]
        direction TB
        CC1[Oficina / Serviços]
        CC2[CRC]
        CC3[Contratos]
        CC4[Peças CSN]
        CC5[Peças Wirtgen]
        CC6["Peças e Acessórios (RESGATE BRANCO)"]
    end

    subgraph FUNIL["3. Funil de Vendas (Raiz Proteus)"]
        direction LR
        ORIGEM[ORIGEM: Balcão vs Oficina] --> MOV[MOVIMENTAÇÃO: Orçamentos]
        MOV --> STATUS{STATUS}
        STATUS --> S1[EM ABERTO]
        STATUS --> S2[FATURADO]
        STATUS --> S3[CANCELADO]
        
        S1 & S2 & S3 --> COMP[Comparativo: YoY / MoM]
    end

    GESTAO -.-> SEGMENTACAO
    SEGMENTACAO -.-> FUNIL
```

## Resumo dos Fluxos:
1.  **Faturamento:** Flui de cima para baixo (Filial ➔ Centros de Custo ➔ Consultores).
2.  **Orçamentação (Funil):** Flui da **esquerda para a direita** (Origem ➔ Status ➔ Comparativo).
3.  **Resgate:** A categoria "Peças e Acessórios" atua como um capturador de transações sem centro de custo definido.
