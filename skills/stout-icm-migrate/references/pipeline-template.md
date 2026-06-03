# Template: CONTEXT.md — Contrato de Pipeline ICM

Use este template para o CONTEXT.md raiz do projeto. Ele define a ordem dos estágios, as regras do pipeline e o handoff final.

```markdown
---
pipeline: <nome-do-projeto>
layer: 2
role: pipeline_contract
stages: [01_extrair, 02_auditar, 03_gerar, 04_validar, 05_exportar]
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
- **GATE no estágio <XX>:** Se `<output>.json` retornar `passed: false`, o pipeline BLOQUEIA. Não avance.
- **FORÇAR execução:** Se `FORCAR_VALIDACAO=true`, ignore o gate e prossiga mesmo com falhas, registrando alerta.
- **SEMPRE** consuma o output do estágio anterior como input do próximo.
- **SEMPRE** carregue as regras de identidade antes de iniciar (`./GEMINI.md`, `./CLAUDE.md` ou `..\..\GEMINI.md`).
- **NUNCA** envie output final se o gate estiver BLOQUEADO sem `FORCAR_VALIDACAO=true`.

## Handoff Final

Após o último estágio, o output está em `<caminho>`. Pronto para consumo.

## Notas de Migração

- Projeto migrado de `<entry_point>.py` (procedural) para pipeline ICM (`<N>` estágios)
- Scripts originais em `<src_dir>/` preservados
- Migrado em: `<YYYY-MM-DD>`
```

## Regras de Preenchimento

| Campo | Regra |
|-------|-------|
| `stages` | Lista no frontmatter YAML. Nomes sem número (o número é o diretório) |
| GATE | Sempre no estágio de auditoria/validação. Se o projeto tem múltiplos gates, liste todos |
| FORCAR_VALIDACAO | Padronize o nome da flag — use exatamente este nome em todos os pipelines |
| Notas de Migração | Obrigatório. Documenta de onde veio e o que mudou |

## Exemplo Real (Inova-Daily)

```markdown
---
pipeline: inova-daily
layer: 2
role: pipeline_contract
stages: [01_extrair, 02_auditar, 03_gerar, 04_validar, 05_exportar]
---

# CONTEXT.md — Pipeline: Inova Daily

Orquestrador de relatório executivo diário. Extrai dados do Fabric e motores Stout, 
audita integridade, gera email em markdown para o Roberto Reis.

## Ordem dos Estágios

| Ordem | Estágio | Propósito | Carregamento |
|-------|---------|-----------|--------------|
| 0 | `00_research/` | Glossário de domínio + pesquisas | Cold storage |
| 1 | `01_extrair/` | M2 + snapshot + recap + scanners | Sequencial |
| 2 | `02_auditar/` | Validar snapshot, recap, reconciliar fontes | Sequencial — **GATE** |
| 3 | `03_gerar/` | Preencher template → email markdown | Sequencial |
| 4 | `04_validar/` | Validar markdown: placeholders, zeros, seções vazias | Sequencial |
| 5 | `05_exportar/` | Audit NF + output final | Sequencial |

## Regras do Pipeline

- GATE no estágio 02: Se `audit.json` retornar `passed: false`, pipeline BLOQUEIA
- FORÇAR: Se `FORCAR_VALIDACAO=true`, ignore o gate e prossiga com alerta
- NUNCA envie email se o gate estiver BLOQUEADO sem FORCAR_VALIDACAO=true

## Notas de Migração

- Projeto migrado de `run_daily.py` (procedural) para pipeline ICM (5 estágios)
- Scripts originais em `src/` preservados
- Migrado em: 2026-05-28
```
