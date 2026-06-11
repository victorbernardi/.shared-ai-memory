# Fase 2 — Superpowers Cleaner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar módulo `superpowers_cleaner.py` que lê specs/plans de `docs/superpowers/` no root do Stout, aplica a Layer 2 da peneira (descarta frontmatter, checklists, placeholders, metainfo; preserva decisões, arquitetura, aprendizados), e escreve output em `memory/context-agent/cleaned/`. Integração com o comando `save` do context-agent para executar automaticamente.

**Architecture:** Módulo Python compartilhado em um único local (OpenCode install, por ser a instalação principal que já aponta a storage unificado), importado pelas demais instalações via `sys.path`. Cleaner opera sobre arquivos `.md` idempotentemente — reprocessar o mesmo arquivo não gera duplicatas. Output `cleaned/spec-<slug>.md` é referência; o sync para `raw/_pending/` acontece em fase posterior (integração com Ar9av).

**Tech Stack:** Python 3.13, pytest, stdlib (re, pathlib, datetime). Sem novas dependências.

---

## Contexto para o engenheiro

Pré-requisito: Fase 1 concluída (storage unificado em `memory/context-agent/cleaned/` existe).

Leia o spec em `docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md`, seção "Fase 2 — Limpeza de spec/plan do Superpowers", para ver as regras de limpeza completas.

**Estado atual:**
- `docs/superpowers/specs/` no root do Stout tem 15+ arquivos `.md` (specs de diversos projetos)
- `docs/superpowers/plans/` tem 10+ arquivos `.md`
- Nenhum deles foi processado ainda
- Os arquivos seguem um formato consistente: frontmatter YAML opcional, título H1, seções `## Problema`, `## Solução`, `## Arquitetura`, `## Fases`, `## Testes`, etc.

**Regras de limpeza (Layer 2):**

| Descarta | Preserva |
|---|---|
| Frontmatter YAML da skill | Título e data |
| Seção `## Checklist` de processo | Seção `## Problema` / `## Solução` |
| Placeholders (`TBD`, `TODO`, `<slug>`, `<placeholder>`) | Decisões explícitas |
| Referências a skills (`use X skill`, `skill Y`) | Arquitetura, fluxos, diagramas |
| Metainfo de aprovação (`Status: Aprovado`, `Status: Em revisão`) | Aprendizados e tradeoffs |
| Seção `## Out of scope` / `## Fora de escopo` | Seção `## In scope` / `## Em escopo` |
| Seção `## Execution Notes` / `## Execution Handoff` | Conteúdo técnico substantivo |
| Blocos de TDD steps (checkboxes com `- [ ]` e instrução passo-a-passo) | Blocos de código de exemplo (não-TDD) |

**Convenções:**
- Idempotência: mesma entrada → mesma saída; nunca duplica
- Nome de saída: `cleaned/spec-<slug>.md` ou `cleaned/plan-<slug>.md` onde `<slug>` vem do nome do arquivo original (sem data e sem extensão)
- Cabeçalho do arquivo limpo: título original + linha de origem (`> Origem: docs/superpowers/specs/<arquivo>.md`) + data
- Arquivos puramente processuais (TDD plan sem decisões) podem resultar em output vazio — não gerar arquivo nesse caso

---

## File Structure

**Será criado:**
- `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- `tests/context_agent/test_superpowers_cleaner.py`
- `tests/context_agent/fixtures/sample_spec_with_noise.md`
- `tests/context_agent/fixtures/sample_plan_with_tdd.md`
- `tests/context_agent/fixtures/sample_spec_pure_process.md`

**Será modificado:**
- `.opencode/skills/context-agent/scripts/config.py` (adicionar `SUPERPOWERS_DOCS_ROOT`, `CLEANED_DIR`)
- `.claude/skills/context-agent/scripts/config.py` (idem)
- `antigravity/skills/context-agent/scripts/config.py` (idem)
- `.opencode/skills/context-agent/scripts/context_manager.py` (adicionar comando `clean-superpowers`; comando `save` invoca cleaner)
- `.claude/skills/context-agent/scripts/context_manager.py` (idem)
- `antigravity/skills/context-agent/scripts/context_manager.py` (idem)

**Nota:** para evitar duplicação, as outras duas instalações (Claude, Antigravity) importarão o módulo via `sys.path` ou via cópia sincronizada. Escolhemos cópia sincronizada (simplicidade; scripts Python têm histórico de serem copiados entre instalações).

---

## Task 1: Fixtures de teste

**Files:**
- Create: `tests/context_agent/fixtures/sample_spec_with_noise.md`
- Create: `tests/context_agent/fixtures/sample_plan_with_tdd.md`
- Create: `tests/context_agent/fixtures/sample_spec_pure_process.md`

- [ ] **Step 1: Criar fixture com ruído típico de spec**

Criar `C:\Projetos\Stout\tests\context_agent\fixtures\sample_spec_with_noise.md`:

```markdown
---
name: exemplo-spec
description: Spec de exemplo para testar limpeza
status: Aprovado
---

# Exemplo — Feature X

**Data:** 2026-04-23
**Status:** Aprovado

## Problema

O sistema atual não suporta Y. Decidimos adotar Z como solução por três motivos:
1. Compatível com nossa arquitetura
2. Battle-tested
3. Baixo custo de migração

## Solução

Adotar Z com camada de adapter preservando contratos externos.

### Arquitetura

```
[Componente A] → [Adapter novo] → [Z]
```

TODO: detalhar interfaces do adapter.

## Checklist

- [x] Validar requisitos
- [ ] Escrever spec
- [ ] Obter aprovação

## In scope

- Adapter de Z
- Testes de regressão

## Out of scope

- Migração de componente A
- UI changes

## Execution Notes

Para executar: use a skill `writing-plans`. TBD sobre integração com CI.
```

- [ ] **Step 2: Criar fixture de plano com muito TDD**

Criar `C:\Projetos\Stout\tests\context_agent\fixtures\sample_plan_with_tdd.md`:

```markdown
# Plan — Feature X

**Goal:** Implementar Y.

**Architecture:** Z adapter em Python.

## Task 1: Setup

- [ ] **Step 1: Criar arquivo**

```python
def foo():
    pass
```

- [ ] **Step 2: Rodar teste**

Run: `pytest`
Expected: PASS

- [ ] **Step 3: Commit**

## Decisões

Optamos por manter o adapter stateless para facilitar testes.
```

- [ ] **Step 3: Criar fixture puramente processual**

Criar `C:\Projetos\Stout\tests\context_agent\fixtures\sample_spec_pure_process.md`:

```markdown
# Checklist de release

## Checklist

- [ ] Rodar testes
- [ ] Criar tag
- [ ] Publicar release

## Execution Notes

Use a skill `writing-plans`. TBD.

## Out of scope

Tudo fora do processo de release.
```

- [ ] **Step 4: Commit fixtures**

```bash
git add tests/context_agent/fixtures/
git commit -m "test: fixtures para superpowers_cleaner"
```

---

## Task 2: Módulo `superpowers_cleaner.py` — função `strip_frontmatter`

**Files:**
- Create: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- Test: `tests/context_agent/test_superpowers_cleaner.py`

- [ ] **Step 1: Escrever teste para `strip_frontmatter`**

Criar `C:\Projetos\Stout\tests\context_agent\test_superpowers_cleaner.py`:

```python
"""Testes do superpowers_cleaner."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
FIXTURES = STOUT_ROOT / "tests" / "context_agent" / "fixtures"
CLEANER_DIR = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(CLEANER_DIR))
    for m in ("superpowers_cleaner", "config"):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(CLEANER_DIR))


def test_strip_frontmatter_removes_yaml_block() -> None:
    from superpowers_cleaner import strip_frontmatter
    text = "---\nname: x\nstatus: Aprovado\n---\n\n# Title\nBody"
    result = strip_frontmatter(text)
    assert result == "# Title\nBody"


def test_strip_frontmatter_no_frontmatter_passthrough() -> None:
    from superpowers_cleaner import strip_frontmatter
    text = "# Title\nBody"
    assert strip_frontmatter(text) == "# Title\nBody"


def test_strip_frontmatter_handles_windows_newlines() -> None:
    from superpowers_cleaner import strip_frontmatter
    text = "---\r\nname: x\r\n---\r\n\r\n# Title"
    result = strip_frontmatter(text)
    assert result.startswith("# Title")
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py::test_strip_frontmatter_removes_yaml_block -v`
Expected: FAIL — módulo `superpowers_cleaner` não existe.

- [ ] **Step 3: Criar módulo com `strip_frontmatter`**

Criar `C:\Projetos\Stout\.opencode\skills\context-agent\scripts\superpowers_cleaner.py`:

```python
"""
Layer 2 da peneira: limpeza de spec/plan do Superpowers.
Lê arquivos em docs/superpowers/{specs,plans}/ e produz versões limpas
em memory/context-agent/cleaned/.

Regras completas: ver docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md,
seção Fase 2.
"""

from __future__ import annotations

import re
from pathlib import Path


def strip_frontmatter(text: str) -> str:
    """Remove bloco YAML frontmatter do topo, se existir."""
    if not text.startswith("---"):
        return text
    # Encontrar o próximo "---" que fecha o frontmatter
    pattern = re.compile(r"^---\r?\n.*?\r?\n---\r?\n\r?\n?", re.DOTALL)
    return pattern.sub("", text, count=1)
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add .opencode/skills/context-agent/scripts/superpowers_cleaner.py \
        tests/context_agent/test_superpowers_cleaner.py
git commit -m "feat: strip_frontmatter no superpowers_cleaner"
```

---

## Task 3: Remover seções descartáveis (checklist, out-of-scope, execution notes)

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- Modify: `tests/context_agent/test_superpowers_cleaner.py`

- [ ] **Step 1: Escrever teste para remoção de seções**

Adicionar ao fim de `tests/context_agent/test_superpowers_cleaner.py`:

```python


def test_remove_sections_strips_checklist() -> None:
    from superpowers_cleaner import remove_sections
    text = "# T\n\n## Problema\nA\n\n## Checklist\n- x\n\n## Solucao\nB\n"
    result = remove_sections(text)
    assert "## Checklist" not in result
    assert "## Problema" in result
    assert "## Solucao" in result


def test_remove_sections_strips_out_of_scope() -> None:
    from superpowers_cleaner import remove_sections
    text = "## In scope\nA\n\n## Out of scope\nB\n\n## Notes\nC\n"
    result = remove_sections(text)
    assert "## Out of scope" not in result
    assert "## In scope" in result


def test_remove_sections_strips_portuguese_variants() -> None:
    from superpowers_cleaner import remove_sections
    text = "## Em escopo\nA\n\n## Fora de escopo\nB\n"
    result = remove_sections(text)
    assert "## Fora de escopo" not in result
    assert "## Em escopo" in result


def test_remove_sections_strips_execution_notes() -> None:
    from superpowers_cleaner import remove_sections
    text = "# T\n\n## Problema\nX\n\n## Execution Notes\nTBD\n"
    result = remove_sections(text)
    assert "Execution Notes" not in result


def test_remove_sections_is_case_insensitive() -> None:
    from superpowers_cleaner import remove_sections
    text = "## CHECKLIST\nx\n\n## Problema\ny\n"
    result = remove_sections(text)
    assert "## CHECKLIST" not in result
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 5 novos testes FALHAM.

- [ ] **Step 3: Implementar `remove_sections`**

Adicionar ao fim de `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`:

```python


DISCARDABLE_HEADINGS = [
    r"checklist",
    r"out\s*of\s*scope",
    r"fora\s*de\s*escopo",
    r"execution\s*notes",
    r"execution\s*handoff",
    r"self[- ]review",
]


def remove_sections(text: str) -> str:
    """Remove secoes H2 com titulos descartaveis ate o proximo H2 ou EOF."""
    pattern_str = (
        r"^##\s+(?:" + "|".join(DISCARDABLE_HEADINGS) + r")\b.*?"
        r"(?=^##\s+|\Z)"
    )
    pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return pattern.sub("", text)
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add .opencode/skills/context-agent/scripts/superpowers_cleaner.py \
        tests/context_agent/test_superpowers_cleaner.py
git commit -m "feat: remove_sections descarta secoes processuais"
```

---

## Task 4: Remover linhas de metainfo e referencias a skills

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- Modify: `tests/context_agent/test_superpowers_cleaner.py`

- [ ] **Step 1: Escrever teste**

Adicionar ao `tests/context_agent/test_superpowers_cleaner.py`:

```python


def test_remove_metainfo_strips_status_line() -> None:
    from superpowers_cleaner import remove_metainfo
    text = "# Title\n\n**Status:** Aprovado\n\n**Data:** 2026-04-23\n\nBody"
    result = remove_metainfo(text)
    assert "**Status:**" not in result
    assert "**Data:**" in result  # Data eh preservado


def test_remove_metainfo_strips_skill_references() -> None:
    from superpowers_cleaner import remove_metainfo
    text = "Use a skill `writing-plans` para executar. Blah."
    result = remove_metainfo(text)
    assert "writing-plans" not in result
    assert "Blah" in result


def test_remove_metainfo_strips_tdd_markers() -> None:
    from superpowers_cleaner import remove_metainfo
    text = "- [ ] **Step 1: Write test**\n\nConteudo importante."
    result = remove_metainfo(text)
    assert "Step 1" not in result
    assert "Conteudo importante" in result


def test_remove_metainfo_strips_placeholders() -> None:
    from superpowers_cleaner import remove_metainfo
    text = "Decidimos X. TODO: validar. TBD sobre Y."
    result = remove_metainfo(text)
    # Remove linhas com placeholders, nao conteudo ao redor
    # Aqui as tres ficam na mesma linha, esperamos a linha inteira desaparecer
    assert "TBD" not in result
    assert "TODO" not in result
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 4 novos testes FALHAM.

- [ ] **Step 3: Implementar `remove_metainfo`**

Adicionar ao `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`:

```python


_METAINFO_PATTERNS = [
    # Linhas começando com **Status:** (bold)
    re.compile(r"^\*\*Status:\*\*.*$", re.MULTILINE),
    # Referencias a skills (`writing-plans`, `superpowers:X`)
    re.compile(r"(?:a\s+)?skill\s+[`\"']?[\w:-]+[`\"']?", re.IGNORECASE),
    # TDD step markers: - [ ] **Step N: ...**
    re.compile(r"^-\s*\[\s*[x ]\s*\]\s*\*\*Step\s+\d+:.*?\*\*.*$", re.MULTILINE | re.IGNORECASE),
    # Linhas com placeholders TBD/TODO isolados ou embutidos
    re.compile(r"^.*\b(?:TBD|TODO)\b.*$", re.MULTILINE),
]


def remove_metainfo(text: str) -> str:
    """Remove linhas de metainfo (status, refs a skills, TDD markers, placeholders)."""
    for pattern in _METAINFO_PATTERNS:
        text = pattern.sub("", text)
    # Colapsar linhas em branco multiplas
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 12 passed.

- [ ] **Step 5: Commit**

```bash
git add .opencode/skills/context-agent/scripts/superpowers_cleaner.py \
        tests/context_agent/test_superpowers_cleaner.py
git commit -m "feat: remove_metainfo descarta status, refs e placeholders"
```

---

## Task 5: Função `clean_file` orquestra as transformações

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- Modify: `tests/context_agent/test_superpowers_cleaner.py`

- [ ] **Step 1: Escrever teste usando fixtures**

Adicionar ao `tests/context_agent/test_superpowers_cleaner.py`:

```python


def test_clean_file_spec_with_noise_preserves_substance() -> None:
    from superpowers_cleaner import clean_file
    input_path = FIXTURES / "sample_spec_with_noise.md"
    result = clean_file(input_path)

    assert result is not None
    # Preserva titulo
    assert "# Exemplo — Feature X" in result
    # Preserva problema e decisao
    assert "não suporta Y" in result
    assert "Decidimos adotar Z" in result
    # Preserva arquitetura
    assert "[Componente A]" in result
    # Remove frontmatter
    assert "name: exemplo-spec" not in result
    # Remove checklist
    assert "## Checklist" not in result
    # Remove out of scope
    assert "Out of scope" not in result
    # Remove execution notes
    assert "Execution Notes" not in result
    # Remove placeholders TODO/TBD
    assert "TODO:" not in result
    assert "TBD" not in result
    # Remove status
    assert "**Status:**" not in result
    # Remove ref a skill writing-plans
    assert "writing-plans" not in result


def test_clean_file_pure_process_returns_none() -> None:
    """Arquivo sem conteudo substantivo resulta em None (nao gera arquivo)."""
    from superpowers_cleaner import clean_file
    input_path = FIXTURES / "sample_spec_pure_process.md"
    result = clean_file(input_path)

    # Output vazio ou quase vazio deve ser None
    assert result is None or len(result.strip().split("\n")) < 3


def test_clean_file_plan_with_tdd_preserves_decisions() -> None:
    from superpowers_cleaner import clean_file
    input_path = FIXTURES / "sample_plan_with_tdd.md"
    result = clean_file(input_path)

    assert result is not None
    # Decisoes preservadas
    assert "Optamos por manter" in result
    # TDD steps removidos
    assert "Step 1" not in result
    assert "pytest" not in result
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 3 novos testes FALHAM (função não existe).

- [ ] **Step 3: Implementar `clean_file`**

Adicionar ao fim de `superpowers_cleaner.py`:

```python


_MIN_CLEANED_LINES = 3  # Se resultar em menos linhas, considera vazio


def clean_file(path: Path) -> str | None:
    """Le um arquivo spec/plan e retorna versao limpa, ou None se vazio."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")

    cleaned = strip_frontmatter(text)
    cleaned = remove_sections(cleaned)
    cleaned = remove_metainfo(cleaned)

    # Colapsar whitespace final
    cleaned = cleaned.strip()
    if not cleaned:
        return None

    substantive_lines = [
        line for line in cleaned.split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    if len(substantive_lines) < _MIN_CLEANED_LINES:
        return None

    # Adicionar cabecalho com origem
    header = f"> Origem: {path.as_posix()}\n\n"
    return header + cleaned + "\n"
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 15 passed.

- [ ] **Step 5: Commit**

```bash
git add .opencode/skills/context-agent/scripts/superpowers_cleaner.py \
        tests/context_agent/test_superpowers_cleaner.py
git commit -m "feat: clean_file orquestra transformacoes da Layer 2"
```

---

## Task 6: Função `clean_all` escreve em `memory/context-agent/cleaned/`

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py`
- Modify: `.opencode/skills/context-agent/scripts/config.py` (adicionar `SUPERPOWERS_DOCS_ROOT`, `CLEANED_DIR`)
- Modify: `tests/context_agent/test_superpowers_cleaner.py`

- [ ] **Step 1: Adicionar paths ao config.py**

Em `C:\Projetos\Stout\.opencode\skills\context-agent\scripts\config.py`, após `DB_PATH`, adicionar:

```python

# ── Superpowers docs (input da Layer 2) ─────────────────────────────
SUPERPOWERS_DOCS_ROOT = STOUT_ROOT / "docs" / "superpowers"
SPECS_DIR = SUPERPOWERS_DOCS_ROOT / "specs"
PLANS_DIR = SUPERPOWERS_DOCS_ROOT / "plans"

# ── Cleaned output (Layer 2) ────────────────────────────────────────
CLEANED_DIR = CONTEXT_AGENT_DATA_ROOT / "cleaned"
```

Repetir a mesma adição nos outros dois `config.py`:
- `C:\Projetos\Stout\.claude\skills\context-agent\scripts\config.py`
- `C:\Projetos\Stout\antigravity\skills\context-agent\scripts\config.py`

- [ ] **Step 2: Escrever teste para `clean_all`**

Adicionar ao `tests/context_agent/test_superpowers_cleaner.py`:

```python


def test_clean_all_writes_spec_files(tmp_path: Path, monkeypatch) -> None:
    from superpowers_cleaner import clean_all
    # Redirecionar paths para tmp
    sys.path.insert(0, str(CLEANER_DIR))
    import superpowers_cleaner
    specs = tmp_path / "specs"
    plans = tmp_path / "plans"
    cleaned = tmp_path / "cleaned"
    specs.mkdir()
    plans.mkdir()
    cleaned.mkdir()

    spec_src = FIXTURES / "sample_spec_with_noise.md"
    (specs / "2026-04-23-feature-x-design.md").write_text(
        spec_src.read_text(encoding="utf-8"), encoding="utf-8"
    )

    monkeypatch.setattr(superpowers_cleaner, "SPECS_DIR", specs)
    monkeypatch.setattr(superpowers_cleaner, "PLANS_DIR", plans)
    monkeypatch.setattr(superpowers_cleaner, "CLEANED_DIR", cleaned)

    written = clean_all()
    assert len(written) == 1
    assert (cleaned / "spec-feature-x.md").exists()


def test_clean_all_skips_pure_process_files(tmp_path: Path, monkeypatch) -> None:
    from superpowers_cleaner import clean_all
    sys.path.insert(0, str(CLEANER_DIR))
    import superpowers_cleaner
    specs = tmp_path / "specs"
    plans = tmp_path / "plans"
    cleaned = tmp_path / "cleaned"
    specs.mkdir(); plans.mkdir(); cleaned.mkdir()

    pure = FIXTURES / "sample_spec_pure_process.md"
    (specs / "2026-04-23-release-checklist-design.md").write_text(
        pure.read_text(encoding="utf-8"), encoding="utf-8"
    )

    monkeypatch.setattr(superpowers_cleaner, "SPECS_DIR", specs)
    monkeypatch.setattr(superpowers_cleaner, "PLANS_DIR", plans)
    monkeypatch.setattr(superpowers_cleaner, "CLEANED_DIR", cleaned)

    written = clean_all()
    assert written == []
    assert list(cleaned.iterdir()) == []


def test_clean_all_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    """Rodar duas vezes o mesmo input produz o mesmo output."""
    from superpowers_cleaner import clean_all
    sys.path.insert(0, str(CLEANER_DIR))
    import superpowers_cleaner
    specs = tmp_path / "specs"
    plans = tmp_path / "plans"
    cleaned = tmp_path / "cleaned"
    specs.mkdir(); plans.mkdir(); cleaned.mkdir()

    spec_src = FIXTURES / "sample_spec_with_noise.md"
    (specs / "2026-04-23-feature-x-design.md").write_text(
        spec_src.read_text(encoding="utf-8"), encoding="utf-8"
    )

    monkeypatch.setattr(superpowers_cleaner, "SPECS_DIR", specs)
    monkeypatch.setattr(superpowers_cleaner, "PLANS_DIR", plans)
    monkeypatch.setattr(superpowers_cleaner, "CLEANED_DIR", cleaned)

    first = clean_all()
    first_content = (cleaned / "spec-feature-x.md").read_text(encoding="utf-8")
    second = clean_all()
    second_content = (cleaned / "spec-feature-x.md").read_text(encoding="utf-8")
    assert first_content == second_content
```

- [ ] **Step 3: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 3 novos testes FALHAM.

- [ ] **Step 4: Implementar `clean_all` e helper de slug**

No topo de `superpowers_cleaner.py`, adicionar import:

```python
from config import SPECS_DIR, PLANS_DIR, CLEANED_DIR
```

Adicionar ao fim do arquivo:

```python


_SLUG_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_SLUG_DESIGN_SUFFIX = re.compile(r"-design$")


def _slug_from_filename(filename: str) -> str:
    """Extrai slug util do nome do arquivo."""
    stem = Path(filename).stem
    stem = _SLUG_DATE_PREFIX.sub("", stem)
    stem = _SLUG_DESIGN_SUFFIX.sub("", stem)
    return stem


def clean_all() -> list[Path]:
    """Processa todos os specs e plans; retorna lista de arquivos gravados."""
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for src_dir, prefix in [(SPECS_DIR, "spec"), (PLANS_DIR, "plan")]:
        if not src_dir.exists():
            continue
        for src in sorted(src_dir.glob("*.md")):
            result = clean_file(src)
            if result is None:
                continue
            slug = _slug_from_filename(src.name)
            out_path = CLEANED_DIR / f"{prefix}-{slug}.md"
            # Idempotencia: so escreve se conteudo mudou
            if out_path.exists() and out_path.read_text(encoding="utf-8") == result:
                written.append(out_path)
                continue
            out_path.write_text(result, encoding="utf-8")
            written.append(out_path)
    return written
```

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_superpowers_cleaner.py -v`
Expected: 18 passed.

- [ ] **Step 6: Commit**

```bash
git add .opencode/skills/context-agent/scripts/superpowers_cleaner.py \
        .opencode/skills/context-agent/scripts/config.py \
        .claude/skills/context-agent/scripts/config.py \
        antigravity/skills/context-agent/scripts/config.py \
        tests/context_agent/test_superpowers_cleaner.py
git commit -m "feat: clean_all itera specs/plans e grava cleaned/ idempotente"
```

---

## Task 7: Sincronizar `superpowers_cleaner.py` para as outras 2 instalações

**Files:**
- Copy: `.opencode/skills/context-agent/scripts/superpowers_cleaner.py` → `.claude/skills/context-agent/scripts/superpowers_cleaner.py`
- Copy: idem → `antigravity/skills/context-agent/scripts/superpowers_cleaner.py`
- Test: `tests/context_agent/test_cleaner_sync.py`

- [ ] **Step 1: Escrever teste que valida cópias sincronizadas**

Criar `C:\Projetos\Stout\tests\context_agent\test_cleaner_sync.py`:

```python
"""Valida que superpowers_cleaner.py tem mesmo conteudo nas 3 installs."""
import hashlib
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")
INSTALLS = [
    STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts" / "superpowers_cleaner.py",
    STOUT_ROOT / ".claude" / "skills" / "context-agent" / "scripts" / "superpowers_cleaner.py",
    STOUT_ROOT / "antigravity" / "skills" / "context-management" / "context-agent" / "scripts" / "superpowers_cleaner.py",
]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cleaner_identical_across_installs() -> None:
    assert all(p.exists() for p in INSTALLS), f"Missing: {[p for p in INSTALLS if not p.exists()]}"
    hashes = [_hash(p) for p in INSTALLS]
    assert len(set(hashes)) == 1, f"Divergencia entre installs: {hashes}"
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_cleaner_sync.py -v`
Expected: FAIL — arquivos não existem nas outras 2 installs.

- [ ] **Step 3: Copiar o arquivo**

```bash
cp .opencode/skills/context-agent/scripts/superpowers_cleaner.py .claude/skills/context-agent/scripts/superpowers_cleaner.py
cp .opencode/skills/context-agent/scripts/superpowers_cleaner.py antigravity/skills/context-agent/scripts/superpowers_cleaner.py
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_cleaner_sync.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/context-agent/scripts/superpowers_cleaner.py \
        antigravity/skills/context-agent/scripts/superpowers_cleaner.py \
        tests/context_agent/test_cleaner_sync.py
git commit -m "chore: sincroniza superpowers_cleaner.py nas 3 installs"
```

---

## Task 8: Novo comando CLI `clean-superpowers` e integração com `save`

**Files:**
- Modify: `.opencode/skills/context-agent/scripts/context_manager.py` (e nas 3 installs)
- Test: `tests/context_agent/test_cleaner_cli.py`

- [ ] **Step 1: Escrever teste de CLI**

Criar `C:\Projetos\Stout\tests\context_agent\test_cleaner_cli.py`:

```python
"""Valida CLI do cleaner."""
import subprocess
import sys
from pathlib import Path

STOUT_ROOT = Path(r"C:\Projetos\Stout")


def test_clean_superpowers_command_exists_opencode() -> None:
    script = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts" / "context_manager.py"
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert "clean-superpowers" in result.stdout


def test_clean_superpowers_command_runs_opencode() -> None:
    script = STOUT_ROOT / ".opencode" / "skills" / "context-agent" / "scripts" / "context_manager.py"
    result = subprocess.run(
        [sys.executable, str(script), "clean-superpowers"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest tests/context_agent/test_cleaner_cli.py -v`
Expected: FAIL.

- [ ] **Step 3: Adicionar comando `clean-superpowers` ao `context_manager.py`**

Em `C:\Projetos\Stout\.opencode\skills\context-agent\scripts\context_manager.py`:

Após a linha `from search import init_search_db, index_session, search as fts_search, reindex_all` (linha 51), adicionar:

```python
from superpowers_cleaner import clean_all as clean_superpowers_all
```

Adicionar função antes de `def main():`:

```python
def cmd_clean_superpowers(args):
    """Aplica Layer 2 da peneira: limpa specs e plans do Superpowers."""
    written = clean_superpowers_all()
    if not written:
        print("Nenhum spec/plan com conteudo substantivo para limpar.")
        return
    print(f"Processados {len(written)} arquivo(s):")
    for path in written:
        print(f"  - {path.name}")
```

Dentro de `def main():`, após `subparsers.add_parser("maintain", help="Auto-manutenção")`, adicionar:

```python
    # clean-superpowers
    subparsers.add_parser("clean-superpowers", help="Aplicar Layer 2 da peneira em specs/plans")
```

Dentro do dict `commands` (antes de `commands[args.command](args)`), adicionar entrada:

```python
        "clean-superpowers": cmd_clean_superpowers,
```

Adicionar invocação automática ao final de `cmd_save`, antes do print final ("Contexto da sessão ..."):

```python
    # Layer 2: limpar specs/plans do Superpowers
    try:
        cleaned_paths = clean_superpowers_all()
        if cleaned_paths:
            print(f"  Layer 2: {len(cleaned_paths)} spec/plan limpos")
    except Exception as exc:  # noqa: BLE001
        print(f"  Aviso: falha ao limpar superpowers ({exc})")
```

- [ ] **Step 4: Aplicar as mesmas mudanças nas outras 2 installs**

Aplicar exatamente as mesmas modificações acima em:
- `C:\Projetos\Stout\.claude\skills\context-agent\scripts\context_manager.py`
- `C:\Projetos\Stout\antigravity\skills\context-agent\scripts\context_manager.py`

- [ ] **Step 5: Rodar teste para confirmar que passa**

Run: `pytest tests/context_agent/test_cleaner_cli.py -v`
Expected: 2 passed.

- [ ] **Step 6: Rodar suite completa para garantir sem regressao**

Run: `pytest tests/context_agent/ -v`
Expected: todos os ~20 testes da Fase 1 + Fase 2 passam.

- [ ] **Step 7: Smoke test manual em specs reais**

Run:
```bash
python .opencode/skills/context-agent/scripts/context_manager.py clean-superpowers
```
Expected: processa specs em `docs/superpowers/specs/` e plans em `docs/superpowers/plans/`, gera `memory/context-agent/cleaned/spec-*.md` e `plan-*.md`.

Inspecionar manualmente alguns outputs em `memory/context-agent/cleaned/` — verificar que são legíveis e preservam decisões/arquitetura.

- [ ] **Step 8: Commit**

```bash
git add .opencode/skills/context-agent/scripts/context_manager.py \
        .claude/skills/context-agent/scripts/context_manager.py \
        antigravity/skills/context-agent/scripts/context_manager.py \
        tests/context_agent/test_cleaner_cli.py
git commit -m "feat: comando clean-superpowers + auto-invocacao no save"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ Modulo `superpowers_cleaner.py` criado
- ✅ Varre `docs/superpowers/specs/` e `docs/superpowers/plans/` → Task 6 (`clean_all`)
- ✅ Regras de descarte aplicadas (frontmatter, checklist, out-of-scope, execution notes, metainfo, skill refs, TDD markers, placeholders)
- ✅ Preserva título/data/decisões/arquitetura/aprendizados
- ✅ Output em `memory/context-agent/cleaned/`
- ✅ Idempotencia
- ✅ Arquivos puramente processuais geram None (sem output)
- ✅ Integracao com `save` do context-agent
- ✅ Sincronizacao entre 3 installs (Task 7)

**2. Placeholder scan:** nenhum TBD/TODO no plano; código completo em cada step; comandos exatos.

**3. Type consistency:** `clean_file` retorna `str | None`; `clean_all` retorna `list[Path]`; consistent across tasks.

---

## Dependencies

- **Bloqueado por:** Fase 1 (storage unificado e `SESSION_ORIGIN` em config.py)
- **Bloqueia:** Fase 3 (adapter `cleaned_to_pending.py` depende de arquivos em `cleaned/`)

---

## Execution Notes

- Se um spec tiver muito YAML frontmatter complexo, ajustar regex em `strip_frontmatter` para suportar aninhamento.
- Se `clean_all()` retornar menos arquivos do que o esperado, provavelmente `_MIN_CLEANED_LINES=3` está descartando conteúdo legítimo. Ajustar após ver outputs reais.
- A integração com `cmd_save` pode gerar ruído no log se docs/superpowers/ estiver vazio. Aceitável — o cleaner retorna lista vazia silenciosamente.
