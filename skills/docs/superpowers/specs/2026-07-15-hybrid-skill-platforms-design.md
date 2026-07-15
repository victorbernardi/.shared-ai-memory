# Modernizacao do Pipeline de Skills Hibridas

## Objetivo

Atualizar o pipeline Stout de criacao, promocao e gerenciamento de skills para
suportar somente Codex, Claude Code e CommandCode. Remover Antigravity do
comportamento ativo sem perder os metadados internos usados por governanca,
auditoria e descoberta local.

## Contrato Hibrido

Cada skill gerada tera uma unica fonte portatil: `SKILL.md`.

- O frontmatter compartilhado tera somente `name` e `description`.
- `description` contera a acao, o contexto de uso e frases de acionamento
  representativas em PT-BR e, quando util, ingles.
- O corpo contera apenas instrucoes executaveis nos tres runtimes.
- Nao usar diretivas `@if`, pois dependem de preprocessamento nao garantido
  pelos runtimes de destino.
- Diferencas de runtime serao documentadas em referencias, nunca exigidas para
  executar o fluxo comum.

## Metadados Internos

`blueprint.json`, `skill.config.json` e a entrada correspondente no
`registry.json` permanecem parte do pipeline.

- `blueprint.json` continua sendo o contrato entre o orquestrador e o
  scaffolder, incluindo `target_platforms` e `triggers` de governanca.
- `skill.config.json` continua descrevendo as plataformas alvo e secoes do
  artefato; ele deixa de conter Antigravity.
- `registry.json` continua armazenando `triggers` para busca local e auditoria
  de sobreposicao.
- Nenhum runtime deve depender do campo `triggers` no frontmatter de
  `SKILL.md`.

## Referencias de Plataforma

Criar `references/platform-codex.md` usando a documentacao oficial do Codex:

- `name` e `description` sao os metadados de ativacao.
- Manter `SKILL.md` conciso e mover detalhes para `references/`.
- Usar `scripts/` somente para operacoes deterministicas e `assets/` somente
  para arquivos que integram a saida.

Atualizar `platform-claude.md` e `platform-commandcode.md` para separar
capacidades opcionais do contrato compartilhado. Criar
`references/platform-hybrid.md` para centralizar as regras de autoria comuns.

## Alteracoes do Pipeline

- `stout-create-skill`: remover Antigravity de defaults, exemplos, templates,
  referencias e instrucoes de agentes; incluir Codex como plataforma alvo.
- `stout-skill-manager`: remover junctions Antigravity e instrucoes de runtime
  obsoletas; manter Codex, Claude Code e CommandCode.
- `stout-promote-skill`: confirmar que nao assume runtime especifico; atualizar
  apenas se houver referencia encontrada no escopo ativo.
- O gerador de blueprint recebera um diretorio de saida explicito para nao
  gravar os artefatos no diretorio atual do processo.

## Validacao

Adicionar uma validacao deterministica que confirme:

1. `SKILL.md` usa somente `name` e `description` no frontmatter compartilhado.
2. A descricao contem contexto de acionamento.
3. Nao ha referencias ativas a Antigravity, caminhos `.gemini/antigravity-*` ou
   diretivas `@if platform` no pipeline atualizado.
4. `blueprint.json` e `skill.config.json` gerados contem exatamente Codex,
   Claude Code e CommandCode.
5. As referencias de plataforma citadas pelo agente redator existem.

## Fora de Escopo

Nao alterar conteudo em `_archived` nem skills independentes que citam
Antigravity, salvo se forem chamadas diretamente por este pipeline.
