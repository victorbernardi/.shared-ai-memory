# Plano: Governança de Recência — M4 (Estratégia)

> **Versão:** v1.0  
> **Data:** 2026-05-20  
> **Status:** Aprovado  
> **Escopo:** `04_Estrategia/run.py` e `shared/generate_recency_report.py`  
> **Referência:** `spec_v1_governanca_recencia_m3.md` (padrão replicado)

---

## 1. Contexto

M4 é o produtor do parquet soberano (`dataset_final_estrategico_v1.parquet`), consumido por todos os `projects/` e pelo stage 05. O padrão de governança de recência (pre-flight + post-flight) foi definido e aprovado na spec do M3. Este plano aplica o mesmo padrão ao M4 sem desvios de design.

`governance_sensor.py` já existe em `shared/` — sem pré-requisitos bloqueantes.

---

## 2. Modificações

### [MODIFY] `04_Estrategia/run.py`

**Pre-flight** — inserir logo após o setup de logging, antes de `extract()`:

```python
from governance_sensor import run_preflight
...
def main() -> None:
    run_preflight(str(_shared_dir), fail_fast=False)
    log.info("=== Motor de Estrategia V1 — inicio ===")
    ...
```

**Post-flight** — inserir após `save()` com sucesso, antes de `sys.exit(0)`:

```python
import subprocess
...
        save(df_export, df_prospects, df_super, auditoria, DATA_DIR, SHARED_DATA)
        try:
            subprocess.run(
                [sys.executable, str(_shared_dir / "generate_recency_report.py")],
                check=False,
            )
        except Exception as exc:
            log.warning("Post-flight: falha ao atualizar relatorio de recencia: %s", exc)
        log.info("=== Motor de Estrategia V1 — concluido com sucesso ===")
        sys.exit(0)
```

---

### [MODIFY] `shared/generate_recency_report.py`

Corrigir naming incorreto: `"M5 (Estratégico)"` → `"M4 (Estratégia)"`.

```python
# De:
"M5 (Estratégico)": {
    "path": shared_data / "dataset_final_estrategico_v1.parquet",
    ...
}
# Para:
"M4 (Estratégia)": {
    "path": shared_data / "dataset_final_estrategico_v1.parquet",
    ...
}
```

---

## 3. Verificação

| ID | Teste | Critério |
|---|---|---|
| T-001 | `python -m py_compile run.py generate_recency_report.py` | Exit 0, sem erros de sintaxe |
| T-002 | Executar `run.py` com parquets de entrada presentes | `recency_status.md` atualizado com `"M4 (Estratégia)"` e status correto |
| T-003 | `python validate_pipeline.py --skip-run` | Sem falhas estruturais |
