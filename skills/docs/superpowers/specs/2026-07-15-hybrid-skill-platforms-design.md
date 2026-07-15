# Modernizacao do Pipeline de Skills Hibridas

## Objetivo

Atualizar o pipeline Stout de criacao, promocao e gerenciamento de skills para
suportar somente Codex, Claude Code e CommandCode. Remover Antigravity do
comportamento ativo sem perder os metadados internos usados por governanca,
auditoria e descoberta local.

## Criterios de Aceitacao

| ID | Criterio observavel |
| --- | --- |
| AC-1 | O pipeline ativo de criacao e gerenciamento lista somente Codex, Claude Code e CommandCode como plataformas suportadas. |
| AC-2 | A fabrica continua a gerar `blueprint.json` e `skill.config.json`, incluindo os `triggers` internos e gravando os arquivos em um diretorio de saida declarado. |
| AC-3 | O pacote de referencias inclui instrucoes atualizadas para Codex, Claude Code, CommandCode e autoria hibrida. |
| AC-4 | Uma validacao automatica falha para frontmatter incompativel, diretivas de preprocessamento ou referencias ativas ao Antigravity. |

## Requisitos Funcionais

| ID | Implementa | Requisito |
| --- | --- | --- |
| FR-001 | AC-1 | `blueprint_engine.py`, os templates, o agente redator e o manager devem declarar somente `codex`, `claude-code` e `commandcode`. |
| FR-002 | AC-2 | `blueprint_engine.py` deve receber `--output-dir`, criar o diretorio quando necessario e gravar nele os dois artefatos JSON. `triggers` deve permanecer nos JSONs e no registry, mas nao no frontmatter hibrido. |
| FR-003 | AC-3 | A fabrica deve disponibilizar `platform-codex.md`, `platform-claude.md`, `platform-commandcode.md` e `platform-hybrid.md`, e o agente redator deve consulta-las antes de gerar uma skill. |
| FR-004 | AC-1 | O manager deve remover as entradas de junction e as instrucoes operacionais do Antigravity, preservando as junctions de Claude Code e CommandCode. Ele nao deve criar ou substituir junction para o diretorio global do Codex. |
| FR-005 | AC-4 | Um validador deve retornar erro para campos de frontmatter fora de `name` e `description`, diretivas `@if platform`, targets fora das tres plataformas e referencias ativas ao Antigravity. |

## Requisitos Nao Funcionais

| ID | Valida | Requisito e justificativa |
| --- | --- | --- |
| NFR-001 | AC-2 | Os scripts devem executar offline, com Python e dependencias ja usadas pelo projeto, para manter a fabrica utilizavel no ambiente local. |
| NFR-002 | AC-4 | A validacao deve ser deterministica, produzir mensagens de erro acionaveis e encerrar com codigo diferente de zero em qualquer violacao. |

## Cenarios de Teste

| ID | FR | Cenario |
| --- | --- | --- |
| T-001 | FR-001, FR-002 | Executar `blueprint_engine.py` sem `--platforms` e verificar que ambos os JSONs listam exatamente `codex`, `claude-code` e `commandcode`. |
| T-002 | FR-002 | Executar `blueprint_engine.py --output-dir <diretorio-temporario>` e verificar que nenhum JSON foi escrito no diretorio de trabalho. |
| T-003 | FR-003 | Verificar que as quatro referencias existem e que o agente redator as lista como leitura obrigatoria. |
| T-004 | FR-004 | Carregar `junction_map.yaml` e verificar que ele nao possui uma entrada cujo `platform` ou `junction` contenha `antigravity`. |
| T-005 | FR-005 | Validar uma fixture hibrida correta e tres fixtures invalidas: frontmatter com `triggers`, diretiva `@if platform` e target `antigravity`. |

## Matriz de Rastreabilidade

| AC | FR | Testes | NFR |
| --- | --- | --- | --- |
| AC-1 | FR-001, FR-004 | T-001, T-004 | - |
| AC-2 | FR-002 | T-001, T-002 | NFR-001 |
| AC-3 | FR-003 | T-003 | - |
| AC-4 | FR-005 | T-005 | NFR-002 |

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
