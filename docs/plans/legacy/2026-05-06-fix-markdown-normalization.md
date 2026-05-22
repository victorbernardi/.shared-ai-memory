# Refatoração do Normalizador de Markdown (IA-Friendly)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transformar o script `normalize_endpoint_blocks.py` em um gerador de Markdown de alta qualidade, livre de erros de linting e otimizado para IAs.

**Architecture:** Refatoração da função `build_markdown` para utilizar um pipeline de sanitização de strings e templates estruturados, garantindo unicidade de cabeçalhos, formatação rigorosa de JSON e alinhamento correto de tabelas.

**Tech Stack:** Python 3, Pytest (para TDD).

---

## 1. Task 1: Infraestrutura de Testes (TDD)

**Files:**

- Create: `tests/test_markdown_normalization.py`
- Modify: `scripts/normalize_endpoint_blocks.py`

### 1.1 Step 1: Criar teste para reproduzir erros de linting

```python
import pytest
from scripts.normalize_endpoint_blocks import build_markdown

def test_markdown_linting_rules():
    normalized = [
        {"method": "GET", "path": "/test1", "description": "Desc 1\n\n", "parameters": "Params 1", "request_json": "", "response_json": "{\"id\":1}"},
        {"method": "GET", "path": "/test2", "description": "Desc 2", "parameters": "Params 2", "request_json": "", "response_json": ""}
    ]
    result = build_markdown("Test API", "https://example.com/api", normalized)
    
    # MD024: Cabeçalhos duplicados (devemos mudar para algo único por endpoint)
    assert "### Descrição\n" not in result, "Ainda existe o cabeçalho estático '### Descrição'"
    assert "### Descrição: GET /test1" in result, "Cabeçalho não possui unicidade de endpoint"
    
    # Numeração dinâmica
    assert "## 2. GET /test1" in result, "Primeiro endpoint deve ser numerado como 2"
    assert "## 3. POST /test2" in result, "Segundo endpoint deve ser numerado como 3"
    
    # MD012: Múltiplas linhas em branco
    assert "\n\n\n" not in result, "Existem múltiplas linhas em branco consecutivas (> 1 linha vazia)"
    
    # MD034: Bare URLs
    assert "<https://example.com/api>" in result, "URL fonte não está envolvida em <>"
    
    # MD060: Alinhamento de Tabelas (pipes com espaço para estilo compact/aligned)
    assert "| --- | --- | --- |" in result, "Tabela não formatada com espaçamento correto | --- |"
    
    # MD031/MD040: Blocos de código JSON e espaços
    assert "```json\n{\n    \"id\": 1\n}\n```" in result, "JSON não foi formatado corretamente ou falta linha em branco"
    
    # MD040: Fallback para text se JSON for inválido
    assert "```text\ninvalid json\n```" in result, "Falha no fallback de linguagem para texto inválido"
```

### 1.2 Step 2: Executar teste e verificar falha

Run: `pytest tests/test_markdown_normalization.py -v`
Expected: FAIL (AssertionErrors)

---

## 2. Task 2: Refatoração da Lógica de Montagem (Headers e Strings)

**Files:**

- Modify: `scripts/normalize_endpoint_blocks.py`

### 2.1 Step 1: Implementar função auxiliar `sanitize_content(text)`

Adicionar uma função que faz `strip()` e colapsa quebras de linha (`re.sub(r'\n{3,}', '\n\n', text)`).

### 2.2 Step 2: Atualizar `build_markdown` para usar cabeçalhos únicos

Alterar os títulos estáticos para incluir o contexto do endpoint:

- `### Descrição: {method} {path}`
- `### Parâmetros / Campos: {method} {path}`
- `### Response Fields: {method} {path}`
- `### Exemplo JSON: {method} {path}`

### 2.3 Step 3: Corrigir formatação de URLs e Tabelas

- Envolver `{source}` em `<{source}>`.
- Mudar o separador da tabela de `|---|---|---|` para `| --- | --- | --- |`.

---

## 3. Task 3: Normalização de JSON (IA-Friendly)

**Files:**

- Modify: `scripts/normalize_endpoint_blocks.py`

### 3.1 Step 1: Implementar formatação rigorosa no `build_markdown`

Ao processar `ep["request_json"]` e `ep["response_json"]`:

- Tentar fazer `json.loads()` e depois `json.dumps(..., indent=4)`.
- Se falhar (JSON inválido da origem), manter o texto original mas ainda assim envolver com ` ```json `.
- Adicionar linha em branco obrigatória antes e depois dos blocos de código.

### 3.2 Step 2: Validar contra testes

Run: `pytest tests/test_markdown_normalization.py -v`
Expected: PASS

---

## 4. Task 4: Validação Final e Regeneração

**Files:**

- Modify: `output/md/field-operations.md` (via regeneração)

### 4.1 Step 1: Executar o script contra o arquivo real

Run: `python scripts/normalize_endpoint_blocks.py output/md/field-operations.raw.md --source https://developer.deere.com/dev-docs/field-operations --output-md output/md/field-operations.md`

### 4.2 Step 2: Verificar ausência de warnings no linter

Abrir `output/md/field-operations.md` e verificar visualmente ou via CLI se os erros sumiram.
