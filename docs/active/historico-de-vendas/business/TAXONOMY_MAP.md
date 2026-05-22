# 🗺️ TAXONOMY_MAP - Dicionário de Hierarquia e Produtos

Este documento serve como a "Bússola" para navegar entre a taxonomia técnica do Protheus e a visão comercial do Motor de Faturamento.

---

## 🏗️ Estrutura de Hierarquia
A granularidade segue a lógica abaixo:
1. **GRUPO (Protheus):** Macro-categoria contábil (ex: 0100 - Peças).
2. **SUBGRUPO (Técnico):** Sigla de 4 letras (ex: FLGD, JDPC).
3. **SUBGRUPO (Comercial/BI):** Nomes amigáveis na `vw_VENDAS` (ex: LUBRIFICANTE, FILTROS).
4. **FAMÍLIA:** Granularidade intermediária (ex: FUEL GARD, ADITIVOS).
5. **ITEM (SKU):** O código do produto (ex: CQM20126).

---

## 📒 Glossário: De/Para (Técnico -> Comercial)

| Sigla Protheus | Nome Comercial (BI) | Descrição do Subgrupo | Notas de Negócio |
| :--- | :--- | :--- | :--- |
| **FLGD** | BACTERICIDA | Bactericidas e Aditivos | **ALERTA:** Possível transição de SKUs em 2025. |
| **JDPC** | PECAS JOHN DEERE | Peças de Consumo John Deere | Em forte aceleração (2025+). |
| **CBIT** | PECAS CIBER BITS | Bits e Pontas de Fresagem | Alta rotatividade. |
| **LUB** | LUBRIFICANTE | Óleos e Fluidos | Subdivisões por litragem (1L, 5L, 20L). |
| **CBPC** | ORIGINAIS CIBER | Peças Genuínas Ciber | Gestão direta de fábrica. |

---

## 🔬 Caso de Estudo: Bactericida (FUEL GARD)

**O "PQ" da Queda:**
- No relatório histórico (36m), o volume acumulado é massivo devido aos anos de 2023-2024.
- No faturamento recente (`vw_VENDAS` 2025+), o produto **FUEL GARD 1L (CQM20126)** cresceu **168%** de 2025 para 2026.
- **Veredito:** O produto não está morrendo no mercado atual; a "morte" no relatório de 3 anos é reflexo de uma mudança no patamar de consumo ou codificação em relação ao passado remoto.

---

## ⚠️ Observações de Governança
- **vw_VENDAS:** Fonte para análise de tendência curta e performance de vendedores (Dados 2025+).
- **Excel Consolidado:** Fonte para análise de ciclo de vida longo e estoque morto (Dados 2023+).
