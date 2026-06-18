---
name: inova-pipeline-01
description: "Use quando precisar atualizar, rodar ou orquestrar o pipeline potencial-clientes da Inova. Esta skill executa a sequência de motores M0 a M5 e valida a integridade dos dados e outputs gerados. Triggers: atualizar pipeline, rodar pipeline comercial, potencial-clientes, inova-pipeline-01."
---

# inova-pipeline-01

## Objetivo
Atualizar e orquestrar de forma íntegra o pipeline potencial-clientes da Inova (motores M0 a M5).

<!-- @if platform=claude -->
## Fluxo Detalhado

Este fluxo deve ser executado para rodar a sequência completa de motores.

1. **Pre-flight checks**:
   - Execute o sensor de governança: `python shared/governance_sensor.py --shared shared`
   - Verifique a recência dos dados em `shared/recency_status.md`

2. **Execução do Pipeline**:
   - Execute o script principal do pipeline: `python pipelines/potencial-clientes/ligar_motores.py`
   - Ou rode cada motor individualmente na ordem definida em `CONTEXT.md` se precisar debugar.

3. **Validação**:
   - Execute o script de validação: `python pipelines/potencial-clientes/validate_pipeline.py`
   - Confirme se os parquets de handoff foram criados no diretório `shared/data/` e se a planilha final foi gerada em `05_Segmentacao/data/`.

## Referências
- [CONTEXT.md](file:///C:/Projetos/Inova/pipelines/potencial-clientes/CONTEXT.md)
<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->
## Fluxo

1. Execute a verificação de governança e recência de dados rodando `python shared/governance_sensor.py --shared shared`.
2. Execute o pipeline completo rodando o script `python pipelines/potencial-clientes/ligar_motores.py`.
3. Valide o pipeline rodando `python pipelines/potencial-clientes/validate_pipeline.py` e inspecionando os relatórios de validação gerados.
<!-- @endif -->

## Constraints

- NUNCA execute o pipeline se a verificação de governança falhar ou se houver dados obsoletos sem justificar.
- SEMPRE utilize `shared/config_inova_identity.py` para normalização.
- NUNCA pule estágios na execução sequencial (00 a 05).
- SEMPRE verifique se todos os testes passam ao final.

## Scripts

- `pipelines/potencial-clientes/ligar_motores.py` — Executa a sequência de motores M0 a M5
- `pipelines/potencial-clientes/validate_pipeline.py` — Valida a integridade física dos parquets e saídas

## Critérios de Conclusão

A skill é considerada concluída quando todos os estágios do pipeline potencial-clientes rodam sequencialmente sem falhas de integridade nos dados finais.
