# Especificação: Filtro de Consultores BUP 2026 (v1)

## Contexto
O Motor BUP (Base Única de Pós-Venda) utiliza um filtro de "Vendedores Ativos 2026" para atribuir consultores aos clientes. Inicialmente, o filtro automático identificou 35 nomes. A coordenação refinou esta lista para **14 consultores de peças** oficiais.

## Mapeamento de Consultores (Ouro)

| ID | Nome Protheus | Nome Referência (Coordenação) |
|---|---|---|
| 000720 | LUANA ESTER COSTA MACHADO | Luana Ester Costa Machado |
| 000559 | TOMAZ LOYOLA ZEI | TOMAZ LOYOLA ZEI |
| 000906 | DANILO ALVES RIBEIRO NETO | DANILO ALVES RIBEIRO NETO |
| 000357 | AURELIO APARECIDO DA COSTA | AURELIO APARECIDO DA COSTA |
| 000488 | ANDRE VITOR MIRANDA ALVES | ANDRE VITOR MIRANDA ALVES |
| 000885 | DANILLO ANDRADE BERMUDES | DANILLO ANDRADE BERMUDES |
| 000431 | LUIZ MARCELUS PROSPERI | LUIZ MARCELUS PROSPERI |
| 000818 | LUIS PAULO PEREIRA BARBOSA | LUIS PAULO PEREIRA BARBOSA |
| 000651 | GRAZIANE FRANCISCA DA SILVA LEITE | GRAZIANE LEITE MOREIRA |
| 000449 | PAULA EBERT DOS REIS | PAULA EBERT DOS REIS |
| 000657 | SAMARA VITORIA ALMEIDA DE SOUZA | SAMARA VITORIA ALMEIDA DE SOUZA |
| 000884 | VINICIUS DO NASCIMENTO LENZI | VINICIUS HENRIQUE LENZI |
| 000666 | MOISES DE SOUZA ANDRADE DE CARVALHO | MOISES CARVALHO DE OLIVEIRA |
| 000730 | NATHALIA FERREIRA DE MENEZES | NATHALIA MENEZES DE SOUZA |

## Análise de Discrepância (35 vs 14)
A diferença de 21 nomes deve-se a consultores que atuam em Centros de Custo de **Oficina** e **CRC**. Embora esses profissionais consumam/vendam peças, eles não são os "Consultores de Pós-Venda" responsáveis pela carteira de clientes BUP.

**Padrão Identificado**:
- Consultores Reais: Focados em CCs de vendas diretas (`PECAS CSN`, `PECAS ATVOS`).
- Consultores Excluídos: Vinculados a `SERVICOS PECAS`, `SERVICOS CRC`, `MANUTENCAO PREDITAL`, etc.

## Ação Técnica
1. Atualizar `data/config/vendedores_ativos_2026.json`.
2. Refinar a query SQL em `scripts/generate_active_sellers_config.py` para priorizar apenas CCs de peças diretas ou usar a White List.
