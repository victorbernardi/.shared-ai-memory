# Plano de correção: sessão independente de review do sdd-cmdc-opencode

> **Para execução:** usar `superpowers:executing-plans` em uma nova sessão. O
> objetivo deste plano é corrigir a infraestrutura e o contrato de review; não
> reimplementar a tarefa já concluída no branch `feat/sdd-cmdc-opencode`.

## Objetivo

Permitir testar e executar o review delegado de uma implementação existente em
uma sessão host limpa, independente da sessão que implementou o código, sem
acionar novamente o Command Code. A sessão deve terminar com evidência
auditável ou com `REVIEW INCOMPLETE`/`BLOCKED`; nunca com aprovação implícita.

## Diagnóstico confirmado

- `review-package` concluiu para o range `0f3d86c..d5eddb8`.
- `ocr delegate preview` e `ocr delegate rule` concluíram para os três
  arquivos Python reviewable; `SKILL.md` foi explicitamente excluído por
  `unsupported_ext`.
- A sessão `codex exec --ephemeral --sandbox read-only` limpa não produziu
  mensagem final dentro do limite de 184 segundos e terminou com exit code
  `124`.
- O resultado correto foi `REVIEW INCOMPLETE`; nenhum re-review ou aprovação
  foi emitido.
- O smoke test não alterou arquivos rastreados. A evidência está em
  `.superpowers/sdd/issue-129-recovery/review-only-smoke-test.md`.

## Restrições globais

- Fonte canônica: `skills/sdd-cmdc-opencode` neste worktree; não editar a cópia
  instalada durante a implementação.
- Não modificar `skills/sdd-cmdc`, `skills/subagent-driven-development` ou
  qualquer skill não relacionada.
- A implementação original já está concluída; o modo `review-only` não pode
  chamar `scripts/cmdc-implementer.py`, criar um novo implementador ou iniciar
  um fix round automaticamente.
- Todo review continua exigindo `open-code-review-delegate`,
  `ocr delegate preview`, `ocr delegate rule` e leitura do diff exato.
- Nunca executar `ocr review`, `ocr llm test`, configurar `OCR_LLM_*` ou
  `OPENAI_API_KEY`, nem publicar comentários no GitHub.
- O executor da sessão host deve ser somente leitura, efêmero, não interativo e
  limitado a um processo filho explicitamente identificado.
- Timeout, processo órfão, saída parcial, ausência de mensagem final ou
  evidência inválida nunca produzem `REVIEW CLEAN`.
- Preservar mudanças não relacionadas e não usar `reset --hard`, force push ou
  remoção destrutiva de worktrees.

## Arquivos e interfaces

| Caminho | Mudança |
| --- | --- |
| `skills/sdd-cmdc-opencode/scripts/review-session.py` | Novo launcher de uma sessão host limpa, com timeout, captura e limpeza verificável |
| `skills/sdd-cmdc-opencode/task-reviewer-prompt.md` | Template canônico do review inicial do range `BASE..HEAD`, consumido pela sessão host e não por um reviewer Codex |
| `skills/sdd-cmdc-opencode/re-review-prompt.md` | Template canônico do re-review restrito do range `FIX_BASE..HEAD`, com findings anteriores e vereditos `ADDRESSED`/`NOT ADDRESSED` |
| `skills/sdd-cmdc-opencode/tests/test_review_session.py` | Testes unitários/integração controlada do launcher |
| `skills/sdd-cmdc-opencode/SKILL.md` | Contrato explícito para `review-only`, sessão independente e estados de saída |
| `skills/sdd-cmdc-opencode/tests/test_skill_contract.py` | Regressões estruturais do contrato novo |
| `skills/sdd-cmdc-opencode/tests/pressure/clean-review-session.md` | Cenário de pressão para timeout, pedido de permissão e saída parcial |
| `docs/superpowers/specs/2026-08-01-sdd-cmdc-opencode-design.md` | Atualizar o design para registrar a sessão host limpa como limite de contexto, não como fallback de review |

### Interface proposta do launcher

Implementar uma interface determinística, documentada no `--help`:

```text
review-session.py PLAN_FILE BASE HEAD PROMPT_FILE REPORT_FILE
    [--timeout-seconds N]
    [--repo REPOSITORY]
    [--evidence-dir DIRECTORY]
```

O launcher deve:

1. validar que `PLAN_FILE`, `PROMPT_FILE`, `REPORT_FILE` e o repositório
   existem; validar `BASE` e `HEAD` antes de iniciar a sessão;
2. gerar o comando somente com `codex exec --ephemeral --sandbox read-only
   --cd REPO --json --output-last-message REPORT_FILE -`, recebendo o prompt
   pelo stdin;
3. resolver o executável Codex sem aceitar `C:\Windows\System32\cmd.exe` como
   backend e registrar o caminho efetivamente usado;
4. capturar stdout JSONL, stderr, PID, início/fim, duração, timeout, exit code,
   caminho do relatório e o range exato em arquivos de evidência separados;
5. aplicar timeout configurável e, ao expirar, encerrar somente a árvore do
   processo filho criado pelo launcher, confirmar que ela terminou e preservar
   a saída parcial;
6. retornar `0` somente quando a sessão terminou, a mensagem final existe e o
   relatório contém os campos obrigatórios do review; retornar `124` para
   timeout e código não zero específico para processo órfão, saída ausente ou
   falha de execução;
7. emitir um resumo JSON final com `status`, usando `REVIEW CLEAN` apenas se o
   relatório host declarar esse estado e toda a evidência determinística
   estiver presente. Caso contrário, usar `REVIEW INCOMPLETE` para timeout ou
   saída parcial, e `BLOCKED` para falha de execução/evidência.

O launcher não executa OCR nem decide achados. Ele apenas garante a fronteira
da sessão host e a evidência de ciclo de vida; o prompt fornecido pelo
controller contém os resultados de `preview`, `rule`, diffs e regras a serem
revisados.

Os prompts de review são separados por intenção, como na skill
`subagent-driven-development`: `task-reviewer-prompt.md` define o review
inicial e `re-review-prompt.md` define exclusivamente a verificação de uma
correção. Eles são templates de instrução para a nova sessão host, não
seletores de modelo nem autorização para usar um reviewer Codex. O controller
renderiza cada template em um `PROMPT_FILE` dentro do workspace ignorado do
plano; a sessão deve receber somente o template renderizado e as evidências
do range correspondente.

## Tarefas

### Task 1 — Especificar o contrato de review-only e da sessão limpa

**Arquivos:** `SKILL.md`, `test_skill_contract.py`, cenário de pressão e
especificação de design.

- Adicionar uma seção `Review-only` com entradas obrigatórias: plano, `BASE`
  (ou `MERGE_BASE`), `HEAD`, pacote de review, saída de `preview`, grupos de
  regras, diffs e caminho do relatório.
- Criar `task-reviewer-prompt.md` e `re-review-prompt.md` como templates
  versionados e distintos. O primeiro cobre o review inicial de `BASE..HEAD`;
  o segundo cobre apenas `FIX_BASE..HEAD`, recebe a lista de findings anterior
  e exige o veredito `ADDRESSED` ou `NOT ADDRESSED` para cada item.
- Determinar a sequência: gerar pacote; executar preview; validar escopo;
  resolver regras; ler diffs; iniciar uma sessão host limpa; registrar o
  veredito.
- Declarar que review-only não chama implementador, não corrige findings e não
  inicia re-review sem autorização explícita; ele somente reporta findings e
  estado.
- Definir a independência: novo processo efêmero, sem histórico da sessão
  implementadora, com acesso somente leitura ao mesmo worktree e ao mesmo
  range. Isso não é fallback para OCR; OCR continua sendo pré-requisito.
- Definir o contrato do relatório: `Files reviewed`, `Excluded files`,
  `Commands`, `Exit codes`, `Critical/High`, `Medium`, `Review status`,
  evidência de `BASE`/`HEAD`, e recomendações com `path`, `start_line` e
  `end_line` quando aplicável.
- Atualizar o design para distinguir “host session boundary” de “Codex review
  fallback”; manter as proibições de API/LLM e GitHub.
- Declarar que os templates separados não criam um backend de review novo:
  ambos continuam exigindo OCR prévio e são executados somente pelo launcher
  da sessão host limpa.
- Adicionar asserções estruturais para `review-only`, `review-session.py`,
  `--ephemeral`, `--sandbox read-only`, `REVIEW INCOMPLETE`, `BLOCKED`,
  existência dos dois templates, separação entre review e re-review,
  ausência de CMDc no caminho review-only e ausência de fallback.

### Task 2 — Implementar o launcher com fail-closed e limpeza de processos

**Arquivo:** `skills/sdd-cmdc-opencode/scripts/review-session.py`.

- Implementar funções pequenas e testáveis para resolver o Codex, construir o
  comando, validar refs, iniciar a sessão, coletar evidência, aplicar timeout,
  encerrar a árvore e classificar o resultado.
- Não herdar `OPENAI_API_KEY`, `OCR_LLM_*` ou outras configurações de endpoint
  como mecanismo do review; não adicionar flags de bypass de sandbox ou de
  aprovação.
- No Windows, usar criação de grupo/processo filho e uma rotina de cleanup
  limitada ao PID criado; após cleanup, confirmar ausência do processo e
  registrar qualquer falha como `BLOCKED`.
- Tornar o timeout explícito e suficientemente amplo para o review completo,
  mas sempre finito; documentar o valor default e permitir um valor maior no
  smoke test sem retirar o limite.
- Não interpretar exit code zero como aprovação. A saída final deve existir,
  conter o status do review e estar acompanhada da evidência de OCR fornecida
  pelo controller.

### Task 3 — Criar testes do ciclo de vida e regressões

**Arquivo:** `skills/sdd-cmdc-opencode/tests/test_review_session.py`.

Cobrir com executáveis falsos e fixtures locais, sem chamar a rede ou uma
assinatura real:

- comando correto, sandbox somente leitura, processo efêmero, `--json`,
  `--output-last-message` e prompt via stdin;
- sucesso com relatório completo e status `REVIEW CLEAN` somente com evidência
  válida;
- exit code zero sem mensagem final ou sem campos obrigatórios → `BLOCKED`;
- timeout → exit code `124`, `REVIEW INCOMPLETE`, stdout/stderr preservados e
  nenhum processo filho sobrevivente;
- processo filho que não encerra → `BLOCKED` e diagnóstico explícito;
- falha ao resolver Codex, ref inválida ou arquivo obrigatório ausente →
  `BLOCKED` antes de iniciar qualquer processo;
- prompt contendo tentativa de CMDc, API ou comentário GitHub não altera a
  política do launcher e não é executado como ação adicional.

Usar `subprocess` com fixtures controladas e `tmp_path`; não fazer asserts
frágeis sobre tempo exato, apenas sobre limite, estado e evidência.

### Task 4 — Integrar o launcher ao workflow e testar um review-only real

**Arquivos:** `SKILL.md`, `test_skill_contract.py` e artefatos ignorados em
`.superpowers/sdd/<plan-basename>/`.

- Documentar o comando de review-only usando o range já implementado
  `0f3d86c..d5eddb8` como exemplo de fixture histórica, sem hardcode desse
  range no código.
- Para uma execução real, gerar um pacote novo com
  `scripts/review-package PLAN_FILE BASE HEAD` e registrar o caminho.
- Executar `ocr delegate preview --from BASE --to HEAD` no shell que resolva
  corretamente as refs; registrar shell, comando e exit code.
- Executar `ocr delegate rule` para cada arquivo reviewable; registrar
  excluídos e justificativas. Não omitir `SKILL.md` sem registrar a razão.
- Montar o prompt da nova sessão limpa com apenas as evidências do range e
  instrução de review, renderizando `task-reviewer-prompt.md` para review
  inicial ou `re-review-prompt.md` para re-review, sem contexto acumulado e
  sem autorização para editar.
- Executar o launcher com timeout finito. Se terminar, verificar o relatório
  independentemente; se expirar, preservar `REVIEW INCOMPLETE` e não repetir
  automaticamente.
- Registrar no ledger o estado, PID, exit code, timeout, arquivos cobertos,
  arquivos excluídos, relatório e diagnóstico de cleanup.
- Validar que o review-only não alterou o worktree e não chamou
  `cmdc-implementer.py`, `ocr review`, `ocr llm test` ou qualquer endpoint.

### Task 5 — Verificar, promover e preparar o handoff operacional

- Rodar a suíte direcionada, a suíte completa da skill, `git diff --check`,
  `py_compile` do launcher e os validadores de documentação disponíveis.
- Verificar que `skills/sdd-cmdc` e `skills/subagent-driven-development` não
  possuem diff.
- Comparar conjuntos de arquivos, ausência de `.git` copiado e SHA-256 de
  `SKILL.md` entre fonte e destinos somente depois da validação.
- Sincronizar a skill completa para `.agents\skills\sdd-cmdc-opencode` e
  `.codex\skills\sdd-cmdc-opencode`, sem adicionar esses destinos ao commit.
- Fazer uma nova sessão limpa apenas para executar o review-only real. Um
  timeout continua sendo `REVIEW INCOMPLETE`, mesmo que o processo externo
  retorne exit code zero.
- Commitar somente a fonte canônica e o plano/artefatos rastreados, fazer push
  normal na branch de feature e registrar SHA, status da worktree e destinos
  sincronizados no handoff.

## Critérios de aceitação

1. Existe um caminho documentado e testado para revisar implementação pronta
   sem executar CMDc.
2. Toda sessão host limpa tem timeout finito, captura de stdout/stderr,
   relatório final, exit code, PID e cleanup verificado.
3. Timeout, saída parcial, processo órfão, ref inválida ou evidência ausente
   terminam em `REVIEW INCOMPLETE` ou `BLOCKED`, nunca em `REVIEW CLEAN`.
4. `REVIEW CLEAN` exige preview/rule/diff completos, relatório host válido e
   evidência de comandos/exit codes.
5. Os testes não usam rede, API key, OCR LLM ou GitHub e não deixam processos
   filhos ativos.
6. A implementação original, as skills irmãs e o checkout `C:\Projetos\Inova`
   permanecem intocados.

## Validação sugerida

```powershell
python -m pytest skills/sdd-cmdc-opencode/tests -q
python -m py_compile skills/sdd-cmdc-opencode/scripts/review-session.py
git diff --check
git diff --name-only -- skills/sdd-cmdc skills/subagent-driven-development
```

Para o smoke test real, registrar o resultado em um arquivo ignorado do
workspace do plano. O único resultado aceitável sem relatório final é:

```text
REVIEW INCOMPLETE — CLEAN_HOST_TIMEOUT: sessão independente sem mensagem final
```
