---
name: inova-bi-faturamento
description: Atualiza os parquets de faturamento do BI (Detalhamento-Peças) executando o scraper Playwright contra o Power BI da Inova. Use quando os arquivos detalhamento_vendas_2025/2026.parquet estiverem desatualizados ou quando o M2 precisar de dados frescos para validação.
trigger_phrases:
  - "atualizar bi de faturamento"
  - "exportar detalhamento pecas"
  - "bi desatualizado"
  - "faturamento bi"
  - "inova-bi-faturamento"
---

# Skill: inova-bi-faturamento

Executa o pipeline de extração do relatório "Detalhamento de Peças" no Power BI e persiste os parquets em `shared/data/`.

## Pré-requisitos

- **Browser headed obrigatório** — Azure AD SSO bloqueia headless. O browser vai abrir visualmente.
- **Sessão Power BI ativa** — se expirada, autenticar primeiro via `authenticate.py`.
- **Venv:** `C:\Projetos\Inova\.venv`

## Execução

### Caso mais comum: atualizar 2026 (carga total Jan/2026 → hoje)

```powershell
$env:PYTHONIOENCODING = "utf-8"
Set-Location "C:\Projetos\Inova\projects\Detalhamento-Pecas"
& "C:\Projetos\Inova\.venv\Scripts\python.exe" run.py --ano 2026
```

### Refresh histórico 2025 (somente se dados de 2025 forem alterados no BI)

```powershell
$env:PYTHONIOENCODING = "utf-8"
Set-Location "C:\Projetos\Inova\projects\Detalhamento-Pecas"
& "C:\Projetos\Inova\.venv\Scripts\python.exe" run.py --ano 2025
```

### Sessão expirada — re-autenticar antes

```powershell
Set-Location "C:\Projetos\Inova\projects\Detalhamento-Pecas"
& "C:\Projetos\Inova\.venv\Scripts\python.exe" authenticate.py
```

## O que o pipeline faz (5 etapas internas)

1. **Extrair** — Playwright abre Power BI, aplica filtro de data, exporta XLSX
2. **Transformar** — remove metadata do BI, valida schema de colunas
3. **Validar threshold** — aborta se variação vs parquet anterior > 10%
4. **Persistir** — salva `shared/data/detalhamento_vendas_{ano}.parquet`
5. **Recência** — dispara `generate_recency_report.py` automaticamente

## Artefatos de saída

| Arquivo | Localização |
|---------|-------------|
| `detalhamento_vendas_2025.parquet` | `C:\Projetos\Inova\shared\data\` |
| `detalhamento_vendas_2026.parquet` | `C:\Projetos\Inova\shared\data\` |

## Pós-execução recomendada

Após atualizar os parquets, rodar o M2 com cache para disparar a auditoria com dados frescos:

```powershell
$env:PYTHONIOENCODING = "utf-8"
& "C:\Projetos\Inova\.venv\Scripts\python.exe" `
  "C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\run.py" --cache
```

## Armadilhas

| Problema | Causa | Fix |
| --- | --- | --- |
| Sessão expirada | `state.json` venceu | Rodar `authenticate.py` primeiro |
| Export truncado | Filtro de data no BI com formato errado | Checar DD/MM/AAAA no slicer |
| Botão confirmar não aparece | Diálogo está dentro do iframe do PBI | O script já trata — re-tentar (3x automático) |
| Threshold > 10% | Variação anômala vs parquet anterior | Investigar antes de forçar — pode ser dado errado |

## Referências

- Pipeline: `C:\Projetos\Inova\projects\Detalhamento-Pecas\`
- CONTEXT.md do projeto: descreve os 6 estágios ICM-CDD
- Motor que consome os parquets: `02_Faturamento` (M2)
