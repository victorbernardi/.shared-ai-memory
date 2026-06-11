# Spec v1.1 — Correções e Melhorias de Usabilidade no Modo Interativo SEO_GE CLI

## 1. Problema
No Modo Interativo do `seo_ge_cli.py` (CLI do Motor de Identidade M0), ao exibir as sugestões de unificação, a tabela gerada não exibe os números sequenciais de cada candidato (ex: 1, 2, 3). Isso impede que o usuário saiba de forma clara qual número deve passar para os comandos de ação (ex: `V1` ou `D2`).

Além disso, o parser de comandos interativos é frágil e propício a falhas de execução (`ValueError`) se o usuário digitar apenas as letras (`V`, `v`, `D`, `d`) sem o índice correspondente, ou se digitar comandos com espaços (ex: `V 1`). Por fim, a mensagem de erro recomenda a letra `W` (Weld) enquanto o código espera estritamente a letra `V` (Vincular).

## 2. Objetivo
Refinar a usabilidade e a resiliência do menu de unificação interativa, adicionando números visuais claros às sugestões de candidatos e aplicando uma camada de parsing tolerante e amigável (com suporte a regex, tolerância a espaços, suporte tanto a `V` quanto a `W` para vinculação, e tratamento correto de erros sem quebrar a execução).

## 3. Requisitos
- **R1 (Numeração Visual)**: A tabela de sugestões de unificação deve incluir uma coluna `#` à esquerda, exibindo os números sequenciais baseados em 1 (1, 2, 3, etc.) para cada sugestão mostrada.
- **R2 (Parsing Resiliente de Input)**: O parser deve processar comandos tolerando minúsculas/maiúsculas, espaços extras e ser capaz de processar tanto `V` quanto `W` como sinônimos para Vincular/Soldar.
- **R3 (Tratamento Amigável de Erros)**: Se o usuário digitar um comando malformado (ex: apenas `V`, apenas `v`, `vinculado`, ou números fora do intervalo), o script não deve quebrar com um traceback de erro. Deve exibir uma mensagem clara e instrucional (ex: `"Erro: Use o formato V1 para vincular o candidato 1 ou D2 para descartá-lo."`) e aguardar uma nova entrada.
- **R4 (Consistência de Comandos)**: Garantir compatibilidade com `V` (Vincular), `W` (Weld) e `D` (Descartar).

## 4. Design de UX Proposto
### Tabela de Sugestões:
```
                                 Sugestões de Unificação (IA)                                 
                                                                                              
  #   Score  Candidato                      CGC/CNPJ        Veredito  Motivo                  
 ──────────────────────────────────────────────────────────────────────────────────────────── 
  1     70%  AMBIPAR ENVIRONMENTAL SUP...   00512573000102  HOLDING   Elo Societário (QSA)... 
  2     70%  AMBIPAR ENVIRONMENTAL MIN...   61059978000628  HOLDING   Elo Societário (QSA)... 
```

### Prompt & Parser:
Se o usuário digitar `V` ou `v` ou `vinculado` ou `V ` ou `V99`:
- Mensagem: `[red]Erro: Comando inválido. Use ex: V1 para vincular o candidato 1 ou D2 para descartar o candidato 2.[/red]` (Se índice for inválido, avisar que o índice está fora do intervalo).

## 5. Critérios de Aceite
- A tabela mostra uma coluna de numeração sequencial de 1 a N.
- Comandos válidos como `v1`, `V 1`, `w1`, `W 1` e `d1`, `D 1` funcionam e realizam a vinculação/descarte com sucesso.
- Comandos inválidos (ex: `V`, `v`, `W`, `D`, `vinculado`, `D 99`) não quebram o loop do CLI e exibem aviso instrutivo.
