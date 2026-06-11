# Plan v1.1 — Correções e Melhorias de Usabilidade no Modo Interativo CLI

## 1. Abordagem Técnica
Modificar o script `scripts/seo_ge_cli.py` para incluir o índice sequencial das sugestões na tabela e aplicar um parser robusto baseado em Expressão Regular (`re`) para tratar os comandos interativos de forma limpa, resiliente e instrucional.

## 2. Passos de Execução

### Passo 2.1: Modificar a geração da tabela de sugestões (Interface Visual)
No arquivo [scripts/seo_ge_cli.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/seo_ge_cli.py), na função `show_cli_layout`:
1. Adicionar uma nova coluna `#` (ID sequencial) como a primeira coluna do componente `Table` da biblioteca `rich`:
   ```python
   table = Table(title="Sugestões de Unificação (IA)", box=box.ROUNDED, header_style="bold magenta")
   table.add_column("#", justify="center", style="bold cyan") # Nova coluna
   table.add_column("Score", justify="right")
   ...
   ```
2. No loop de preenchimento da tabela (linhas ~302-308), passar o valor de `count + 1` como string na primeira coluna da linha adicionada:
   ```python
   table.add_row(
       str(count + 1), # Índice 1-indexed
       f"{s['score']:.0f}%",
       s['nome'],
       cgc_cand,
       f"[{style}]{veredito}[/{style}]",
       reason
   )
   ```

### Passo 2.2: Refatorar o parser do Comando Interativo (Lógica e Robustez)
Na lógica de seleção interativa da função `show_cli_layout` (linhas ~318-356):
1. Capturar o input e aplicar o seguinte parsing:
   - Limpar espaços e converter para maiúsculas.
   - Tratar tecla Enter (vazia) para Pular/Sair do loop de seleção.
   - Utilizar a regex `r'^([VW D])\s*(\d+)$'` para separar o comando da sugestão e o número sequencial de forma flexível e tolerante a espaços.
2. Validar o comando e o índice informado:
   - Se a entrada for apenas letras de comando válidas (`V`, `W`, `D`) sem número, exibir instrução clara sem lançar exceção.
   - Se a entrada não casar com a regex de comando estruturado, exibir aviso instrutivo: `"Erro: Comando inválido. Use ex: V1 para vincular o candidato 1 ou D2 para descartar o candidato 2."`.
   - Se o índice for menor que 1 ou maior que o total de sugestões exibidas, exibir aviso de índice inválido: `"Erro: Índice fora do intervalo (1 a {count})."`.
3. Processar ações aceitando tanto `V` quanto `W` como "WELD" (vinculação) e `D` como "DISCARD" (descarte):
   - Comando `V` ou `W`: Realiza `record_decision_safe` com a ação `'WELD'`.
   - Comando `D`: Realiza `record_decision_safe` com a ação `'DISCARD'`.

## 3. Plano de Validação e Teste
1. **Verificação de Importação e Sintaxe**:
   - Rodar validação estática no script `scripts/seo_ge_cli.py`.
2. **Teste Interativo Visual**:
   - Executar o script no terminal interativo: `python scripts/seo_ge_cli.py`
   - Realizar a busca de um CNPJ (ex: `10550896000136` ou outro termo do topo).
   - Validar se a tabela renderizada exibe a coluna `#` de 1 a N.
3. **Teste de Robustez do Input**:
   - Digitar comandos inválidos e testar o tratamento de exceções:
     - `V` (apenas a letra de vinculação) -> Esperado: mensagem de instrução clara, sem crash.
     - `v` (letra minúscula) -> Esperado: mensagem de instrução clara, sem crash.
     - `vinculado` -> Esperado: mensagem de instrução clara, sem crash.
     - `V99` (índice fora do intervalo) -> Esperado: mensagem de índice inválido, sem crash.
     - `V 1` (letra + espaço + número) -> Esperado: vincula o candidato 1 com sucesso.
     - `w1` ou `W 1` -> Esperado: vincula o candidato 1 com sucesso.
     - `d1` ou `D 1` -> Esperado: descarta o candidato 1 com sucesso.
