# ONEPAGE_SPEC - Executive Earth Dashboard

## 1. Visão Geral do Componente
O Dashboard é uma aplicação single-page (SPA) de alta performance que consome snapshots estáticos do Motor M6.

## 2. Estrutura do Layout (Bento Grid)
| Componente | Tamanho (Grid) | Função | Lottie Icon |
| :--- | :--- | :--- | :--- |
| **KPI Hero** | 2x1 | Faturamento Mês Atual vs Meta | Wallet/Money |
| **KPI Meta Ano** | 1x1 | Progresso acumulado 2026 | Target |
| **KPI Pipeline** | 1x1 | Volume total em aberto | Rocket |
| **Morph Center** | 3x2 | Evolução vs Meta (Morph via Scroll) | N/A (Canvas) |
| **Status Funil** | 1x2 | Donut interativo por status | Pie-Chart |
| **Branch Grid** | Full Width | Cards individuais por Filial | Building |

## 3. Mapeamento de Dados (Motor M6)
| Campo UI | Fonte Excel (Motor M6) | Lógica |
| :--- | :--- | :--- |
| `valFaturamento` | `VALOR_REALIZADO` | Soma(MES_ATUAL) |
| `valMeta` | `VALOR_META` | Soma(MES_ATUAL) |
| `valAcumulado` | `VALOR_REALIZADO` | Soma(ANO_ATUAL) |
| `valPipeline` | `VALOR_FUNIL` | Soma(STATUS_ABERTO) |

## 4. Regras de Negócio de Visualização
- **Filtros:** Ano, Mês e Filial. Devem atualizar os dados em memória sem refresh.
- **Formatação:** Aplicar `k` para milhar e `M` para milhão. Ex: `R$ 1.250.000` -> `R$ 1.25M`.
- **Tooltips ApexCharts:** Devem exibir o valor cheio e a porcentagem de contribuição no hover.

## 5. Especificação de Movimento
- **ScrollTrigger:** Ativar o morphing de partículas quando a seção central atingir `top: 20%` da viewport.
- **Lottie States:**
    - `hover`: Aciona a animação de "excitação" do ícone.
    - `click`: Aciona a animação de "confirmação/pulse".
