---
name: inova-bi-telemetry
description: "Use quando precisar atualizar, rodar ou reprocessar o relatório jd-bi-acs-telemetry. Esta skill executa o pipeline completo via run.py com pré-flight operacional, validação de governança e conferência dos artefatos gerados. Triggers: atualizar telemetry, atualizar jd bi acs telemetry, rodar jd-bi-acs-telemetry, executar run.py telemetry."
version: 1.0.0
author: Victor
category: engineering
tier: 1
tools:
  - claude-code
  - commandcode
  - codex
triggers:
  - atualizar telemetry
  - atualizar jd bi acs telemetry
  - rodar jd-bi-acs-telemetry
  - executar run.py telemetry
---

# inova-bi-telemetry

## Objetivo

Atualizar de forma íntegra o relatório `jd-bi-acs-telemetry`, executando o pipeline completo pelo entry point `run.py` e validando os sinais operacionais já produzidos pelo projeto.

## Inputs esperados

- **URL do relatório Power BI**: argumento obrigatório `--report-url` exigido por `run.py`.
- **Segredos locais do projeto**: `.env` com as chaves necessárias para geocoding e demais integrações do pipeline.
- **Ambiente Python canônico**: `C:\Projetos\Inova\.venv` ou `uv run --no-project python`.
- **Contexto do projeto**: `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\CONTEXT.md`.

<!-- @if platform=claude -->
## Fluxo Detalhado

O projeto fica em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry`.

1. **Pre-flight**:
   - Configure o terminal Windows com `chcp 65001` e `PYTHONIOENCODING=utf-8`.
   - Use sempre `uv run --no-project python` ou `C:\Projetos\Inova\.venv\Scripts\python.exe`.
   - Verifique `C:\Projetos\Inova\shared\recency_status.md` antes da execução.
   - Confirme que `--report-url` está disponível.
   - Confirme que o `.env` do projeto existe e está legível.

2. **Execução do pipeline completo**:
   - Entre em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry`.
   - Execute:
     ```powershell
     uv run --no-project python run.py --report-url "<REPORT_URL>"
     ```
   - Use `--headless` apenas quando a execução realmente exigir navegador sem interface:
     ```powershell
     uv run --no-project python run.py --report-url "<REPORT_URL>" --headless
     ```
   - O `run.py` orquestra internamente `extract`, `transform`, `load` e `enrich`, além do preflight de governança.

3. **Validação pós-execução**:
   - Confirme o `status` retornado pela execução.
   - Verifique o log `C:\Projetos\Inova\docs\run_logs\jd_bi_acs_telemetry_runs.jsonl`.
   - Verifique o snapshot atual em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\data\output\jd_bi_acs_telemetry_snapshot_v1.parquet`.
   - Verifique o histórico canônico em `C:\Projetos\Inova\shared\data\jd_bi_acs_telemetry_events_v1.parquet`.
   - Verifique o log de anomalias em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\data\logs\jd_bi_acs_telemetry_anomalies.jsonl`.
<!-- @endif -->

<!-- @if platform=commandcode,codex -->
## Fluxo

1. Configure o terminal com `chcp 65001` e `PYTHONIOENCODING=utf-8`, e use `uv run --no-project python` ou `C:\Projetos\Inova\.venv\Scripts\python.exe`.
2. Em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry`, execute `run.py` com `--report-url` obrigatório; use `--headless` só quando necessário.
3. Valide `status`, `C:\Projetos\Inova\docs\run_logs\jd_bi_acs_telemetry_runs.jsonl`, o snapshot em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\data\output\`, o histórico em `C:\Projetos\Inova\shared\data\` e o anomaly log em `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\data\logs\`.
<!-- @endif -->

## Constraints

- NUNCA rode estágios isolados se a tarefa for atualizar o relatório ponta a ponta; use sempre `run.py`.
- NUNCA use `python` nu; use `uv run --no-project python` ou o executável explícito do venv canônico.
- SEMPRE configure `PYTHONIOENCODING=utf-8` e `chcp 65001` no terminal Windows antes da execução.
- SEMPRE verifique `shared/recency_status.md` antes de rodar.
- NUNCA invente `post-flight`; a validação final deve usar apenas os logs e artefatos já produzidos pelo projeto.
- Se o pipeline falhar, PARE e reporte a etapa que falhou com base na mensagem do `run.py` e no `run summary`.

## Scripts

- `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\run.py` - entry point do pipeline.
- `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\extract.py` - extração do relatório Power BI.
- `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\transform.py` - tipagem, normalização e deduplicação.
- `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\load.py` - snapshot, histórico e anomaly log.
- `C:\Projetos\Inova\projects\jd-bi-acs-telemetry\enrich.py` - enriquecimento geográfico.

## Critérios de Conclusão

A skill é concluída quando o `run.py` termina sem erro e os artefatos esperados ficam observáveis no `run summary`, no snapshot atual, no histórico canônico e no log de anomalias.

