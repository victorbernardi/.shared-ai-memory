# Design: inova-parquet-to-excel

## Objetivo

Criar uma skill que converte um arquivo `.parquet` em uma pasta de trabalho
Excel `.xlsx`, em uma única aba.

## Interação

1. A skill identifica o arquivo de entrada a partir de um caminho explicitamente
   mencionado no pedido ou de um anexo disponível.
2. Se houver mais de um candidato, nenhum candidato, ou incerteza sobre o
   destino, solicita ao usuário o respectivo caminho.
3. Para um destino não informado, sugere a mesma pasta e o mesmo nome-base do
   Parquet, com extensão `.xlsx`, e pede confirmação antes de gravar.

## Conversão

- Lê o Parquet com uma biblioteca Python disponível no ambiente.
- Exporta todas as linhas e colunas para uma única aba, preservando os tipos
  compatíveis com Excel.
- Não divide dados entre abas e não fornece fallback CSV nesta primeira versão.

## Validações e falhas

- O arquivo de entrada deve existir e ter extensão `.parquet`.
- O destino deve terminar em `.xlsx` e não pode ser o próprio arquivo de entrada.
- Antes de gravar, a skill valida o limite de 1.048.576 linhas por aba do Excel.
  Se o arquivo excedê-lo, encerra sem gerar arquivo parcial e informa o limite.
- Dependências ausentes, arquivos corrompidos e falhas de escrita devem retornar
  uma mensagem acionável sem apagar ou sobrescrever arquivos sem confirmação.

## Resultado

Ao terminar, a skill informa o caminho absoluto do `.xlsx` criado, a quantidade
de linhas e colunas exportadas e o nome da aba.

## Critérios de aceitação

- Um Parquet válido dentro do limite é convertido para `.xlsx` em uma única aba.
- Caminhos ambíguos ou ausentes são solicitados ao usuário.
- O limite do Excel é recusado antes da criação do arquivo de saída.
- A nova skill é registrada no Ledger com papel e gatilhos específicos.
