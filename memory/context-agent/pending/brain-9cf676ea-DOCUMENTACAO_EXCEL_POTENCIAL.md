# 📑 Documentação Técnica: ESTUDO — Potencial Peças Brasil Inova

## 📋 Controle de Versão
| Versão | Data | Autor | Descrição |
| :--- | :--- | :--- | :--- |
| v1.0 | 09/04/2026 | Antigravity | Criação inicial com dump completo de fórmulas. |
| v2.0 | 09/04/2026 | Antigravity | Limpeza cirúrgica: remoção de colunas administrativas. |
| v3.0 | 09/04/2026 | Antigravity | Tradução de fórmulas técnicas para nomes de negócio (amigável). |

## 1. Visão Geral da Aba
- **Objetivo:** Consolidar o inventário de máquinas com os custos técnicos da Sobratema.
- **Cabeçalho Principal:** Linha 07.
- **Início dos Dados:** Linha 08.

## 2. Dicionário de Cálculos (Lógica de Negócio)

| Campo | Descrição / Lógica Comercial (Fórmula Traduzida) |
| :--- | :--- |
| **Modelo** | Chave de busca para os custos operacionais (Base Modelos). |
| **Custo Unitário** | Valor por hora de peças, pneus ou lubrificantes (via VLOOKUP). |
| **Horas de Uso/Ano** | Intensidade de utilização anual (Telemetria ou Estimado). |
| **Fator de Utilização** | Multiplicador Sobratema baseado na severidade do uso (4 Faixas). |
| **Potencial Anual** | `[Custo Unitário] * [Horas de Uso/Ano] * [Fator de Utilização]` |
| **Potencial Proporcional** | `[Potencial Anual] * ([Meses Decorridos] / 12)` |

## 3. Detalhamento dos Componentes Financeiros
| Componente | Fórmula Base |
| :--- | :--- |
| **Peças** | `[Custo Hora Peças] * [Horas Anuais] * [Fator Uso]` |
| **Pneus** | `[Custo Hora Pneus] * [Horas Anuais] * [Fator Uso]` |
| **Lubrificantes** | `[Custo Hora Lubrificantes] * [Horas Anuais] * [Fator Uso]` |
| **Mat. Rodante** | `[Custo Hora Mat. Rodante] * [Horas Anuais] * [Fator Uso]` |

## 4. Lógica de Cálculo (Chave de Negócio)

1. **VLOOKUP Técnico:** O Excel usa o modelo (Coluna 10) para buscar os valores unitários na aba `Base Modelos`.
2. **Fator de Uso (BM):** A célula `BM` é o fator dinâmico baseado na intensidade de horas (0-1k, 1k-2k, 2k-4k, >4k).
3. **Cálculo de Potencial:** O valor anual é o produto de `Custo Unitário` x `Horas Anuais` x `Fator de Utilização`.
4. **Proporcionamento Temporal:** Existe uma lógica (Coluna 60) que calcula o potencial baseado em quantos meses se passaram desde uma data de corte fixa (`$BU$1`).

---
*Nota: Este documento é um Artefato do Antigravity para suporte a edição colaborativa.*
