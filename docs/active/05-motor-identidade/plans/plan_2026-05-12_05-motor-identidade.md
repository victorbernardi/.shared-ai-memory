# QSA Scan Watchdog Implementation Plan

This plan establishes a robust monitoring and auto-restart mechanism for the QSA (Quadro de Sócios e Administradores) crawler to ensure it completes the data collection for corporate groups (~19k roots) which is currently at 11.9%.

## User Review Required

> [!IMPORTANT]
> The watchdog will use a background process. We need to ensure that previous manual attempts to run the crawler are stopped to avoid API rate limiting conflicts.

## Proposed Changes

### Motor Identidade (00_Motor_Identidade)

#### [NEW] [seo_ge_qsa_watchdog.py](file:///c:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/seo_ge_qsa_watchdog.py)
Create a Python script that:
- Periodically checks if the crawler is running.
- Restarts it if it exits prematurely.
- Logs events and progress.
- Detects the "FINISH" state to stop itself.

#### [MODIFY] [GEMINI.md](file:///c:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/GEMINI.md)
Update the "Estado Atual" and "Tarefas Pendentes" to document the implementation of the watchdog and the current progress (11.9%).

## Verification Plan

### Automated Tests
- Run the watchdog script and verify it spawns a crawler process.
- Verify that `crawler_log.txt` is being updated.

### Manual Verification
- Monitor the log for at least 5 minutes to ensure no immediate crashes occur.
- Verify the root count in `qsa_base.json` increases over time.
