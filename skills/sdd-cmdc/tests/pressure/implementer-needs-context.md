# Pressão: implementador precisa de contexto

## Contexto

O worker Command Code retorna `NEEDS_CONTEXT` porque o brief não informa uma
interface necessária. O reviewer ainda não foi executado.

## Resultado esperado

- não iniciar review com trabalho incompleto;
- registrar a pergunta e a lacuna no relatório/ledger;
- preparar uma nova invocação `cmdc` com o mesmo modelo fixo,
  brief/relatório/findings e o contexto adicional;
- só gerar o pacote de review após um relatório `DONE` ou
  `DONE_WITH_CONCERNS` válido.
