# Especificação Técnica: Relatório de Vendas e Segmentação (M6)

## 1. Objetivo
Criar um motor de relatórios (M6) que consolide as vendas por Loja, Vendedor e Produto, integrando a classificação da Pirâmide de Segmentação (M5) e comparando com as Metas de Peças John Deere 2026.

## 2. Fontes de Dados
- **Vendas (M2):** `dataset_ouro_pecas_grupo_v1.parquet` e cache transacional `cache_vendas_rfm.parquet`.
- **Segmentação (M5):** `Segmentacao_Executiva_2025_v1.xlsx` (ou o motor `motor_segmentacao_v1.py`).
- **Metas:** `Metas de peças John Deere 2026 - Revisão março.xlsx`.
- **Dicionário de Segmentos:** Mapeamento de `DESCRICAO_CC` para os segmentos de metas (Contratos, CRC, CSN, Serviços, Acessórios).

## 3. Lógica de Negócio (Pirâmide)
Conforme brainstorming de 14/04/2026 (Transcrição de Áudio):
- **Eixo Potencial (Valor):**
  - **1:** > R$ 1.000.000
  - **2:** R$ 500.000 - R$ 1.000.000
  - **3:** < R$ 500.000
- **Eixo Participação (% SOW):**
  - **A:** >= 40%
  - **B:** 24% a 40%
  - **C:** < 24%
  - **D:** Potencial > 0 mas sem compra.
- **Clusters RFM (X, Y, Z):** Clientes sem potencial mapeado, classificados por Recência, Frequência e Valor.

## 4. Estrutura dos Outputs
### Output 1: Visão Executiva / Metas
- Agrupamento por **Loja** e **Segmento de Produto**.
- Comparativo: Venda Real vs. Meta (Excel Março/2026).
- Indicador: % Atingimento.

### Output 2: Hierarquia Comercial
- Estrutura: `FILIAL` -> `NOME_VENDEDOR (Consultor)` -> `Segmento_Produto`.
- Integração da **Classificação da Pirâmide** (ex: "A1", "B2") ao lado de cada cliente atendido pelo consultor.

## 5. Próximos Passos (Fase de Estratégia)
- Criar o script `motor_relatorios_v1.py`.
- Implementar o de-para de Segmentos (CC -> Metas).
- Gerar os arquivos Excel formatados conforme a identidade visual Inova.

---
> [!IMPORTANT]
> **Validação de Hierarquia:** O consultor no ERP é o campo `NOME_VENDEDOR`. Confirmar se existe algum nível abaixo (ex: Assistente) ou se este é o nível final solicitado.
