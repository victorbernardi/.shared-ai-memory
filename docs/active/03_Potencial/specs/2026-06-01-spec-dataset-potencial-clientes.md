# Spec: dataset_ouro_potencial_clientes

**Data:** 2026-06-01
**Motor:** 03_Potencial
**Status:** Aprovada

---

## 1. Objetivo

Criar `dataset_ouro_potencial_clientes` — visão de potencial no **nível cliente individual** (por CNPJ + NOME_CLIENTE), em contraste com `dataset_ouro_potencial_v1` que está no nível grupo econômico.

Permite que M4 e M5 consumam o potencial por cliente individual e façam o agrupamento por grupo econômico usando `CNPJ_GRUPO`.

---

## 2. Contexto e Motivação

`dataset_ouro_potencial_v1` está em produção agregado por `CNPJ_GRUPO` (nível grupo econômico). Não pode ser alterado sem impacto conhecido em M4 e M5.

O novo dataset não substitui o anterior — coexiste com ele até validação e migração dos motores downstream.

**Problema identificado:** a coluna `Customer` no `dataset_ouro_potencial_chassi_v1` retorna o nome do grupo econômico (vindo de `Nome Dono Oficial` do M1), não o nome do cliente individual. Esse problema será corrigido no M1 em sessão separada. Quando M1 for corrigido, `NOME_CLIENTE` passará a refletir o nome individual automaticamente, sem nenhuma alteração adicional no M3.

---

## 3. Requisitos Funcionais

### 3.1 Granularidade

Uma linha por `CNPJ` + `NOME_CLIENTE` (cliente individual).

### 3.2 Colunas de saída

| Coluna | Origem | Regra |
|---|---|---|
| `NOME_CLIENTE` | `Customer` do chassis | `first()` — técnico (todos os chassis do mesmo CNPJ já têm o mesmo valor) |
| `CNPJ` | `CNPJ` do chassis | chave de agrupamento |
| `CNPJ_GRUPO` | M0 via `_injetar_m0` | `first()` — técnico (mesmo valor para todos os chassis do CNPJ) |
| `Razao_Social_Grupo` | M0 via `_injetar_m0` | `first()` — técnico (mesmo valor para todos os chassis do CNPJ) |
| `Qtd_Maquinas` | contagem de PINs | `count` |
| `Horimetro_Medio` | média de `Horimetro_Final` | `mean` |
| `Potencial Peças Anual` | soma | `sum` |
| `Potencial Proporcional` | soma de `Potencial Total Proporcional` | `sum` |
| `Potencial Total` | soma de `Potencial Total Anual` | `sum` |
| `Potencial Pneus Anual` | soma | `sum` |
| `Potencial Material Rodante Anual` | soma | `sum` |
| `Potencial Lubrificantes Anual` | soma | `sum` |
| `Potencial Peças de Desgaste Anual` | soma | `sum` |

### 3.3 Arquivos gerados

| Arquivo | Local |
|---|---|
| `dataset_ouro_potencial_clientes.parquet` | `shared/data/` e `data/` |
| `dataset_ouro_potencial_clientes.xlsx` | `data/` |

---

## 4. Requisitos Não-Funcionais

- Nenhuma alteração em `dataset_ouro_potencial_v1` ou `dataset_ouro_potencial_chassi_v1`
- Nenhuma alteração em M0, M1, M4 ou M5
- O novo dataset deve ser gerado na mesma execução do M3 (`run.py`) sem etapas adicionais

---

## 5. Design Técnico

### 5.1 Onde implementar

- **`03_Potencial/transform.py`** — função `build_exports`: adicionar geração de `df_potencial_clientes`
- **`03_Potencial/load.py`** — função `save`: adicionar persistência do novo dataset
- **`03_Potencial/run.py`** — passar `df_potencial_clientes` para `save`

### 5.2 Lógica de agrupamento

```python
df_potencial_clientes = (
    df.groupby(["CNPJ", "Customer"])
    .agg(
        NOME_CLIENTE=("Customer", "first"),
        CNPJ_GRUPO=("CNPJ_GRUPO", "first"),
        Razao_Social_Grupo=("Razao_Social_Grupo", "first"),
        Qtd_Maquinas=("PIN", "count"),
        Horimetro_Medio=("Horimetro_Final", "mean"),
        Potencial_Pecas_Anual=("Potencial Peças Anual", "sum"),
        Potencial_Pneus_Anual=("Potencial Pneus Anual", "sum"),
        Potencial_Mat_Rodante_Anual=("Potencial Material Rodante Anual", "sum"),
        Potencial_Lubrificantes_Anual=("Potencial Lubrificantes Anual", "sum"),
        Potencial_Desgaste_Anual=("Potencial Peças de Desgaste Anual", "sum"),
        Potencial_Total_Anual=("Potencial Total Anual", "sum"),
        Potencial_Total_Proporcional=("Potencial Total Proporcional", "sum"),
    )
    .reset_index(drop=True)
)
```

Colunas finais na ordem:
`NOME_CLIENTE`, `CNPJ`, `CNPJ_GRUPO`, `Razao_Social_Grupo`, `Qtd_Maquinas`, `Horimetro_Medio`, `Potencial Peças Anual`, `Potencial Proporcional`, `Potencial Total`, `Potencial Pneus Anual`, `Potencial Material Rodante Anual`, `Potencial Lubrificantes Anual`, `Potencial Peças de Desgaste Anual`

### 5.3 Retorno de build_exports

`build_exports` passa a retornar 5 valores (antes: 4):

```python
return df_chassi, df_cliente, df_potencial_clientes, df_feedback, auditoria
```

---

## 6. Plano de Validação

| Verificação | Critério |
|---|---|
| Sem PINs duplicados por cliente | `df_potencial_clientes.groupby(["CNPJ","NOME_CLIENTE"])["Qtd_Maquinas"].sum()` deve igualar contagem do chassis |
| Potencial Total consistente | Soma de `Potencial Total` no novo dataset ≈ soma no `dataset_ouro_potencial_v1` |
| CNPJ_GRUPO correto | Cruzar amostra com M0 e confirmar que `CNPJ_GRUPO` bate |
| CSN como caso de teste | Grupo `08902291` deve aparecer com linhas distintas por subsidiária |

---

## 7. Log de Decisões

| Decisão | Alternativas consideradas | Motivo |
|---|---|---|
| Novo arquivo, não substituição | Modificar `dataset_ouro_potencial_v1` | Impacto desconhecido em M4/M5 em produção |
| Agrupar por `CNPJ + Customer` | Agrupar só por `CNPJ` | `Customer` pode ser diferente para mesmo CNPJ em casos de inconsistência de dados |
| `first()` para `CNPJ_GRUPO`/`Razao_Social_Grupo` | Qualquer outra função | Técnico — todos os chassis do mesmo CNPJ têm o mesmo valor por definição do M0 |
| Renomear `Customer` → `NOME_CLIENTE` | Manter `Customer` | Nomenclatura em PT-BR alinhada ao padrão Inova |
| Implementar em sandbox primeiro | Direto em produção | Motor em produção — validar antes de alterar qualquer comportamento existente |

---

## 8. Caminho de Migração

1. ✅ **Esta spec** — criar `dataset_ouro_potencial_clientes` no M3
2. ⏳ **Validação** — comparar com `dataset_ouro_potencial_v1`, validar caso CSN
3. ⏳ **M1** — corrigir `Nome Dono Oficial` para retornar nome individual (sessão separada)
4. ⏳ **M4/M5** — migrar para ler `dataset_ouro_potencial_clientes` após validação
