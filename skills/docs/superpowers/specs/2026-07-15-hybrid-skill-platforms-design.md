# Plataforma de Skills Multi-Formato

## Objetivo

Modernizar a fabrica Stout para manter uma fonte versionada de cada skill e
gerar, validar e instalar tres pacotes independentes: Codex, Claude Code e
CommandCode. Antigravity e junctions sao legado e nao participam do pipeline
ativo.

## Criterios de Aceitacao

| ID | Criterio observavel |
| --- | --- |
| AC-1 | Uma skill criada com os tres `platforms` gera tres pacotes validos e os instala diretamente nos diretorios globais documentados de Codex, Claude Code e CommandCode. |
| AC-2 | A skill possui uma fonte canonica versionada, um fluxo comum portatil e extensoes por plataforma declaradas, nunca tres copias editadas manualmente. |
| AC-3 | Uma extensao opcional e gerada somente nos destinos que a suportam; uma extensao obrigatoria sem suporte bloqueia a operacao antes de qualquer instalacao. |
| AC-4 | A fabrica continua a produzir `blueprint.json` e `skill.config.json`, com `triggers` internos, em um diretorio de saida explicitamente informado. |
| AC-5 | O pipeline nao usa junctions nem contem referencias operacionais ao Antigravity. |
| AC-6 | A validacao e a instalacao produzem diagnosticos acionaveis, relatorio de compatibilidade e rollback quando uma promocao nao puder concluir. |

## Diretorios Globais de Destino

| Plataforma | ID interno | Diretorio global |
| --- | --- | --- |
| Codex | `codex` | `~/.agents/skills/<nome>/` |
| Claude Code | `claude-code` | `~/.claude/skills/<nome>/` |
| CommandCode | `commandcode` | `~/.commandcode/skills/<nome>/` |

Os destinos acima sao copias instaladas. A fonte de verdade permanece em
`~/.shared-ai-memory/skills/<nome>/` e nunca e acessada por junction.

## Requisitos Funcionais

| ID | Implementa | Requisito |
| --- | --- | --- |
| FR-001 | AC-1, AC-5 | `blueprint_engine.py`, os templates, os agentes e o manager devem reconhecer somente `codex`, `claude-code` e `commandcode`. A configuracao de distribuicao deve declarar os tres diretorios globais e nao deve conter nem invocar `junction_map.yaml` ou `junction_guard.py`. |
| FR-002 | AC-4 | `blueprint_engine.py` e `create_pipeline.py` devem exigir `--output-dir`, criar o diretorio e gravar nele `blueprint.json`, `skill.config.json` e os relatorios gerados. `triggers` permanecem nos JSONs e no registry, nunca no frontmatter salvo se uma extensao de plataforma registrada o permitir. |
| FR-003 | AC-2 | Cada fonte de skill deve conter `SKILL.md` portatil, `skill.platforms.yaml` e, quando necessario, `platform-overrides/<platform>/`. O manifesto deve declarar `targets`; na ausencia de escolha explicita, a fabrica deve usar os tres IDs suportados. |
| FR-004 | AC-1, AC-2 | Um renderizador deve criar um pacote por target, copiar `scripts/`, `references/`, `assets/` e templates compartilhados, e aplicar somente os overrides e metadados autorizados para aquele target. Os pacotes renderizados devem ser independentes da fonte canonica em tempo de uso. |
| FR-005 | AC-3, AC-6 | Um catalogo versionado de capacidades deve mapear cada extensao para plataformas, esquema de entrada, arquivos gerados e fonte oficial. A pre-validacao deve classificar cada extensao como `included`, `skipped` ou `error`; extensao desconhecida, invalida ou obrigatoria sem suporte deve retornar erro antes da renderizacao ou instalacao. |
| FR-006 | AC-1, AC-6 | O manager deve promover pacotes ja validados diretamente para os destinos selecionados; o padrao sao os tres. Colisao de nome deve falhar sem escrita, salvo `--replace` apos exibir o diff. A promocao deve fazer preflight de todos os destinos, criar backups, restaurar destinos ja alterados se qualquer copia falhar e registrar hashes e status junto a fonte canonica. |
| FR-007 | AC-2, AC-3 | As referencias de autoria devem documentar o contrato comum e as diferencas oficiais de Codex, Claude Code e CommandCode. O agente redator deve le-las antes de criar ou alterar uma skill e deve declarar extensoes no manifesto, nao no corpo comum. |
| FR-008 | AC-5 | Um validador deve detectar referencias operacionais a Antigravity, caminhos `.gemini/antigravity*`, diretivas de preprocessamento e suporte a junctions. A varredura deve examinar apenas fontes operacionais do pipeline e ignorar `_archived`, testes, fixtures e o proprio detector. |

## Requisitos Nao Funcionais

| ID | Valida | Requisito e justificativa |
| --- | --- | --- |
| NFR-001 | AC-4, AC-6 | Renderizacao, validacao e promocao devem executar offline com Python e dependencias ja usadas pelo projeto. O catalogo de capacidades e as referencias oficiais sao versionados localmente. |
| NFR-002 | AC-3, AC-5 | Todas as validacoes devem ser deterministicas, emitir uma mensagem por violacao e encerrar com codigo diferente de zero em erro. |
| NFR-003 | AC-1, AC-6 | Nenhum destino global pode ficar parcialmente atualizado apos falha de promocao; backups temporarios devem ser removidos somente depois da conclusao bem-sucedida. |
| NFR-004 | AC-2, AC-3 | O corpo comum deve funcionar sem recurso exclusivo de runtime; extensoes so podem acrescentar comportamento documentado e declarado no manifesto. |

## Cenarios de Teste

| ID | FR | Cenario |
| --- | --- | --- |
| T-001 | FR-001, FR-002 | Executar o gerador com `--output-dir` temporario e verificar que `blueprint.json` e `skill.config.json` listam exatamente `codex`, `claude-code` e `commandcode`, sem escrever no diretorio atual. |
| T-002 | FR-003 | Criar uma fonte sem targets explicitos e verificar que a fabrica cria `SKILL.md` portatil e `skill.platforms.yaml` com os tres targets e nenhuma extensao. |
| T-003 | FR-004 | Renderizar uma skill com arquivos compartilhados e verificar tres pacotes independentes, cada qual com `SKILL.md` e somente seus overrides permitidos. |
| T-004 | FR-005 | Declarar uma extensao opcional exclusiva de uma plataforma e verificar `included` no destino compativel, `skipped` nos demais e relatorio JSON e Markdown. |
| T-005 | FR-005, NFR-002 | Declarar extensao desconhecida, invalida e obrigatoria sem suporte; verificar nenhuma instalacao, uma mensagem acionavel por violacao e codigo de saida nao zero. |
| T-006 | FR-006, NFR-003 | Promover para tres diretorios temporarios, testar colisao sem `--replace`, substituicao aprovada com diff e falha simulada no segundo destino com restauracao do primeiro. |
| T-007 | FR-007 | Verificar a existencia das tres referencias de plataforma e do contrato comum; verificar que todos os agentes redatores as listam como leitura obrigatoria. |
| T-008 | FR-008 | Verificar que fontes operacionais com Antigravity, preprocessamento ou junction falham, enquanto uma fixture, `_archived` e o proprio arquivo do detector nao geram falso positivo. |
| T-009 | FR-001, FR-006 | Carregar a configuracao de destinos e verificar os tres diretorios globais, ausencia de `junction`/`.gemini` e ausencia de chamada a `junction_guard.py`. |

## Matriz de Rastreabilidade

| AC | FR | Testes | NFR |
| --- | --- | --- | --- |
| AC-1 | FR-001, FR-004, FR-006 | T-001, T-003, T-006, T-009 | NFR-003 |
| AC-2 | FR-003, FR-004, FR-007 | T-002, T-003, T-007 | NFR-004 |
| AC-3 | FR-005, FR-007 | T-004, T-005, T-007 | NFR-002, NFR-004 |
| AC-4 | FR-002 | T-001 | NFR-001 |
| AC-5 | FR-001, FR-008 | T-001, T-008, T-009 | NFR-002 |
| AC-6 | FR-005, FR-006 | T-004, T-005, T-006 | NFR-001, NFR-002, NFR-003 |

## Contrato de Fonte e Formatos Renderizados

`SKILL.md` e o fluxo comum sao a fonte portatil. Seu frontmatter contem, por
padrao, somente `name` e `description`; o nome deve coincidir com o diretorio
da skill. O corpo nao pode depender de ferramentas, substituicoes ou
preprocessamento exclusivos de runtime.

`skill.platforms.yaml` e a declaracao versionada de targets e extensoes. Uma
extensao deve informar seu ID de catalogo, valor e se e obrigatoria. Extensoes
ficam ausentes por padrao. O renderizador pode acrescentar frontmatter,
arquivos ou instrucoes especificas apenas quando a extensao correspondente for
registrada e compativel.

Cada pacote final contem uma versao propria de `SKILL.md`. Uma extensao
opcional ausente em um target nao impede que esse target receba a skill-base;
uma extensao obrigatoria nao suportada bloqueia toda a operacao.

## Referencias de Plataforma

As regras de capacidade devem manter uma referencia local e o URL oficial que
as fundamenta:

- Codex: `name` e `description` em `SKILL.md`; metadados de interface
  especificos ficam em `agents/openai.yaml` quando declarados.
  Fonte: https://learn.chatgpt.com/docs/build-skills.md
- Claude Code: `~/.claude/skills`, frontmatter e recursos opcionais como
  `allowed-tools`, argumentos e contexto dinamico so quando declarados.
  Fonte: https://code.claude.com/docs/en/skills
- CommandCode: `~/.commandcode/skills`, `name` e `description` obrigatorios;
  demais campos de frontmatter somente por extensao registrada.
  Fonte: https://commandcode.ai/docs/skills

## Alteracoes do Pipeline

- `skills/stout-create-skill`: cria a fonte canonica, o manifesto, o catalogo
  de capacidades, os renderizadores e os relatorios no `--output-dir`.
- `skills/stout-skill-manager`: deixa de criar, verificar ou restaurar
  junctions; promove artefatos renderizados para os tres diretorios globais
  com preflight, `--replace`, backup e rollback.
- `skills/stout-promote-skill`: promove somente pacotes que tenham passado na
  validacao de plataforma e registra o estado de instalacao junto a fonte.
- `skills/stout-create-skill/references`: substitui referencias Antigravity por
  referencias Codex e pelo contrato de autoria multi-formato.

## Validacao

Antes de instalar, o pipeline deve confirmar que:

1. a fonte e o manifesto sao validos e todos os targets pertencem ao conjunto
   permitido;
2. cada pacote renderizado satisfaz o contrato do respectivo runtime;
3. o relatorio de compatibilidade enumera todas as extensoes e seus status;
4. nenhum erro de extensao obrigatoria, formato ou legado ativo existe;
5. todos os destinos podem receber a atualizacao antes da primeira escrita;
6. a instalacao concluida possui hashes iguais aos artefatos aprovados.

## Fora de Escopo

- Alterar conteudo em `_archived` ou fixtures somente porque mencionam
  Antigravity.
- Inventar uma extensao sem documentacao oficial e sem entrada no catalogo.
- Tornar uma extensao exclusiva obrigatoria em plataformas que nao a suportam.
- Usar junctions, links simbolicos ou caminhos compartilhados como mecanismo
  de distribuicao.
