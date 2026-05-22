# Walkthrough: Auditoria de Ferramentas Nativas

Realizamos uma validação sistemática de todas as ferramentas de interação com o sistema para sanar as dúvidas de mapeamento.

## Resultados da Auditoria

| Comando Documentado (`gemini-tools.md`) | Status do Teste | Comando "Sugerido" | Status do Alias |
|------------------------------------------|-----------------|--------------------|-----------------|
| `view_file`                              | ✅ Funcional    | `read_file`        | ❌ Não existe   |
| `write_to_file`                          | ✅ Funcional    | `write_file`       | ❌ Não existe   |
| `replace_file_content`                   | ✅ Funcional    | `replace` / `edit` | ❌ Não existe   |
| `multi_replace_file_content`             | ✅ Funcional    | -                  | -               |
| `list_dir`                               | ✅ Funcional    | -                  | -               |
| `grep_search`                            | ✅ Funcional    | -                  | -               |
| `run_command`                            | ✅ Funcional    | `run_shell`        | ❌ Não existe   |

## O que foi testado

1.  **Leitura:** Verificamos o arquivo `ANTIGRAVITY.md` com sucesso via `view_file`.
2.  **Escrita:** Criamos um arquivo em `./scratch/audit/test.txt` via `write_to_file`.
3.  **Edição:** Alteramos o arquivo de teste usando `replace_file_content` e `multi_replace_file_content` sem falhas.
4.  **Busca:** Localizamos strings via `grep_search` e listamos diretórios via `list_dir`.
5.  **Execução:** Executamos `Get-Content` via `run_command` no Powershell.

## Conclusão
A documentação atual em `gemini-tools.md` é a **fonte da verdade definitiva** para este ambiente. Os nomes alternativos (como `read_file`) provavelmente pertencem a outros ecossistemas (como Claude Code ou implementações legadas) e não devem ser usados aqui.

> [!TIP]
> Sempre que houver dúvida, consulte a aba de ferramentas (tools) do sistema, que reflete exatamente o que está declarado no prompt.

---
**Auditoria Finalizada em: 2026-05-05**
