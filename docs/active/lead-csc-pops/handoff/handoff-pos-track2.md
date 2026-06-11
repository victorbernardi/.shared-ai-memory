# Handoff: Pós Track 2 — Pendências e Próximas Sessões

**Data:** 2026-06-08  
**Branch de origem:** `feat/auditoria-preenchimento-leads`  
**Status:** Track 2 completo, aguardando merge e continuidade

---

## Contexto

O Track 2 (preservação de Retorno/Obs em `lead-csc-pops`) foi implementado via TDD com 19 testes e 5 commits. A branch `feat/auditoria-preenchimento-leads` está pronta mas o merge em `master` está bloqueado porque o workspace do monorepo tem dezenas de arquivos pendentes de outras sessões/projetos que precisam ser organizados antes.

---

## Sessão 1 — Limpar workspace e mergear Track 2

**Objetivo:** Workspace zerado + Track 2 em `master`.

**Passos:**

1. Identificar para cada arquivo pendente se é relevante ou descartável:

   ```
   cd C:\Projetos\Inova
   git status --short
   ```

2. Para arquivos relevantes, criar branches por projeto (ver Sessão 2+).  
   Para arquivos descartáveis, descartar via `git checkout -- <arquivo>`.

3. Após workspace limpo, fazer o merge:

   ```powershell
   git stash --include-untracked   # se ainda houver pendências
   git checkout master
   git merge --no-ff feat/auditoria-preenchimento-leads
   git branch -d feat/auditoria-preenchimento-leads
   git stash pop                   # se usou stash
   ```

4. Validar com `python scripts/comparar_track2.py` rodando em `master`.

**Arquivos bloqueadores identificados:**

| Projeto | Arquivos tracked modificados |
|---------|------------------------------|
| lead-csc-pops | `scripts/scheduler_daily.ps1`, `src/config.py`, `tests/test_load_consultor.py` |
| M3 Potencial | `03_Potencial/run.py`, `transform.py`, 2 arquivos de teste |
| M4 Estratégia | 3 relatórios `.xlsx`, `gerar_diagrama.bat` |
| shared/data | 8 arquivos `.parquet`, `recency_status.md`, `run_recency_report.bat` |
| Inova-Daily | `run_daily_task.bat`, `run_email_task.bat` |
| motor-cevap | `.claude/settings.local.json` + arquivos `.stout/` |
| root | `.claude/settings.local.json`, `.vscode/settings.json`, `CLAUDE.md` |
| BUP | `projects/BUP-base-unica-pós-venda` |

---

## Sessão 2 — Organizar pendências: lead-csc-pops e shared

**Objetivo:** Commitar alterações pendentes do próprio `lead-csc-pops` e dos dados compartilhados.

**Branch:** `chore/lead-csc-pops-config-scheduler`

**Arquivos:**

- `projects/lead-csc-pops/scripts/scheduler_daily.ps1`
- `projects/lead-csc-pops/src/config.py`
- `projects/lead-csc-pops/tests/test_load_consultor.py`

**Branch:** `chore/shared-data-parquets`

**Arquivos:**

- `shared/data/*.parquet` (8 arquivos)
- `shared/recency_status.md`
- `shared/run_recency_report.bat`

**Passos:**

1. Entender o que mudou em cada arquivo (`git diff <arquivo>`)
2. Nomear o commit adequadamente conforme o conteúdo
3. Criar branch, adicionar arquivos, commitar

---

## Sessão 3 — Organizar pendências: M3 Potencial

**Objetivo:** Commitar alterações do Motor M3 Potencial em branch própria.

**Branch:** `feat/m3-potencial-horimetro` *(ou nome mais adequado após revisar o diff)*

**Arquivos:**

- `pipelines/potencial-clientes/03_Potencial/run.py`
- `pipelines/potencial-clientes/03_Potencial/transform.py`
- `pipelines/potencial-clientes/03_Potencial/tests/test_horimetro_oficina.py`
- `pipelines/potencial-clientes/03_Potencial/tests/test_potencial_clientes.py`

**Passos:**

1. Ler `git diff` de cada arquivo para entender o escopo das mudanças
2. Verificar relação com Track 3 (bug do `Horimetro_Final` em `extract.py`) — podem ser a mesma branch
3. Rodar os testes do M3 antes de commitar

---

## Sessão 4 — Track 3: fix de horímetro em extract.py

**Objetivo:** Corrigir `extract.py` para usar `Horimetro_Final` (estimativa M3) em vez de `Forecasted Machine Hours` (leitura bruta AOR).

**Branch:** `fix/lead-csc-pops-horimetro-final`

**Contexto técnico:**

- `Forecasted Machine Hours` = leitura bruta do AOR (pode estar zerada ou desatualizada)
- `Horimetro_Final` = estimativa processada pelo M3 com imputação para leituras inválidas
- `STATUS_USO` = `"REAL"` (leitura recente) ou `"ESTIMADO"` (imputado)
- Fonte: `shared/data/dataset_ouro_potencial_chassi_v1.parquet`
- Bug identificado durante o brainstorming do Track 2 — não bloqueava o Track 2

**Arquivo a modificar:** `projects/lead-csc-pops/src/extract.py`

**Passos:**

1. Ler spec: `docs/specs/2026-06-08-auditoria-preenchimento-leads.md` seção 8.7
2. Fazer brainstorming da mudança (impacto nos ciclos existentes — transição gradual)
3. Escrever testes primeiro (TDD)
4. Implementar e validar com `comparar_track2.py`

---

## Sessão 5 — Organizar pendências: Inova-Daily, motor-cevap, M4, root

**Objetivo:** Limpar as últimas pendências do workspace.

**Branches:**

| Branch | Arquivos |
|--------|----------|
| `chore/inova-daily-scripts` | `projects/Inova-Daily/run_daily_task.bat`, `run_email_task.bat` |
| `chore/motor-cevap-settings` | `projects/motor-cevap/.claude/settings.local.json` + `.stout/` |
| `chore/m4-estrategia-relatorios` | 3 xlsx de relatórios + `gerar_diagrama.bat` |
| `chore/root-config` | `.claude/settings.local.json`, `.vscode/settings.json`, `CLAUDE.md` |
| `chore/bup-base-unica` | `projects/BUP-base-unica-pós-venda` |

**Passos:**

1. `git diff` em cada arquivo para confirmar o conteúdo
2. Criar branch, add, commit por projeto
3. Confirmar workspace zerado ao final: `git status --short` deve retornar vazio (exceto untracked de sessão)

---

## Referências

- **Spec Track 2:** `docs/specs/2026-06-08-auditoria-preenchimento-leads.md`
- **Plano Track 2:** `docs/superpowers/plans/2026-06-08-track2-preservacao-retorno-obs.md`
- **Script de validação:** `projects/lead-csc-pops/scripts/comparar_track2.py`
- **Branch pronta para merge:** `feat/auditoria-preenchimento-leads`
