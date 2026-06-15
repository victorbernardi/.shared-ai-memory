---
pipeline: <nome-do-projeto>
layer: 2
role: pipeline_contract
stages: [<estagio1>, <estagio2>, ...]
---

# CONTEXT.md — Pipeline: <Nome>

<Breve descrição do que este pipeline faz — uma ou duas frases.>

## Ordem dos Estágios

| Ordem | Estágio | Propósito | Carregamento |
|-------|---------|-----------|--------------|
| 0 | `00_research/` | <propósito> | Cold storage — sob demanda |
| 1 | `01_<estagio>/` | <propósito> | Sequencial |
| 2 | `02_<estagio>/` | <propósito> | Sequencial — **GATE** |
| 3 | `03_<estagio>/` | <propósito> | Sequencial |
| 4 | `04_<estagio>/` | <propósito> | Sequencial |
| 5 | `05_<estagio>/` | <propósito> | Sequencial |

## Regras do Pipeline

- **NUNCA** pule estágios. A ordem numérica é absoluta.
- **NUNCA** avance para o próximo estágio sem que o atual atinja todos os critérios de conclusão.
- **SEMPRE** consuma o output do estágio anterior como input do próximo.
- **GATE no estágio <XX>:** Se `<output>.json` retornar `passed: false`, o pipeline BLOQUEIA. Não avance.
- **FORÇAR execução:** Se `FORCAR_VALIDACAO=true`, ignore o gate e prossiga mesmo com falhas, registrando alerta.
- **NUNCA** envie output final se o gate estiver BLOQUEADO sem `FORCAR_VALIDACAO=true`.
- **SEMPRE** carregue `./CLAUDE.md` (identidade do workspace) e `./CONTEXT.md` (este arquivo) antes de executar.

## Handoff Final

Após o último estágio, os artefatos estão em `<caminho>`. Pronto para consumo/arquivamento.

## Notas de Migração

- Projeto migrado de `<entry_point>.py` (procedural) para pipeline ICM (`<N>` estágios)
- Scripts originais em `<src_dir>/` preservados
- Migrado em: `<YYYY-MM-DD>`
