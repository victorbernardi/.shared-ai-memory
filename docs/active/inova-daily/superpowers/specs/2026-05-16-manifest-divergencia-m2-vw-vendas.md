# Spec: Manifest de Divergência M2 vs vw_VENDAS

**Data:** 2026-05-16  
**Roadmap:** H1 — Item 1.2  
**Estimativa:** 2h

## Contexto

`foto_ontem()` em `snapshot_diario.py` já consulta duas fontes para o mesmo dia:

- **M2** (`cache_vendas_rfm.parquet`) — fonte de verdade para totais; aplica `TES_ALL_VALID`
- **vw_VENDAS** (Fabric SQL live) — usada para `NOME_VENDEDOR`; aplica o mesmo `TES_ALL_VALID`

Por usarem o mesmo filtro TES, deveriam retornar o mesmo total de `VALOR_DO_PRODUTO`. Divergência > 0.05% indica que o cache M2 não foi atualizado antes do `run_daily.py`.

## Objetivo

Detectar automaticamente quando M2 está desatualizado e notificar o leitor do email com uma linha de aviso condicional.

## Design

### 1. `snapshot_diario.foto_ontem()` — calcular divergência

Após construir `df_vw`, calcular:

```python
vw_total = float(df_vw["RECEITA"].sum()) if not df_vw.empty else 0.0
divergencia_pct = abs((vw_total - total) / total * 100) if total > 0 else 0.0
```

Adicionar ao dict de retorno:

```python
"m2_total": total,
"vw_total": vw_total,
"divergencia_pct": divergencia_pct,
```

### 2. `auditor.registrar_execucao()` — gravar no JSONL

Os campos `m2_total`, `vw_total`, `divergencia_pct` já chegam via `snapshot` dict. Incluí-los na linha JSONL de cada execução em `data/audit/audit_YYYYMMDD.jsonl`.

### 3. `generator.py` — nota condicional no email

Se `snapshot["divergencia_pct"] > 0.05`, injetar no rodapé do email (antes da linha `*Gerado automaticamente*`):

```
⚠️ Atenção: M2 pode estar desatualizado — divergência de {X:.1f}% em relação ao banco ao vivo.
```

Se `≤ 0.05%`, silêncio total — nenhuma linha adicionada.

### 4. `templates/email_template_v3.md` — placeholder opcional

Adicionar `{{ aviso_divergencia }}` no rodapé, antes da linha de geração. O generator injeta a string de aviso ou string vazia.

## Threshold

| Divergência | Ação |
|---|---|
| ≤ 0.05% | Nenhuma (silêncio) |
| > 0.05% | Nota no email + campo no JSONL |

O valor 0.05% é a margem estatística esperada para arredondamentos de float. Qualquer coisa acima indica staleness do cache.

## Arquivos Modificados

| Arquivo | Mudança |
|---|---|
| `src/snapshot_diario.py` | +3 campos no dict de retorno |
| `src/auditor.py` | +3 campos no JSONL |
| `src/generator.py` | lógica condicional de aviso |
| `templates/email_template_v3.md` | `{{ aviso_divergencia }}` no rodapé |

## Testes

- `test_snapshot_diario.py` — mock `df_vw` com total diferente de `m2_total`; verificar que `divergencia_pct` é calculado corretamente
- `test_auditor.py` — verificar que campos aparecem no JSONL
- `test_generator.py` — snapshot com `divergencia_pct=1.0` gera aviso; com `divergencia_pct=0.01` não gera

## Fora de Escopo

- Não recalcular totais por vendedor com M2 (não tem `NOME_VENDEDOR`)
- Não bloquear execução se M2 divergir (apenas aviso)
- Não alterar a lógica de escolha de fonte
