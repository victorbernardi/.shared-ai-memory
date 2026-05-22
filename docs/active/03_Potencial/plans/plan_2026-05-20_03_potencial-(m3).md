# Implementation Plan - Governança de Recência (M3 & M2 Centralizado)

Este plano descreve as modificações técnicas para centralizar o utilitário de governança e recência de dados no repositório **Inova** e habilitar os sensores pre-flight e post-flight no motor **M3 (Potencial Clientes)**.

## User Review Required

> [!IMPORTANT]
> **Modificações Compartilhadas:** A migração moverá o arquivo `governance_sensor.py` para a pasta comum `/shared`. Isso exige ajustes em dois motores ao mesmo tempo (**M2** e **M3**) para evitar quebras de importação.
> 
> O plano assume a **Opção A** (tolerante a falhas) para o sensor pre-flight e post-flight do M3, mantendo a consistência com o modelo estabelecido.

---

## Proposed Changes

Grouped by component layer.

### 📁 Component: Shared Infrastructure (`/shared`)

#### [NEW] [governance_sensor.py](file:///C:/Projetos/Inova/shared/governance_sensor.py)
*   Criar o arquivo centralizado baseado no script original localizado em `02_Faturamento`. Ele proverá as funções `check_utf8_hygiene()`, `check_fabric_connector()` e `parse_recency_report()`.

#### [MODIFY] [generate_recency_report.py](file:///C:/Projetos/Inova/shared/generate_recency_report.py)
*   Substituir a entrada da chave `"Vendas M3 RFM"` (antiga e obsoleta) pelas duas saídas críticas do M3:
    *   `"M3 (Potencial Clientes)"` -> `shared_data / "dataset_ouro_potencial_v1.parquet"`
    *   `"M3 (Potencial por Chassi)"` -> `shared_data / "dataset_ouro_potencial_chassi_v1.parquet"`

---

### 📁 Component: Motor M2 (`02_Faturamento`)

#### [DELETE] [governance_sensor.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/src/tools/governance_sensor.py)
*   Remover a versão local duplicada para consolidar a Golden Copy global em `/shared`.

#### [MODIFY] [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/run.py)
*   Ajustar a linha de importação do pre-flight check para consumir da biblioteca compartilhada:
    ```python
    # De:
    from src.tools.governance_sensor import run_preflight
    # Para:
    from governance_sensor import run_preflight
    ```

---

### 📁 Component: Motor M3 (`03_Potencial`)

#### [MODIFY] [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/03_Potencial/run.py)
*   Integrar a execução do **Pre-flight Check** na decolagem do motor:
    ```python
    # Bloco inicial de main()
    try:
        from governance_sensor import run_preflight
        run_preflight(str(_shared_dir), fail_fast=False)
    except Exception as exc:
        log.warning("Falha ao executar o Pre-flight check: %s", exc)
    ```
*   Integrar a execução do **Post-flight Check** (atualização do relatório de recência) ao finalizar o processamento com sucesso:
    ```python
    # Bloco final de main() após o save()
    log.info("[INICIO] Post-flight: Atualizando Relatorio de Recencia")
    import subprocess
    report_script = _shared_dir / "generate_recency_report.py"
    subprocess.run([sys.executable, str(report_script)], check=False)
    log.info("[OK]    Post-flight: Relatorio de Recencia")
    ```

---

## Verification Plan

### Automated Tests
*   **Integração do M3:** Executar localmente o runner `C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial\run.py` e garantir saída `exit code 0`.
*   **Regeneração do Status:** Validar se o `/shared/recency_status.md` foi reescrito, contém as novas linhas para M3 e está com bolinha verde `🟢`.
*   **Integração do M2:** Executar o runner `C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\run.py` para validar a importação centralizada.
*   **Script de Validação:** Executar `python validate_pipeline.py --skip-run` para atestar a conformidade e os schemas dos dados de ouro gerados.
