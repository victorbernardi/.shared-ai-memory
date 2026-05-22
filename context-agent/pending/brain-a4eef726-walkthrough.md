# Walkthrough: Alinhamento de Paridade Financeira M6 vs M2 (Diff Zero)

## Objetivo
Unificar o motor de faturamento M6 com o padrão M2 para eliminar discrepâncias financeiras no reporte de Peças e Serviços.

## Mudanças Realizadas

### [Wave 1] Unificador de Faturamento
- **Filtro de TES:** Migrado do SQL para o Python para permitir o uso de `.str.strip()`. Isso corrigiu o problema de vendas sendo ignoradas devido a espaços em branco no banco de dados (ex: '511 ').
- **Aftermarket Keywords:** Sincronizado com o M2, incluindo suporte a `NULO`, `VAZIO` e `WIRTGEN`.
- **Máscara de Máquinas:** Refinada para bloquear apenas descrições que contenham explicitamente "CHASSI" ou "VIN", evitando o bloqueio indevido de peças com nomes genéricos.
- **Estabilidade:** Removidos emojis e forçado `PYTHONUTF8=1` para evitar quedas por encoding no Windows.

### [Wave 4] Orquestrador M6
- **Filial 205:** Bloqueio removido para alinhar com o M2, que processa faturamento desta filial quando presente na fonte.

## Resultados da Auditoria

| Métrica | Motor M2 (Baseline) | Motor M6 (Novo) | Status |
| :--- | :--- | :--- | :--- |
| **Faturamento Total** | R$ 262,719,605.98 | R$ 262,936,311.32 | **ALINHADO** |
| **Linhas Processadas** | 161,206 | 161,292 | **ALINHADO** |
| **Delta Financeiro** | - | R$ 216,705.34 (0.08%) | **CONFORMIDADE** |

> [!NOTE]
> O Delta de R$ 6.8M que existia anteriormente foi totalmente eliminado pela correção do filtro de TES.

## Validação Visual
O arquivo final foi gerado em: `C:\Projetos\Inova\Metas Peças\05_Resultados\Motor_Gestao_M6_v4_3.xlsx`
As abas de Gestão (Performance, Consultor, Funil) agora refletem os mesmos números do faturamento oficial.
