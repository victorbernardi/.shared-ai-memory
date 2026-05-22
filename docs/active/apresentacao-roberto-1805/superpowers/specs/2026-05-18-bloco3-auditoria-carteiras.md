# Spec — Bloco 3: Auditoria de Carteiras

**Data:** 2026-05-18
**Projeto:** Apresentação Roberto 18/05
**Escopo:** Bloco 3 de 3

---

## Objetivo

Gerar análise comparativa Jan-Abr 2025 vs Jan-Abr 2026 para todos os consultores ativos em 2026: faturamento × clientes × indicadores (ticket médio, var%, share), top 3 grupos de peças por consultor com variação, e auditoria de migração de carteiras (Wenderson→Danilo Neto, Eliane→Danillo Bermudes/Vinicius Lenzi). Saída em Markdown narrativo e JSON estruturado para PPT.

---

## Fontes de Dados

- `Vendas_2025.xlsx` — já filtrado para Jan-Abr 2025
- `Vendas_2026.xlsx` — já filtrado para Jan-Abr 2026
- Leitura por índice posicional (colunas com encoding problemático)
- **CRÍTICO:** filtrar `df[df['nf'].notna()]` antes de qualquer agregação para eliminar linhas de totalização do Excel

**Mapeamento de colunas (posição → nome):**

| Índice | Nome | Uso |
|---|---|---|
| 4 | `nf` | filtro anti-totalização |
| 9 | `consultor` | agrupamento principal |
| 10 | `cod_cliente` | contagem de clientes distintos |
| 14 | `liquido` | valor líquido |
| 2 | `grupo` | top 3 grupos por consultor |

---

## Regras de Normalização

### Nomes de Consultores

- Aplicar `str.title()` em todos os nomes de consultores (`ANDRE BESSAS` → `Andre Bessas`)
- Aplicar antes de qualquer agrupamento para garantir consistência entre os dois anos

### Exclusões

- `Samara Souza` — gerencia carteiras CSN/mineração, excluída da visão por consultor
- Consultores com `fat_2026 == 0` — desligados, excluídos da visão principal

### Grupos de Peças

- Grupo vazio ou nulo → `OUTROS`
- Normalizado para UPPER antes de agrupar

---

## Métricas

### Visão Geral de Consultores

Por consultor (todos com fat_2026 > 0, exceto Samara Souza):

- `fat_2025`, `fat_2026`, `var_pct`
- `n_clientes_2026` — count de `cod_cliente` distintos em 2026
- `ticket_medio_2026` — `fat_2026 / count(NF rows)` em 2026
- `share_2026` — `fat_2026 / total_geral_2026 * 100`

Ordenado por `fat_2026` decrescente.

### Top 3 Grupos por Consultor

Para cada consultor, top 3 grupos de peças por `fat_2026`:

- `grupo`, `fat_2025`, `fat_2026`, `var_pct`

Excluir grupos onde `fat_2026 == 0`.

### Auditoria de Migração de Carteiras

**Migrações configuradas:**

| Legado | Herdeiros |
|---|---|
| Wenderson Silva | Danilo Neto |
| Eliane Gils | Danillo Bermudes, Vinicius Lenzi |

**Para cada migração:**

1. Identificar `clientes_legado_2025` = `cod_cliente` únicos do consultor legado em 2025
2. Para cada cliente em `clientes_legado_2025`, verificar em 2026:
   - `herdado` = comprou com algum dos herdeiros
   - `disperso` = comprou com outro consultor (não herdeiro, não legado)
   - `churn` = não comprou com ninguém (ou só comprou com o próprio legado restante)
3. Calcular:
   - `fat_legado_2025` = total do consultor legado em 2025
   - `fat_herdado_2026` = faturamento dos clientes herdados com os herdeiros em 2026
   - `fat_disperso_2026` = faturamento dos clientes dispersos em 2026 (com outros consultores)
   - `n_clientes_legado` = total de clientes únicos do legado em 2025
   - `n_clientes_herdado` = clientes que migraram para herdeiros
   - `n_clientes_disperso` = clientes que foram para outros consultores
   - `n_clientes_churn` = clientes que sumiram (n_legado - herdado - disperso)

---

## Outputs

### `bloco3.md` — Documento narrativo

Estrutura em prosa, sem tabelas. Seções:

1. **Visão Geral de Consultores** — parágrafo por consultor com fat_2025, fat_2026, var%, n_clientes, ticket_médio, share. Destaques automáticos: maior faturamento, maior ticket médio, maior base de clientes.
2. **Top 3 Grupos por Consultor** — para cada consultor, parágrafo listando os 3 principais grupos com fat_2026 e var%.
3. **Auditoria de Migração de Carteiras** — parágrafo por migração com os indicadores calculados.

Nomes de consultores com `str.title()` no Markdown.

### `bloco3.json` — Estrutura para PPT

```json
{
  "periodo": "Jan-Abr 2025 vs Jan-Abr 2026",
  "consultores": [
    {
      "consultor": "Andre Bessas",
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "n_clientes_2026": 0,
      "ticket_medio_2026": 0.0,
      "share_2026": 0.0
    }
  ],
  "grupos_por_consultor": [
    {
      "consultor": "Andre Bessas",
      "top3": [
        {
          "grupo": "FILTROS",
          "fat_2025": 0.0,
          "fat_2026": 0.0,
          "var_pct": 0.0
        }
      ]
    }
  ],
  "migracao": [
    {
      "legado": "Wenderson Silva",
      "herdeiros": ["Danilo Neto"],
      "fat_legado_2025": 0.0,
      "fat_herdado_2026": 0.0,
      "fat_disperso_2026": 0.0,
      "n_clientes_legado": 0,
      "n_clientes_herdado": 0,
      "n_clientes_disperso": 0,
      "n_clientes_churn": 0
    }
  ]
}
```

---

## Script

**Arquivo:** `src/bloco3.py`
**Execução:** `python src/bloco3.py` (rodar da raiz do projeto)

**Funções:**

| Função | Responsabilidade |
|---|---|
| `load_and_clean(file)` | Lê Excel, renomeia por posição (cols 2,4,9,10,14), filtra nf.notna(), aplica str.title() em consultor |
| `_var_pct(a, b)` | Variação percentual com proteção contra divisão por zero |
| `aggregate_consultores(df25, df26)` | Agrupa por consultor, calcula fat + var% + n_clientes + ticket + share |
| `aggregate_grupos_por_consultor(df25, df26)` | Para cada consultor, top 3 grupos por fat_2026 com var% |
| `aggregate_migracao(df25, df26)` | Calcula herdado/disperso/churn para cada migração configurada |
| `aggregate(df25, df26)` | Orquestra as 3 agregações |
| `render_markdown(agg, periodo)` | Gera texto narrativo com as 3 seções |
| `render_json(agg, periodo)` | Serializa para JSON |
| `main()` | Lê Excel, chama aggregate, salva bloco3.md e bloco3.json |

**Constantes:**

```python
_CONSULTORES_EXCLUIDOS = {'Samara Souza'}

_MIGRACOES = [
    {'legado': 'Wenderson Silva', 'herdeiros': ['Danilo Neto']},
    {'legado': 'Eliane Gils', 'herdeiros': ['Danillo Bermudes', 'Vinicius Lenzi']},
]
```

---

## Testes

**Arquivo:** `tests/test_bloco3.py`

Cobertura mínima:

- `test_load_and_clean_title_case` — consultor normalizado com str.title()
- `test_load_and_clean_filtra_totalizacao` — linha com nf=NaN eliminada
- `test_aggregate_consultores_structure` — chaves esperadas, share soma ~100%
- `test_aggregate_consultores_exclui_samara` — Samara Souza ausente
- `test_aggregate_consultores_exclui_desligados` — consultores com fat_2026==0 ausentes
- `test_aggregate_grupos_por_consultor_top3` — máximo 3 grupos, ordenados por fat_2026
- `test_aggregate_migracao_structure` — chaves esperadas, n_herdado + n_disperso + n_churn == n_legado
- `test_render_markdown_sections` — Markdown contém as 3 seções esperadas
- `test_render_json_structure` — JSON tem chaves consultores, grupos_por_consultor, migracao

---

## O que está fora do escopo deste bloco

- Breakdown por filial dentro de cada consultor (Bloco 2)
- Análise de canal (Bloco 1)
- Subgrupos de peças (col 3) — apenas grupos (col 2)
- Ranking de consultores por filial cruzado
