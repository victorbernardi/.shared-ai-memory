# Design Spec — PriceWatch JD

**Data:** 2026-05-13
**Status:** Aprovado
**Autor:** Victor Bernardi + Claude Code

---

## 1. Objetivo

Monitorar preços de peças John Deere praticados pelo mercado paralelo, comparando com os valores da Inova e do catálogo oficial JD. O output é um Excel consolidado que identifica o concorrente mais barato por peça, subsidiando decisões de precificação e campanhas comerciais.

---

## 2. Arquitetura Geral

```text
INPUT
lista_pecas.csv
(numero_peca, descricao, categoria, valor_oficial_jd, valor_inova)
        │
        ▼
scraper.py  ←  concorrentes.json (modo: scraper/ia/manual)
  ├── adaptadores/mercadolivre.py
  ├── adaptadores/agrofy.py
  ├── adaptadores/mfrural.py
  └── adaptadores/tblagro.py
        │                          │
        ▼                          ▼
output/concorrentes/          output/fila_pendentes.csv
  mercadolivre.xlsx           (peças não encontradas +
  tblagro.xlsx                 concorrentes modo ia/manual)
  egpecas.xlsx
  ...
        │
        ▼
consolidar.py
        │
        ▼
output/resultados.xlsx
(menor preço global por peça)
```

---

## 3. Componentes

### 3.1 `concorrentes.json` — Fonte de Verdade

Localização: `scripts/01-mapeamento/concorrentes.json`

Registra todos os concorrentes conhecidos, independente do modo de coleta.

**Schema:**

```json
[
  {
    "nome": "EG Peças",
    "url_base": "https://egindustriadepecas.com.br",
    "prioridade": 1,
    "ativo": true,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": false,
      "protecao": "Cloudflare",
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "TBL Agro Peças",
    "url_base": "https://loja.tblagropecas.com.br",
    "prioridade": 2,
    "ativo": true,
    "modo": "scraper",
    "adaptador": "tblagro",
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": true,
      "protecao": null,
      "recomendacao": "scraper",
      "data": "2026-05-13"
    }
  }
]
```

**Modos:**

| Modo | Comportamento |
|------|---------------|
| `scraper` | Adaptador Python processa automaticamente |
| `ia` | Entra direto na `fila_pendentes.csv` com contexto para o agente |
| `manual` | Entra na fila com flag `manual` — preenchimento humano |

---

### 3.2 `diagnostico.py` — Análise de Novo Concorrente

Localização: `scripts/02-pesquisa/diagnostico.py`

Roda uma vez antes de cadastrar um novo concorrente. Verifica:

1. Site acessível (HTTP 200)
2. Tem campo de busca
3. Retorna preço na página de resultado
4. Detecta proteção anti-bot (Cloudflare, CAPTCHA, JS obrigatório)

Gera relatório detalhado no terminal e recomenda o modo. Solicita confirmação antes de gravar em `concorrentes.json`.

**Uso:**

```bash
python scripts/02-pesquisa/diagnostico.py --url https://site.com.br --nome "Nome Concorrente"
```

---

### 3.3 `adaptadores/_base.py` — Interface Comum

Todos os adaptadores implementam:

```python
def buscar(numero_peca: str) -> list[dict] | str | None:
    ...
```

Retorna:

- `list[dict]` — até 3 resultados (os 3 menores preços encontrados no site)
- `None` — peça não encontrada no site
- `str` — motivo do bloqueio (ex: `"protecao_antibot"`, `"captcha"`, `"timeout"`)

O scraper usa o tipo do retorno para preencher o campo `motivo` em `fila_pendentes.csv`: `None` → `"nao_encontrado"`, `str` → valor retornado.

**Schema do resultado:**

```json
{
  "numero_peca": "RE509672",
  "concorrente": "TBL Agro Peças",
  "preco": 120.00,
  "url_fonte": "https://...",
  "disponibilidade": "Em estoque",
  "tipo_peca": "original",
  "observacao": "",
  "data_pesquisa": "2026-05-13"
}
```

`tipo_peca` sempre explícito: `"original"` ou `"similar"`.

---

### 3.4 `integrar_bd.py` — Preparação da Lista de Peças

Localização: `scripts/03-banco/integrar_bd.py`

Converte o CSV exportado do BD Inova para o formato padrão esperado pelo scraper.

**Input:** CSV exportado manualmente do BD Fabric com qualquer separador (`,` ou `;`), valores monetários com `R$` ou ponto/vírgula decimal.

**Output:** `data/lista_pecas.csv` com colunas padronizadas:

```
numero_peca, descricao, categoria, valor_oficial_jd, valor_inova
```

Valida que nenhuma linha tenha `numero_peca` vazio. Interrompe com mensagem de erro se o CSV de entrada não contiver as colunas mínimas (`numero_peca`, `valor_inova`).

**Uso:**

```bash
python scripts/03-banco/integrar_bd.py --input caminho/exportacao_bd.csv
```

---

### 3.5 `scraper.py` — Orquestrador em Lote

Localização: `scripts/02-pesquisa/scraper.py`

**Fluxo por peça:**

1. Para cada peça da lista, itera concorrentes ativos ordenados por prioridade
2. Concorrentes modo `ia` ou `manual` → adiciona direto à `fila_pendentes.csv`
3. Concorrentes modo `scraper` → chama `adaptador.buscar(numero_peca)`
4. Encontrou → grava/atualiza `output/concorrentes/<adaptador>.xlsx` imediatamente (incremental)
5. Não encontrou → adiciona à `fila_pendentes.csv`

Rate limit: pausa de 5–10s entre requisições por site.

**Uso:**

```bash
python scripts/02-pesquisa/scraper.py --lista data/lista_pecas.csv
python scripts/02-pesquisa/scraper.py --lista data/lista_pecas.csv --concorrente tblagro
python scripts/02-pesquisa/scraper.py --lista data/lista_pecas.csv --retomar
python scripts/02-pesquisa/scraper.py --ver-fila
```

`--retomar`: pula peças cuja `data_pesquisa` no arquivo do concorrente seja igual à data de execução do script (`date.today()`). A comparação é feita no momento da execução — execuções em dias diferentes nunca se interferem.

---

### 3.6 `buscar_peca.py` — Busca Pontual

Localização: `scripts/02-pesquisa/buscar_peca.py`

Busca uma peça específica em todos os adaptadores `scraper` ativos. Imprime resultado no terminal.

**Regra de gravação:**

- Peça **sem valor cadastrado** no arquivo do concorrente → salva automaticamente
- Preço encontrado **menor que o existente** → exibe comparação e aguarda `s/n`
- Preço encontrado **maior ou igual** → imprime no terminal, não salva

**Uso:**

```bash
python scripts/02-pesquisa/buscar_peca.py RE509672
python scripts/02-pesquisa/buscar_peca.py RE509672 --concorrente mercadolivre
```

---

### 3.7 `consolidar.py` — Geração do Excel Final

Localização: `scripts/04-consolidacao/consolidar.py`

Lê todos os arquivos em `output/concorrentes/*.xlsx`, elege o menor preço por peça entre todos os concorrentes e gera `output/resultados.xlsx`.

**Colunas do `resultados.xlsx`:**

| Coluna | Fonte |
|--------|-------|
| `numero_peca` | lista_pecas.csv |
| `descricao` | lista_pecas.csv |
| `categoria` | lista_pecas.csv |
| `valor_oficial_jd` | lista_pecas.csv |
| `valor_inova` | lista_pecas.csv |
| `menor_preco_paralelo` | consolidador |
| `concorrente_mais_barato` | consolidador |
| `url_fonte` | arquivo do concorrente |
| `tipo_peca` | arquivo do concorrente |
| `diferenca_rs` | calculado |
| `diferenca_pct` | calculado |
| `conclusao` | calculado |
| `data_pesquisa` | arquivo do concorrente |
| `status` | `Pesquisado` / `Pendente IA` / `Pendente Manual` |

`conclusao`: `"Inova mais competitiva"`, `"Paralelo mais barato"` ou `"Pesquisa pendente"`.

**Uso:**

```bash
python scripts/04-consolidacao/consolidar.py
python scripts/04-consolidacao/consolidar.py --merge-ia output/ia_resultados.csv
```

`--merge-ia`: incorpora resultados do agente IA antes de consolidar.

---

### 3.8 `output/concorrentes/<site>.xlsx` — Schema por Concorrente

Até 3 linhas por peça (os 3 menores preços encontrados no site):

```
numero_peca | preco | tipo_peca | url_fonte | disponibilidade | observacao | data_pesquisa | fonte
```

`fonte`: `scraper`, `ia` ou `manual`.

---

### 3.9 `output/ia_resultados.csv` — Output do Agente IA

Arquivo gerado pelo agente IA (Gemini CLI / Claude) após processar a `fila_pendentes.csv`. Schema idêntico ao resultado dos adaptadores scraper (mesmos nomes de campo):

```
numero_peca | concorrente | preco | tipo_peca | url_fonte | disponibilidade | observacao | data_pesquisa | fonte
```

`fonte` sempre `"ia"`. Incorporado ao consolidador via `--merge-ia`.

---

### 3.10 `output/fila_pendentes.csv` — Input para Agente IA

```
numero_peca | descricao | concorrente | url_base | modo | motivo
```

`motivo`: `"nao_encontrado"`, `"protecao_antibot"`, `"modo_ia"`, `"modo_manual"`.

---

## 4. Estrutura de Arquivos

```text
pricewatch-jd/
├── scripts/
│   ├── 01-mapeamento/
│   │   └── concorrentes.json
│   ├── 02-pesquisa/
│   │   ├── scraper.py
│   │   ├── buscar_peca.py
│   │   ├── diagnostico.py
│   │   └── adaptadores/
│   │       ├── _base.py
│   │       ├── mercadolivre.py
│   │       ├── agrofy.py
│   │       ├── mfrural.py
│   │       └── tblagro.py
│   ├── 03-banco/
│   │   └── integrar_bd.py       # Converte CSV do BD Inova → data/lista_pecas.csv
│   └── 04-consolidacao/
│       └── consolidar.py
├── data/
│   └── lista_pecas.csv          # Gerado por integrar_bd.py
└── output/
    ├── concorrentes/
    │   ├── mercadolivre.xlsx
    │   └── tblagro.xlsx
    ├── fila_pendentes.csv
    ├── ia_resultados.csv
    └── resultados.xlsx
```

---

## 5. Regras de Negócio

1. `resultados.xlsx` é **sempre gerado pelo consolidador** — nunca escrito diretamente pelo scraper
2. Excel de concorrente atualizado **incrementalmente** — progresso não se perde se o scraper travar
3. Cada arquivo de concorrente guarda os **3 menores preços** por peça
4. Concorrentes modo `ia`/`manual` vão direto para `fila_pendentes.csv` — nunca tentam scraping
5. `tipo_peca` sempre explícito (`original` ou `similar`) — nunca deixar em branco
6. `url_fonte` obrigatória para auditoria — resultado sem URL não é salvo
7. Novo concorrente só entra em produção após rodar `diagnostico.py` e gravar em `concorrentes.json`

---

## 6. Dependências Python

```
pandas
openpyxl
requests
beautifulsoup4
```

---

## 7. Fora de Escopo (v1)

| Item | Por que não (v1) |
|------|-----------------|
| Interface web ou dashboard | Aumenta complexidade de deploy; Excel cobre a necessidade de apresentação ao gerente |
| Agendamento automático (cron/scheduler) | Execução manual controlada pelo usuário é suficiente no volume inicial (50–500 peças) |
| Histórico de preços (série temporal) | Requer estrutura de banco de dados; v1 é snapshot pontual com data de pesquisa |
| Notificações de variação de preço | Depende de histórico (item acima); fora de escopo por dependência |
| Cálculo de distância entre lojas (geopy) | Útil para análise geográfica futura; não impacta a coleta de preços v1 |
