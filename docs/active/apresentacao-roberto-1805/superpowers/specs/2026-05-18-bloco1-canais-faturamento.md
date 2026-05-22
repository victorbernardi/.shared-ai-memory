# Spec — Bloco 1: Canais de Faturamento × Marca

**Data:** 2026-05-18
**Projeto:** Apresentação Roberto 18/05
**Escopo:** Bloco 1 de 3

---

## Objetivo

Gerar análise comparativa Jan-Abr 2025 vs Jan-Abr 2026 do faturamento líquido por canal e marca, com saída em Markdown narrativo e JSON estruturado para uso no PPT.

---

## Fontes de Dados

- `Vendas_2025.xlsx` — já filtrado para Jan-Abr 2025
- `Vendas_2026.xlsx` — já filtrado para Jan-Abr 2026
- Leitura por índice posicional (colunas com encoding problemático)

**Mapeamento de colunas (posição → nome):**

| Índice | Nome |
|---|---|
| 6 | cc (código centro de custo) |
| 7 | dcc (descrição centro de custo) |
| 9 | consultor |
| 10 | cod_cliente |
| 14 | liquido (valor líquido) |

---

## Regras de Classificação

### Marca

- **Wirtgen:** `dcc` contém `WIRTGEN`
- **John Deere:** todos os demais

### Canal (hierarquia — primeira regra que bater ganha)

| Prioridade | Canal | Critério no campo `dcc` |
|---|---|---|
| 1 | Wirtgen | contém `WIRTGEN` |
| 2 | CSN/Minérios | contém `CSN` |
| 3 | CRC | contém `CRC` |
| 4 | Serviços/Oficina | contém `SERVIC` |
| 5 | Balcão | vazio (`''`) |
| 6 | Varejo JD | demais |

---

## Outputs

### `bloco1.md` — Documento narrativo

Estrutura em prosa, sem tabelas. Seções:

1. **Visão Geral** — total geral 2025 vs 2026, var%, qual marca puxou o resultado
2. **John Deere** — parágrafo por canal (Balcão, CSN/Minérios, CRC, Serviços, Varejo), total JD
3. **Wirtgen** — parágrafo com total e participação no mix
4. **Destaques automáticos** — canal de maior crescimento, canal de maior queda, canal dominante

Comentários gerados automaticamente pelo script com base nos números (ex: participação %, maior canal, variação). Comentários de negócio aprofundados são adicionados manualmente após geração.

### `bloco1.json` — Estrutura para PPT

```json
{
  "periodo": "Jan-Abr 2025 vs Jan-Abr 2026",
  "total_geral": {
    "fat_2025": 0.0,
    "fat_2026": 0.0,
    "var_pct": 0.0
  },
  "marcas": {
    "John Deere": {
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "canais": [
        {
          "canal": "Balcão",
          "fat_2025": 0.0,
          "fat_2026": 0.0,
          "var_pct": 0.0,
          "share_2026": 0.0
        }
      ]
    },
    "Wirtgen": {
      "fat_2025": 0.0,
      "fat_2026": 0.0,
      "var_pct": 0.0,
      "canais": []
    }
  }
}
```

---

## Script

**Arquivo:** `src/bloco1.py`
**Execução:** `python src/bloco1.py` (rodar da raiz do projeto)

**Funções:**

| Função | Responsabilidade |
|---|---|
| `load_and_clean(file)` | Lê Excel, renomeia por posição, normaliza dcc |
| `classify(df)` | Adiciona colunas `marca` e `canal` pela hierarquia |
| `aggregate(df25, df26)` | Agrupa por marca × canal, calcula fat + var% + share |
| `render_markdown(agg)` | Gera texto narrativo com comentários automáticos |
| `render_json(agg)` | Gera estrutura JSON |
| `main()` | Orquestra tudo, salva arquivos |

---

## O que está fora do escopo deste bloco

- Abertura por loja/filial (Bloco 2)
- Análise de carteiras herdadas / migração de consultores (Bloco 3)
- Número de clientes e ticket médio (Bloco 2)
- Grupos e subgrupos de peças (Bloco 2)
