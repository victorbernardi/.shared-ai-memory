# Superpowers Update — Especificação de Design

**Data:** 2026-07-28  
**Status:** aprovado pelo usuário

## Objetivo

Criar a skill `superpowers-update` para detectar alterações em `skills/` do repositório público `obra/superpowers` na branch `main` e sincronizar somente as skills modificadas com a fonte local `.shared-ai-memory\skills` e os runtimes instalados do usuário.

## Fonte da verdade

- Repositório: `https://github.com/obra/superpowers.git`
- Branch: `main`
- A fonte local não substitui o repositório público; ela é um espelho versionado para os destinos instalados.
- A comparação de conteúdo ignora somente diferenças de final de linha CRLF/LF.

## Destinos padrão

1. `C:\Users\victor.bernardi\.shared-ai-memory\skills`
2. `C:\Users\victor.bernardi\.agents\skills`
3. `C:\Users\victor.bernardi\.codex\skills`
4. `C:\Users\victor.bernardi\.claude\skills`
5. `C:\Users\victor.bernardi\.commandcode\skills`

O comando aceitará destinos adicionais explicitamente para projetos que tenham um catálogo local próprio.

## Comportamento

### Modo `check`

- Consulta o SHA atual de `obra/main`.
- Obtém uma cópia temporária do repositório público.
- Enumera todas as pastas `skills/<nome>` que contenham `SKILL.md`.
- Compara arquivos canônicos entre a fonte pública e cada destino.
- Classifica skills presentes na fonte pública como novas, modificadas ou iguais.
- Reporta skills e arquivos extras locais sem removê-los. Uma pasta local ausente da fonte não é declarada como removida sem evidência de que era gerenciada pelo Superpowers, evitando confundir skills próprias do ecossistema com skills removidas do projeto público.
- Não modifica repositórios, instalações ou arquivos de relatório persistentes.

### Modo `apply`

- Executa o mesmo preflight do modo `check`.
- Se não houver diferença, encerra como `NO_OP` sem escrever arquivos.
- Se houver diferença, atualiza somente as skills afetadas.
- Preserva arquivos extras que não existem na fonte pública.
- Cria backup temporário para rollback transacional.
- Verifica os hashes após a cópia.
- Remove o diretório temporário e o relatório ao terminar.

### Relatórios

- A saída resumida é exibida no terminal.
- O relatório detalhado é criado somente em `%TEMP%\superpowers-update\<run-id>\report.json`.
- O diretório temporário é removido ao final, inclusive após falha quando possível.
- A opção `--report <caminho>` permite persistir um relatório explicitamente solicitado.
- Nenhum `audit_result.json` ou outro artefato é criado em `skills/` durante a execução normal.

## Segurança e limites

- Não apagar arquivos extras automaticamente.
- Não executar `git reset`, `git clean`, `git force-push` ou exclusão de branches.
- Não fazer commit, push ou merge automaticamente; a skill deve reportar as mudanças para o fluxo Git normal.
- Falhas de rede, fonte inválida, destino não gravável ou verificação pós-cópia inconsistente devem abortar com rollback.

## Interface proposta

```text
python scripts/superpowers_update.py check [--target PATH ...] [--report PATH]
python scripts/superpowers_update.py apply [--target PATH ...] [--report PATH]
```

Saídas principais:

- `NO_OP`: nenhuma skill precisa de atualização.
- `CHANGES_AVAILABLE`: o modo `check` encontrou diferenças.
- `UPDATED`: o modo `apply` sincronizou as skills e verificou os destinos.
- `FAILED`: operação abortada; detalhes ficam no terminal ou no relatório explícito.

## Testes

- Detecção de skill nova, modificada, igual e de candidatas removidas somente quando marcadas como gerenciadas.
- Ignorar CRLF/LF na comparação.
- Atualizar somente a skill modificada.
- Preservar arquivos extras.
- Não escrever relatório persistente por padrão.
- Limpar relatório temporário em sucesso.
- Rollback quando um destino falhar.
- Validação final de hashes nos cinco destinos padrão.
