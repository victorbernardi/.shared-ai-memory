# Detalhamento de Pecas — Especificação Técnica do Scraper Power BI

**Data:** 2026-06-10  
**Versão:** 1.0  
**Status:** Design Aprovado  
**Autor:** Claude (Brainstorming Stout)

---

## 1. Objetivo

Implementar um scraper Playwright que extrai o relatório "Detalhamento de Vendas" do Power BI (página "Detalhamento Peças"), com duas estratégias de carregamento:

- **2025:** Carga histórica única (01/01/2025 a 31/12/2025)
- **2026:** Atualizações diárias incrementais (último_dia+1 até hoje)

Dados serão salvos como parquets em `shared/data/` e integrados à governança de recência do ecossistema Inova.

---

## 2. Requisitos

### 2.1 Requisitos Funcionais

| ID | Requisito | Critério de Aceitação |
|----|-----------|-----------------------|
| RF-1 | Extrair dados de 2025 em carga única | Execução: 01/01/2025 a 31/12/2025, salvando em `detalhamento_vendas_2025.parquet` |
| RF-2 | Extrair dados de 2026 diariamente | Task agendada diária, range: último_dia_carregado+1 a hoje |
| RF-3 | Limpar metadata do Power BI | Remover 3 linhas finais (Total, vazio, Applied filters) usando critério Nota Fiscal |
| RF-4 | Validar dados com threshold de variação | Comparar totais (receita/quantidade) com período anterior, alertar se Δ > 10% |
| RF-5 | Retry automático em falhas | 3 tentativas com backoff exponencial antes de falhar |
| RF-6 | Armazenar parquets separados | 2025 em `detalhamento_vendas_2025.parquet`, 2026 em `detalhamento_vendas_2026.parquet` |
| RF-7 | Integrar com governança de recência | Registrar em `shared/recency_status.md` + atualizar `shared/generate_recency_report.py` |
| RF-8 | Logging essencial | Registrar erros + resumo (X registros, Y removidos por metadata, Z validados) |

### 2.2 Requisitos Não-Funcionais

| ID | Requisito | Valor/Descrição |
|----|-----------|-----------------|
| NF-1 | Timeout de scrape | Máx 5 minutos por execução (navegação + render + export) |
| NF-2 | Autenticação | Reusar `.browser_state/state.json` de `dashboard-inova-data-export` |
| NF-3 | Volume de dados | Máx ~200k registros/dia (tabela simples) |
| NF-4 | Retenção de histórico | 2025 (imutável), 2026 (sobrescrever diariamente) |
| NF-5 | Confiabilidade | Retry 3x com backoff; logging completo de falhas |
| NF-6 | Compatibilidade | Python 3.10+, Playwright, pandas, pyarrow |

---

## 3. Arquitetura

### 3.1 Estrutura de Pastas

```
projects/Detalhamento-Pecas/
├── src/
│   ├── __init__.py
│   ├── config.py              # URLs, paths, timeouts
│   ├── extract.py             # Scraper Playwright
│   ├── transform.py           # Limpeza de metadata + validação
│   └── load.py                # Salvar parquets + registrar recency
├── data/
│   └── output/                # Arquivos locais (temporário)
├── .browser_state/            # Compartilhado com dashboard-inova-data-export
├── run.py                      # Orquestrador (entry point)
├── tests/
│   └── test_detalhamento.py   # Testes de governança
├── docs/
│   └── specs/
│       └── 2026-06-10-detalhamento-pecas-scraper.md (este arquivo)
└── requirements.txt            # Dependências
```

### 3.2 Fluxo de Dados

```
Power BI Report
    ↓
[Playwright] extrair_detalhamento_pecas(data_inicio, data_fim)
    ↓
DataFrame bruto (com metadata)
    ↓
[Transform] limpar_metadata_powerbi() + validar_schema()
    ↓
DataFrame limpo
    ↓
[Validação] comparar_totais_com_periodo_anterior()
    ↓ (se passou)
[Load] salvar_parquet() → shared/data/
    ↓
[Governance] atualizar_recency_status()
    ↓
[Post-flight] generate_recency_report.py (subprocess)
```

### 3.3 Módulos

#### `src/config.py`

- URLs do Power BI (BASE_URL, ORG_URL, REPORT_URL, página "Detalhamento Peças")
- Paths (BROWSER_STATE, OUTPUT_DIR, SHARED_DATA_DIR)
- Timeouts (PAGE_LOAD_TIMEOUT=60s, NAVIGATION_DELAY=25s, RENDER_WAIT=15s)
- Viewport (1920x1080)

#### `src/extract.py`

- `extrair_detalhamento_pecas(data_inicio, data_fim) → DataFrame`
  - Carrega state.json de dashboard-inova-data-export
  - Navega até aba "Detalhamento Peças"
  - Aplica filtros de data (se houver slicers)
  - Localizador para tabela "Detalhamento de Vendas"
  - Clica "Exportar para Excel", aguarda download
  - Lê arquivo do Downloads, retorna DataFrame

#### `src/transform.py`

- `limpar_metadata_powerbi(df) → DataFrame`
  - Remove linhas onde "Nota Fiscal" é NaN (critério: toda venda válida tem Nota Fiscal)
  - Retorna contagem de removidas

- `validar_schema(df) → bool`
  - Verifica colunas essenciais: Nota Fiscal, Data, CNPJ
  - Retorna True/False

- `transformar_detalhamento_pecas(df) → DataFrame`
  - Pipeline: validar schema → limpar metadata

#### `src/load.py`

- `salvar_parquet(df, nome_arquivo) → Path`
  - Salva em `shared/data/` com engine pyarrow

- `atualizar_recency_status(arquivo_parquet, linhas_processadas, linhas_removidas)`
  - Registra em `shared/recency_status.md`:

    ```
    | Detalhamento-Pecas (2026) | 2026-06-10 | 45,230 | 3 | 45,227 |
    ```

#### `run.py`

- Orquestrador principal
- Argumentos:
  - `--ano {2025,2026}` — qual ano extrair
  - `--data-inicio YYYY-MM-DD` — override (para 2026: calcula automaticamente)
  - `--data-fim YYYY-MM-DD` — override
  - `--no-cache` — desativa cache de state.json
  - `--forcar-validacao` — força validação rigorosa mesmo com pequenas variações

- Fluxo:
  1. Log de início
  2. Pre-flight: governance_sensor.py (se implementado)
  3. Extract: `extrair_detalhamento_pecas()`
  4. Transform: `transformar_detalhamento_pecas()`
  5. Validação: comparar totais com período anterior
  6. Load: `salvar_parquet()` + `atualizar_recency_status()`
  7. Post-flight: `subprocess.run([...generate_recency_report.py])`
  8. Log de conclusão (X registros, Y removidos, Z validados)

---

## 4. Validação (Plano de Testes)

### 4.1 Testes Unitários

| Teste | Expectativa |
|-------|-------------|
| `test_limpar_metadata_powerbi_remove_3_linhas` | Dado DataFrame com 1003 linhas (1000 válidas + 3 metadata), retorna 1000 |
| `test_validar_schema_columns_existem` | Verifica se "Nota Fiscal", "Data", "CNPJ" existem |
| `test_validar_schema_fail_sem_coluna` | Retorna False se faltar coluna obrigatória |
| `test_salvar_parquet_cria_arquivo` | Confirma arquivo salvo em shared/data/ |
| `test_carregar_parquet_preserva_tipos` | Recarrega parquet, tipos de dados intactos |

### 4.2 Testes de Integração

| Teste | Expectativa |
|-------|-------------|
| `test_extrair_2025_completo` | Executa scrape de 01/01/2025 a 31/12/2025, retorna DataFrame não-vazio |
| `test_atualizar_2026_incremental` | Dado estado anterior (ex: até 2026-06-09), extrai apenas 2026-06-10, concatena, valida |
| `test_validacao_threshold_passa` | Dados com Δ < 10% passam validação |
| `test_validacao_threshold_falha` | Dados com Δ > 10% falham e não atualizam parquet |
| `test_retry_3x_com_backoff` | Falha 2x (mock), sucesso 3x → completa com sucesso |
| `test_recency_status_atualizado` | `shared/recency_status.md` registra nova entrada |

### 4.3 Testes de Governança

| Teste | Expectativa |
|-------|-------------|
| `test_generate_recency_report_include_detalhamento` | Script de relatório inclui Detalhamento-Pecas na lista de fontes |
| `test_postflight_subprocess_chamado` | run.py chama `subprocess.run([...generate_recency_report.py])` no fim |

### 4.4 Testes Manuais (E2E)

1. **Carga 2025:**

   ```bash
   python run.py --ano 2025
   ```

   Verifica: `detalhamento_vendas_2025.parquet` criado, ~12-15k registros esperados

2. **Atualização 2026 (primeira vez):**

   ```bash
   python run.py --ano 2026
   ```

   Verifica: `detalhamento_vendas_2026.parquet` criado com dados até hoje

3. **Atualização 2026 (incremental):**

   ```bash
   python run.py --ano 2026
   ```

   (próximo dia)  
   Verifica: parquet atualizado apenas com novos registros do dia anterior

4. **Validação rigorosa (threshold):**
   Mock dados com Δ > 10%, verifica se processo falha e parquet não é atualizado

---

## 5. Decision Log

| Decisão | Alternativas Consideradas | Razão da Escolha |
|---------|---------------------------|------------------|
| **2 Parquets separados** | Arquivo único consolidado (2025+2026) | Facilita reprocessamento de 2025 sem afetar 2026; simplifica versionamento |
| **Sobrescrever 2026 diariamente** | Versioning com timestamps | Reduz acúmulo de versões; último estado sempre reflete "hoje" |
| **Range incremental (último+1 até hoje)** | Refazer último dia sempre | Evita duplicatas; mais eficiente em volume |
| **Validação com threshold 10%** | Sem validação / validação simples | Detecta anomalias (erro de PBI, mudança de período); threshold 10% é conservador |
| **Retry 3x com backoff** | Fail-fast / best-effort | Cobre glitches temporários; não entope logs com falsos positivos |
| **Reusar state.json de dashboard-inova-data-export** | Auth MSAL device-code própria | State já existe; reduz complexidade; mantém autenticação sincronizada |
| **Integração com recency_status.md + generate_recency_report.py** | Logging isolado | Alinha com padrão Inova (M0-M5); governança unificada |

---

## 6. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| **PBI desatualiza layout/selectors** | Média | Alto | Monitoramento diário de logs; fallback para seletores alternativos em código |
| **State.json expira ou não sincroniza com dashboard-inova-data-export** | Baixa | Alto | Implementar fallback para device-code MSAL; refresh automático a cada 7 dias |
| **Timeout (scrape > 5 min)** | Baixa | Médio | Retry com backoff; logs detalhados; alertar se > 3 falhas consecutivas |
| **Threshold de validação muito restritivo** | Baixa | Médio | Monitorar histórico de variações; ajustar threshold trimestralmente se necessário |
| **Duplicatas ao carregar incrementalmente** | Muito Baixa | Alto | Validação de chaves primárias (CNPJ + Data + Nota Fiscal) antes de concatenar |

---

## 7. Dependências Externas

- **Power BI:** Relatório em `https://grupoinova.powerembedded.com.br/Organization/ff465635-ed04-49c0-8180-ba6ee10f2104/Report/fae8ab2e-8f74-4617-8aae-3383d8a4ba8c`
- **dashboard-inova-data-export:** `.browser_state/state.json` (compartilhado)
- **shared/:** `recency_status.md` + `generate_recency_report.py`
- **Python libs:** Playwright, pandas, pyarrow, logging

---

## 8. Próximos Passos (Implementação)

1. **Setup da estrutura** — criar `src/`, `.browser_state/`, `docs/specs/`, etc.
2. **Implementar módulos core** — `config.py`, `extract.py`, `transform.py`, `load.py`
3. **Testes unitários** — validação de limpeza, schema, I/O
4. **Testes de integração** — scrape mock, pipeline end-to-end
5. **Integração com governança** — atualizar `generate_recency_report.py`
6. **Task agendada** — criar task que roda `run.py --ano 2026` diariamente
7. **Documentação final** — runbook de manutenção, troubleshooting

---

**FIM DA ESPECIFICAÇÃO**
