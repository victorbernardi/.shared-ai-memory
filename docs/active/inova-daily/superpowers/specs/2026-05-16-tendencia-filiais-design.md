# Spec: Tendência por Filial — H1.3

**Data:** 2026-05-16  
**Roadmap:** H1 — Item 1.3  
**Estimativa:** 1 dia

## Contexto

`foto_ontem()` hoje retorna `top_filiais` (top 3, dict `{nome: receita}`). O email exibe apenas receita absoluta. O objetivo é substituir por ranking completo de todas as filiais ativas no dia, com comparação vs média diária do mês corrente.

## Objetivo

Mostrar no email todas as filiais ordenadas por receita de ontem, cada uma com sua média diária do mês e o desvio percentual — para identificar filiais em queda ou aceleração em relação ao padrão mensal.

## Design

### Fonte de dados

Tudo calculado a partir do M2 (cache parquet) — sem query nova ao Fabric:

- **Receita de ontem por filial:** `df_dia_m2.groupby("FILIAL")["VALOR_DO_PRODUTO"].sum()`
- **Acumulado do mês por filial:** `df_mes.groupby("FILIAL")["VALOR_DO_PRODUTO"].sum()`  
  (`df_mes` já carregado em `foto_ontem()` via `fat.por_mes()`)
- **Média diária por filial:** `acumulado_filial / dias_corridos`  
  (`dias_corridos` já calculado em `foto_ontem()`)

### Estrutura de dados retornada

`foto_ontem()` passa a retornar `filiais_ranking` em vez de `top_filiais`:

```python
"filiais_ranking": [
    {
        "nome": "Contagem",       # str — via FILIAL_MAP
        "ontem": 513_494.26,      # float
        "media_dia": 458_000.0,   # float — acumulado_mes_filial / dias_corridos
        "delta_pct": 12.1,        # float — pode ser negativo
    },
    ...  # todas as filiais com receita > 0 no dia, ordenadas por ontem desc
]
```

Filiais com receita zero em `df_dia_m2` são excluídas do ranking.  
`media_dia = 0` quando filial não aparece no mês → `delta_pct = 0.0` (evita divisão por zero).

### Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/faturamento.py` | +`receita_por_filial(df) -> dict[str, float]`: groupby FILIAL sem limite de n |
| `src/snapshot_diario.py` | Substituir cálculo de `top_fil` por `filiais_ranking` (lista de dicts) |
| `src/generator.py` | +`_filiais_ranking_md()` → formata cada linha; substituir uso de `snap_top_filiais` por `snap_filiais_ranking` |
| `templates/email_template_v3.md` | `{{ snap_top_filiais }}` → `{{ snap_filiais_ranking }}`; label "Top filiais:" → "Filiais *(por receita de ontem)*:" |

### Formato no email

```
**Filiais** *(por receita de ontem)*:
1. Contagem: R$ 513.494 | média do mês: R$ 458.000 (+12,1%)
2. Uberlândia: R$ 70.797 | média do mês: R$ 95.200 (-25,6%)
3. Serra: R$ 30.031 | média do mês: R$ 28.400 (+5,7%)
4. Tanguá: R$ 18.200 | média do mês: R$ 21.000 (-13,3%)
```

### `_filiais_ranking_md()` em `generator.py`

```python
def _filiais_ranking_md(filiais: list[dict]) -> str:
    linhas = []
    for i, f in enumerate(filiais, 1):
        sinal = "+" if f["delta_pct"] >= 0 else ""
        linhas.append(
            f"{i}. **{f['nome']}:** R$ {_brl(f['ontem'])} "
            f"| média do mês: R$ {_brl(f['media_dia'])} "
            f"({sinal}{f['delta_pct']:.1f}%)"
        )
    return "\n".join(linhas)
```

## Testes

- `test_faturamento.py` — `receita_por_filial()` retorna dict com todas as filiais, sem limite
- `test_snapshot_diario.py`:
  - `filiais_ranking` presente no dict de retorno
  - Ordenado por `ontem` desc
  - `delta_pct` calculado corretamente
  - Filial com `media_dia = 0` → `delta_pct = 0.0`
- `test_generator.py` — `_filiais_ranking_md()` formata linha corretamente com sinal e percentual

## Fora de escopo

- Filiais com receita zero no dia não aparecem no ranking
- Não há threshold de alerta (isso é H4)
- Não há histórico de N dias (isso é H2.3)
