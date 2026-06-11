---
id: spec-horimetro-staleness
stage: 03_Potencial
date: 2026-05-29
status: approved
author: Victor Bernardi
---

# Spec: Detecção e Reclassificação de Horímetro Defasado

## 1. Objetivo

Corrigir a classificação `STATUS_USO = "REAL"` para máquinas cujo horímetro não é atualizado há mais de 120 dias. Atualmente, qualquer máquina com `Forecasted Machine Hours >= 10` recebe REAL — sem verificar a recência da leitura. Isso distorce o potencial calculado.

## 2. Problema

- A coluna `AOR Last Location Date` do POPS informa a última atualização do horímetro
- O critério atual ignora essa data: uma leitura de 2 anos atrás ainda resulta em `STATUS_USO = "REAL"`
- Máquinas sem manutenção há >4 meses são candidatas a leads de peças — mas o horímetro defasado mascara isso

## 3. Escopo

### Em Escopo

- Script sandbox read-only de validação estatística (`sandbox_horimetro_staleness.py`)
- Constante `HORIMETRO_STALE_THRESHOLD_DAYS` em `shared/config.py`
- Lógica `Dias_Desde_Horimetro` em `_preparar_pops`
- Expansão do critério de `STATUS_USO` em `_imputar_horimetro`
- Exportação de `Dias_Desde_Horimetro` no dataset chassi

### Fora do Escopo (CON-006)

- Extrapolação linear do horímetro com base na taxa histórica
- Criação de novo status `"PROJETADO"` ou `"STALE"`
- Alteração de lógica nos stages M4 ou M5
- Retreinamento de modelos preditivos de uso

## 4. Requisitos Funcionais

| ID     | Descrição | Implements |
|--------|-----------|------------|
| FR-001 | O sandbox SHALL calcular e exportar para `analise_a_distribuicao.csv`: média, mediana, desvio padrão, skewness e outliers (Tukey) dos horímetros `STATUS_USO = "REAL"`, agrupados por `Model Grupo` | AC-1 |
| FR-002 | O sandbox SHALL classificar cada máquina `STATUS_USO = "REAL"` em RECENTE (≤ 120 dias), DEFASADA (> 120 dias) ou NULA (data ausente), calculando volume (absoluto e %), potencial atual, potencial com mediana e delta R$, exportando para `analise_b_impacto_corte.csv` | AC-1, AC-2 |
| FR-003 | O sandbox SHALL calcular, para cada `Model Grupo`, o teste Mann-Whitney U (RECENTE × DEFASADA), a cobertura de máquinas RECENTES e a flag `MEDIANA_CONFIAVEL`, exportando para `analise_c_validacao_cruzada.csv` | AC-3, AC-4 |
| FR-004 | O arquivo `shared/config.py` SHALL declarar `HORIMETRO_STALE_THRESHOLD_DAYS = 120` como constante nomeada | NFR-001 |
| FR-005 | A função `_preparar_pops` SHALL parsear `aorLastLocationDate` como datetime, calcular `Dias_Desde_Horimetro = (hoje - data).days` e atribuir `999` a registros com data nula | AC-7 |
| FR-006 | A função `_imputar_horimetro` SHALL classificar cada máquina em RECENTE / DEFASADA / ZERADO e imputar o horímetro conforme a Seção 4.1 (Opção A: cada coorte usa a própria mediana) | AC-5, AC-6 |
| FR-007 | A função `build_exports` SHALL incluir a coluna `Dias_Desde_Horimetro` no dataset chassi de saída | AC-7 |

### 4.1 Imputação por Coorte (Opção A — aprovada no gate 2026-05-29)

`_imputar_horimetro` classifica cada máquina em três categorias e imputa o horímetro com fontes de mediana distintas:

| Categoria | Critério | STATUS_USO | Horímetro imputado | METODO_HORIMETRO |
|-----------|----------|------------|--------------------|------------------|
| RECENTE | leitura ≤ 120 dias (não zerada) | REAL | `Horimetro_Anual_Real` (telemetria) | TELEMETRIA |
| DEFASADA | leitura > 120 dias (não zerada) | ESTIMADO | mediana da coorte **DEFASADA** por `Model_Clean` | MEDIANA_DEFASADA |
| ZERADO | `Forecasted Machine Hours < 10` (sem leitura) | ESTIMADO | mediana das **RECENTES** por `Model_Clean`/`Ano_Venda` | MEDIANA |

Após a imputação base, o pathway de oficina (VO1010) existente continua sobrescrevendo qualquer máquina `STATUS_USO = "ESTIMADO"` que tenha OS válida → `METODO_HORIMETRO = "OFICINA"`. Logo as DEFASADAS com histórico de oficina ganham horímetro via dado real de manutenção.

**Justificativa (gate):** a coorte DEFASADA diverge estatisticamente da RECENTE (Mann-Whitney p<0.05 em 6 modelos). Forçar a mediana das RECENTES sobre as DEFASADAS seria incorreto; usar a mediana da própria coorte respeita cada distribuição e dissolve o bloqueio do gate por divergência. Impacto medido: -R$ 9,94M sobre 1.157 máquinas DEFASADAS (-2,3% do potencial REAL total), proveniente de regularizar outliers de leituras travadas.

**Fase futura (não neste escopo):** modelo preditivo de taxa de uso treinado nas RECENTES, validado em holdout vs este baseline de mediana. Ver memória `project_horimetro_modelo_spike`.

## 5. Requisitos Não-Funcionais

| ID      | Requisito | Rationale |
|---------|-----------|-----------|
| NFR-001 | Threshold configurável em `config.py` — zero hardcode na lógica de transformação | Facilita calibragem futura sem tocar em transform.py |
| NFR-002 | Script sandbox é estritamente read-only — não modifica nenhum parquet | Sandbox deve ser seguro para reexecução a qualquer momento |
| NFR-003 | Nulos em `AOR Last Location Date` recebem `Dias_Desde_Horimetro = 999` | Postura conservadora: sem data confirmada = tratar como defasado |
| NFR-004 | Análises do sandbox executáveis independentemente do pipeline principal | Permite validação sem depender de re-execução de M0→M2 |
| NFR-005 | Limiar de `MEDIANA_CONFIAVEL`: `p > 0.05` (Mann-Whitney) AND cobertura_recente ≥ 20% | 20% garante que a mediana seja calculada sobre base estatisticamente representativa; Mann-Whitney é não-paramétrico, adequado para distribuições assimétricas de horímetro |

## 6. Gate entre Fases (CON-004)

**Fase 2 inicia somente após aprovação explícita dos CSVs do sandbox pelo Victor.**

Critério de gate: Victor confirma, após análise de `analise_b_impacto_corte.csv` e `analise_c_validacao_cruzada.csv`, que:

- O delta de potencial é aceitável para o negócio
- Nenhum `Model Grupo` com `N_Recente >= 5` apresenta `MEDIANA_CONFIAVEL = False`

## 7. Critérios de Aceite

| ID   | Critério |
|------|----------|
| AC-1 | Análise B exporta percentual de máquinas DEFASADAS (absoluto e %) por bucket |
| AC-2 | Análise B exporta delta de potencial total R$ antes × depois da reclassificação |
| AC-3 | Análise C calcula flag `MEDIANA_CONFIAVEL` para todos os `Model Grupo` presentes no parquet |
| AC-4 | Nenhum `Model Grupo` com `N_Recente >= 5` apresenta `MEDIANA_CONFIAVEL = False` no resultado do sandbox |
| AC-5 | `assert (df['Potencial Total'] >= 0).all()` continua passando após a implementação |
| AC-6 | `assert not df['PIN'].duplicated().any()` continua passando após a implementação |
| AC-7 | Coluna `Dias_Desde_Horimetro` presente e não nula no `dataset_ouro_potencial_chassi_v1.parquet` |

## 8. Cenários de Teste

| ID    | Cenário | FR |
|-------|---------|-----|
| T-001 | `_preparar_pops` com `aorLastLocationDate` de 200 dias atrás → `Dias_Desde_Horimetro > 120` | FR-005 |
| T-002 | `_preparar_pops` com `aorLastLocationDate = None` → `Dias_Desde_Horimetro == 999` | FR-005 |
| T-003 | `_imputar_horimetro` com `Forecasted Machine Hours = 2000` e `Dias_Desde_Horimetro = 200` → `STATUS_USO = "ESTIMADO"`, `METODO_HORIMETRO = "MEDIANA_DEFASADA"` | FR-006 |
| T-004 | `_imputar_horimetro` com `Forecasted Machine Hours = 2000` e `Dias_Desde_Horimetro = 30` → `STATUS_USO = "REAL"` | FR-006 |
| T-005 | `build_exports` retorna coluna `Dias_Desde_Horimetro` no dataframe chassi | FR-007 |
| T-006 | Suite completa existente (`test_horimetro_oficina.py`) continua passando após as mudanças | FR-006, FR-007 |

## 9. Fonte de Dados

| Fonte | Coluna chave | Uso |
|-------|-------------|-----|
| `Product_details_full.xlsx` | `AOR Last Location Date`, `Serial Number` | Data da última leitura do horímetro |
| `dataset_ouro_potencial_chassi_v1.parquet` | `PIN`, `STATUS_USO`, `Horimetro_Final`, `Model Grupo` | Output existente para join no sandbox |

## 10. Decision Log

| Decisão | Alternativas consideradas | Motivo |
|---------|--------------------------|--------|
| Reclassificar como ESTIMADO (não extrapolar) | Extrapolação linear; novo status PROJETADO | Mediana é mais robusta para máquinas sem histórico de OS; evita complexidade desnecessária |
| Threshold configurável em config.py | Hardcoded 120 dias | Facilita calibragem futura sem tocar na lógica |
| Nulos tratados como DEFASADA | Ignorar nulos; bucket separado | Postura conservadora — sem data = sem garantia de recência |
| Nulos com count separado na Análise B | Misturar com DEFASADA silenciosamente | Visibilidade para governança de dados |
| Sandbox antes da implementação | Implementar direto | Validar que mediana não superestima antes de propagar para M4/M5 |
| 3 análises em sequência (D) | Só impacto (B) | Distribuição e validação cruzada garantem que B não é enganoso |
| Limiar MEDIANA_CONFIAVEL: N_Recente >= 5 | Sem limiar (qualquer N) | Modelos com < 5 amostras recentes têm mediana estatisticamente fraca |
