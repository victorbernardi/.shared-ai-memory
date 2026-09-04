---
name: inova-wirtgen-coordinates-refresh
description: Use when refreshing the Wirtgen coordinates report from Machine Analyzer through run.py, updating local parquet artifacts (snapshot and history), and publishing the validated dataset to Wirtgen Supabase with daily or intraday mode.
---

# Inova Wirtgen Coordinates Refresh

Produtor operacional de coordenadas Wirtgen para atualização local e publicação no Supabase.
O único ponto de entrada operacional do projeto é `run.py` em `C:\Projetos\Inova.maquinas\Wirtgen-OPC-Telemetry`.

## Pré-requisitos e Credenciais

- **Ambiente Python:** `C:\Projetos\Inova\.venv\Scripts\python.exe` (ou `uv run --no-project python`).
- **Credenciais Machine Analyzer (John Deere SSO):**
  - Variáveis de ambiente `WIRTGEN_DEERE_USER` e `WIRTGEN_DEERE_PASSWORD`, ou gerenciadas no Windows Credential Manager sob o alvo `Inova-Wirtgen-Machine-Analyzer`.
  - Extração live requer navegador Chromium (Playwright). Se o SSO solicitar 2FA (SMS), o operador deve digitar o código diretamente na janela do navegador (timeout de 2 minutos).
- **Credenciais e URLs Supabase:**
  - Base URLs no ambiente: `SUPABASE_WIRTGEN_TELEMETRY_PUBLISHER_DB_BASE_URL` e `SUPABASE_WIRTGEN_TELEMETRY_READER_DB_BASE_URL`.
  - Senhas de banco no Windows Credential Manager: `Inova-Supabase-Wirtgen-Telemetry-Publisher` e `Inova-Supabase-Wirtgen-Telemetry-Reader`.
  - O script `scripts/bootstrap_wirtgen_supabase.py` valida e injeta os DSNs completos (`SUPABASE_WIRTGEN_TELEMETRY_PUBLISHER_DB_URL` e `SUPABASE_WIRTGEN_TELEMETRY_READER_DB_URL`) no processo filho sem persistir nem vazar segredos.
  - O pacote `inova-supabase` deve estar previamente instalado no ambiente Python.

> [!NOTE]
> **Autenticação Supabase:** A integração Wirtgen com Supabase **não usa tokens OAuth temporários nem JWT de usuário**. Ela utiliza conexões diretas ao Transaction Pooler PostgreSQL via DSN autenticado. Portanto, as credenciais do banco não expiram por inatividade/OAuth.

## Agendamento Automático (Task Scheduler)

Para automação e execução agendada diária:
- **Tarefa do Windows:** `\Inova_Update_Wirtgen_Telemetry`
- **Horário:** Diariamente às **08:45**
- **Script do Scheduler:** [`run_wirtgen_telemetry_task.bat`](file:///C:/Projetos/Inova.maquinas/Wirtgen-OPC-Telemetry/run_wirtgen_telemetry_task.bat) localizado na raiz do projeto.

## Fluxo Operacional

1. **Navegue até o diretório do projeto e prepare o runtime:**
   ```powershell
   Set-Location 'C:\Projetos\Inova.maquinas\Wirtgen-OPC-Telemetry'
   $python = 'C:\Projetos\Inova\.venv\Scripts\python.exe'
   $skillScript = 'C:\Users\victor.bernardi\.agents\skills\inova-wirtgen-coordinates-refresh\scripts\bootstrap_wirtgen_supabase.py'
   ```

2. **Execução completa diária (Local + Supabase):**
   ```powershell
   & $python $skillScript -- $python run.py --publish-supabase --update-mode daily
   ```
   *(Para execuções intermediárias adicionais no mesmo dia, utilize `--update-mode intraday`).*

3. **Execução via Batch do Agendador:**
   ```powershell
   .\run_wirtgen_telemetry_task.bat
   ```

4. **Etapas executadas sequencialmente pelo `run.py`:**
   - **`extract.py`**: Login no Machine Analyzer, seleção do filtro `Wirtgen - Coordenadas`, download e manifesto.
   - **`transform.py`**: Normalização de tipos/colunas, enriquecimento geográfico (`enrich.py` / IBGE / OpenCage / aliases) e classificação material do histórico (`classify_history`).
   - **`load.py`**: Gravação com compressão Snappy, reabertura e validação estrita de schema dos dois Parquets:
     - `output/wirtgen_opc_telemetry_snapshot_v1.parquet` (exatamente 14 colunas)
     - `output/wirtgen_opc_telemetry_history_v1.parquet` (exatamente 18 colunas)
   - **`retain_downloads()`**: Retenção dos 5 downloads timestampados mais recentes em `input/`.
   - **`supabase_publish.py`**: Publicação transacional remota via `inova_supabase.wirtgen_telemetry` nas tabelas dedicadas:
     - `public.wirtgen_telemetry_machine_current`
     - `public.wirtgen_telemetry_event_history`
     - `public.wirtgen_telemetry_ingestion_run`
     - `public.wirtgen_telemetry_machine_attributes`
     - `public.wirtgen_telemetry_event_attributes`
   - **Recência (observador pós-ETL)**: Se `INOVA_RECENCY_REPORT_SCRIPT` estiver configurado, atualiza o status compartilhado de recência.

5. **Validação dos Resultados:**
   - Confirme saída com `status=success` e `supabase_status=SUCCESS`.
   - Inspecione as contagens publicadas (`supabase_snapshot_row_count`, `supabase_event_published_count`).
   - Verifique que os dois arquivos Parquet locais foram atualizados e reabertos com sucesso.

## Comportamento em Caso de Falha

- **Falha no Supabase (Rede / Credenciais / DSN / Banco):**
  - O pipeline grava e valida os Parquets locais **antes** de tentar publicar no Supabase.
  - Se a publicação falhar, `run.py` reporta `status=failed stage=supabase supabase_status=FAILED` e encerra com código `1`.
  - **Os artefatos locais permanecem 100% íntegros e preservados em `output/`**.
- **Sessão Expirada no Machine Analyzer (Deere SSO):**
  - Se a sessão exigir novo login ou 2FA SMS, a janela do navegador aguarda a entrada do código SMS pelo operador (até 120s).
  - Em caso de timeout de 2FA ou erro de autenticação, o processo encerra no estágio `extract`, preservando os dados anteriores.
- **Nenhum Fallback Silencioso:**
  - O modo live nunca recorre silenciosamente ao fixture.
  - Não invente coordenadas, cidades ou horímetros ausentes.