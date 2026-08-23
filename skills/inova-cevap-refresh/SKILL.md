---
name: inova-cevap-refresh
description: Use quando for solicitado um refresh do CEVAP, o snapshot de ativação estiver desatualizado ou um BUP do dia precisar ser validado antes da preservação comercial.
trigger_phrases:
  - "refresh CEVAP"
  - "atualizar CEVAP"
  - "consolidar CEVAP"
  - "ativação de clientes inativos"
  - "planilha CEVAP"
version: 1.0.0
tier: 2
category: orchestrator
author: Victor
dependencies:
  - inova-bup-refresh
---

# inova-cevap-refresh

## Objetivo

Executar o motor de ativação CEVAP somente após um BUP validado no dia corrente. O consolidator filtra clientes com `Dias_Inativo >= 90`, seleciona `Consultor=CEVAP` e preserva por `CNPJ_Cliente` os campos comerciais da planilha ativa.

## Pré-requisitos

- `inova-bup-refresh` terminou com sucesso no mesmo dia.
- O checkout canônico é `C:\Projetos\Inova.maquinas\motor-cevap`.
- `CEVAP_BUP_PATH` aponta para o BUP validado; `CEVAP_ONEDRIVE_PATH` aponta para a planilha ativa que contém os controles comerciais.
- O preflight standalone deve bloquear BUP ausente, ilegível ou fora da recência declarada no manifesto local.

## Fluxo

1. Verificar o worktree standalone e preservar alterações locais. Não executar o motor a partir de checkout legado.
2. Definir as fontes upstream e de preservação antes da execução:

   ```powershell
   $project = "C:\Projetos\Inova.maquinas\motor-cevap"
   $env:CEVAP_BUP_PATH = "C:\Projetos\Inova\projects\BUP-base-unica-pós-venda\data\BUP_POS_VENDA.xlsx"
   $env:CEVAP_ONEDRIVE_PATH = Join-Path $env:USERPROFILE "OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\CEVAP_ATIVACAO.xlsx"
   Set-Location $project
   if (-not (Test-Path $env:CEVAP_BUP_PATH)) { throw "BUP upstream não encontrado" }
   if (-not (Test-Path $env:CEVAP_ONEDRIVE_PATH)) { throw "Planilha CEVAP para preservação não encontrada" }
   ```

3. Rodar o QA focused antes da consolidação:

   ```powershell
   if (Test-Path ".venv\Scripts\python.exe") {
     & ".venv\Scripts\python.exe" -m pytest tests\test_inactivity_filter.py tests\test_governance.py tests\test_onedrive.py -q
   } else {
     uv run --no-project pytest tests\test_inactivity_filter.py tests\test_governance.py tests\test_onedrive.py -q
   }
   if ($LASTEXITCODE -ne 0) { throw "QA CEVAP falhou" }
   ```

4. Executar `scripts/consolidate_cevap.py` no checkout standalone:

   ```powershell
   if (Test-Path ".venv\Scripts\python.exe") {
     & ".venv\Scripts\python.exe" scripts\consolidate_cevap.py
   } else {
     uv run --no-project python scripts/consolidate_cevap.py
   }
   if ($LASTEXITCODE -ne 0) { throw "Consolidação CEVAP falhou" }
   ```

5. Confirmar o snapshot `data/CEVAP_ATIVACAO_<YYYYMMDD_HHMM>.xlsx`, a atualização do ativo e a preservação por CNPJ de `Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2` e `Observacao`. Novos clientes recebem somente os defaults do consolidator.
6. Reabrir o artefato e confirmar que o monitor identifica `CEVAP (Ativacao)` pelo snapshot mais recente. Em falha de governança, não publicar uma atualização degradada.

## Preservação comercial

Antes de considerar o refresh concluído, auditar a interseção antiga/nova por `CNPJ_Cliente`. Qualquer divergência nos cinco campos manuais é bloqueio. Backups locais em `data/backups/` são evidência de recuperação e não devem ser apagados sem autorização.

## Constraints

- Nunca executar sem BUP do mesmo dia, ignorar preflight ou usar snapshot antigo.
- Nunca substituir a planilha ativa com `copy`, `to_excel` ou comando fora do consolidator.
- Nunca perder os cinco campos manuais nem inferir os valores de `Venda`, `Nao Venda` ou `Sem Contato`.
- Nunca usar Python global/Anaconda, editar Task Scheduler, fazer commit, push, merge ou limpeza destrutiva durante o refresh.

## Saída esperada

Relatar BUP/preflight, snapshot CEVAP, contagens antes/depois da peneira, auditoria dos cinco campos, backup criado e estado do arquivo ativo.
