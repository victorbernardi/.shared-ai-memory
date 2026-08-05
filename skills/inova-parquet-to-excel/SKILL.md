---
name: inova-parquet-to-excel
version: 1.0.0
description: >
  Converte arquivos Parquet em Excel de uma única aba, resolvendo ou solicitando
  os caminhos de entrada e saída.
tools:
  - claude-code
  - codex
  - commandcode
tier: 1
category: utility
triggers:
  - converter parquet para excel
  - parquet xlsx
  - parquet to excel
  - inova-parquet-to-excel
author: Victor
---

# inova-parquet-to-excel

## Objetivo

Converter um arquivo `.parquet` em um `.xlsx` com todos os dados em uma única
aba chamada `Dados`.

## Fluxo

1. Identifique o caminho do `.parquet` mencionado no pedido ou anexo.
2. Se houver zero ou vários candidatos, pergunte ao usuário qual arquivo usar.
3. Identifique o caminho `.xlsx` informado. Se estiver ausente, sugira a mesma
   pasta e o mesmo nome-base do Parquet e peça confirmação.
4. Se o destino já existir, peça confirmação explícita antes de sobrescrever.
5. Execute na raiz desta skill:

```bash
python scripts/convert.py --input "<caminho-parquet>" --output "<caminho-xlsx>"
```

Para uma substituição confirmada, acrescente `--overwrite`.

## Validações

- A entrada deve existir e terminar em `.parquet`.
- A saída deve terminar em `.xlsx` e ser diferente da entrada.
- Recuse arquivos com mais de 1.048.576 linhas antes da gravação.
- Em qualquer erro, informe a causa e não deixe saída parcial.

## Resultado

Informe o caminho absoluto do arquivo criado, quantidade de linhas e colunas e
o nome da aba (`Dados`).

## Constraints

- Nunca divida a exportação em múltiplas abas nesta versão.
- Nunca sobrescreva saída sem confirmação explícita.
- Preserve os dados e índices não devem ser exportados como coluna adicional.

<!-- @if platform=codex -->
## Fluxo Codex/GPT

Use o fluxo acima e execute o comando Python diretamente no ambiente autorizado.
<!-- @endif -->

<!-- @if platform=claude -->
## Fluxo Claude Code

Use o fluxo acima e execute o comando Python via ferramenta de terminal, pedindo
confirmação antes de qualquer sobrescrita.
<!-- @endif -->

<!-- @if platform=commandcode -->
## Fluxo CommandCode

Use o fluxo acima; mostre os caminhos detectados e aguarde confirmação quando o
destino estiver ausente ou já existir.
<!-- @endif -->
