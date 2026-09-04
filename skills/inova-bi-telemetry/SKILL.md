---
name: inova-bi-telemetry
description: Use when updating, rerunning, or reprocessing the jd-bi-acs-telemetry report via the standalone producer run.py, updating local parquet artifacts (snapshot and events), and publishing to Supabase with operational validation.
---

# Inova BI Telemetry

Use o produtor standalone como o único caminho de execução da telemetria John Deere ACS:
`C:\Projetos\Inova.maquinas\jd-bi-acs-telemetry`.

## Pré-requisitos e Credenciais

- `PBI_REPORT_URL` no processo, no `.env` ou uma URL explícita em `--report-url`; o argumento pode substituir a configuração do projeto.
- Perfil persistente externo e gerenciado definido por `PBI_USER_PROFILE_DIR`; nunca usar um perfil dentro do projeto, `state.json`, `storage_state` ou o checkout legado.
- Ambiente Python: `C:\Projetos\Inova\.venv\Scripts\python.exe` ou `uv run --no-project python`; nunca `python` sem ambiente.
- **Credenciais Supabase e Bootstrap Seguro:**
  - Base URLs no processo ou `.env`: `SUPABASE_PUBLISHER_DB_BASE_URL` e `SUPABASE_READER_DB_BASE_URL`.
  - Senhas no Windows Credential Manager sob os alvos `Inova-Supabase-Telemetry-Publisher` e `Inova-Supabase-Telemetry-Reader`.
  - O wrapper `scripts/bootstrap_jd_supabase.py` valida e injeta os DSNs completos (`SUPABASE_PUBLISHER_DB_URL` e `SUPABASE_READER_DB_URL`) exclusivamente na memória do processo filho, sem persistir segredos em disco.
- Configurações de geocoding e demais integrações disponíveis no processo ou no `.env`, quando exigidas pelo escopo. Não copie credenciais ou segredos para logs, Git ou documentação.

> [!NOTE]
> **Autenticação Supabase:** A publicação no Supabase conecta diretamente ao Transaction Pooler PostgreSQL via DSN. Não utiliza tokens temporários OAuth nem expira por inatividade de sessão de usuário.

Não procure Docker ou PostgreSQL local. Nenhum dos dois faz parte do refresh operacional.

## Fluxo Operacional

1. Entre no projeto standalone, configure `chcp 65001` e `PYTHONIOENCODING=utf-8`, e valide as fontes de configuração sem imprimir valores sensíveis. O bootstrap headed é feito uma vez com autorização; depois o Scheduler opera headless e unattended com o mesmo perfil.
2. **Execução local sem publicação (Offline/Local-only):**
   ```powershell
   C:\Projetos\Inova\.venv\Scripts\python.exe run.py --headless
   ```
3. **Execução com publicação Supabase (via Bootstrap Seguro):**
   ```powershell
   $python = 'C:\Projetos\Inova\.venv\Scripts\python.exe'
   $bootstrap = 'C:\Users\victor.bernardi\.agents\skills\inova-bi-telemetry\scripts\bootstrap_jd_supabase.py'
   & $python $bootstrap -- $python run.py --headless --publish-supabase --update-mode daily
   ```
   *(Para execuções intermediárias adicionais no mesmo dia, utilize `--update-mode intraday`).*
4. **Execução agendada (Scheduler):**
   Use somente `run_jd_bi_acs_telemetry_task.bat` do mesmo diretório. Não acrescente `run_recency_report.bat`.
5. **Validação dos Resultados:**
   - Inspecione o último resumo em `data/logs/jd_bi_acs_telemetry_runs.jsonl`. Exija `status=SUCCESS` e um `supabase_status` compatível com o modo escolhido.
   - Valide os 5 artefatos operacionais:
     - `data/output/jd_bi_acs_telemetry_snapshot_v1.parquet`
     - `data/output/jd_bi_acs_telemetry_events_v1.parquet`
     - `data/logs/jd_bi_acs_telemetry_anomalies.jsonl`
     - `data/logs/jd_bi_acs_telemetry_runs.jsonl`
     - `data/pending_mesoregiao.jsonl`

`shared\recency_status.md` é um sinal de saída para observabilidade e consumidores, não um pre-flight.

## Comportamento em Caso de Falha e Limites

- **Resiliência Local-First:** O pipeline local conclui e valida os arquivos Parquet locais antes de publicar no Supabase. Se houver falha de rede, banco ou DSN no Supabase, os Parquets locais permanecem 100% íntegros e preservados em `data/output/`.
- Use sempre `run.py` ponta a ponta; não rode estágios isolados nem o executor do monorepo.
- Pare em qualquer código diferente de zero do `run.py`.
- Não ignore erros, crie marcadores, copie Parquets/JSONL ou altere o Scheduler sem autorização operacional separada.
- Não aceite fallback para `data/browser_state/user_profile`; perfil ausente, vazio ou expirado bloqueia o Scheduler headless e unattended até novo bootstrap autorizado.
- Não declare publicação produtiva com `supabase_status=NOT_REQUESTED`.