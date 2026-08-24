---
name: inova-bup-refresh
description: Use quando for solicitado um refresh do BUP, a base pós-venda estiver desatualizada ou os outputs upstream precisarem de validação governada.
trigger_phrases:
  - "refresh BUP"
  - "atualizar BUP"
  - "consolidar BUP"
  - "base única pós-venda"
  - "recência BUP"
version: 1.0.0
tier: 2
category: orchestrator
author: Victor
dependencies:
  - inova-pipeline-01
  - inova-motor-faturamento
  - inova-motor-orcamentos
---

# inova-bup-refresh

## Objetivo

Executar o refresh da BUP somente quando as entradas upstream exigidas estiverem comprovadamente atuais. O contrato em `shared/refresh_governance.json` é a fonte de verdade; caches e caminhos legados não são fallback.

## Pré-requisitos

- O repositório `C:\Projetos\Inova` e `projects/BUP-base-unica-pós-venda` estão disponíveis.
- O Python governado é `C:\Projetos\Inova\.venv\Scripts\python.exe`.
- A branch do projeto não é `fix/jd-acs-telemetry-resolver`.
- M0 Identidade, M5 Estratégia, M3/RFM, frota, cadastro SA1010 e os parquets atuais de orçamentos estão dentro da janela de recência.

## Fluxo

1. Verificar branch e worktree do projeto. Preservar alterações locais; não executar o refresh a partir da branch JD ACS.
2. Regenerar o relatório de recência:

   ```powershell
   $repo = "C:\Projetos\Inova"
   $python = Join-Path $repo ".venv\Scripts\python.exe"
   if (-not (Test-Path $python)) { throw "Python governado não encontrado: $python" }
   & $python (Join-Path $repo "shared\generate_recency_report.py")
   if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar recência" }
   ```

3. Rodar o preflight de dependências. Ele bloqueia fonte ausente, fonte fora da janela comercial ou consumidor não permitido:

   ```powershell
   & $python (Join-Path $repo "shared\dependency_governance.py") `
     --product bup --repo-root $repo
   if ($LASTEXITCODE -ne 0) { throw "BUP bloqueado por dependência upstream" }
   ```

4. Executar o sensor e o QA mínimo antes da consolidação:

   ```powershell
   & $python (Join-Path $repo "shared\governance_sensor.py") `
     --shared (Join-Path $repo "shared")
   if ($LASTEXITCODE -ne 0) { throw "Preflight BUP falhou" }

   $project = Join-Path $repo "projects\BUP-base-unica-pós-venda"
   Push-Location $project
   try {
     & $python -m pytest tests\test_bup_scheduler_log.py tests\test_bup_output_invariants.py -q
     if ($LASTEXITCODE -ne 0) { throw "QA BUP falhou" }
   } finally { Pop-Location }
   ```

5. Executar `scripts/consolidate_bup.py` a partir do projeto BUP. O consolidator usa os outputs atuais do Motor de Orçamentos e `m0_cache_sa1010.parquet`; não usar `metas-pecas` nem caches nomeados por hash antigo.
6. Regenerar a recência e confirmar `data/BUP_POS_VENDA.xlsx` e um snapshot `data/BUP_POS_VENDA_<YYYYMMDD_HHMM>.xlsx`. Em falha de governança, não publicar uma atualização degradada.

## Contrato de dependências

O BUP exige as fontes declaradas no manifesto e não depende de CEVAP ou de qualquer output downstream. O único consumidor declarado do BUP é `inova-cevap-refresh`.

## Constraints

- Nunca ignorar preflight, usar `--force` ou ressuscitar caminhos legados.
- Nunca usar Python global, Anaconda ou um `.venv` local fora do caminho governado.
- Nunca remover feedback comercial sem o merge de preservação do consolidator.
- Não editar Task Scheduler durante o refresh.
- Não fazer commit, push, merge ou limpeza destrutiva como parte da execução.

## Saída esperada

Relatar preflight, bloqueadores upstream, caminho do snapshot, estado de `BUP_POS_VENDA.xlsx` e código de saída final.
