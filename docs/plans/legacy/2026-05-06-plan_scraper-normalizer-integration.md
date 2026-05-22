# Scraper-Normalizer Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Criar um pipeline unificado que converte HTML dinâmico (Playwright) para Markdown limpo (Markdownify) e, em seguida, aplica a normalização estruturada (Gold Standard) para garantir a consistência das APIs.

**Architecture:** 
- `scripts/dynamic_scraper.py`: Renderiza e salva HTML bruto.
- `scripts/converter.py`: Converte HTML -> .raw.md (limpeza básica).
- `scripts/normalize_endpoint_blocks.py`: Aplica a estrutura "Gold Standard" (YAML, cabeçalhos, tabelas).

**Tech Stack:** Python, Playwright, BeautifulSoup, Markdownify.

---

### Task 1: Criar Módulo de Conversão HTML -> Raw Markdown

**Files:**
- Create: `scripts/converter.py`

**Step 1: Implementar conversão bruta**
```python
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import sys

def convert_to_raw_md(html_file, md_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
        for e in soup(['nav', 'footer', 'header']): e.decompose()
        md_text = md(str(soup), heading_style="ATX")
        with open(md_file, 'w', encoding='utf-8') as out:
            out.write(md_text)

if __name__ == "__main__":
    convert_to_raw_md(sys.argv[1], sys.argv[2])
```

**Step 2: Commit**
```bash
git add scripts/converter.py
git commit -m "feat: add converter module for raw markdown"
```

---

### Task 2: Integrar Pipeline no Dispatcher

**Files:**
- Modify: `scripts/master_dispatcher.py`

**Step 1: Atualizar dispatcher para chamar o pipeline completo (scraper -> converter -> normalizer)**
```python
# ... logic to run:
# 1. dynamic_scraper.py
# 2. converter.py
# 3. normalize_endpoint_blocks.py
```

**Step 2: Commit**
```bash
git add scripts/master_dispatcher.py
git commit -m "feat: integrate pipeline in dispatcher"
```
