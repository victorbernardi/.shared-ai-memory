---
title: "sdd-cmdc: implementação de tarefas via Command Code"
date: 2026-07-30
status: approved-design
---

# sdd-cmdc: implementação de tarefas via Command Code

## Objetivo

Criar uma skill independente chamada `sdd-cmdc`, derivada de
`subagent-driven-development`, para executar planos de implementação com o
mesmo ciclo de ledger, brief, revisão por tarefa, correções limitadas e revisão
final. A única substituição de backend será a execução do implementador: em
vez de um subagente Codex, cada implementador será uma invocação do Command
Code CLI (`cmdc`) usando `deepseek/deepseek-v4-flash`.

O Codex continuará sendo o orquestrador da sessão e continuará executando os
reviewers de especificação/qualidade, re-reviewers e reviewer final conforme a
skill original.

## Fronteira de responsabilidade

### Permanece igual ao `subagent-driven-development`

- pré-flight, worktree isolada e ledger por plano;
- leitura de plano e criação de briefs por tarefa;
- uma implementação por vez;
- contrato `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` e `BLOCKED`;
- revisão de especificação e qualidade após cada tarefa;
- ciclo de até cinco rodadas de correção;
- re-review escopado após cada rodada;
- registro de minors, findings parked e bloqueios no ledger;
- revisão ampla final e fluxo de finalização da branch.

### Muda

- somente o dispatch do implementador;
- o implementador roda por `cmdc`, em modo de edição, com o modelo fixo
  `deepseek/deepseek-v4-flash`;
- no Windows, `cmdc` é o executável preferencial para evitar a colisão de
  `cmd` com `C:\Windows\System32\cmd.exe`;
- cada rodada de implementação é uma nova invocação de `cmdc`; a continuidade
  é mantida pelos artefatos do plano, relatório persistente e findings
  explícitos, não por uma sessão viva do subagente.

## Estrutura proposta

`skills/sdd-cmdc/` será uma cópia independente dos arquivos auxiliares da
skill original:

- `SKILL.md`: fluxo completo com a única troca de backend documentada;
- `implementer-prompt.md`: contrato do implementador adaptado para Command
  Code;
- `task-reviewer-prompt.md`: cópia sem alteração funcional, para reviewer
  Codex;
- `re-review-prompt.md`: cópia sem alteração funcional, para re-reviewer
  Codex;
- `scripts/sdd-workspace`, `scripts/task-brief` e `scripts/review-package`:
  cópias funcionais dos auxiliares originais;
- `scripts/cmdc-implementer.py`: adaptador determinístico para resolução do
  executável, montagem do comando, execução, preservação de stdout/stderr e
  emissão do contrato de status.

O adaptador será local à skill. Não haverá dependência de clone ou checkout
do repositório externo em tempo de execução. O repositório
`Lehsqa/command-code-subagent` será usado como referência para o padrão de
wrapper e invocação, mas `sdd-cmdc` terá um contrato próprio e mais estreito.

## Fluxo de implementação

1. O orquestrador registra `BASE`, gera o `task-N-brief.md` e prepara o prompt
   do implementador com o caminho do relatório.
2. O adaptador verifica se o workspace e o prompt existem e resolve `cmdc`.
3. O adaptador executa, por padrão:

   ```text
   cmdc -p --model deepseek/deepseek-v4-flash --max-turns 20
        --trust --skip-onboarding --yolo
   ```

4. O implementador Command Code lê somente o brief e os caminhos relevantes,
   implementa, testa, faz self-review, commita e grava o relatório completo.
5. O orquestrador valida o relatório e só então gera o pacote de review e
   despacha o reviewer Codex.
6. Rodadas de correção repetem o mesmo adaptador com os findings completos e
   o relatório persistente; não há fallback silencioso para implementação
   direta pelo Codex.

O limite de `20` turnos será o padrão do adaptador e poderá ser alterado pelo
orquestrador para uma tarefa específica sem alterar o modelo obrigatório.

## Contrato de erros e bloqueios

Uma falha operacional do Command Code não será representada por um bloqueio
silencioso. O adaptador deverá preservar diagnóstico suficiente para que o
orquestrador decida o próximo passo.

Formato mínimo emitido em stdout/stderr e anexado ao relatório quando
possível:

```text
STATUS: BLOCKED
BLOCKER_CODE: CMD_NOT_FOUND | AUTH_REQUIRED | MODEL_UNAVAILABLE | RATE_LIMITED | TIMEOUT | PROCESS_FAILED | REPORT_MISSING
MESSAGE: <causa legível>
COMMAND: <comando sem segredos>
EXIT_CODE: <inteiro ou N/A>
STDERR: <diagnóstico preservado>
ACTION: <ação concreta recomendada>
```

Regras:

- `CMD_NOT_FOUND`: instalar/configurar o Command Code ou corrigir o PATH;
- `AUTH_REQUIRED`: autenticar o Command Code, sem repetir em loop;
- `MODEL_UNAVAILABLE`: confirmar `cmdc --list-models` e disponibilidade do
  modelo fixo;
- `RATE_LIMITED`: parar novas invocações e aguardar intervenção;
- `TIMEOUT`: registrar o limite atingido e permitir reexecução controlada;
- `PROCESS_FAILED`: preservar exit code e stderr;
- `REPORT_MISSING`: tratar processo sem relatório como falha do contrato,
  mesmo que o exit code seja zero.

O orquestrador registrará no ledger uma linha como:

```text
Task N: BLOCKED — MODEL_UNAVAILABLE: deepseek/deepseek-v4-flash não aceito pelo plano da conta
```

Ele não iniciará o reviewer da tarefa enquanto o implementador não produzir
um status válido. Se o processo retornar um relatório válido com
`NEEDS_CONTEXT` ou `BLOCKED` produzido pelo próprio implementador, o fluxo de
tratamento do SDD original continuará sendo aplicado. Falhas do adaptador não
serão convertidas em `DONE` nem em implementação Codex.

## Resolução do executável

- padrão: `cmdc`;
- Windows: aceitar `cmdc`, `cmdc.cmd` ou `cmdc.ps1` conforme o PATH local;
- `cmd` somente poderá ser usado se a resolução demonstrar que não é o
  `cmd.exe` nativo;
- o erro de resolução deverá informar os caminhos candidatos encontrados e
  recomendar `cmdc`;
- a skill não instalará o CLI nem alterará credenciais do usuário.

## Testes e validação

O artefato será validado em camadas:

1. **Estrutural:** frontmatter, nome `sdd-cmdc`, arquivos auxiliares, cópia
   dos scripts e ausência de alterações na skill original.
2. **Unitário do adaptador:** executável fake para verificar argumentos,
   modelo fixo, modo de edição, propagação de stdout/stderr, exit codes e
   códigos de bloqueio.
3. **Smoke local:** `cmdc --version`, `cmdc --list-models` e uma invocação
   mínima read-only com o modelo configurado, sem modificar arquivos do
   workspace.
4. **Pressão do processo:** cenários sem `cmdc`, modelo indisponível,
   autenticação ausente, timeout, relatório ausente e implementador que
   retorna `NEEDS_CONTEXT`; o orquestrador deverá registrar a causa e parar no
   ponto correto.
5. **Regressão do fluxo:** confirmar que reviewers continuam Codex, que uma
   tarefa não passa sem review, que cada fix wave gera re-review e que o
   breaker de cinco rodadas permanece intacto.

## Não objetivos

- substituir `subagent-driven-development` existente;
- trocar brainstorming, especificação ou plano do Codex;
- usar Command Code para reviewers;
- adicionar sharding paralelo ou um controlador Command Code intermediário;
- fazer fallback automático para Codex quando Command Code falhar;
- instalar, autenticar ou atualizar o Command Code automaticamente;
- alterar a topologia de junctions ou sincronização de outras skills.

## Critérios de aceitação

- `sdd-cmdc` pode ser selecionada explicitamente sem alterar o comportamento
  de `subagent-driven-development`;
- implementadores usam `cmdc` e o modelo exato
  `deepseek/deepseek-v4-flash`;
- reviewers e demais gates continuam Codex e preservam a ordem original;
- qualquer falha de infraestrutura produz `BLOCKED` com código, mensagem,
  exit code, stderr e ação recomendada;
- o ledger deixa claro por que a tarefa não avançou;
- testes estruturais, unitários, smoke e de pressão passam ou registram
  bloqueio reproduzível;
- a skill e seu artefato de auditoria ficam salvos no source canônico
  `.shared-ai-memory\skills` e não modificam skills não relacionadas.
