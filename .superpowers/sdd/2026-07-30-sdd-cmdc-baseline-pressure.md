# Baseline de pressão — sdd-cmdc — 2026-07-30

## Resultado

O baseline externo foi executado em um workspace temporário sem arquivos da
skill copiados para ele, usando o CLI local `cmdc.ps1`, modelo
`deepseek/deepseek-v4-flash` e limite de três turnos. O processo terminou com
sucesso e respondeu aos quatro cenários.

Essa execução não é evidência válida de comportamento sem a skill: a resposta
do agente citou explicitamente o contrato de `sdd-cmdc` e referências de linhas
desse fluxo. Isso indica carregamento/contaminação por skills globais do
ambiente Command Code, apesar do workspace temporário estar isolado.

## Observações úteis, sem promoção a evidência de baseline

- CLI ausente: respondeu `BLOCK`, com preservação do fail-closed.
- Modelo indisponível: respondeu `BLOCK`, sem fallback de modelo.
- Relatório ausente: respondeu `BLOCK`, sem aceitar sucesso aparente.
- `NEEDS_CONTEXT`: pediu contexto adicional antes de revisão.

## Decisão

O resultado é marcado como `BASELINE_INVALID_GLOBAL_SKILL_CONTAMINATION`, não
como aprovação do baseline. Os contratos verificáveis permanecem cobertos pelos
testes locais do adaptador, pelos cenários em `skills/sdd-cmdc/tests/pressure/`
e pelo bloqueio fail-closed implementado no adaptador.
