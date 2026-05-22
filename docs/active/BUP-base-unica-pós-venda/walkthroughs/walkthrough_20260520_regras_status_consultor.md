# Walkthrough — Refatoração das Regras de Status e Consultor (2026-05-20)

## Contexto

Sessão de diagnóstico e correção das colunas `Status_Oportunidade` e `Consultor` do BUP pós-venda.
Ponto de partida: clientes com compra recente aparecendo com `Consultor = CEVAP`.

---

## Bugs Encontrados

### Bug 1 — Filtro de filial restritivo demais na query `LastSalesActive`

**Sintoma:** COMPANHIA BRAS. DE MET. E MINERACAO (`Consultor = CEVAP`) com compra há 13 dias.

**Causa:** A query filtrava `f.F2_FILIAL IN ('0201', '0301')`. A CBMM compra pela filial `0204`, que era excluída silenciosamente.

**Fix:** `(f.F2_FILIAL LIKE '02%' OR f.F2_FILIAL LIKE '03%')` — igual ao critério já aplicado nos orçamentos.

**Aprendizado:** Filtros hard-coded de filial são uma bomba-relógio. A filial dos orçamentos já estava certa; a das vendas estava desatualizada e ninguém percebeu.

---

### Bug 2 — `Dias_Inativo` calculado sobre qualquer venda, não só de consultores ativos

**Sintoma:** Cliente com compra recente (< 90 dias) por consultor de outro departamento recebia `Status = CONVERSÃO: COMPRA` mas `Consultor = CEVAP` — contradição.

**Causa:** `Dias_Inativo` era calculado a partir de `Ultima_Compra` do parquet M3 (qualquer venda do ERP), enquanto `Consultor_Ultima_Venda` só vinha de vendas por consultores da lista ativa 2026. As duas fontes eram inconsistentes.

**Fix:** `Dias_Inativo` passou a ser calculado a partir de `DT_Ultima_Venda_Ativa`, derivada da query `LastSalesActive` (que já filtra por consultor ativo). Se o cliente nunca teve venda por consultor ativo, `Dias_Inativo = 999`.

**Aprendizado:** Nunca use duas fontes diferentes para calcular condições que dependem uma da outra. "Comprou recentemente" e "tem consultor ativo" devem derivar do mesmo dataset.

---

### Bug 3 — `Status_Oportunidade` e `Consultor` calculados de forma independente

**Sintoma:** Possível ter `Status = CONVERSÃO: COMPRA` com `Consultor = CEVAP`.

**Causa:** As duas colunas eram calculadas em blocos separados sem sincronismo:

- `Consultor` era definido pela função `atribuir_consultor_bup_final` (regras próprias)
- `Status_Oportunidade` era definido por outro bloco (regras próprias)
- Nenhum dos dois verificava o resultado do outro

**Fix:** Unificação em uma única função pura `calcular_status_e_consultor()` que retorna `(status, consultor)` sempre consistentes. `PENDENTE: INATIVO` implica `CEVAP` — garantido estruturalmente, não por convenção.

**Aprendizado:** Duas colunas derivadas das mesmas regras de negócio devem ser calculadas juntas, por uma única função com uma única decisão.

---

### Bug 4 — Coluna `Consultor_Ultima_Venda` inicializada com `None` antes do merge

**Sintoma:** `CONVERSÃO: COMPRA = 0` no output após todas as correções acima. CBMM ainda aparecia como `CONVERSÃO: ORÇAMENTO` mesmo com `Dias_Inativo = 1`.

**Causa:** A linha `df_cevap['Consultor_Ultima_Venda'] = None` (pré-existente, linha 289) criava a coluna antes do merge. Quando o merge acontecia, pandas detectava conflito de nomes e criava `Consultor_Ultima_Venda_x` (todos `None`) e `Consultor_Ultima_Venda_y` (com os nomes reais). A função `aplicar_status_e_consultor` lia a coluna `Consultor_Ultima_Venda` que não existia mais — `row.get()` retornava `None`.

**Este bug era pré-existente** e mascarado porque a rota de orçamento às vezes resgatava o consultor correto por outro caminho.

**Fix:** Remover a inicialização de `Consultor_Ultima_Venda` (e `Consultor_Orcamento`) antes do merge. As colunas são criadas pelo próprio merge.

**Aprendizado:** Nunca inicialize uma coluna que vai ser populada por um merge subsequente com o mesmo nome. É um erro silencioso — o código roda sem exceção, mas lê dados errados.

---

### Bug 5 — Regra de orçamento com data limite desnecessária

**Sintoma (design):** Orçamento `ABERTO` com data > 90 dias não gerava `CONVERSÃO: ORÇAMENTO`.

**Causa:** O bloco de status checava `df_orc_aberto['Data Abertura'] >= limit_date_90d` — descartava orçamentos abertos "antigos".

**Fix:** Orçamento `ABERTO` → `CONVERSÃO: ORÇAMENTO` independente da data. A lógica de 90 dias se aplica apenas a orçamentos `FECHADO/CANCELADO`.

---

## O que Eu Errei

| Erro | O que deveria ter feito |
|---|---|
| Não detectei o Bug 4 (merge conflict) antes de rodar o script | Verificar `df.columns.tolist()` após cada merge durante desenvolvimento |
| Validei o output só após rodar — `CONVERSÃO: COMPRA = 0` precisou de uma segunda rodada | Adicionar assertion pós-merge: `assert 'Consultor_Ultima_Venda' in df.columns` |
| A discussão das regras de negócio tomou muitas rodadas antes de chegar ao modelo mental correto | Escrever a tabela de decisão (prioridade 1/2/3) antes de qualquer código |

---

## O que Funcionou

- **TDD:** A função `calcular_status_e_consultor` foi extraída, testada com 14 casos antes de tocar o script principal. Isso garantiu que a lógica estava correta independentemente dos problemas de pipeline (merge, etc.).
- **Auditoria no Fabric:** Rodar a query sem filtros para a CBMM revelou exatamente qual filtro falhava (filial), sem precisar adivinhar.
- **Diagnóstico incremental:** Confirmar o problema da coluna `_x/_y` com um script de 5 linhas antes de alterar o código.

---

## Como Não Cometer os Mesmos Erros

### Regra 1 — Assertions pós-merge

```python
df = pd.merge(df, df_right[['key', 'col_nova']], on='key', how='left')
assert 'col_nova' in df.columns, f"Merge falhou — colunas: {df.columns.tolist()}"
assert 'col_nova_x' not in df.columns, "Conflito de coluna detectado no merge"
```

### Regra 2 — Nunca inicialize uma coluna que o merge vai criar

```python
# ERRADO
df['Consultor_Ultima_Venda'] = None  # cria conflito _x/_y no merge
df = pd.merge(df, df_right[['key', 'Consultor_Ultima_Venda']], ...)

# CERTO
df = pd.merge(df, df_right[['key', 'Consultor_Ultima_Venda']], ...)
# Se o merge pode não acontecer (df_right is None), inicialize DEPOIS:
if 'Consultor_Ultima_Venda' not in df.columns:
    df['Consultor_Ultima_Venda'] = None
```

### Regra 3 — Colunas co-dependentes = função única

Se duas colunas derivam das mesmas regras de negócio, elas devem ser calculadas por uma única função que retorna ambas. Nunca calcular separadamente e esperar consistência.

### Regra 4 — Validar invariantes no output

```python
# Adicionar ao final do script, antes de salvar
inconsistentes = df[(df['Status_Oportunidade'].str.contains('CONVERSÃO')) & (df['Consultor'] == 'CEVAP')]
assert inconsistentes.empty, f"{len(inconsistentes)} clientes com CONVERSÃO+CEVAP — bug nas regras"
```

---

## Como Melhorar o Projeto

### Imediato

1. **Adicionar assertion de invariante no `consolidate_bup.py`** antes do `df_cevap.to_excel(...)`:

   ```python
   inc = df_cevap[(df_cevap['Status_Oportunidade'].str.contains('CONVERSÃO')) & (df_cevap['Consultor'] == 'CEVAP')]
   assert inc.empty, f"ERRO: {len(inc)} clientes com Status=CONVERSÃO e Consultor=CEVAP"
   ```

2. **Adicionar assertion após cada merge crítico** para detectar conflito de colunas.

3. **Adicionar teste de integração** que roda `calcular_status_e_consultor` sobre um DataFrame simulado end-to-end e verifica os invariantes.

### Médio prazo

1. **Extrair mais lógica pura do `consolidate_bup.py`** para módulos testáveis (`scripts/`). O script principal deveria ser só orquestração (extract → transform → load), não lógica de negócio.

2. **Centralizar a definição de "consultor ativo"** — hoje o filtro `F2_VEND1 IN (...)` está inline na query SQL. Se os IDs ativos mudarem, há risco de esquecer de atualizar. Uma função `ids_ativos_sql()` tornaria isso explícito.

3. **Testar o filtro de filial contra o cadastro real** — um teste que verifica se as filiais retornadas pela query estão todas no padrão `0[23]XX` evitaria regressão silenciosa.

### Longo prazo

1. **Separar o `consolidate_bup.py` em `extract.py`, `transform.py`, `load.py`, `run.py`** seguindo o padrão ETL do `CLAUDE.md`. A lógica de negócio ficaria em `transform.py`, completamente testável sem conexão com o Fabric.

---

## Resultado Final

| Métrica | Antes | Depois |
|---|---|---|
| `CONVERSÃO: COMPRA` | 0 (bug) | 1.038 |
| `CONVERSÃO: ORÇAMENTO` | 799 | 241 |
| `PENDENTE: INATIVO` | 16.682 | 16.202 |
| Inconsistências `CONVERSÃO + CEVAP` | desconhecido | **0** |
| Testes cobrindo as regras | 0 | **14** |
| CBMM (`Consultor`) | `CEVAP` | `TOMAZ LOYOLA ZEI` ✓ |
