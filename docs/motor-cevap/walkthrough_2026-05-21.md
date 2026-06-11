# Walkthrough — Sessão 2026-05-21

## Entregas

### 1. AGENTS.md Preenchido

Preenchimento completo do `AGENTS.md` com todas as seções baseadas no conteúdo existente do projeto (GEMINI.md, ANTIGRAVITY.md, scripts, docs, learnings):

- **Project Overview** — stack, KPI, domínio, estrutura de diretórios
- **Code Style Guidelines** — 7 regras (pathlib, rate_match, timestamp, edição cirúrgica + 3 originais)
- **Architecture Notes** — pipeline principal (4 scripts), scripts de diagnóstico (4), ferramentas cross-project, schema Gold V5 (22 colunas), regras de negócio (6), MCPs (3), fontes de dados (7), governança
- **Common Workflows** — 5 comandos documentados

### 2. Governança de Recência Integrada

**Arquivo:** `consolidate_cevap.py`

Motor CEVAP agora segue o mesmo padrão dos motores 02_Faturamento, 03_Potencial e 05_Segmentacao:

- **Pre-flight:** `governance_sensor.run_preflight(str(_shared_dir), fail_fast=False)` no início de `run_consolidation()`, try/except não-bloqueante
- **Post-flight:** `subprocess.run([sys.executable, str(_shared_dir / "generate_recency_report.py")], check=False)` ao final, try/except não-bloqueante
- `check_recency_report()` preservado — roda logo após o Pre-flight
- `import subprocess` e `import shutil` adicionados

### 3. Monitoramento na Tabela de Recência Global

**Arquivo:** `shared/generate_recency_report.py`

- Fonte `"CEVAP (Ativacao)"` adicionada com suporte a glob (`CEVAP_ATIVACAO_*.xlsx`)
- Output aparece no `recency_status.md`

### 4. Cópia OneDrive com Preservação de Controle Comercial

**Arquivo:** `consolidate_cevap.py`

- Lê arquivo existente no OneDrive, extrai colunas de controle (`Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2`, `Observacao`)
- Merge por `CNPJ_Cliente` preserva preenchimentos do Filipe
- Novos clientes iniciam com `""` / `"Pendente"`
- Normalização de tipos (`object` vs `int64`) para evitar erro no merge
- Auditoria: contagem antes/depois, identificação de CNPJs órfãos (solda de identidade)
- Primeira exportação usa `shutil.copy2`
- **Execução real validada:** 2.910/32.759 preenchimentos preservados, 74 CNPJs órfãos detectados

### 5. Testes

| Teste | O que valida |
|---|---|
| `test_columns.py` | 22 colunas do schema Gold V5 |
| `test_cevap_recency_alert.py` ×4 | `check_recency_report` (atualizado, desatualizado, ausente, invocação) |
| `test_governance.py` | `run_preflight` + Post-flight invocados |
| `test_onedrive.py` ×4 | Primeira exportação, merge com preservação, novos clientes, solda de CNPJs |

**10/10 passando.**

### 6. Correção de Path

`PATH_CADASTRO` corrigido de `m0_cache_sa1010_983280b9.parquet` para `m0_cache_sa1010.parquet`.

### 7. Execução Real Validada

```
Motor CEVAP — 2026-05-21 18:32
✅ Pre-flight: passou
✅ Recência: todas as fontes atualizadas
✅ Consolidação: 162.634 registros M3 → 955 clientes
✅ Post-flight: recency_status.md atualizado
✅ OneDrive: merge com preservação (2.910/32.759)
⚠️ 74 CNPJs órfãos (solda identidade) — logados
```

## Fluxo Final do Motor

```
run_consolidation()
  ├── Pre-flight: governance_sensor.run_preflight()     [try/except]
  ├── check_recency_report()                            [existente]
  ├── Carga M5 → M3 → Cadastro → Máquinas → Orçamentos
  ├── Seedz → InovaPay → Formatação → Exportação XLSX
  ├── OneDrive: merge com preservação de controle       [try/except, auditoria]
  └── Post-flight: subprocess generate_recency_report   [try/except]
```
