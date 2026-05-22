# PriceWatch JD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o pipeline de monitoramento de preços de peças John Deere — do CSV do BD Inova até o Excel comparativo final, passando por scraping automático, fila para agente IA e consolidação.

**Architecture:** Pipeline orientado a arquivos: cada etapa lê e escreve arquivos intermediários independentes. O scraper itera uma lista de peças contra concorrentes configurados em `concorrentes.json`, grava resultados por concorrente incrementalmente, e o consolidador gera o Excel final. A interface de cada adaptador de scraping é padronizada via `_base.py`.

**Tech Stack:** Python 3.10+, pandas, openpyxl, requests, beautifulsoup4, argparse, pytest

---

## Mapa de Arquivos

| Arquivo | Responsabilidade |
|---------|-----------------|
| `scripts/01-mapeamento/concorrentes.json` | Fonte de verdade de todos os concorrentes (modo, prioridade, diagnóstico) |
| `scripts/02-pesquisa/adaptadores/_base.py` | Tipo `ResultadoBusca` e contrato da função `buscar()` |
| `scripts/02-pesquisa/adaptadores/mercadolivre.py` | Adaptador Mercado Livre |
| `scripts/02-pesquisa/adaptadores/tblagro.py` | Adaptador TBL Agro Peças |
| `scripts/02-pesquisa/adaptadores/agrofy.py` | Adaptador Agrofy |
| `scripts/02-pesquisa/adaptadores/mfrural.py` | Adaptador MF Rural |
| `scripts/02-pesquisa/diagnostico.py` | Analisa site novo e recomenda modo |
| `scripts/02-pesquisa/scraper.py` | Orquestrador em lote |
| `scripts/02-pesquisa/buscar_peca.py` | Busca pontual de uma peça |
| `scripts/03-banco/integrar_bd.py` | Converte CSV do BD Inova → `data/lista_pecas.csv` |
| `scripts/04-consolidacao/consolidar.py` | Gera `output/resultados.xlsx` a partir dos Excels por concorrente |
| `tests/test_integrar_bd.py` | Testes de `integrar_bd.py` |
| `tests/test_base.py` | Testes do contrato `_base.py` |
| `tests/test_scraper.py` | Testes do orquestrador |
| `tests/test_consolidar.py` | Testes do consolidador |
| `tests/test_buscar_peca.py` | Testes da busca pontual |

---

## Task 1: Estrutura inicial e `concorrentes.json`

**Files:**

- Create: `scripts/01-mapeamento/concorrentes.json`
- Create: `scripts/02-pesquisa/adaptadores/__init__.py` (vazio)
- Create: `tests/__init__.py` (vazio)

- [ ] **Step 1: Criar `concorrentes.json` com os 12 concorrentes iniciais**

```json
[
  {
    "nome": "Mercado Livre",
    "url_base": "https://lista.mercadolivre.com.br",
    "prioridade": 1,
    "ativo": true,
    "modo": "scraper",
    "adaptador": "mercadolivre",
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": true,
      "protecao": null,
      "recomendacao": "scraper",
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
  },
  {
    "nome": "Agrofy",
    "url_base": "https://www.agrofy.com.br",
    "prioridade": 3,
    "ativo": true,
    "modo": "scraper",
    "adaptador": "agrofy",
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": true,
      "protecao": null,
      "recomendacao": "scraper",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "MF Rural",
    "url_base": "https://www.mfrural.com.br",
    "prioridade": 4,
    "ativo": true,
    "modo": "scraper",
    "adaptador": "mfrural",
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": true,
      "protecao": null,
      "recomendacao": "scraper",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "EG Peças",
    "url_base": "https://egindustriadepecas.com.br",
    "prioridade": 5,
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
    "nome": "Super Tractor",
    "url_base": "https://www.supertractor.com.br",
    "prioridade": 6,
    "ativo": true,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": false,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "Rech Peças",
    "url_base": "https://www.rech.com",
    "prioridade": 7,
    "ativo": true,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "Ditrac",
    "url_base": "https://www.ditrac.com.br",
    "prioridade": 8,
    "ativo": true,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "Canaparts",
    "url_base": "https://canaparts.com.br",
    "prioridade": 9,
    "ativo": true,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": true,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "Dispetral",
    "url_base": "https://www.dispetral.com.br",
    "prioridade": 10,
    "ativo": false,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": false,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "BBX",
    "url_base": "https://www.bbxtratores.com.br",
    "prioridade": 11,
    "ativo": false,
    "modo": "ia",
    "adaptador": null,
    "diagnostico": {
      "acessivel": true,
      "tem_busca": false,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "ia",
      "data": "2026-05-13"
    }
  },
  {
    "nome": "Pangea Parts",
    "url_base": "https://www.pangeaparts.com.br",
    "prioridade": 12,
    "ativo": false,
    "modo": "manual",
    "adaptador": null,
    "diagnostico": {
      "acessivel": false,
      "tem_busca": false,
      "retorna_preco": false,
      "protecao": null,
      "recomendacao": "manual",
      "data": "2026-05-13"
    }
  }
]
```

- [ ] **Step 2: Criar arquivos `__init__.py` vazios**

```bash
echo "" > scripts/02-pesquisa/adaptadores/__init__.py
echo "" > tests/__init__.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/01-mapeamento/concorrentes.json scripts/02-pesquisa/adaptadores/__init__.py tests/__init__.py
git commit -m "feat(pricewatch): scaffold concorrentes.json com 12 players iniciais"
```

---

## Task 2: Contrato base dos adaptadores (`_base.py`)

**Files:**

- Create: `scripts/02-pesquisa/adaptadores/_base.py`
- Create: `tests/test_base.py`

- [ ] **Step 1: Escrever o teste do contrato**

```python
# tests/test_base.py
import pytest
from scripts.adaptadores._base import ResultadoBusca, validar_resultado, carregar_adaptador

def test_resultado_busca_campos_obrigatorios():
    r = ResultadoBusca(
        numero_peca="RE509672",
        concorrente="Teste",
        preco=100.0,
        url_fonte="https://exemplo.com/RE509672",
        disponibilidade="Em estoque",
        tipo_peca="original",
        observacao="",
        data_pesquisa="2026-05-13",
    )
    assert r.numero_peca == "RE509672"
    assert r.tipo_peca in ("original", "similar")

def test_resultado_sem_url_invalido():
    with pytest.raises(ValueError, match="url_fonte"):
        ResultadoBusca(
            numero_peca="RE509672",
            concorrente="Teste",
            preco=100.0,
            url_fonte="",
            disponibilidade="Em estoque",
            tipo_peca="original",
            observacao="",
            data_pesquisa="2026-05-13",
        )

def test_tipo_peca_invalido():
    with pytest.raises(ValueError, match="tipo_peca"):
        ResultadoBusca(
            numero_peca="RE509672",
            concorrente="Teste",
            preco=100.0,
            url_fonte="https://exemplo.com",
            disponibilidade="Em estoque",
            tipo_peca="desconhecido",
            observacao="",
            data_pesquisa="2026-05-13",
        )
```

- [ ] **Step 2: Rodar o teste para confirmar falha**

```bash
cd C:\Projetos\Inova\projects\pricewatch-jd
python -m pytest tests/test_base.py -v
```

Esperado: `ModuleNotFoundError` ou `ImportError`.

- [ ] **Step 3: Implementar `_base.py`**

```python
# scripts/02-pesquisa/adaptadores/_base.py
from dataclasses import dataclass, field
from datetime import date
import importlib
import json
from pathlib import Path

TIPOS_VALIDOS = ("original", "similar")
CONCORRENTES_JSON = Path(__file__).parents[3] / "01-mapeamento" / "concorrentes.json"


@dataclass
class ResultadoBusca:
    numero_peca: str
    concorrente: str
    preco: float
    url_fonte: str
    disponibilidade: str
    tipo_peca: str
    observacao: str
    data_pesquisa: str = field(default_factory=lambda: date.today().isoformat())

    def __post_init__(self):
        if not self.url_fonte:
            raise ValueError("url_fonte é obrigatória para auditoria")
        if self.tipo_peca not in TIPOS_VALIDOS:
            raise ValueError(f"tipo_peca deve ser um de {TIPOS_VALIDOS}, recebeu '{self.tipo_peca}'")

    def to_dict(self) -> dict:
        return {
            "numero_peca": self.numero_peca,
            "concorrente": self.concorrente,
            "preco": self.preco,
            "url_fonte": self.url_fonte,
            "disponibilidade": self.disponibilidade,
            "tipo_peca": self.tipo_peca,
            "observacao": self.observacao,
            "data_pesquisa": self.data_pesquisa,
            "fonte": "scraper",
        }


def carregar_adaptador(nome: str):
    """Importa dinamicamente um adaptador pelo nome (ex: 'mercadolivre')."""
    modulo = importlib.import_module(f"scripts.adaptadores.{nome}")
    if not hasattr(modulo, "buscar"):
        raise AttributeError(f"Adaptador '{nome}' não implementa a função buscar()")
    return modulo


def carregar_concorrentes() -> list[dict]:
    with open(CONCORRENTES_JSON, encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 4: Ajustar o import no teste para o caminho correto**

Editar `tests/test_base.py` linha 3:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "02-pesquisa"))
from adaptadores._base import ResultadoBusca, carregar_adaptador, carregar_concorrentes
```

E remover a linha original de import.

- [ ] **Step 5: Rodar os testes**

```bash
python -m pytest tests/test_base.py -v
```

Esperado: 3 testes PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/02-pesquisa/adaptadores/_base.py tests/test_base.py
git commit -m "feat(pricewatch): contrato base ResultadoBusca e carregamento dinâmico de adaptadores"
```

---

## Task 3: `integrar_bd.py` — Preparação da lista de peças

**Files:**

- Create: `scripts/03-banco/integrar_bd.py`
- Create: `tests/test_integrar_bd.py`
- Create: `tests/fixtures/bd_export_ponto_virgula.csv`
- Create: `tests/fixtures/bd_export_virgula.csv`

- [ ] **Step 1: Criar fixtures de teste**

`tests/fixtures/bd_export_ponto_virgula.csv`:

```
numero_peca;descricao;categoria;valor_oficial_jd;valor_inova
RE509672;Filtro Óleo Motor;Filtros;R$ 185,00;R$ 150,00
RE504836;Filtro Óleo Donaldson;Filtros;195,50;160,00
```

`tests/fixtures/bd_export_virgula.csv`:

```
numero_peca,descricao,categoria,valor_oficial_jd,valor_inova
RE509672,Filtro Óleo Motor,Filtros,"R$ 185,00","R$ 150,00"
```

- [ ] **Step 2: Escrever os testes**

```python
# tests/test_integrar_bd.py
import sys
from pathlib import Path
import pytest
import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "03-banco"))
from integrar_bd import normalizar_csv, COLUNAS_SAIDA, COLUNAS_MINIMAS

FIXTURES = Path(__file__).parent / "fixtures"

def test_leitura_separador_ponto_virgula():
    df = normalizar_csv(FIXTURES / "bd_export_ponto_virgula.csv")
    assert list(df.columns) == COLUNAS_SAIDA
    assert len(df) == 2

def test_leitura_separador_virgula():
    df = normalizar_csv(FIXTURES / "bd_export_virgula.csv")
    assert len(df) == 1

def test_remove_simbolo_real():
    df = normalizar_csv(FIXTURES / "bd_export_ponto_virgula.csv")
    assert df["valor_inova"].dtype == float
    assert df["valor_oficial_jd"].dtype == float

def test_falha_sem_coluna_obrigatoria(tmp_path):
    csv = tmp_path / "invalido.csv"
    csv.write_text("descricao,valor_inova\nFiltro,10.0")
    with pytest.raises(ValueError, match="numero_peca"):
        normalizar_csv(csv)

def test_falha_numero_peca_vazio(tmp_path):
    csv = tmp_path / "vazio.csv"
    csv.write_text("numero_peca,descricao,valor_inova\n,Filtro,10.0")
    with pytest.raises(ValueError, match="numero_peca vazio"):
        normalizar_csv(csv)
```

- [ ] **Step 3: Rodar para confirmar falha**

```bash
python -m pytest tests/test_integrar_bd.py -v
```

Esperado: `ModuleNotFoundError`.

- [ ] **Step 4: Implementar `integrar_bd.py`**

```python
# scripts/03-banco/integrar_bd.py
import argparse
import re
import sys
from pathlib import Path
import pandas as pd

COLUNAS_MINIMAS = {"numero_peca", "valor_inova"}
COLUNAS_SAIDA = ["numero_peca", "descricao", "categoria", "valor_oficial_jd", "valor_inova"]
DEST_PADRAO = Path(__file__).parents[2] / "data" / "lista_pecas.csv"


def _limpar_valor(serie: pd.Series) -> pd.Series:
    """Remove 'R$', espaços e converte vírgula decimal para ponto."""
    return (
        serie.astype(str)
        .str.replace(r"R\$\s*", "", regex=True)
        .str.replace(r"\.", "", regex=True)   # remove separador de milhar
        .str.replace(",", ".", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )


def normalizar_csv(caminho: Path) -> pd.DataFrame:
    # Detecta separador
    amostra = Path(caminho).read_text(encoding="utf-8")[:512]
    sep = ";" if amostra.count(";") > amostra.count(",") else ","

    df = pd.read_csv(caminho, sep=sep, encoding="utf-8", dtype=str)
    df.columns = [c.strip().lower() for c in df.columns]

    faltando = COLUNAS_MINIMAS - set(df.columns)
    if faltando:
        raise ValueError(f"CSV não contém colunas obrigatórias: {faltando}")

    if df["numero_peca"].isnull().any() or (df["numero_peca"].str.strip() == "").any():
        raise ValueError("Há linhas com numero_peca vazio — corrija o CSV de entrada")

    for col in ("valor_oficial_jd", "valor_inova"):
        if col in df.columns:
            df[col] = _limpar_valor(df[col])

    for col in COLUNAS_SAIDA:
        if col not in df.columns:
            df[col] = ""

    return df[COLUNAS_SAIDA]


def main():
    parser = argparse.ArgumentParser(description="Converte CSV do BD Inova para lista_pecas.csv")
    parser.add_argument("--input", required=True, help="Caminho para o CSV exportado do BD")
    parser.add_argument("--output", default=str(DEST_PADRAO), help="Destino (padrão: data/lista_pecas.csv)")
    args = parser.parse_args()

    df = normalizar_csv(Path(args.input))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"[OK] {len(df)} peças escritas em {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar os testes**

```bash
python -m pytest tests/test_integrar_bd.py -v
```

Esperado: 5 testes PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/03-banco/integrar_bd.py tests/test_integrar_bd.py tests/fixtures/
git commit -m "feat(pricewatch): integrar_bd.py — normaliza CSV do BD Inova para lista_pecas.csv"
```

---

## Task 4: Adaptadores de scraping

**Files:**

- Create: `scripts/02-pesquisa/adaptadores/mercadolivre.py`
- Create: `scripts/02-pesquisa/adaptadores/tblagro.py`
- Create: `scripts/02-pesquisa/adaptadores/agrofy.py`
- Create: `scripts/02-pesquisa/adaptadores/mfrural.py`

> Os adaptadores implementam scraping real. Use `requests` + `BeautifulSoup`. Se o site mudar estrutura, só o adaptador correspondente precisa ser atualizado — o resto do pipeline não muda.

- [ ] **Step 1: Implementar `mercadolivre.py`**

```python
# scripts/02-pesquisa/adaptadores/mercadolivre.py
import re
import time
import requests
from bs4 import BeautifulSoup
from ._base import ResultadoBusca

NOME = "Mercado Livre"
URL_BUSCA = "https://lista.mercadolivre.com.br/{peca}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def _extrair_preco(texto: str) -> float | None:
    match = re.search(r"[\d.,]+", texto.replace(".", "").replace(",", "."))
    return float(match.group()) if match else None


def buscar(numero_peca: str) -> list[dict] | str | None:
    url = URL_BUSCA.format(peca=numero_peca)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        return f"timeout:{e}"

    if resp.status_code == 403:
        return "protecao_antibot"

    soup = BeautifulSoup(resp.text, "html.parser")

    # Detectar Cloudflare/CAPTCHA
    if "cf-browser-verification" in resp.text or "captcha" in resp.text.lower():
        return "captcha"

    itens = soup.select("li.ui-search-layout__item")[:5]
    resultados = []

    for item in itens:
        preco_el = item.select_one(".andes-money-amount__fraction")
        link_el = item.select_one("a.ui-search-link")
        if not preco_el or not link_el:
            continue

        preco = _extrair_preco(preco_el.get_text())
        if not preco:
            continue

        titulo = (item.select_one(".ui-search-item__title") or item).get_text(strip=True)
        tipo = "similar" if numero_peca.upper() not in titulo.upper() else "original"

        try:
            resultados.append(
                ResultadoBusca(
                    numero_peca=numero_peca,
                    concorrente=NOME,
                    preco=preco,
                    url_fonte=link_el["href"].split("?")[0],
                    disponibilidade="Disponível",
                    tipo_peca=tipo,
                    observacao=titulo[:120],
                ).to_dict()
            )
        except ValueError:
            continue

    if not resultados:
        return None

    resultados.sort(key=lambda r: r["preco"])
    return resultados[:3]
```

- [ ] **Step 2: Implementar `tblagro.py`**

```python
# scripts/02-pesquisa/adaptadores/tblagro.py
import re
import requests
from bs4 import BeautifulSoup
from ._base import ResultadoBusca

NOME = "TBL Agro Peças"
URL_BUSCA = "https://loja.tblagropecas.com.br/busca?q={peca}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _extrair_preco(texto: str) -> float | None:
    match = re.search(r"[\d.]+,\d{2}", texto)
    if match:
        return float(match.group().replace(".", "").replace(",", "."))
    return None


def buscar(numero_peca: str) -> list[dict] | str | None:
    url = URL_BUSCA.format(peca=numero_peca)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        return f"timeout:{e}"

    if resp.status_code == 403:
        return "protecao_antibot"

    soup = BeautifulSoup(resp.text, "html.parser")
    itens = soup.select(".product-item, .shelf-item")[:5]
    resultados = []

    for item in itens:
        preco_el = item.select_one(".price, .product-price")
        link_el = item.select_one("a[href]")
        if not preco_el or not link_el:
            continue

        preco = _extrair_preco(preco_el.get_text())
        if not preco:
            continue

        titulo = (item.select_one(".product-name, h2, h3") or item).get_text(strip=True)
        tipo = "similar" if numero_peca.upper() not in titulo.upper() else "original"
        href = link_el["href"]
        if not href.startswith("http"):
            href = "https://loja.tblagropecas.com.br" + href

        try:
            resultados.append(
                ResultadoBusca(
                    numero_peca=numero_peca,
                    concorrente=NOME,
                    preco=preco,
                    url_fonte=href,
                    disponibilidade="Disponível",
                    tipo_peca=tipo,
                    observacao=titulo[:120],
                ).to_dict()
            )
        except ValueError:
            continue

    if not resultados:
        return None

    resultados.sort(key=lambda r: r["preco"])
    return resultados[:3]
```

- [ ] **Step 3: Implementar `agrofy.py`**

```python
# scripts/02-pesquisa/adaptadores/agrofy.py
import re
import requests
from bs4 import BeautifulSoup
from ._base import ResultadoBusca

NOME = "Agrofy"
URL_BUSCA = "https://www.agrofy.com.br/busca?q={peca}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _extrair_preco(texto: str) -> float | None:
    match = re.search(r"[\d.]+,\d{2}", texto)
    if match:
        return float(match.group().replace(".", "").replace(",", "."))
    return None


def buscar(numero_peca: str) -> list[dict] | str | None:
    url = URL_BUSCA.format(peca=numero_peca)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        return f"timeout:{e}"

    if resp.status_code in (403, 429):
        return "protecao_antibot"

    soup = BeautifulSoup(resp.text, "html.parser")

    if "captcha" in resp.text.lower():
        return "captcha"

    itens = soup.select(".product-card, [class*='product']")[:5]
    resultados = []

    for item in itens:
        preco_el = item.select_one("[class*='price'], [class*='valor']")
        link_el = item.select_one("a[href]")
        if not preco_el or not link_el:
            continue

        preco = _extrair_preco(preco_el.get_text())
        if not preco:
            continue

        titulo = item.get_text(strip=True)[:120]
        tipo = "similar" if numero_peca.upper() not in titulo.upper() else "original"
        href = link_el["href"]
        if not href.startswith("http"):
            href = "https://www.agrofy.com.br" + href

        try:
            resultados.append(
                ResultadoBusca(
                    numero_peca=numero_peca,
                    concorrente=NOME,
                    preco=preco,
                    url_fonte=href,
                    disponibilidade="Disponível",
                    tipo_peca=tipo,
                    observacao="",
                ).to_dict()
            )
        except ValueError:
            continue

    if not resultados:
        return None

    resultados.sort(key=lambda r: r["preco"])
    return resultados[:3]
```

- [ ] **Step 4: Implementar `mfrural.py`**

```python
# scripts/02-pesquisa/adaptadores/mfrural.py
import re
import requests
from bs4 import BeautifulSoup
from ._base import ResultadoBusca

NOME = "MF Rural"
URL_BUSCA = "https://www.mfrural.com.br/busca/{peca}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _extrair_preco(texto: str) -> float | None:
    match = re.search(r"[\d.]+,\d{2}", texto)
    if match:
        return float(match.group().replace(".", "").replace(",", "."))
    return None


def buscar(numero_peca: str) -> list[dict] | str | None:
    url = URL_BUSCA.format(peca=numero_peca)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        return f"timeout:{e}"

    if resp.status_code == 403:
        return "protecao_antibot"

    soup = BeautifulSoup(resp.text, "html.parser")
    itens = soup.select(".item-busca, .produto-item")[:5]
    resultados = []

    for item in itens:
        preco_el = item.select_one(".preco, [class*='price']")
        link_el = item.select_one("a[href]")
        if not preco_el or not link_el:
            continue

        preco = _extrair_preco(preco_el.get_text())
        if not preco:
            continue

        titulo = (item.select_one("h2, h3, .titulo") or item).get_text(strip=True)
        tipo = "similar" if numero_peca.upper() not in titulo.upper() else "original"
        href = link_el["href"]
        if not href.startswith("http"):
            href = "https://www.mfrural.com.br" + href

        try:
            resultados.append(
                ResultadoBusca(
                    numero_peca=numero_peca,
                    concorrente=NOME,
                    preco=preco,
                    url_fonte=href,
                    disponibilidade="Verificar anúncio",
                    tipo_peca=tipo,
                    observacao=titulo[:120],
                ).to_dict()
            )
        except ValueError:
            continue

    if not resultados:
        return None

    resultados.sort(key=lambda r: r["preco"])
    return resultados[:3]
```

- [ ] **Step 5: Commit**

```bash
git add scripts/02-pesquisa/adaptadores/
git commit -m "feat(pricewatch): adaptadores de scraping — mercadolivre, tblagro, agrofy, mfrural"
```

---

## Task 5: `scraper.py` — Orquestrador em lote

**Files:**

- Create: `scripts/02-pesquisa/scraper.py`
- Create: `tests/test_scraper.py`

- [ ] **Step 1: Escrever os testes (com adaptador mock)**

```python
# tests/test_scraper.py
import sys
import json
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "02-pesquisa"))
from scraper import classificar_retorno, montar_entrada_fila

RESULTADO_MOCK = [
    {
        "numero_peca": "RE509672",
        "concorrente": "Mercado Livre",
        "preco": 120.0,
        "url_fonte": "https://ml.com/item/1",
        "disponibilidade": "Disponível",
        "tipo_peca": "original",
        "observacao": "",
        "data_pesquisa": "2026-05-13",
        "fonte": "scraper",
    }
]

def test_classificar_retorno_lista():
    assert classificar_retorno(RESULTADO_MOCK) == "encontrado"

def test_classificar_retorno_none():
    assert classificar_retorno(None) == "nao_encontrado"

def test_classificar_retorno_str_bloqueio():
    assert classificar_retorno("captcha") == "bloqueado"
    assert classificar_retorno("protecao_antibot") == "bloqueado"

def test_montar_entrada_fila_none():
    entrada = montar_entrada_fila("RE509672", "Filtro", {"nome": "EG Peças", "url_base": "https://eg.com", "modo": "ia"}, None)
    assert entrada["motivo"] == "nao_encontrado"
    assert entrada["modo"] == "ia"

def test_montar_entrada_fila_bloqueio():
    entrada = montar_entrada_fila("RE509672", "Filtro", {"nome": "EG Peças", "url_base": "https://eg.com", "modo": "scraper"}, "captcha")
    assert entrada["motivo"] == "captcha"
```

- [ ] **Step 2: Rodar para confirmar falha**

```bash
python -m pytest tests/test_scraper.py -v
```

Esperado: `ImportError`.

- [ ] **Step 3: Implementar `scraper.py`**

```python
# scripts/02-pesquisa/scraper.py
import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from adaptadores._base import carregar_adaptador, carregar_concorrentes

RAIZ = Path(__file__).parents[2]
OUTPUT_DIR = RAIZ / "output" / "concorrentes"
FILA_PATH = RAIZ / "output" / "fila_pendentes.csv"
COLUNAS_CONCORRENTE = [
    "numero_peca", "preco", "tipo_peca", "url_fonte",
    "disponibilidade", "observacao", "data_pesquisa", "fonte",
]
COLUNAS_FILA = ["numero_peca", "descricao", "concorrente", "url_base", "modo", "motivo"]


def classificar_retorno(retorno) -> str:
    if isinstance(retorno, list):
        return "encontrado"
    if retorno is None:
        return "nao_encontrado"
    return "bloqueado"


def montar_entrada_fila(numero_peca: str, descricao: str, concorrente: dict, retorno) -> dict:
    if isinstance(retorno, str):
        motivo = retorno
    elif concorrente["modo"] in ("ia", "manual"):
        motivo = f"modo_{concorrente['modo']}"
    else:
        motivo = "nao_encontrado"
    return {
        "numero_peca": numero_peca,
        "descricao": descricao,
        "concorrente": concorrente["nome"],
        "url_base": concorrente["url_base"],
        "modo": concorrente["modo"],
        "motivo": motivo,
    }


def _gravar_resultados(adaptador_nome: str, resultados: list[dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUTPUT_DIR / f"{adaptador_nome}.xlsx"

    if dest.exists():
        df_atual = pd.read_excel(dest)
    else:
        df_atual = pd.DataFrame(columns=COLUNAS_CONCORRENTE)

    df_novo = pd.DataFrame(resultados)[COLUNAS_CONCORRENTE]
    df_combined = pd.concat([df_atual, df_novo], ignore_index=True)
    df_combined.to_excel(dest, index=False)


def _ja_pesquisado_hoje(adaptador_nome: str, numero_peca: str) -> bool:
    dest = OUTPUT_DIR / f"{adaptador_nome}.xlsx"
    if not dest.exists():
        return False
    df = pd.read_excel(dest)
    hoje = date.today().isoformat()
    mask = (df["numero_peca"] == numero_peca) & (df["data_pesquisa"].astype(str) == hoje)
    return mask.any()


def _gravar_fila(entradas: list[dict]):
    FILA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_novo = pd.DataFrame(entradas, columns=COLUNAS_FILA)
    if FILA_PATH.exists():
        df_atual = pd.read_csv(FILA_PATH)
        df_combined = pd.concat([df_atual, df_novo], ignore_index=True)
    else:
        df_combined = df_novo
    df_combined.drop_duplicates(subset=["numero_peca", "concorrente"]).to_csv(FILA_PATH, index=False)


def rodar(lista_path: Path, filtro_concorrente: str | None = None, retomar: bool = False):
    df_lista = pd.read_csv(lista_path)
    concorrentes = [c for c in carregar_concorrentes() if c["ativo"]]

    if filtro_concorrente:
        concorrentes = [c for c in concorrentes if c.get("adaptador") == filtro_concorrente]

    concorrentes.sort(key=lambda c: c["prioridade"])
    fila: list[dict] = []

    for _, peca in df_lista.iterrows():
        numero = peca["numero_peca"]
        descricao = str(peca.get("descricao", ""))

        for conc in concorrentes:
            adaptador_nome = conc.get("adaptador")

            if conc["modo"] in ("ia", "manual"):
                fila.append(montar_entrada_fila(numero, descricao, conc, None))
                continue

            if retomar and _ja_pesquisado_hoje(adaptador_nome, numero):
                print(f"  [SKIP] {numero} já pesquisado hoje em {conc['nome']}")
                continue

            try:
                mod = carregar_adaptador(adaptador_nome)
            except Exception as e:
                print(f"  [ERRO] Adaptador {adaptador_nome}: {e}")
                fila.append(montar_entrada_fila(numero, descricao, conc, f"erro_adaptador:{e}"))
                continue

            print(f"  [{conc['nome']}] buscando {numero}...", end=" ")
            retorno = mod.buscar(numero)
            status = classificar_retorno(retorno)
            print(status)

            if status == "encontrado":
                _gravar_resultados(adaptador_nome, retorno)
            else:
                fila.append(montar_entrada_fila(numero, descricao, conc, retorno))

            time.sleep(7)

    if fila:
        _gravar_fila(fila)
        print(f"\n[FILA] {len(fila)} entradas salvas em {FILA_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Scraper de preços PriceWatch JD")
    parser.add_argument("--lista", help="CSV com lista de peças")
    parser.add_argument("--concorrente", help="Rodar só este adaptador")
    parser.add_argument("--retomar", action="store_true", help="Pular peças já pesquisadas hoje")
    parser.add_argument("--ver-fila", action="store_true", help="Exibe fila_pendentes.csv agrupada")
    args = parser.parse_args()

    if args.ver_fila:
        if not FILA_PATH.exists():
            print("Fila vazia.")
            return
        df = pd.read_csv(FILA_PATH)
        for conc, grupo in df.groupby("concorrente"):
            print(f"\n{conc} ({len(grupo)} peças):")
            for _, r in grupo.iterrows():
                print(f"  {r['numero_peca']} — {r['motivo']}")
        return

    if not args.lista:
        parser.error("--lista é obrigatório quando não usando --ver-fila")

    rodar(Path(args.lista), args.concorrente, args.retomar)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar os testes**

```bash
python -m pytest tests/test_scraper.py -v
```

Esperado: 5 testes PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/02-pesquisa/scraper.py tests/test_scraper.py
git commit -m "feat(pricewatch): scraper.py — orquestrador em lote com rate limit e fila de pendentes"
```

---

## Task 6: `buscar_peca.py` — Busca pontual

**Files:**

- Create: `scripts/02-pesquisa/buscar_peca.py`
- Create: `tests/test_buscar_peca.py`

- [ ] **Step 1: Escrever os testes**

```python
# tests/test_buscar_peca.py
import sys
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "02-pesquisa"))
from buscar_peca import decidir_gravacao

RESULTADO = {
    "numero_peca": "RE509672",
    "concorrente": "Mercado Livre",
    "preco": 100.0,
    "url_fonte": "https://ml.com/1",
    "disponibilidade": "Disponível",
    "tipo_peca": "original",
    "observacao": "",
    "data_pesquisa": "2026-05-13",
    "fonte": "scraper",
}

def test_gravar_automatico_sem_historico():
    # Sem histórico = preco_existente None → deve gravar sem perguntar
    acao = decidir_gravacao(RESULTADO, preco_existente=None)
    assert acao == "gravar"

def test_gravar_menor_preco(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "s")
    acao = decidir_gravacao(RESULTADO, preco_existente=150.0)
    assert acao == "gravar"

def test_ignorar_preco_maior():
    resultado_caro = {**RESULTADO, "preco": 200.0}
    acao = decidir_gravacao(resultado_caro, preco_existente=150.0)
    assert acao == "ignorar"

def test_ignorar_quando_usuario_recusa(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    acao = decidir_gravacao(RESULTADO, preco_existente=150.0)
    assert acao == "ignorar"
```

- [ ] **Step 2: Rodar para confirmar falha**

```bash
python -m pytest tests/test_buscar_peca.py -v
```

Esperado: `ImportError`.

- [ ] **Step 3: Implementar `buscar_peca.py`**

```python
# scripts/02-pesquisa/buscar_peca.py
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from adaptadores._base import carregar_adaptador, carregar_concorrentes
from scraper import _gravar_resultados, OUTPUT_DIR

COLUNAS = ["numero_peca", "preco", "tipo_peca", "url_fonte", "disponibilidade", "observacao", "data_pesquisa", "fonte"]


def _preco_existente(adaptador_nome: str, numero_peca: str) -> float | None:
    dest = OUTPUT_DIR / f"{adaptador_nome}.xlsx"
    if not dest.exists():
        return None
    df = pd.read_excel(dest)
    linha = df[df["numero_peca"] == numero_peca]
    if linha.empty:
        return None
    return linha["preco"].min()


def decidir_gravacao(resultado: dict, preco_existente: float | None) -> str:
    if preco_existente is None:
        return "gravar"
    if resultado["preco"] < preco_existente:
        resp = input(
            f"  Preço atual: R$ {preco_existente:.2f} → Novo: R$ {resultado['preco']:.2f}. Gravar? [s/n] "
        ).strip().lower()
        return "gravar" if resp == "s" else "ignorar"
    return "ignorar"


def main():
    parser = argparse.ArgumentParser(description="Busca pontual de uma peça JD")
    parser.add_argument("numero_peca", help="Código da peça (ex: RE509672)")
    parser.add_argument("--concorrente", help="Rodar só este adaptador")
    args = parser.parse_args()

    concorrentes = [
        c for c in carregar_concorrentes()
        if c["ativo"] and c["modo"] == "scraper"
    ]
    if args.concorrente:
        concorrentes = [c for c in concorrentes if c.get("adaptador") == args.concorrente]

    concorrentes.sort(key=lambda c: c["prioridade"])
    encontrou = False

    for conc in concorrentes:
        adaptador_nome = conc["adaptador"]
        print(f"[{conc['nome']}] buscando {args.numero_peca}...", end=" ")

        try:
            mod = carregar_adaptador(adaptador_nome)
            retorno = mod.buscar(args.numero_peca)
        except Exception as e:
            print(f"ERRO: {e}")
            continue

        if not isinstance(retorno, list):
            print(f"não encontrado ({retorno})")
            continue

        encontrou = True
        for resultado in retorno:
            print(f"\n  R$ {resultado['preco']:.2f} | {resultado['tipo_peca']} | {resultado['url_fonte']}")
            preco_atual = _preco_existente(adaptador_nome, args.numero_peca)
            acao = decidir_gravacao(resultado, preco_atual)
            if acao == "gravar":
                _gravar_resultados(adaptador_nome, [resultado])
                print(f"  [SALVO] em output/concorrentes/{adaptador_nome}.xlsx")

    if not encontrou:
        print(f"\nNenhum resultado encontrado para {args.numero_peca}.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar os testes**

```bash
python -m pytest tests/test_buscar_peca.py -v
```

Esperado: 4 testes PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/02-pesquisa/buscar_peca.py tests/test_buscar_peca.py
git commit -m "feat(pricewatch): buscar_peca.py — busca pontual com gravação condicional"
```

---

## Task 7: `diagnostico.py` — Análise de novo concorrente

**Files:**

- Create: `scripts/02-pesquisa/diagnostico.py`

> Este componente não tem teste unitário puro — depende de rede real. O teste é manual: rodar contra um site conhecido.

- [ ] **Step 1: Implementar `diagnostico.py`**

```python
# scripts/02-pesquisa/diagnostico.py
import argparse
import json
import sys
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from adaptadores._base import carregar_concorrentes, CONCORRENTES_JSON

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SINAIS_PROTECAO = ["cf-browser-verification", "cloudflare", "captcha", "recaptcha", "__cf_bm"]


def _detectar_protecao(html: str, headers: dict) -> str | None:
    html_lower = html.lower()
    for sinal in SINAIS_PROTECAO:
        if sinal in html_lower:
            return sinal
    if "set-cookie" in str(headers).lower() and "__cf" in str(headers).lower():
        return "cloudflare_cookie"
    return None


def diagnosticar(url: str, nome: str) -> dict:
    resultado = {
        "acessivel": False,
        "tem_busca": False,
        "retorna_preco": False,
        "protecao": None,
        "recomendacao": "manual",
        "data": date.today().isoformat(),
    }

    print(f"\n[DIAGNOSTICO] {nome} — {url}")

    # 1. Acessibilidade
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resultado["acessivel"] = resp.status_code == 200
        print(f"  Acessível: {resultado['acessivel']} (HTTP {resp.status_code})")
    except requests.RequestException as e:
        print(f"  Acessível: False ({e})")
        return resultado

    # 2. Proteção anti-bot
    resultado["protecao"] = _detectar_protecao(resp.text, resp.headers)
    if resultado["protecao"]:
        print(f"  Proteção detectada: {resultado['protecao']}")
        resultado["recomendacao"] = "ia"
        return resultado

    soup = BeautifulSoup(resp.text, "html.parser")

    # 3. Campo de busca
    campo_busca = soup.find("input", {"type": ["search", "text"], "name": lambda n: n and "search" in n.lower()})
    if not campo_busca:
        campo_busca = soup.find("form", {"action": lambda a: a and "busca" in str(a).lower()})
    resultado["tem_busca"] = campo_busca is not None
    print(f"  Tem campo de busca: {resultado['tem_busca']}")

    # 4. Retorna preço — testa busca com peça genérica
    try:
        url_busca = url.rstrip("/") + "/busca?q=filtro"
        resp2 = requests.get(url_busca, headers=HEADERS, timeout=15)
        soup2 = BeautifulSoup(resp2.text, "html.parser")
        tem_preco = bool(
            soup2.find(text=lambda t: t and ("R$" in t or "reais" in t.lower()))
        )
        resultado["retorna_preco"] = tem_preco
        print(f"  Retorna preço na busca: {resultado['retorna_preco']}")
    except Exception:
        print(f"  Retorna preço na busca: False (erro ao buscar)")

    # 5. Recomendação
    if resultado["retorna_preco"] and not resultado["protecao"]:
        resultado["recomendacao"] = "scraper"
    elif resultado["acessivel"]:
        resultado["recomendacao"] = "ia"
    else:
        resultado["recomendacao"] = "manual"

    print(f"\n  >> Recomendação: {resultado['recomendacao'].upper()}")
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Diagnostica um site concorrente para o PriceWatch JD")
    parser.add_argument("--url", required=True, help="URL base do site")
    parser.add_argument("--nome", required=True, help="Nome do concorrente")
    args = parser.parse_args()

    diagnostico = diagnosticar(args.url, args.nome)

    resp = input("\nGravar em concorrentes.json? [s/n] ").strip().lower()
    if resp != "s":
        print("Não gravado.")
        return

    concorrentes = carregar_concorrentes()
    existente = next((c for c in concorrentes if c["url_base"] == args.url), None)

    if existente:
        existente["diagnostico"] = diagnostico
        existente["modo"] = diagnostico["recomendacao"]
        print(f"[ATUALIZADO] {args.nome}")
    else:
        concorrentes.append({
            "nome": args.nome,
            "url_base": args.url,
            "prioridade": max((c["prioridade"] for c in concorrentes), default=0) + 1,
            "ativo": True,
            "modo": diagnostico["recomendacao"],
            "adaptador": None if diagnostico["recomendacao"] != "scraper" else args.nome.lower().replace(" ", ""),
            "diagnostico": diagnostico,
        })
        print(f"[ADICIONADO] {args.nome}")

    with open(CONCORRENTES_JSON, "w", encoding="utf-8") as f:
        json.dump(concorrentes, f, ensure_ascii=False, indent=2)

    if diagnostico["recomendacao"] == "scraper":
        print(f"\n[PRÓXIMO PASSO] Crie o adaptador: scripts/02-pesquisa/adaptadores/{concorrentes[-1]['adaptador']}.py")
        print("  Implemente a função: def buscar(numero_peca: str) -> list[dict] | str | None")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Testar manualmente**

```bash
python scripts/02-pesquisa/diagnostico.py --url https://loja.tblagropecas.com.br --nome "TBL Agro Peças"
```

Esperado: relatório no terminal com recomendação `scraper` e prompt de confirmação.

- [ ] **Step 3: Commit**

```bash
git add scripts/02-pesquisa/diagnostico.py
git commit -m "feat(pricewatch): diagnostico.py — analisa site novo e recomenda modo de coleta"
```

---

## Task 8: `consolidar.py` — Excel final

**Files:**

- Create: `scripts/04-consolidacao/consolidar.py`
- Create: `tests/test_consolidar.py`
- Create: `tests/fixtures/concorrentes_mock/` (fixtures de teste)

- [ ] **Step 1: Criar fixtures de teste**

`tests/fixtures/concorrentes_mock/mercadolivre.xlsx` — criar via script:

```python
# Rodar uma vez para gerar a fixture:
import pandas as pd
from pathlib import Path

dest = Path("tests/fixtures/concorrentes_mock")
dest.mkdir(parents=True, exist_ok=True)

pd.DataFrame([
    {"numero_peca": "RE509672", "preco": 120.0, "tipo_peca": "original",
     "url_fonte": "https://ml.com/1", "disponibilidade": "Disponível",
     "observacao": "", "data_pesquisa": "2026-05-13", "fonte": "scraper"},
    {"numero_peca": "RE504836", "preco": 95.0, "tipo_peca": "similar",
     "url_fonte": "https://ml.com/2", "disponibilidade": "Disponível",
     "observacao": "", "data_pesquisa": "2026-05-13", "fonte": "scraper"},
]).to_excel(dest / "mercadolivre.xlsx", index=False)

pd.DataFrame([
    {"numero_peca": "RE509672", "preco": 110.0, "tipo_peca": "original",
     "url_fonte": "https://tblagro.com/1", "disponibilidade": "Disponível",
     "observacao": "", "data_pesquisa": "2026-05-13", "fonte": "scraper"},
]).to_excel(dest / "tblagro.xlsx", index=False)
```

Executar: `python -c "exec(open('tests/fixtures/criar_fixtures_consolidar.py').read())"` — ou copiar e rodar direto no terminal Python.

- [ ] **Step 2: Escrever os testes**

```python
# tests/test_consolidar.py
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts" / "04-consolidacao"))
from consolidar import consolidar_concorrentes, calcular_conclusao

FIXTURES = Path(__file__).parent / "fixtures" / "concorrentes_mock"

def test_elege_menor_preco_entre_concorrentes():
    df = consolidar_concorrentes(FIXTURES)
    row = df[df["numero_peca"] == "RE509672"].iloc[0]
    # tblagro tem 110, ml tem 120 — menor é tblagro
    assert row["menor_preco_paralelo"] == 110.0
    assert row["concorrente_mais_barato"] == "TBL Agro Peças" or "tblagro" in row["concorrente_mais_barato"].lower()

def test_conclusao_paralelo_mais_barato():
    assert calcular_conclusao(valor_inova=200.0, menor_paralelo=110.0) == "Paralelo mais barato"

def test_conclusao_inova_mais_competitiva():
    assert calcular_conclusao(valor_inova=100.0, menor_paralelo=150.0) == "Inova mais competitiva"

def test_conclusao_sem_paralelo():
    assert calcular_conclusao(valor_inova=100.0, menor_paralelo=None) == "Pesquisa pendente"
```

- [ ] **Step 3: Rodar para confirmar falha**

```bash
python -m pytest tests/test_consolidar.py -v
```

Esperado: `ImportError`.

- [ ] **Step 4: Implementar `consolidar.py`**

```python
# scripts/04-consolidacao/consolidar.py
import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).parents[2]
sys.path.insert(0, str(RAIZ / "scripts" / "02-pesquisa"))
from adaptadores._base import carregar_concorrentes  # noqa: E402
OUTPUT_DIR = RAIZ / "output" / "concorrentes"
RESULTADO_PATH = RAIZ / "output" / "resultados.xlsx"
LISTA_PATH = RAIZ / "data" / "lista_pecas.csv"

COLUNAS_RESULTADO = [
    "numero_peca", "descricao", "categoria", "valor_oficial_jd", "valor_inova",
    "menor_preco_paralelo", "concorrente_mais_barato", "url_fonte", "tipo_peca",
    "diferenca_rs", "diferenca_pct", "conclusao", "data_pesquisa", "status",
]


def calcular_conclusao(valor_inova: float, menor_paralelo: float | None) -> str:
    if menor_paralelo is None:
        return "Pesquisa pendente"
    if menor_paralelo < valor_inova:
        return "Paralelo mais barato"
    return "Inova mais competitiva"


def _mapa_adaptador_para_nome() -> dict[str, str]:
    """Mapeia slug do adaptador (nome do arquivo) para nome completo do concorrente."""
    try:
        concorrentes = carregar_concorrentes()
        return {c["adaptador"]: c["nome"] for c in concorrentes if c.get("adaptador")}
    except Exception:
        return {}


def consolidar_concorrentes(concorrentes_dir: Path) -> pd.DataFrame:
    """Lê todos os xlsx de concorrentes e retorna df com menor preço por peça."""
    mapa_nomes = _mapa_adaptador_para_nome()
    frames = []
    for xlsx in concorrentes_dir.glob("*.xlsx"):
        df = pd.read_excel(xlsx)
        slug = xlsx.stem
        df["_arquivo"] = mapa_nomes.get(slug, slug)  # nome completo ou slug como fallback
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    df_all = pd.concat(frames, ignore_index=True)

    # Menor preço por peça × concorrente (pode haver 3 linhas por peça por site)
    idx_min = df_all.groupby(["numero_peca", "_arquivo"])["preco"].idxmin()
    df_melhor_por_site = df_all.loc[idx_min]

    # Menor preço global por peça
    idx_global = df_melhor_por_site.groupby("numero_peca")["preco"].idxmin()
    df_final = df_melhor_por_site.loc[idx_global].copy()
    df_final = df_final.rename(columns={
        "preco": "menor_preco_paralelo",
        "_arquivo": "concorrente_mais_barato",
    })
    return df_final


def main(merge_ia: Path | None = None):
    if not LISTA_PATH.exists():
        print(f"[ERRO] {LISTA_PATH} não encontrado. Execute integrar_bd.py primeiro.")
        sys.exit(1)

    df_lista = pd.read_csv(LISTA_PATH)
    df_concorrentes = consolidar_concorrentes(OUTPUT_DIR)

    # Merge resultados IA se fornecidos
    if merge_ia and merge_ia.exists():
        df_ia = pd.read_csv(merge_ia)
        df_ia = df_ia.rename(columns={"preco": "menor_preco_paralelo", "concorrente": "concorrente_mais_barato"})
        df_concorrentes = pd.concat([df_concorrentes, df_ia], ignore_index=True)

    # Join com lista de peças
    df = df_lista.merge(df_concorrentes[
        ["numero_peca", "menor_preco_paralelo", "concorrente_mais_barato",
         "url_fonte", "tipo_peca", "data_pesquisa"]
    ], on="numero_peca", how="left")

    df["diferenca_rs"] = df["valor_inova"] - df["menor_preco_paralelo"]
    df["diferenca_pct"] = (df["diferenca_rs"] / df["valor_inova"] * 100).round(1)
    df["conclusao"] = df.apply(
        lambda r: calcular_conclusao(r["valor_inova"], r.get("menor_preco_paralelo")), axis=1
    )
    df["status"] = df["menor_preco_paralelo"].apply(
        lambda v: "Pesquisado" if pd.notna(v) else "Pendente IA"
    )

    df = df[COLUNAS_RESULTADO]
    RESULTADO_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(RESULTADO_PATH, index=False)
    print(f"[OK] {len(df)} peças consolidadas em {RESULTADO_PATH}")

    competitivas = (df["conclusao"] == "Inova mais competitiva").sum()
    print(f"  Inova mais competitiva: {competitivas}/{len(df)} ({competitivas/len(df)*100:.0f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolida resultados e gera Excel final")
    parser.add_argument("--merge-ia", type=Path, help="CSV com resultados do agente IA")
    args = parser.parse_args()
    main(args.merge_ia)
```

- [ ] **Step 5: Rodar os testes**

```bash
python -m pytest tests/test_consolidar.py -v
```

Esperado: 4 testes PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/04-consolidacao/consolidar.py tests/test_consolidar.py tests/fixtures/concorrentes_mock/
git commit -m "feat(pricewatch): consolidar.py — elege menor preço por peça e gera resultados.xlsx"
```

---

## Task 9: Smoke test end-to-end e README de uso

**Files:**

- Create: `tests/test_e2e_smoke.py`
- Modify: `README.md`

- [ ] **Step 1: Escrever smoke test e2e**

```python
# tests/test_e2e_smoke.py
"""
Smoke test: valida que o pipeline completo roda sem erros usando dados fictícios.
Não faz requisições reais — usa mocks para os adaptadores.
"""
import sys
import shutil
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "02-pesquisa"))
sys.path.insert(0, str(ROOT / "scripts" / "03-banco"))
sys.path.insert(0, str(ROOT / "scripts" / "04-consolidacao"))

from integrar_bd import normalizar_csv
from consolidar import calcular_conclusao, consolidar_concorrentes


@pytest.fixture
def tmp_projeto(tmp_path):
    (tmp_path / "output" / "concorrentes").mkdir(parents=True)
    (tmp_path / "data").mkdir()
    return tmp_path


def test_pipeline_integrar_bd(tmp_path):
    csv = tmp_path / "bd.csv"
    csv.write_text("numero_peca;descricao;categoria;valor_oficial_jd;valor_inova\nRE509672;Filtro;Filtros;185;150")
    df = normalizar_csv(csv)
    assert df.iloc[0]["numero_peca"] == "RE509672"
    assert df.iloc[0]["valor_inova"] == 150.0


def test_pipeline_consolidar_vazio(tmp_path):
    (tmp_path / "concorrentes").mkdir()
    df = consolidar_concorrentes(tmp_path / "concorrentes")
    assert df.empty


def test_calcular_conclusao_todos_casos():
    assert calcular_conclusao(200, 100) == "Paralelo mais barato"
    assert calcular_conclusao(100, 200) == "Inova mais competitiva"
    assert calcular_conclusao(100, None) == "Pesquisa pendente"
```

- [ ] **Step 2: Rodar smoke test**

```bash
python -m pytest tests/test_e2e_smoke.py -v
```

Esperado: 3 testes PASS.

- [ ] **Step 3: Rodar todos os testes**

```bash
python -m pytest tests/ -v --tb=short
```

Esperado: todos PASS.

- [ ] **Step 4: Commit final**

```bash
git add tests/test_e2e_smoke.py
git commit -m "test(pricewatch): smoke test e2e do pipeline completo"
```

---

## Referência Rápida de Comandos

```bash
# 1. Preparar lista de peças a partir do BD
python scripts/03-banco/integrar_bd.py --input exportacao_bd.csv

# 2. Diagnosticar novo concorrente
python scripts/02-pesquisa/diagnostico.py --url https://site.com --nome "Nome"

# 3. Rodar scraper completo
python scripts/02-pesquisa/scraper.py --lista data/lista_pecas.csv

# 4. Retomar execução interrompida
python scripts/02-pesquisa/scraper.py --lista data/lista_pecas.csv --retomar

# 5. Buscar uma peça específica
python scripts/02-pesquisa/buscar_peca.py RE509672

# 6. Ver fila de pendentes para o agente IA
python scripts/02-pesquisa/scraper.py --ver-fila

# 7. Gerar Excel final
python scripts/04-consolidacao/consolidar.py

# 8. Incorporar resultados do agente IA e gerar Excel final
python scripts/04-consolidacao/consolidar.py --merge-ia output/ia_resultados.csv

# 9. Rodar todos os testes
python -m pytest tests/ -v
```
