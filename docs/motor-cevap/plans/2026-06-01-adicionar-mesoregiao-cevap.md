# Plano de Implementação: Adição da Coluna Mesorregião no Motor CEVAP

> **Status:** Aprovado
> **Data:** 2026-06-01
> **Autor:** Gemini CLI Builder / Engenheiro de Software

---

## Passo 1: Preparação do Mapeamento de Cidades

No script `polimento_final_v5.py`, adicionaremos uma função auxiliar para carregar o JSON de mapeamento com `encoding='utf-8'` de forma segura, garantindo tratamento caso o arquivo esteja ausente.

```python
import json

def carregar_mesoregioes():
    caminho_json = r"C:\Projetos\Inova\projects\lead-csc-pops\data\config\cidade_mesoregiao.json"
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"AVISO: Falha ao carregar cidade_mesoregiao.json de {caminho_json}: {exc}")
        return {}
```

## Passo 2: Algoritmo de Casamento de Mesorregião

Aplicar a normalização e busca para cada linha do DataFrame correspondente à coluna `Cidade`.

```python
def obter_mesoregiao(cidade_uf, mapa_mesoregioes):
    if pd.isna(cidade_uf) or str(cidade_uf).strip() == "" or str(cidade_uf) == "Indisponível":
        return "Indisponível"
    
    # Exemplo: "Belo Horizonte/MG" -> "BELO HORIZONTE / MG"
    cid_limpa = str(cidade_uf).upper().strip()
    if "/" in cid_limpa:
        partes = [p.strip() for p in cid_limpa.split("/")]
        cid_normalizada = " / ".join(partes)
        cidade_pura = partes[0]
    else:
        cid_normalizada = cid_limpa
        cidade_pura = cid_limpa

    # Busca com fallbacks
    if cid_normalizada in mapa_mesoregioes:
        return mapa_mesoregioes[cid_normalizada]
    if cidade_pura in mapa_mesoregioes:
        return mapa_mesoregioes[cidade_pura]
    
    return "Indisponível"
```

## Passo 3: Integração no Pipeline de Polimento (`polimento_final_v5.py`)

No método `formatar_cevap_v4()` de `scripts/polimento_final_v5.py`:
1. Carregar o dicionário de mesorregiões.
2. Aplicar a transformação criando a coluna `Mesoregiao`.
3. Inserir a coluna `Mesoregiao` na lista `cols_finais` logo após a coluna `Cidade`.

## Passo 4: Atualização da Suite de Testes (`tests/test_columns.py`)

Adicionar `"Mesoregiao"` na lista de colunas esperadas `expected_cols` no arquivo `tests/test_columns.py` para garantir que as validações de integridade passem.

## Passo 5: Execução do Pipeline e Validação Empírica

1. Executar o pipeline de ponta a ponta:
   - `python scripts/resgate_dados_v4.py` (caso necessário para novos dados)
   - `python scripts/consolidate_cevap.py` (consolidar base)
   - `python scripts/polimento_final_v5.py` (aplicar polimento e nova coluna)
2. Rodar a validação do QA:
   - `python scripts/qa_latest_output.py`
3. Rodar os testes automatizados com `pytest` para certificar que todas as regras de negócio e contratos de colunas foram mantidos e validados.
