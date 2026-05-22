# BRD - Motor de Relatórios M6 (Inova Equipamentos)

## 1. Executive Summary
Este projeto visa implementar o **Motor de Relatórios M6**, uma ferramenta de inteligência competitiva para a Inova Equipamentos. O motor unifica o funil de vendas do Proteus (orçamentos) com a realidade financeira (faturamento) e as metas corporativas. O diferencial estratégico é a implementação da **Visão de Safra (Cohort)** e a **Gestão de Aging**, eliminando "zumbis" do funil e permitindo uma leitura real da eficiência comercial.

## 2. Business Goals
| Objetivo | Meta SMART |
| :--- | :--- |
| **Acuracidade Financeira** | Garantir 0% de divergência de faturamento contra o Motor M2 oficial. |
| **Visão de Safra** | Implementar métricas baseadas na data de emissão do orçamento (Cohort). |
| **Limpeza de Funil** | Identificar e expurgar 100% de orçamentos em aberto com mais de 60 dias. |
| **Pareamento de Metas** | Cruzar 100% das categorias de metas (Excel) com os Centros de Custo do ERP. |

## 3. Stakeholders (RACI)
| Ator | Papel | Responsabilidade |
| :--- | :--- | :--- |
| **Gestão Comercial** | Owner | Validação das regras de negócio e metas. |
| **Time de Analytics** | User | Operação e extração de insights do relatório. |
| **Engenharia de Dados** | Developer | Implementação e manutenção do Motor M6. |

## 4. Requirements
- **R01:** Unificar base histórica (2017-2025) com a view de faturamento atual.
- **R02:** Traduzir códigos de Centro de Custo para nomes amigáveis das metas.
- **R03:** Aplicar regra de Aging de 60 dias para status "Aberto".
- **R04:** Integrar a segmentação de clientes (Pirâmide M5) ao faturamento.
- **R05:** Exportar consolidado em formato Excel para consumo direto pela diretoria.

## 5. Success Metrics (KPIs)
- **Taxa de Conversão por Safra:** % de orçamentos convertidos em venda no período X.
- **Gap de Metas:** Diferença percentual entre Faturamento Real e Meta 2026.
- **Saúde do Funil:** Relação entre propostas ativas e propostas expiradas.
- **Volume de Resgate Branco:** Quantidade de vendas sem orçamento prévio.
