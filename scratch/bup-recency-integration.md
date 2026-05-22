---
title: Integracao BUP Governanca Recencia
created_at: 2026-05-21
updated_at: 2026-05-21
summary: Plano de implementacao para integrar o BUP a malha de governanca de recencia com validacao pre-flight e atualizacao post-flight do relatorio de recencia.
base_confidence: 0.92
lifecycle: draft
lifecycle_changed: "2026-05-21"
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
tags: [bup, governanca, automacao, inova]
sources: [bup-recency-governance-integration.md]
---

## Objetivo

Fazer o `consolidate_bup.py` atualizar o `shared/recency_status.md` ao final de cada execucao e validar as fontes antes de comecar. Hoje o BUP **le** o relatorio de recencia mas nunca o **atualiza**.

## Design

### Pre-flight (inicio da `run_consolidation()`)

```python
# Apos check_recency_report(), adicionar:
try:
    from governance_sensor import run_preflight
    run_preflight(str(_shared_dir), fail_fast=False)
except Exception as exc:
    print(f"AVISO: Falha ao executar Pre-flight check: {exc}")
```

### Post-flight (final da `run_consolidation()`, apos `df_final.to_excel()`)

```python
print("[INICIO] Post-flight: Atualizando Relatorio de Recencia...")
try:
    import subprocess
    recency_script = _shared_dir / "generate_recency_report.py"
    subprocess.run([sys.executable, str(recency_script)], check=False)
    print("[OK] Post-flight: Relatorio de Recencia atualizado.")
except Exception as exc:
    print(f"AVISO: Falha nao-bloqueante ao gerar relatorio de recencia: {exc}")
```

## Arquivos a modificar

| Arquivo | Mudanca |
|---------|---------|
| `scripts/consolidate_bup.py` | +2 blocos: Pre-flight e Post-flight |
| `tests/test_bup_recency_alert.py` | +2 testes TDD |
| `CLAUDE.md` | Atualizar secao de QA para incluir governanca |

## Testes (TDD)

- `test_preflight_invoked()`: Mocka `governance_sensor.run_preflight` com `fail_fast=False`
- `test_postflight_invoked()`: Mocka `subprocess.run` com `generate_recency_report.py` apos exportacao

## Verificacao

1. `pytest tests/test_bup_recency_alert.py -v` — todos passam
2. `python scripts/consolidate_bup.py` — console mostra Pre-flight e Post-flight
3. `shared/recency_status.md` — timestamp BUP_POS_VENDA atualizado

## Conceitos relacionados

[[governanca-recencia]], [[pipeline-inova]], [[motores-inova]], [[wiki-compiler]]
