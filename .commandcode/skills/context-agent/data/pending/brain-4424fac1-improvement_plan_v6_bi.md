# Improvement Plan - Wave 6: BI & Reporting Premium

## Objetivo
Refinar o output do Motor M6 para atender às exigências de diretoria: simplificação de indicadores, categorização operacional (Balcão vs Oficina) e suporte nativo a cálculos temporais no Excel.

## Mudanças Aprovadas

### 1. Formatação e Métricas (Wide Format)
- `DATA_REFERENCIA`: Formato `dd/mm/aaaa`.
- **Nova Estrutura de Colunas:**
  - `VALOR_REALIZADO`: Faturamento líquido.
  - `VALOR_FUNIL`: Propostas em aberto.
  - `VALOR_META`: Objetivos mensais.
  *(Isso permite usar o Excel para calcular YoY/MoM/WoW comparando colunas diretamente).*

### 2. Governança de Status (3 Estágios)
- Redução da complexidade para apenas:
  - **EM ABERTO**: Status `0` (dentro de 60 dias).
  - **FATURADO**: Status `F/I` (convertido).
  - **CANCELADO**: Status `X`, `C` ou `EXPIRADO (AGING)`.

### 3. Categorização Operacional
- **Origem:**
  - `Oficina`: Centros de Custo contendo "OFICINA" ou "SERVICO".
  - `Balcão`: Demais movimentações.
- **Segmentos:** Mapeamento rigoroso de `DESCRICAO_CC` para:
  - `Oficina / serviços`
  - `CRC`
  - `Contratos`
  - `Peças CSN`
  - `Peças Wirtgen`
  - `Peças e Acessórios` (Resgate)

## Plano de Execução
1. Atualizar o `Wave4_Orquestrador_M6.py` com as novas regras de mapeamento.
2. Refatorar a unificação final (Concat) para o formato Wide.
3. Gerar o novo Excel e validar os totais contra a auditoria.
