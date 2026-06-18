---
name: inova-daily-update
description: "Use quando precisar atualizar ou rodar os dados do pipeline executivo Inova Daily. Esta skill executa a verificação de recência e roda os scripts de atualização de faturamento diário. Triggers: atualizar daily, update-daily, atualizar dados da daily, daily-update, rodar daily."
version: 1.0.0
author: Victor
category: engineering
tier: 2
tools:
  - run_command
---

# inova-daily-update

## Objetivo
Garantir a atualização segura e resiliente dos dados do faturamento executivo diário da Inova, verificando a recência de dados analíticos upstream para evitar mojibake ou divergência de relatórios.

---

<!-- @if platform=claude -->

## Fluxo Detalhado de Operação

### Passo 1 — Validação de Recência
Antes de disparar a daily, execute o auditor de recência:
```bash
python skills/inova-daily-update/scripts/check_recency.py
```
- Se o script retornar código `2`, o pipeline está bloqueado devido a dados analíticos críticos desatualizados (🔴). Pare e notifique o usuário.
- Se retornar código `0`, mas houver fontes com aviso (🟡), notifique o usuário sobre potenciais inconsistências, mas o pipeline poderá prosseguir se desejado.

### Passo 2 — Execução do Pipeline
Dispare a execução do pipeline através do wrapper:
```bash
python skills/inova-daily-update/scripts/run_pipeline.py [--mes MÊS] [--skip-m2-check] [--force]
```
- Se for a primeira semana do mês, informe a flag `--mes <N>` para computar o recap mensal.
- Se houver alertas conhecidos de auditoria aceitáveis, utilize a flag `--force`.

### Passo 3 — Finalização e Rastreabilidade
A saída do script indicará a localização do Markdown executivo gerado (`data/outputs/DAILY_ROBERTO_YYYYMMDD_HHMM.md`) e os arquivos de auditoria de nota fiscal gerados em `data/audit_nf/`.

<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->

## Fluxo de Execução Rápido

1. **Checar Recência:** Execute o script `check_recency.py` para validar a tabela `recency_status.md`.
2. **Rodar Pipeline:** Dispare o wrapper `run_pipeline.py` com as flags necessárias (`--mes`, `--force`).
3. **Validar Outputs:** Verifique o e-mail em Markdown gerado em `data/outputs/` e o audit log.

<!-- @endif -->

---

## Constraints (Restrições)
- **Bloqueio Crítico:** Nunca force a execução se houver fontes com status 🔴 no validador de recência, a menos que autorizado pelo usuário.
- **Ambiente Local:** Utilize `BypassSandbox: true` no terminal Windows e execute comandos chamando o interpretador python adequado.
- **Encoding de Arquivos:** Sempre garanta que os arquivos gerados ou lidos utilizam `encoding='utf-8'` (Vacina contra Mojibake).

## Scripts disponíveis

- `skills/inova-daily-update/scripts/check_recency.py` — Validador de integridade e recência de fontes de dados no `recency_status.md`.
- `skills/inova-daily-update/scripts/run_pipeline.py` — Wrapper para execução estruturada e log do pipeline principal `run_daily.py`.
