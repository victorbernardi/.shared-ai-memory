# Spec — Bloco 2: Eficiência Operacional

**Data:** 2026-05-18
**Projeto:** Apresentação Roberto 18/05
**Escopo:** Bloco 2 de 3

---

## Objetivo

Gerar análise comparativa Jan-Abr 2025 vs Jan-Abr 2026 do faturamento líquido por filial, métricas de eficiência por consultor e por filial (clientes distintos e ticket médio), e mix de grupos de peças. Saída em Markdown narrativo e JSON estruturado para uso no PPT.

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
| 5 | `filial` | breakdown por loja |
| 2 | `grupo` | mix de peças |
| 9 | `consultor` | clientes e ticket médio |
| 10 | `cod_cliente` | contagem de clientes distintos |
| 14 | `liquido` | valor líquido |

---

## Regras de Classificação

### Marca da Filial

- **Wirtgen:** filial começa com `03` (ex: `0301 - Contagem`, `0302 - Pompéu`)
- **John Deere:** demais filiais (prefixo `02`)

### Filiais Conhecidas

| Código | Nome | Marca |
|---|---|---|
| 0201 - Contagem | Contagem | John Deere |
| 0202 - Tanguá | Tanguá | John Deere |
| 0203 - Serra | Serra | John Deere |
| 0204 - Uberlândia | Uberlândia | John Deere |
| 0210 - Pouso Alegre | Pouso Alegre | John Deere |
| 0211 - CRC | CRC | John Deere |
| 0212 - CSN | CSN | John Deere |
| 0301 - Contagem | Contagem Wirtgen | Wirtgen |
| 0302 - Pompéu | Pompéu | Wirtgen |

### Grupos de Peças

Valores diretos do campo `grupo` (col 2): `FILTROS`, `LUBRIFICANTE`, `FPS`, `RODANTE`, `BATERIA`. Linhas com grupo vazio ou nulo classificadas como `OUTROS`.

---

## Métricas

### Filiais

- `fat_2025`, `fat_2026`, `var_pct`, `share_2026` (% do total geral Inova)
- `marca` (John Deere ou Wirtgen)

### Consultores

- `fat_2025`, `fat_2026`, `var_pct`
- `n_clientes_2026` — count de `cod_cliente` distintos em 2026
- `ticket_medio_2026` — `fat_2026 / count(NFs distintas em 2026)` onde cada linha é uma NF

### Eficiência por Filial

- `n_clientes_2026` — count de `cod_cliente` distintos em 2026
- `ticket_medio_2026` — `fat_2026 / count(NFs distintas em 2026)`

### Grupos de Peças

- `fat_2025`, `fat_2026`, `var_pct`, `share_2026` (% do total geral)

---

## Outputs

### `bloco2.md` — Documento narrativo

Estrutura em prosa, sem tabelas. Seções:

1. **Filiais** — parágrafo por filial com fat_2025, fat_2026, var%, share. Destaques automáticos: maior crescimento, maior queda, maior share.
2. **Consultores** — parágrafo por consultor com fat, n_clientes, ticket_médio. Destaques: maior faturamento, maior ticket médio, mais clientes.
3. **Eficiência por Filial** — parágrafo por filial com n_clientes e ticket_médio.
4. **Mix de Peças** — parágrafo por grupo com fat_2025, fat_2026, var%, share. Destaque: grupo dominante, maior crescimento.

Comentários automáticos gerados pelo script com base nos números. Comentários de negócio aprofundados adicionados manualmente após geração.

### `bloco2.json` — Estrutura para PPT

```json
{
  "periodo": "Jan-Abr 2025 vs Jan-Abr 2026",
  "filiais": [
    {
      "filial": "0201 - Contagem",
      "marca": "John Deere",
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "share_2026": 0.0,
      "n_clientes_2026": 0,
      "ticket_medio_2026": 0.0
    }
  ],
  "consultores": [
    {
      "consultor": "Nome",
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "n_clientes_2026": 0,
      "ticket_medio_2026": 0.0
    }
  ],
  "grupos": [
    {
      "grupo": "FILTROS",
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "share_2026": 0.0
    }
  ]
}
```

---

## Script

**Arquivo:** `src/bloco2.py`
**Execução:** `python src/bloco2.py` (rodar da raiz do projeto)

**Funções:**

| Função | Responsabilidade |
|---|---|
| `load_and_clean(file)` | Lê Excel, renomeia por posição (cols 2,4,5,9,10,14), filtra nf.notna() |
| `_var_pct(a, b)` | Calcula variação percentual com proteção contra divisão por zero |
| `aggregate_filiais(df25, df26)` | Agrupa por filial, calcula fat + var% + share + n_clientes + ticket_médio |
| `aggregate_consultores(df25, df26)` | Agrupa por consultor, calcula fat + var% + n_clientes + ticket_médio |
| `aggregate_grupos(df25, df26)` | Agrupa por grupo, calcula fat + var% + share |
| `aggregate(df25, df26)` | Orquestra as 3 agregações, retorna dict único |
| `render_markdown(agg)` | Gera texto narrativo com comentários automáticos |
| `render_json(agg)` | Serializa para JSON |
| `main()` | Lê Excel, chama aggregate, salva bloco2.md e bloco2.json |

---

## Testes

**Arquivo:** `tests/test_bloco2.py`

Cobertura mínima:

- `test_load_and_clean` — filtra linha de totalização, retorna colunas corretas
- `test_aggregate_filiais_structure` — resultado tem chaves esperadas, math correto
- `test_aggregate_consultores_ticket_medio` — ticket_médio = fat / n_NFs
- `test_aggregate_grupos_structure` — grupos reconhecidos, share soma 100%
- `test_render_json_structure` — JSON tem chaves filiais, consultores, grupos
- `test_render_markdown_sections` — Markdown contém seções Filiais, Consultores, Mix de Peças

---

## O que está fora do escopo deste bloco

- Abertura por canal dentro de cada filial (Bloco 1)
- Auditoria de carteiras herdadas / migração de consultores (Bloco 3)
- Subgrupos de peças (col 3) — apenas grupos (col 2)
- Comparativo consultor × filial cruzado
