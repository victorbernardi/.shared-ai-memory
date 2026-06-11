# Fase 5 — INDEX + NLM Sync + Feedback Persistente

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar o ciclo do wiki: (1) gerar `INDEX.md` como ponto de entrada para CLIs, referenciado nos system prompts dos 4 agentes; (2) transformar `SUGESTOES-HOJE.md` em acumulativo com embasamento via NotebookLM; (3) sincronizar automaticamente wiki → NotebookLM (notebook `987bb91c-86a3-4a9a-a3db-4dbaa150bd18`) com manifesto local; (4) portar comportamento de leitura/feedback do Bibliotecário para a skill Superpowers compartilhada entre os 4 agentes.

**Architecture:** Todas as transformações são novos módulos Python em `wiki-compiler/` (exceto as modificações de system prompts, que são arquivos markdown em locais específicos de cada agente). Integração com Ar9av acontece via hooks pós-compile no `run_post_process.sh`. NLM é acessado via MCP `notebooklm-mcp` quando disponível, com degradação graciosa se falhar.

**Tech Stack:** Python 3.13, pytest, MCP `notebooklm-mcp` (via subprocess ou biblioteca Python). Markdown para system prompts. Sem novas dependências diretas.

---

## Contexto para o engenheiro

Pré-requisitos: Fases 1-4 concluídas. Vault em produção, saudável. Context-agent unificado. Ar9av compilando.

Leia:
- `docs/superpowers/specs/2026-04-23-llm-wiki-reforma-design.md`, Seção Fase 5
- `wiki-compiler/docs/superpowers/specs/2026-04-15-retroalimentacao-wiki-antigravity-design.md` (design original do feedback loop; estender para 4 agentes)

**Notebooks NLM importantes:**
- **Output sync:** `987bb91c-86a3-4a9a-a3db-4dbaa150bd18` — destino único dos uploads de páginas do wiki
- **Research (input para sugestões):** todos os notebooks com "estudo" no título (filtrados via `notebook_list()`)

**MCP NLM:**
- Ferramenta esperada: `notebooklm-mcp` (ver se está conectado: `mcp list` ou similar)
- Tools relevantes:
  - `notebook_list()` — lista todos os notebooks
  - `cross_notebook_query(notebook_ids, query)` — consulta múltiplos
  - `source_add(notebook_id, source_type, file_path | text | url)` — adiciona fonte
  - `notebook_get(notebook_id)` — lista sources de um notebook (para sync delta)

Se o MCP estiver offline: rodar `nlm login` ou usar save_auth_tokens. Fallback: scripts logam a pendência e continuam. Nenhuma fase crítica depende 100% do NLM.

**Paths relevantes:**
- Vault: `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/`
- `INDEX.md` — gerado em `<vault>/INDEX.md`
- `SUGESTOES-HOJE.md` — `<vault>/SUGESTOES-HOJE.md` (já existe)
- Manifesto NLM sync: `<vault>/.nlm_sync_manifest.json`

**Skill Superpowers shared location:**
- Claude Code: `~/.claude/skills/using-superpowers/` (via plugin)
- OpenCode: `.opencode/skills/using-superpowers/` (via plugin)
- Gemini CLI + Antigravity: `antigravity/skills/using-superpowers/` (compartilhada)

---

## File Structure

**Será criado:**
- `wiki-compiler/adapters/index_generator.py`
- `wiki-compiler/adapters/suggestions_manager.py`
- `wiki-compiler/adapters/nlm_sync.py`
- `wiki-compiler/adapters/nlm_research.py`
- `wiki-compiler/adapters/nlm_client.py` (wrapper do MCP)
- `wiki-compiler/tests/test_index_generator.py`
- `wiki-compiler/tests/test_suggestions_manager.py`
- `wiki-compiler/tests/test_nlm_sync.py`
- `wiki-compiler/tests/test_nlm_research.py`
- `wiki-compiler/tests/test_nlm_client.py`
- `antigravity/skills/using-superpowers/references/wiki-feedback.md` (novo) — instruções de leitura/resposta
- `.opencode/skills/using-superpowers/references/wiki-feedback.md` (copia)
- `.claude/skills/using-superpowers/references/wiki-feedback.md` (copia)

**Será modificado:**
- `wiki-compiler/adapters/orchestrator.py` (orquestra geração de INDEX e sync NLM)
- `wiki-compiler/run_post_process.sh` (chama INDEX generator e NLM sync)
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, Antigravity instructions (referenciar INDEX)

---

## Task 1: Gerador de `INDEX.md`

**Files:**
- Create: `wiki-compiler/adapters/index_generator.py`
- Test: `wiki-compiler/tests/test_index_generator.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_index_generator.py`:

```python
"""Testes do gerador de INDEX.md."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("index_generator",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def _make_page(path: Path, title: str, tags: list[str]) -> None:
    path.write_text(
        f"# {title}\n\n"
        f"Tags: {', '.join('#' + t for t in tags)}\n\n"
        f"Body content here.\n",
        encoding="utf-8",
    )


def test_generate_index_groups_by_tag(tmp_path: Path) -> None:
    from index_generator import generate_index
    _make_page(tmp_path / "fabric-auth.md", "Fabric Authentication", ["tech"])
    _make_page(tmp_path / "cliente-x.md", "Cliente X Pipeline", ["negocio"])
    _make_page(tmp_path / "context-agent.md", "Context Agent", ["tech"])

    index = generate_index(tmp_path)
    assert "## Tecnologia" in index
    assert "## Negócio" in index
    # Tecnologia deve ter 2 itens
    tech_section = index.split("## Tecnologia")[1].split("##")[0]
    assert "[[fabric-auth]]" in tech_section
    assert "[[context-agent]]" in tech_section
    # Negócio deve ter 1
    neg_section = index.split("## Negócio")[1].split("##")[0]
    assert "[[cliente-x]]" in neg_section


def test_generate_index_excludes_control_files(tmp_path: Path) -> None:
    from index_generator import generate_index
    _make_page(tmp_path / "fabric.md", "Fabric", ["tech"])
    (tmp_path / "SUGESTOES-HOJE.md").write_text("# sugestoes", encoding="utf-8")
    (tmp_path / "PENDENCIAS.md").write_text("# pendencias", encoding="utf-8")
    (tmp_path / "suggestion_ignore.md").write_text("# ignore", encoding="utf-8")
    (tmp_path / "AUDIT_REPORT.md").write_text("# audit", encoding="utf-8")
    (tmp_path / "INDEX.md").write_text("# old index", encoding="utf-8")

    index = generate_index(tmp_path)
    assert "SUGESTOES-HOJE" not in index
    assert "PENDENCIAS" not in index
    assert "suggestion_ignore" not in index
    assert "AUDIT_REPORT" not in index
    assert "INDEX" not in index
    assert "[[fabric]]" in index


def test_generate_index_extracts_summary(tmp_path: Path) -> None:
    from index_generator import generate_index
    (tmp_path / "fabric.md").write_text(
        "# Fabric Auth\n\nTags: #tech\n\n"
        "Conector JDBC para Microsoft Fabric sem admin.\n\n"
        "## Detalhes\n\nMais conteudo.\n",
        encoding="utf-8",
    )
    index = generate_index(tmp_path)
    assert "Conector JDBC para Microsoft Fabric sem admin." in index


def test_write_index_writes_to_vault(tmp_path: Path) -> None:
    from index_generator import write_index
    (tmp_path / "fabric.md").write_text("# Fabric\n\nTags: #tech\n\nX", encoding="utf-8")
    out = write_index(tmp_path)
    assert out == tmp_path / "INDEX.md"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "# Wiki Index" in content
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_index_generator.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar gerador**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\index_generator.py`:

```python
"""
Gerador de INDEX.md para o vault.
Lê todas as paginas .md (exceto arquivos de controle), extrai tags (#tech, #negocio),
agrupa por domínio e gera índice com summary de 1 linha para cada pagina.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


_CONTROL_FILES = {
    "INDEX.md",
    "SUGESTOES-HOJE.md",
    "PENDENCIAS.md",
    "suggestion_ignore.md",
    "AUDIT_REPORT.md",
    "README.md",
}

_TAG_RE = re.compile(r"#(\w+)")
_TITLE_RE = re.compile(r"^#\s+(.+?)$", re.MULTILINE)


def _extract_tags(text: str) -> set[str]:
    return set(_TAG_RE.findall(text))


def _extract_title(path: Path, text: str) -> str:
    m = _TITLE_RE.search(text)
    return m.group(1).strip() if m else path.stem


def _extract_summary(text: str) -> str:
    """Primeira linha não vazia após o título/tags (máximo 120 chars)."""
    lines = text.splitlines()
    in_body = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Pular titulo e linha de tags
        if stripped.startswith("#"):
            in_body = False
            continue
        if stripped.lower().startswith("tags:"):
            in_body = True
            continue
        # Primeira linha de corpo real
        if in_body or (i > 2 and not stripped.startswith("#")):
            return stripped[:120]
    return ""


def _classify(tags: set[str]) -> str:
    if "tech" in tags:
        return "Tecnologia"
    if "negocio" in tags:
        return "Negócio"
    return "Outros"


def generate_index(vault_dir: Path) -> str:
    """Gera texto do INDEX.md."""
    pages_by_group: dict[str, list[tuple[str, str, str]]] = {}
    for page in sorted(vault_dir.glob("*.md")):
        if page.name in _CONTROL_FILES:
            continue
        text = page.read_text(encoding="utf-8")
        tags = _extract_tags(text)
        group = _classify(tags)
        slug = page.stem
        title = _extract_title(page, text)
        summary = _extract_summary(text)
        pages_by_group.setdefault(group, []).append((slug, title, summary))

    total = sum(len(items) for items in pages_by_group.values())
    tech_count = len(pages_by_group.get("Tecnologia", []))
    neg_count = len(pages_by_group.get("Negócio", []))

    today = datetime.now().strftime("%Y-%m-%d")
    lines: list[str] = [
        f"# Wiki Index — {today}",
        f"{total} páginas · {tech_count} #tech · {neg_count} #negocio",
        "",
    ]

    # Ordem fixa: Tecnologia, Negócio, Outros
    for group in ("Tecnologia", "Negócio", "Outros"):
        items = pages_by_group.get(group)
        if not items:
            continue
        lines.append(f"## {group}")
        for slug, _title, summary in items:
            entry = f"- [[{slug}]]"
            if summary:
                entry += f" — {summary}"
            lines.append(entry)
        lines.append("")

    return "\n".join(lines)


def write_index(vault_dir: Path) -> Path:
    """Gera e grava INDEX.md na raiz do vault."""
    content = generate_index(vault_dir)
    path = vault_dir / "INDEX.md"
    path.write_text(content, encoding="utf-8")
    return path
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_index_generator.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/index_generator.py wiki-compiler/tests/test_index_generator.py
git commit -m "feat: index_generator produz INDEX.md agrupado por tag"
```

---

## Task 2: Referenciar INDEX no system prompt dos 4 agentes

**Files:**
- Modify: `CLAUDE.md` (se existir no root do Stout) ou criar
- Modify: `GEMINI.md`
- Modify: `AGENTS.md` (se aplicável)
- Modify: Antigravity system prompt file

- [ ] **Step 1: Identificar cada arquivo de system prompt**

```bash
ls -la C:/Projetos/Stout/ | grep -Ei "claude|gemini|agents|antigravity"
```

Expected: vê `CLAUDE.md`, `GEMINI.md`, etc. Se algum não existir, criar vazio nesta tarefa.

- [ ] **Step 2: Adicionar seção "Wiki Index" em cada um**

Para cada arquivo de system prompt (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`), adicionar (ou fazer append) a seção:

```markdown
## Wiki Knowledge Base

Wiki pessoal localizada em `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/`.

**Ponto de entrada:** `INDEX.md` — agrupa páginas por #tech / #negocio com sumário de 1 linha cada.
Ler INDEX.md no início de qualquer tarefa que referencie conhecimento acumulado.

**Consulta:** abrir páginas específicas via `Read` (ou equivalente) — elas não têm frontmatter, são flat kebab-case.

**Atualização:** o wiki é atualizado apenas pelo pipeline `wiki-compiler/run_wiki_work.sh --production`.
Não editar páginas manualmente fora do Obsidian.
```

Para o Antigravity: localizar o arquivo principal de instruções (provavelmente em `~/.gemini/antigravity/AGENTS.md` ou equivalente) e adicionar a mesma seção.

- [ ] **Step 3: Commit**

```bash
git -C "C:/Projetos/Stout" add CLAUDE.md GEMINI.md AGENTS.md 2>/dev/null || true
git -C "C:/Projetos/Stout" commit -m "docs: referencia wiki INDEX nos system prompts dos 4 agentes"
```

---

## Task 3: `SuggestionsManager` — gerenciar SUGESTOES-HOJE acumulativo

**Files:**
- Create: `wiki-compiler/adapters/suggestions_manager.py`
- Test: `wiki-compiler/tests/test_suggestions_manager.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_suggestions_manager.py`:

```python
"""Testes do gerenciador de SUGESTOES-HOJE acumulativo."""
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("suggestions_manager",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_add_suggestion_appends_new_item(tmp_path: Path) -> None:
    from suggestions_manager import add_suggestion
    sug_file = tmp_path / "SUGESTOES-HOJE.md"

    add_suggestion(
        sug_file,
        title="Configurar OAuth",
        wiki_slug="gemini-cli",
        description="Adicionar auth OAuth no Gemini CLI",
        research="Conforme fontes, OAuth 2.1 é o padrao atual.",
        date="2026-04-23",
    )

    content = sug_file.read_text(encoding="utf-8")
    assert "### Configurar OAuth — [[gemini-cli]]" in content
    assert "**Data:** 2026-04-23" in content
    assert "**Status:** ativa" in content
    assert "Adicionar auth OAuth" in content
    assert "#### Embasamento" in content
    assert "OAuth 2.1" in content


def test_add_suggestion_dedupe_by_title(tmp_path: Path) -> None:
    """Sugestao com titulo similar (Jaccard >= 0.6) nao duplica — atualiza research."""
    from suggestions_manager import add_suggestion
    sug_file = tmp_path / "SUGESTOES-HOJE.md"

    add_suggestion(sug_file, "Configurar OAuth", "gemini-cli", "desc1", "research1", "2026-04-20")
    add_suggestion(sug_file, "Configurar auth OAuth", "gemini-cli", "desc2", "research2", "2026-04-23")

    content = sug_file.read_text(encoding="utf-8")
    # Deve ter apenas 1 sugestao
    assert content.count("### ") == 1
    # Research atualizado para o mais recente
    assert "research2" in content


def test_add_suggestion_keeps_unrelated_suggestions(tmp_path: Path) -> None:
    from suggestions_manager import add_suggestion
    sug_file = tmp_path / "SUGESTOES-HOJE.md"

    add_suggestion(sug_file, "Configurar OAuth", "gemini-cli", "d1", "r1", "2026-04-23")
    add_suggestion(sug_file, "Migrar banco de dados", "db-migration", "d2", "r2", "2026-04-23")

    content = sug_file.read_text(encoding="utf-8")
    assert content.count("### ") == 2
    assert "OAuth" in content
    assert "banco de dados" in content


def test_mark_suggestion_ignored_moves_to_ignore(tmp_path: Path) -> None:
    from suggestions_manager import add_suggestion, mark_ignored
    sug_file = tmp_path / "SUGESTOES-HOJE.md"
    ignore_file = tmp_path / "suggestion_ignore.md"
    ignore_file.write_text("# Ignore\n", encoding="utf-8")

    add_suggestion(sug_file, "Tarefa X", "slug-x", "d", "r", "2026-04-23")
    ok = mark_ignored("Tarefa X", sug_file, ignore_file)

    assert ok
    # Nao aparece mais em SUGESTOES
    assert "Tarefa X" not in sug_file.read_text(encoding="utf-8")
    # Aparece em ignore
    assert "Tarefa X" in ignore_file.read_text(encoding="utf-8")


def test_mark_suggestion_completed_moves_to_ignore(tmp_path: Path) -> None:
    from suggestions_manager import add_suggestion, mark_completed
    sug_file = tmp_path / "SUGESTOES-HOJE.md"
    ignore_file = tmp_path / "suggestion_ignore.md"
    ignore_file.write_text("# Ignore\n", encoding="utf-8")

    add_suggestion(sug_file, "Tarefa Y", "slug-y", "d", "r", "2026-04-23")
    ok = mark_completed("Tarefa Y", sug_file, ignore_file)

    assert ok
    assert "Tarefa Y" not in sug_file.read_text(encoding="utf-8")
    assert "Tarefa Y" in ignore_file.read_text(encoding="utf-8")
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_suggestions_manager.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar `suggestions_manager`**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\suggestions_manager.py`:

```python
"""
Gerenciador de SUGESTOES-HOJE.md com acumulacao e dedupe.
Sugestoes so saem da lista via mark_ignored ou mark_completed.
Dedupe por similaridade Jaccard >= 0.6 entre titulos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Reusa wiki_text_utils se existir
_AUDIT_DIR = Path(__file__).resolve().parent.parent / "audit"
if _AUDIT_DIR.exists():
    sys.path.insert(0, str(_AUDIT_DIR))
    try:
        from wiki_text_utils import jaccard_similarity, normalize_title  # type: ignore
    except ImportError:
        jaccard_similarity = None
        normalize_title = None
    finally:
        sys.path.remove(str(_AUDIT_DIR))
else:
    jaccard_similarity = None
    normalize_title = None


_SUG_HEADER_RE = re.compile(r"^###\s+(.+?)\s+—\s+\[\[", re.MULTILINE)
_JACCARD_THRESHOLD = 0.6


def _fallback_normalize(title: str) -> frozenset[str]:
    return frozenset(w.lower() for w in re.split(r"\W+", title) if len(w) > 2)


def _fallback_jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


_norm = normalize_title or _fallback_normalize
_jacc = jaccard_similarity or _fallback_jaccard


def _split_sections(content: str) -> list[str]:
    """Separa conteudo em blocos ### (cada sugestao)."""
    # Split preservando delimitador
    parts = re.split(r"(?=^###\s)", content, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip()]


def _title_of_block(block: str) -> str:
    m = _SUG_HEADER_RE.match(block)
    return m.group(1).strip() if m else ""


def _format_suggestion(
    title: str, wiki_slug: str, description: str, research: str, date: str,
) -> str:
    parts = [
        f"### {title} — [[{wiki_slug}]]",
        f"**Data:** {date} · **Status:** ativa",
        "",
        description.strip(),
        "",
    ]
    if research:
        parts.extend([
            "#### Embasamento (via NotebookLM)",
            research.strip(),
            "",
        ])
    return "\n".join(parts)


def _ensure_header(file: Path) -> list[str]:
    """Retorna linhas do arquivo, criando cabecalho se vazio."""
    if not file.exists() or not file.read_text(encoding="utf-8").strip():
        return ["# SUGESTOES-HOJE\n"]
    return file.read_text(encoding="utf-8").splitlines(keepends=True)


def add_suggestion(
    file: Path,
    title: str,
    wiki_slug: str,
    description: str,
    research: str,
    date: str,
) -> None:
    """Adiciona sugestao, fazendo dedupe por similaridade de titulo."""
    content = "".join(_ensure_header(file))
    # Split em header + blocos existentes
    m = re.match(r"(^#[^\n]*\n)", content)
    header = m.group(1) if m else "# SUGESTOES-HOJE\n"
    body = content[len(header):]
    blocks = _split_sections(body) if body.strip() else []

    new_block = _format_suggestion(title, wiki_slug, description, research, date)
    new_norm = _norm(title)

    # Dedupe: se algum bloco tem titulo similar, substitui
    merged = False
    updated_blocks: list[str] = []
    for block in blocks:
        block_title = _title_of_block(block)
        if block_title and _jacc(new_norm, _norm(block_title)) >= _JACCARD_THRESHOLD:
            updated_blocks.append(new_block)
            merged = True
        else:
            updated_blocks.append(block)
    if not merged:
        # Adicionar no topo (mais recente primeiro)
        updated_blocks.insert(0, new_block)

    file.write_text(
        header + "\n" + "\n\n".join(updated_blocks) + "\n",
        encoding="utf-8",
    )


def _remove_block_by_title(file: Path, target_title: str) -> str | None:
    """Remove bloco com titulo especifico. Retorna o bloco removido ou None."""
    content = file.read_text(encoding="utf-8") if file.exists() else ""
    m = re.match(r"(^#[^\n]*\n)", content)
    header = m.group(1) if m else "# SUGESTOES-HOJE\n"
    body = content[len(header):]
    blocks = _split_sections(body) if body.strip() else []

    target_norm = _norm(target_title)
    removed: str | None = None
    kept: list[str] = []
    for block in blocks:
        bt = _title_of_block(block)
        if bt and _jacc(target_norm, _norm(bt)) >= _JACCARD_THRESHOLD and removed is None:
            removed = block
        else:
            kept.append(block)

    if removed is None:
        return None
    file.write_text(
        header + "\n" + "\n\n".join(kept) + ("\n" if kept else ""),
        encoding="utf-8",
    )
    return removed


def _append_to_ignore(ignore_file: Path, title: str) -> None:
    ignore_file.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if ignore_file.exists():
        existing = ignore_file.read_text(encoding="utf-8")
    if not existing.strip():
        existing = "# Suggestion Ignore List\n\n"
    if title not in existing:
        existing = existing.rstrip() + f"\n- {title}\n"
    ignore_file.write_text(existing, encoding="utf-8")


def mark_ignored(title: str, sug_file: Path, ignore_file: Path) -> bool:
    """Remove sugestao de SUGESTOES-HOJE e adiciona em suggestion_ignore."""
    removed = _remove_block_by_title(sug_file, title)
    if removed is None:
        return False
    _append_to_ignore(ignore_file, title)
    return True


def mark_completed(title: str, sug_file: Path, ignore_file: Path) -> bool:
    """Concluído tem o mesmo efeito que ignorado: sai da lista, nunca mais sugerir."""
    return mark_ignored(title, sug_file, ignore_file)
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_suggestions_manager.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/suggestions_manager.py wiki-compiler/tests/test_suggestions_manager.py
git commit -m "feat: suggestions_manager acumulativo com dedupe Jaccard"
```

---

## Task 4: Cliente MCP NLM (`nlm_client.py`)

**Files:**
- Create: `wiki-compiler/adapters/nlm_client.py`
- Test: `wiki-compiler/tests/test_nlm_client.py`

O MCP é acessado via subprocess ao `nlm` CLI. Fallback: funcoes retornam None / lista vazia se CLI ausente.

- [ ] **Step 1: Escrever teste com mock do subprocess**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_nlm_client.py`:

```python
"""Testes do nlm_client com mock de subprocess."""
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("nlm_client",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_list_notebooks_parses_json_output() -> None:
    from nlm_client import list_notebooks
    fake_output = json.dumps({
        "notebooks": [
            {"id": "abc", "title": "Estudo — LLM Wiki", "source_count": 100},
            {"id": "def", "title": "Wiki Output", "source_count": 5},
        ]
    })
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=fake_output, stderr="")
        result = list_notebooks()

    assert len(result) == 2
    assert result[0]["title"] == "Estudo — LLM Wiki"


def test_list_notebooks_returns_empty_on_cli_missing() -> None:
    from nlm_client import list_notebooks
    with patch("subprocess.run", side_effect=FileNotFoundError("nlm: command not found")):
        result = list_notebooks()
    assert result == []


def test_list_notebooks_returns_empty_on_nonzero_exit() -> None:
    from nlm_client import list_notebooks
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="auth error")
        result = list_notebooks()
    assert result == []


def test_add_source_file_calls_cli_correctly(tmp_path: Path) -> None:
    from nlm_client import add_source_file
    fake = tmp_path / "page.md"
    fake.write_text("content", encoding="utf-8")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='{"ok": true}', stderr="")
        ok = add_source_file("abc-123", fake)

    assert ok
    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert "abc-123" in call_args
    assert str(fake) in call_args
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_nlm_client.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar cliente**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\nlm_client.py`:

```python
"""
Cliente wrapper do MCP NotebookLM via CLI `nlm`.
Todas as funcoes degradam graciosamente se o CLI estiver ausente ou com erro.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def _run_nlm(args: list[str], timeout: int = 60) -> dict[str, Any] | None:
    """Executa `nlm <args>` e retorna JSON parseado, ou None em falha."""
    try:
        result = subprocess.run(
            ["nlm", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def list_notebooks() -> list[dict[str, Any]]:
    """Retorna lista de notebooks {id, title, source_count, ...}. Vazia se falhar."""
    data = _run_nlm(["list", "--json"])
    if data is None:
        return []
    return data.get("notebooks", [])


def add_source_file(notebook_id: str, file_path: Path) -> bool:
    """Adiciona um arquivo como source do notebook. True se sucesso."""
    data = _run_nlm([
        "source", "add",
        "--notebook", notebook_id,
        "--file", str(file_path),
        "--json",
    ])
    return data is not None and data.get("ok", False)


def cross_notebook_query(notebook_ids: list[str], query: str) -> str | None:
    """Consulta múltiplos notebooks. Retorna resposta em texto, ou None."""
    if not notebook_ids:
        return None
    data = _run_nlm([
        "query", "cross",
        "--notebooks", ",".join(notebook_ids),
        "--query", query,
        "--json",
    ])
    if data is None:
        return None
    return data.get("answer") or data.get("response")


def list_notebook_sources(notebook_id: str) -> list[dict[str, Any]]:
    """Lista sources de um notebook (para sync delta)."""
    data = _run_nlm(["source", "list", "--notebook", notebook_id, "--json"])
    if data is None:
        return []
    return data.get("sources", [])
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_nlm_client.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/nlm_client.py wiki-compiler/tests/test_nlm_client.py
git commit -m "feat: nlm_client wrapper com degradacao graciosa"
```

---

## Task 5: `nlm_research.py` — embasamento para sugestões

**Files:**
- Create: `wiki-compiler/adapters/nlm_research.py`
- Test: `wiki-compiler/tests/test_nlm_research.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_nlm_research.py`:

```python
"""Testes do nlm_research: filtra notebooks por 'estudo' e consulta."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("nlm_research",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_filter_study_notebooks_by_title() -> None:
    from nlm_research import filter_study_notebooks
    notebooks = [
        {"id": "a", "title": "Estudo - LLM Wiki"},
        {"id": "b", "title": "Wiki Output"},
        {"id": "c", "title": "ESTUDO em Rust"},
        {"id": "d", "title": "Random Notes"},
    ]
    result = filter_study_notebooks(notebooks)
    assert {n["id"] for n in result} == {"a", "c"}


def test_research_topic_returns_response() -> None:
    from nlm_research import research_topic
    with patch("nlm_research.list_notebooks") as mock_list, \
         patch("nlm_research.cross_notebook_query") as mock_query:
        mock_list.return_value = [
            {"id": "a", "title": "Estudo - LLM Wiki"},
            {"id": "b", "title": "Random"},
        ]
        mock_query.return_value = "Especialistas indicam X."
        result = research_topic("LLM Wiki")

    assert result == "Especialistas indicam X."
    mock_query.assert_called_once()
    args, _ = mock_query.call_args
    assert args[0] == ["a"]


def test_research_topic_returns_empty_when_no_study_notebooks() -> None:
    from nlm_research import research_topic
    with patch("nlm_research.list_notebooks") as mock_list:
        mock_list.return_value = [{"id": "b", "title": "Random"}]
        result = research_topic("X")
    assert result == ""


def test_research_topic_returns_empty_on_query_failure() -> None:
    from nlm_research import research_topic
    with patch("nlm_research.list_notebooks") as mock_list, \
         patch("nlm_research.cross_notebook_query") as mock_query:
        mock_list.return_value = [{"id": "a", "title": "Estudo X"}]
        mock_query.return_value = None  # falha
        result = research_topic("X")
    assert result == ""
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_nlm_research.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\nlm_research.py`:

```python
"""
Research para sugestoes via NotebookLM: filtra notebooks por 'estudo' no titulo
e executa cross-notebook query. Resultado injetado em SUGESTOES-HOJE.md.
"""

from __future__ import annotations

from typing import Any

from nlm_client import list_notebooks, cross_notebook_query


def filter_study_notebooks(notebooks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retorna notebooks que contem 'estudo' no titulo (case-insensitive)."""
    return [n for n in notebooks if "estudo" in (n.get("title", "").lower())]


def research_topic(topic: str) -> str:
    """Retorna embasamento textual sobre o topico. Vazio se NLM indisponivel."""
    notebooks = list_notebooks()
    study = filter_study_notebooks(notebooks)
    if not study:
        return ""
    ids = [n["id"] for n in study]
    query = f"pesquisa sobre {topic}: embasamento de especialistas e conceitos-chave"
    response = cross_notebook_query(ids, query)
    return response or ""
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_nlm_research.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/nlm_research.py wiki-compiler/tests/test_nlm_research.py
git commit -m "feat: nlm_research filtra notebooks 'estudo' e consulta cross"
```

---

## Task 6: `nlm_sync.py` — auto-sync do vault para o notebook 987bb91c

**Files:**
- Create: `wiki-compiler/adapters/nlm_sync.py`
- Test: `wiki-compiler/tests/test_nlm_sync.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_nlm_sync.py`:

```python
"""Testes do sync vault -> notebook NLM."""
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in ("nlm_sync",):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_sync_uploads_new_pages(tmp_path: Path) -> None:
    from nlm_sync import sync_vault_to_notebook
    (tmp_path / "page1.md").write_text("a", encoding="utf-8")
    (tmp_path / "page2.md").write_text("b", encoding="utf-8")
    manifest = tmp_path / ".nlm_sync_manifest.json"

    with patch("nlm_sync.add_source_file") as mock_add:
        mock_add.return_value = True
        report = sync_vault_to_notebook(tmp_path, "nb-123", manifest)

    assert report["uploaded"] == 2
    assert mock_add.call_count == 2


def test_sync_skips_unchanged_pages(tmp_path: Path) -> None:
    from nlm_sync import sync_vault_to_notebook
    p1 = tmp_path / "page1.md"
    p1.write_text("a", encoding="utf-8")
    manifest = tmp_path / ".nlm_sync_manifest.json"
    # Manifest ja tem hash de p1
    sha = hashlib.sha256(p1.read_bytes()).hexdigest()
    manifest.write_text(json.dumps({"page1.md": sha}), encoding="utf-8")

    with patch("nlm_sync.add_source_file") as mock_add:
        report = sync_vault_to_notebook(tmp_path, "nb-123", manifest)

    assert report["uploaded"] == 0
    mock_add.assert_not_called()


def test_sync_reuploads_changed_pages(tmp_path: Path) -> None:
    from nlm_sync import sync_vault_to_notebook
    p1 = tmp_path / "page1.md"
    p1.write_text("old content", encoding="utf-8")
    manifest = tmp_path / ".nlm_sync_manifest.json"
    old_sha = hashlib.sha256(p1.read_bytes()).hexdigest()
    manifest.write_text(json.dumps({"page1.md": old_sha}), encoding="utf-8")

    # Agora modifica a pagina
    p1.write_text("new content", encoding="utf-8")

    with patch("nlm_sync.add_source_file") as mock_add:
        mock_add.return_value = True
        report = sync_vault_to_notebook(tmp_path, "nb-123", manifest)

    assert report["uploaded"] == 1
    new_sha = hashlib.sha256(p1.read_bytes()).hexdigest()
    assert new_sha != old_sha


def test_sync_skips_control_files(tmp_path: Path) -> None:
    from nlm_sync import sync_vault_to_notebook
    (tmp_path / "page.md").write_text("x", encoding="utf-8")
    (tmp_path / "INDEX.md").write_text("idx", encoding="utf-8")
    (tmp_path / "SUGESTOES-HOJE.md").write_text("s", encoding="utf-8")
    (tmp_path / "AUDIT_REPORT.md").write_text("a", encoding="utf-8")
    manifest = tmp_path / ".nlm_sync_manifest.json"

    with patch("nlm_sync.add_source_file") as mock_add:
        mock_add.return_value = True
        sync_vault_to_notebook(tmp_path, "nb-123", manifest)

    # Apenas page.md deve ter sido enviado
    assert mock_add.call_count == 1
    assert str(mock_add.call_args_list[0][0][1]).endswith("page.md")


def test_sync_degrades_gracefully_on_upload_failure(tmp_path: Path) -> None:
    from nlm_sync import sync_vault_to_notebook
    (tmp_path / "page1.md").write_text("a", encoding="utf-8")
    manifest = tmp_path / ".nlm_sync_manifest.json"

    with patch("nlm_sync.add_source_file") as mock_add:
        mock_add.return_value = False  # NLM offline
        report = sync_vault_to_notebook(tmp_path, "nb-123", manifest)

    assert report["uploaded"] == 0
    assert report["failed"] == 1
    # Manifest nao foi atualizado
    assert not manifest.exists() or json.loads(manifest.read_text(encoding="utf-8")) == {}
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_nlm_sync.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Criar `C:\Projetos\Stout\wiki-compiler\adapters\nlm_sync.py`:

```python
"""
Sync incremental do vault para um notebook NotebookLM especifico.
Usa manifesto JSON local para track delta (hash SHA256 por arquivo).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from nlm_client import add_source_file


_CONTROL_FILES = {
    "INDEX.md",
    "SUGESTOES-HOJE.md",
    "PENDENCIAS.md",
    "suggestion_ignore.md",
    "AUDIT_REPORT.md",
    "README.md",
}


@dataclass
class SyncReport:
    uploaded: int = 0
    skipped: int = 0
    failed: int = 0
    files_uploaded: list[str] = field(default_factory=list)
    files_failed: list[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> int | list[str]:
        return getattr(self, key)


def _load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_manifest(path: Path, manifest: dict[str, str]) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_vault_to_notebook(
    vault_dir: Path,
    notebook_id: str,
    manifest_path: Path,
) -> SyncReport:
    """Faz upload incremental de paginas do vault para o notebook NLM."""
    report = SyncReport()
    manifest = _load_manifest(manifest_path)

    for page in sorted(vault_dir.glob("*.md")):
        if page.name in _CONTROL_FILES:
            continue
        current_sha = _hash_file(page)
        prev_sha = manifest.get(page.name)
        if prev_sha == current_sha:
            report.skipped += 1
            continue

        ok = add_source_file(notebook_id, page)
        if ok:
            manifest[page.name] = current_sha
            report.uploaded += 1
            report.files_uploaded.append(page.name)
        else:
            report.failed += 1
            report.files_failed.append(page.name)

    # Persistir manifesto so se houve uploads (evita corromper em falha total)
    if report.uploaded > 0:
        _save_manifest(manifest_path, manifest)

    return report
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_nlm_sync.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/adapters/nlm_sync.py wiki-compiler/tests/test_nlm_sync.py
git commit -m "feat: nlm_sync incremental com manifesto SHA256"
```

---

## Task 7: Integrar tudo no `run_post_process.sh`

**Files:**
- Modify: `wiki-compiler/run_post_process.sh`

- [ ] **Step 1: Adicionar geração de INDEX e sync NLM ao pipeline de saida**

Em `C:\Projetos\Stout\wiki-compiler\run_post_process.sh`, antes da ultima linha, adicionar:

```bash

# Gerar INDEX.md
echo ""
echo "Gerando INDEX.md..."
python -c "
import sys
sys.path.insert(0, r'$STOUT_ROOT/wiki-compiler/adapters')
from index_generator import write_index
from pathlib import Path
path = write_index(Path(r'$VAULT'))
print(f'INDEX gravado: {path}')
"

# Sync NLM (notebook fixo 987bb91c-86a3-4a9a-a3db-4dbaa150bd18)
NLM_NOTEBOOK_ID="987bb91c-86a3-4a9a-a3db-4dbaa150bd18"
MANIFEST="$VAULT/.nlm_sync_manifest.json"
echo ""
echo "Sincronizando com NotebookLM..."
python -c "
import sys
sys.path.insert(0, r'$STOUT_ROOT/wiki-compiler/adapters')
from nlm_sync import sync_vault_to_notebook
from pathlib import Path
report = sync_vault_to_notebook(
    vault_dir=Path(r'$VAULT'),
    notebook_id='$NLM_NOTEBOOK_ID',
    manifest_path=Path(r'$MANIFEST'),
)
print(f'NLM sync: uploaded={report.uploaded}, skipped={report.skipped}, failed={report.failed}')
if report.failed > 0:
    print('AVISO: upload falhou para alguns arquivos. Verifique se nlm CLI esta autenticado.')
"
```

- [ ] **Step 2: Smoke test (com NLM offline — validar degradação)**

Rodar:
```bash
bash wiki-compiler/run_post_process.sh --production
```

Expected: pipeline completa, INDEX.md gerado, sync NLM pode reportar `failed=N` se offline. **Script não deve abortar** em falha de NLM.

- [ ] **Step 3: Commit**

```bash
git add wiki-compiler/run_post_process.sh
git commit -m "feat: run_post_process gera INDEX e sync NLM"
```

---

## Task 8: Portar feedback loop para skill Superpowers compartilhada

**Files:**
- Create: `antigravity/skills/using-superpowers/references/wiki-feedback.md`
- Copy para: `.opencode/skills/using-superpowers/references/wiki-feedback.md`
- Copy para: `.claude/skills/using-superpowers/references/wiki-feedback.md`

- [ ] **Step 1: Escrever referencia compartilhada**

Criar `C:\Projetos\Stout\antigravity\skills\using-superpowers\references\wiki-feedback.md`:

```markdown
# Wiki Feedback Loop

Esta reference estende `using-superpowers` com o comportamento de leitura e feedback de SUGESTOES-HOJE.md.

## Gatilho de leitura

Quando o usuário mencionar qualquer uma destas palavras, o agente deve ler `<vault>/SUGESTOES-HOJE.md`:
- "wiki"
- "sugestao" / "sugestão" / "sugestoes" / "sugestões"
- "recomenda" / "recomendação"
- "o que o wiki"

Leitura é **dinâmica**: a cada menção, ler fresh o arquivo (pode ter sido atualizado pelo pipeline entre duas menções).

## Apresentação

Incorporar o conteúdo na resposta de forma natural. Não mencionar explicitamente que está lendo um arquivo.

## Respostas do usuário e ações

| Usuário diz | Ação do agente |
|---|---|
| "concluído" / "feito" | Invocar `suggestions_manager.mark_completed` com o título da sugestão |
| "ignora" / "não quero" / "descarta" | Invocar `suggestions_manager.mark_ignored` |
| "pendente" / "depois" | Manter em SUGESTOES-HOJE (não precisa de ação) |

Todas as ações devem ser confirmadas ao usuário:
> "Anotado — [título] marcado como [concluído | ignorado]."

## Invocação programática

Script helper: `wiki-compiler/cli/feedback.py` (criado em Task 9) expõe:
```bash
python wiki-compiler/cli/feedback.py ignored "<título>"
python wiki-compiler/cli/feedback.py completed "<título>"
```

## Leitura do INDEX

No início de qualquer sessão onde conhecimento acumulado é relevante, ler `<vault>/INDEX.md` para mapa do wiki antes de aprofundar páginas específicas.

## Path do vault

```
C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/
```
```

- [ ] **Step 2: Copiar para outras instalações Superpowers**

```bash
STOUT_ROOT="C:/Projetos/Stout"
SRC="$STOUT_ROOT/antigravity/skills/using-superpowers/references/wiki-feedback.md"

mkdir -p "$STOUT_ROOT/.opencode/skills/using-superpowers/references"
mkdir -p "$STOUT_ROOT/.claude/skills/using-superpowers/references"

cp "$SRC" "$STOUT_ROOT/.opencode/skills/using-superpowers/references/"
cp "$SRC" "$STOUT_ROOT/.claude/skills/using-superpowers/references/"
```

- [ ] **Step 3: Criar CLI helper `feedback.py`**

Criar `C:\Projetos\Stout\wiki-compiler\cli\feedback.py`:

```python
#!/usr/bin/env python3
"""
CLI helper para marcar sugestoes como concluido/ignorado a partir de um agente.
Uso:
    python feedback.py ignored "Titulo da sugestao"
    python feedback.py completed "Titulo da sugestao"
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "adapters"))

from suggestions_manager import mark_ignored, mark_completed  # noqa: E402

VAULT = Path(r"C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\wiki")


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in {"ignored", "completed"}:
        print("Uso: feedback.py {ignored|completed} \"Titulo\"")
        return 2
    action = sys.argv[1]
    title = sys.argv[2]
    sug = VAULT / "SUGESTOES-HOJE.md"
    ignore = VAULT / "suggestion_ignore.md"

    if action == "ignored":
        ok = mark_ignored(title, sug, ignore)
    else:
        ok = mark_completed(title, sug, ignore)

    if ok:
        print(f"Anotado: '{title}' marcado como {action}.")
        return 0
    print(f"Nao encontrado: '{title}' nao esta em SUGESTOES-HOJE.md")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

Criar `C:\Projetos\Stout\wiki-compiler\cli\__init__.py` vazio.

- [ ] **Step 4: Commit**

```bash
git add antigravity/skills/using-superpowers/references/wiki-feedback.md \
        .opencode/skills/using-superpowers/references/wiki-feedback.md \
        .claude/skills/using-superpowers/references/wiki-feedback.md \
        wiki-compiler/cli/
git commit -m "feat: porta feedback loop para Superpowers shared + CLI helper"
```

---

## Task 9: Geração de sugestões nova com research NLM

Este task conecta tudo: após compile, o sistema pode ser invocado (ou o Ar9av configurado para tal) para gerar 3 sugestões novas, cada uma com embasamento NLM. Este é o ponto mais "orquestrado": requer decisão sobre QUEM gera sugestões.

**Estratégia:** na versão desta fase, sugestões são geradas por um agente (Claude/Gemini) que lê o vault e o INDEX, propõe 3 temas, e chama `wiki-compiler/cli/suggest.py` para formatar e adicionar.

**Files:**
- Create: `wiki-compiler/cli/suggest.py`
- Create: `wiki-compiler/tests/test_suggest_cli.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_suggest_cli.py`:

```python
"""Testa CLI suggest.py: cria sugestao com research NLM."""
import subprocess
import sys
from pathlib import Path

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
CLI = STOUT_ROOT / "wiki-compiler" / "cli" / "suggest.py"


def test_suggest_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), "--help"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0
    assert "topic" in result.stdout.lower() or "titulo" in result.stdout.lower()
```

- [ ] **Step 2: Rodar teste para confirmar que falha**

Run: `pytest wiki-compiler/tests/test_suggest_cli.py -v`
Expected: FAIL.

- [ ] **Step 3: Implementar CLI**

Criar `C:\Projetos\Stout\wiki-compiler\cli\suggest.py`:

```python
#!/usr/bin/env python3
"""
CLI para adicionar sugestao nova em SUGESTOES-HOJE.md com research NLM.
Uso:
    python suggest.py --title "Configurar OAuth" \
                      --slug gemini-cli \
                      --description "Adicionar auth OAuth no Gemini CLI"
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "adapters"))

from suggestions_manager import add_suggestion  # noqa: E402
from nlm_research import research_topic  # noqa: E402

VAULT = Path(r"C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\wiki")


def main() -> int:
    parser = argparse.ArgumentParser(description="Adiciona sugestao com research NLM")
    parser.add_argument("--title", required=True, help="Titulo da sugestao")
    parser.add_argument("--slug", required=True, help="Slug da pagina wiki de origem")
    parser.add_argument("--description", required=True, help="Descricao curta")
    parser.add_argument("--no-research", action="store_true", help="Pular research NLM")
    args = parser.parse_args()

    research = "" if args.no_research else research_topic(args.title)
    if not research and not args.no_research:
        print("Aviso: research NLM indisponivel (notebook offline ou sem matches 'estudo').")

    sug_file = VAULT / "SUGESTOES-HOJE.md"
    today = datetime.now().strftime("%Y-%m-%d")

    add_suggestion(
        file=sug_file,
        title=args.title,
        wiki_slug=args.slug,
        description=args.description,
        research=research,
        date=today,
    )
    print(f"Sugestao adicionada em {sug_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar teste para confirmar que passa**

Run: `pytest wiki-compiler/tests/test_suggest_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add wiki-compiler/cli/suggest.py wiki-compiler/tests/test_suggest_cli.py
git commit -m "feat: CLI suggest.py adiciona sugestao com research NLM"
```

---

## Task 10: Teste de integração end-to-end

**Files:**
- Test: `wiki-compiler/tests/test_e2e_fase5.py`

- [ ] **Step 1: Escrever teste**

Criar `C:\Projetos\Stout\wiki-compiler\tests\test_e2e_fase5.py`:

```python
"""E2E da Fase 5: INDEX + SUGESTOES + NLM sync integrados."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

STOUT_ROOT = Path(r"C:\Projetos\Stout")
ADAPTERS = STOUT_ROOT / "wiki-compiler" / "adapters"


@pytest.fixture(autouse=True)
def _add_to_path():
    sys.path.insert(0, str(ADAPTERS))
    for m in (
        "index_generator", "suggestions_manager",
        "nlm_client", "nlm_sync", "nlm_research",
    ):
        if m in sys.modules:
            del sys.modules[m]
    yield
    sys.path.remove(str(ADAPTERS))


def test_full_fase5_cycle(tmp_path: Path) -> None:
    """Gera INDEX, adiciona sugestao com research, sincroniza com NLM."""
    from index_generator import write_index
    from suggestions_manager import add_suggestion, mark_ignored
    from nlm_sync import sync_vault_to_notebook

    # Setup vault
    (tmp_path / "fabric-auth.md").write_text(
        "# Fabric Auth\n\nTags: #tech\n\nConector JDBC sem admin.\n",
        encoding="utf-8",
    )
    (tmp_path / "cliente-x.md").write_text(
        "# Cliente X\n\nTags: #negocio\n\nPipeline SLA 4h.\n",
        encoding="utf-8",
    )
    (tmp_path / "suggestion_ignore.md").write_text("# Ignore\n", encoding="utf-8")

    # 1. Gerar INDEX
    idx = write_index(tmp_path)
    assert idx.exists()
    content = idx.read_text(encoding="utf-8")
    assert "[[fabric-auth]]" in content
    assert "[[cliente-x]]" in content

    # 2. Adicionar sugestao
    sug_file = tmp_path / "SUGESTOES-HOJE.md"
    add_suggestion(
        sug_file, "Migrar OAuth", "fabric-auth",
        "Atualizar para OAuth 2.1", "Fontes recomendam 2.1.",
        "2026-04-23",
    )
    assert sug_file.exists()
    assert "Migrar OAuth" in sug_file.read_text(encoding="utf-8")

    # 3. Sync NLM (mockado)
    manifest = tmp_path / ".nlm_sync_manifest.json"
    with patch("nlm_sync.add_source_file") as mock_add:
        mock_add.return_value = True
        report = sync_vault_to_notebook(tmp_path, "nb-test", manifest)
    # Apenas fabric-auth e cliente-x (control files excluidos: INDEX, SUGESTOES, suggestion_ignore)
    assert report.uploaded == 2

    # 4. Marcar sugestao como concluida
    ignore_file = tmp_path / "suggestion_ignore.md"
    ok = mark_ignored("Migrar OAuth", sug_file, ignore_file)
    assert ok
    assert "Migrar OAuth" not in sug_file.read_text(encoding="utf-8")
    assert "Migrar OAuth" in ignore_file.read_text(encoding="utf-8")
```

- [ ] **Step 2: Rodar teste**

Run: `pytest wiki-compiler/tests/test_e2e_fase5.py -v`
Expected: PASS.

- [ ] **Step 3: Suite completa**

Run: `pytest wiki-compiler/tests/ -v`
Expected: todos passam (Fases 3 + 5 tests acumulados).

- [ ] **Step 4: Commit**

```bash
git add wiki-compiler/tests/test_e2e_fase5.py
git commit -m "test: e2e Fase 5 INDEX + suggestions + NLM sync"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ INDEX.md gerado pelo compiler → Task 1
- ✅ Referência INDEX em CLAUDE.md / GEMINI.md / AGENTS.md / Antigravity instructions → Task 2
- ✅ SUGESTOES-HOJE.md acumulativo com dedupe Jaccard → Task 3
- ✅ Research NLM via cross_notebook_query filtrado por "estudo" → Task 5
- ✅ Sync automatico para notebook `987bb91c-86a3-4a9a-a3db-4dbaa150bd18` → Task 6
- ✅ Manifesto local de sync (delta SHA256) → Task 6
- ✅ Degradação graciosa com NLM offline → Tasks 4, 5, 6 (retornos vazios)
- ✅ Portar leitura/feedback do Bibliotecário para Superpowers shared → Task 8
- ✅ CLI helpers para agentes (feedback, suggest) → Tasks 8, 9

**2. Placeholder scan:** sem TBD/TODO.

**3. Type consistency:** `SyncReport` frozen dataclass; todas as funcoes tipadas; Path em tudo.

---

## Dependencies

- **Bloqueado por:** Fase 4 (vault estável em produção)
- **Bloqueia:** nada (fase final)

---

## Execution Notes

- Task 4 requer o CLI `nlm` instalado globalmente (`npm install -g notebooklm-mcp` ou equivalente). Se ausente, todas as funcoes retornam vazio mas o sistema não quebra.
- Task 8 altera system prompts — fazer commit isolado para facilitar rollback se algum agente ficar confuso.
- Sync NLM (Task 7 integração) pode falhar silenciosamente se `nlm` não estiver autenticado. Rodar `nlm login` uma vez após instalação.
- Para gerar sugestões de verdade em produção, chamar `wiki-compiler/cli/suggest.py` é uma interface mínima. Automação completa (onde o agente propõe sem ser chamado) fica para pós-reforma.

---

**Fase 5 conclui a reforma.** Após esta fase, o ecossistema wiki está:
- Unificado em storage (Fase 1)
- Alimentado por peneira dupla (Fases 1 + 2)
- Compilado por motor novo (Fase 3)
- Reconstruído limpo (Fase 4)
- Servindo como input/output para os 4 agentes e NotebookLM (Fase 5)
