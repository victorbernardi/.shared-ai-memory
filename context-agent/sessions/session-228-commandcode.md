# Session 228: lead-csc-pops - Refatoracao sincronizar_pecas + fix extract.py

**Data:** 2026-06-09
**Origin:** commandcode
**Projeto:** lead-csc-pops

## Topicos
- Refatoracao do pipeline de sincronizacao de pecas
- Remocao de coluna Delta Horimetro (16 -> 15 colunas)
- Reescrita de sincronizar_pecas.py: VBA -> Power Query via wb.Queries.Add()
- Reordenacao do run.py: base.xlsx sync antes de Power Query refresh
- Fix conflito de modulo config entre src/ e shared/ (runpy.run_path)
- Fix path do parquet M3 (shared/data/)
- Fix caracteres Unicode (checkmark, warning) no Windows cp1252

## Decisoes
- Remover Delta Horimetro: campo derivado, consultores nao precisam editar
- Power Query via wb.Queries.Add() em vez de VBA: mais simples, sem protecao por senha
- runpy.run_path() para importar shared/config.py: evita conflito de nome com src/config.py no sys.modules
- timeout de 60s via threading.Thread na chamada de sincronizar_pecas()

## Tarefas Concluidas
- [x] Task 1: Testes atualizados para 15 colunas + validacoes N/O (TDD RED)
- [x] Task 2: load.py corrigido - remove Delta Horimetro, fix colunas 14/15 (TDD GREEN)
- [x] Task 3: sincronizar_pecas.py reescrito sem VBA, com Power Query
- [x] Task 4: run.py reordenado - base.xlsx sync antes de sincronizar_pecas()
- [x] Task 5: Verificacao final - 59/59 testes passando
- [x] Fix extract.py: conflito de modulo config (runpy.run_path)
- [x] Fix extract.py: path do parquet M3 corrigido
- [x] Fix extract.py: caracteres Unicode removidos

## Tarefas Pendentes
- [ ] Diagnosticar travamento do COM do Excel em sincronizar_pecas()
- [ ] Configurar query Power Query manualmente no pecas.xlsx como alternativa
- [ ] Commit das alteracoes pendentes (6 arquivos modificados)
- [ ] Rodar pipeline completo com sucesso

## Arquivos Modificados
- projects/lead-csc-pops/tests/test_load_consultor.py (15 colunas, validacoes N/O)
- projects/lead-csc-pops/src/load.py (remove Delta Horimetro, col 14/15)
- projects/lead-csc-pops/scripts/sincronizar_pecas.py (Power Query, sem VBA)
- projects/lead-csc-pops/run.py (reordena step 5, timeout 60s, remove gerenciar_backup_e_rotacao import)
- projects/lead-csc-pops/src/extract.py (runpy.run_path, path M3, Unicode fix)

## Descobertas Tecnicas
- importlib.util.exec_module() trava silenciosamente no Windows ao carregar shared/config.py
- runpy.run_path() funciona como alternativa confiavel
- O COM do Excel via win32com pode travar se o processo Excel nao iniciar corretamente
- Caracteres Unicode (checkmark, warning) causam UnicodeEncodeError no Windows cp1252

## Query Power Query (para configurar manualmente)
```m
let
    Source = Excel.Workbook(File.Contents("C:\\Users\\victor.bernardi\\OneDrive - INOVA EQUIPAMENTOS LTDA\\Documentos\\leads-csc-pops-base.xlsx"), null, true),
    Sheet = Source{[Item="Leads Ativos",Kind="Sheet"]}[Data],
    Headers = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true])
in
    Headers
```

## Handoff
docs/handoff/2026-06-09-refatoracao-sincronizar-pecas.md
