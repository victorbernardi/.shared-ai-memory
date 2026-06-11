# Especificação Técnica - Planilha Desbloqueada com Validação de Dados (v2)

## 1. Contexto do Problema e Novas Diretrizes
O usuário solicitou que a planilha seja gerada sem proteção/bloqueio de células (todas as colunas devem ficar liberadas para edição comum).
No entanto, para manter a consistência dos indicadores comerciais de pós-vendas, as seguintes restrições de validação de dados devem ser aplicadas:
1. **Coluna Retorno do Contato (O / 15):** Restringir o preenchimento apenas às opções da lista dropdown: `"Venda"`, `"Venda Perdida"` ou `"Sem Contato"`.
2. **Coluna Observações (P / 16):** Permitir digitação livre, mas restringir o comprimento do texto a um máximo de **250 caracteres**.

## 2. Requisitos de Implementação no openpyxl
Para atender a esses requisitos:
- A propriedade de proteção da folha (`ws.protection`) deve ser desabilitada ou omitida. Não haverá mais senha `"InovaPosVendas2026"` ou travamento de células.
- **Validação da Lista (Retorno do Contato):**
  - Tipo: `list`
  - Valores permitidos: `"Venda,Venda Perdida,Sem Contato"`
  - Comportamento: Impedir entradas fora da lista exibindo erro explicativo.
- **Validação de Comprimento de Texto (Observações):**
  - Tipo: `textLength`
  - Operador: `lessThanOrEqual`
  - Tamanho máximo: `250`
  - Comportamento: Exibir erro informativo caso o usuário insira um texto superior a 250 caracteres.

## 3. Critérios de Aceitação
- Planilha gerada em formato `.xlsx` sem senha de proteção e totalmente aberta para edição.
- A coluna O (Retorno do Contato) possui validação de dados exigindo seleção exclusiva entre `"Venda"`, `"Venda Perdida"`, `"Sem Contato"`.
- A coluna P (Observações) possui validação de dados limitando o comprimento da entrada a 250 caracteres.
- Outras colunas não têm nenhuma restrição ou trava aplicada.

## 4. Roteiro de Testes
O teste unitário em `tests/test_load_consultor.py` validará:
1. `ws.protection.sheet` é `False` ou `None` (indicando que a planilha não está protegida).
2. A validação de dados do dropdown de retorno está corretamente mapeada no intervalo `O2:O[N]`.
3. A validação de comprimento de texto na coluna de observações está mapeada no intervalo `P2:P[N]` com limite `lessThanOrEqual` de `250`.
