import sys
import os
import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from session_parser import parse_session_file, _parse_raw_entry, get_session_metadata


# ── Task 2: Parse de entradas simples ──────────────────────────────────────


def test_parse_user_simple():
    """Entrada user simples Command Code -> SessionEntry type=user."""
    raw = {"role": "user", "content": "fix the bug"}
    entry = _parse_raw_entry(raw)
    assert entry is not None
    assert entry.type == "user"
    assert entry.content == "fix the bug"


def test_parse_assistant_simple():
    """Entrada assistant simples Command Code -> SessionEntry type=assistant."""
    raw = {"role": "assistant", "content": "I'll fix it."}
    entry = _parse_raw_entry(raw)
    assert entry is not None
    assert entry.type == "assistant"
    assert "fix" in entry.content


# ── Task 3: tool_use, system, tool_result ──────────────────────────────────


def test_parse_system_returns_none():
    """Entrada role=system deve retornar None."""
    raw = {"role": "system", "content": "You are an assistant."}
    entry = _parse_raw_entry(raw)
    assert entry is None


def test_parse_tool_use():
    """Entrada assistant com tool_use block -> tool_calls e files_modified populados."""
    raw = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Vou editar o arquivo."},
            {
                "type": "tool_use",
                "name": "Edit",
                "input": {"file_path": "/src/app.py", "old_string": "x", "new_string": "y"},
            },
        ],
    }
    entry = _parse_raw_entry(raw)
    assert entry is not None
    assert any(tc["name"] == "Edit" for tc in entry.tool_calls)
    assert any(f["path"] == "/src/app.py" for f in entry.files_modified)


def test_parse_tool_result():
    """Entrada user com tool_result block -> texto extraído."""
    raw = {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "content": [{"type": "text", "text": "File saved successfully."}],
            }
        ],
    }
    entry = _parse_raw_entry(raw)
    assert entry is not None
    assert "File saved successfully" in entry.content


def test_parse_tool_result_string_content():
    """tool_result com content string (não lista) -> texto extraído."""
    raw = {
        "role": "user",
        "content": [
            {"type": "tool_result", "content": "Done."},
        ],
    }
    entry = _parse_raw_entry(raw)
    assert entry is not None
    assert "Done" in entry.content


# ── Task 4: Injeção de session_id e timestamp ──────────────────────────────


def test_parse_session_file_injects_session_id_and_timestamp():
    """parse_session_file injeta session_id do path.stem e timestamp do mtime."""
    lines = [
        json.dumps({"role": "user", "content": "olá"}),
        json.dumps({"role": "assistant", "content": "oi"}),
    ]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write("\n".join(lines))
        tmp_path = Path(f.name)

    try:
        entries = parse_session_file(tmp_path)
        assert len(entries) == 2
        for entry in entries:
            assert entry.session_id == tmp_path.stem, (
                f"session_id esperado '{tmp_path.stem}', obtido '{entry.session_id}'"
            )
            assert entry.timestamp != "", "timestamp não deve ser vazio"
    finally:
        tmp_path.unlink(missing_ok=True)


# ── Task 5: Teste de integração com JSONL real ─────────────────────────────


_CC_PROJECT_DIR = (
    Path.home()
    / ".commandcode"
    / "projects"
    / "c-projetos-stout-projetos-configuration-driven-development"
)


def _find_real_jsonl() -> Path | None:
    if not _CC_PROJECT_DIR.exists():
        return None
    files = sorted(
        [p for p in _CC_PROJECT_DIR.glob("*.jsonl") if ".checkpoints" not in p.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


@pytest.mark.skipif(
    _find_real_jsonl() is None,
    reason="Nenhum arquivo JSONL do Command Code encontrado em ~/.commandcode/projects/",
)
def test_save_commandcode_session_generates_summary():
    """Parse de JSONL real do Command Code deve retornar entries > 0 e metadata populado."""
    jsonl_path = _find_real_jsonl()
    assert jsonl_path is not None

    entries = parse_session_file(jsonl_path)
    assert len(entries) > 0, f"Esperado entries > 0, obtido 0 para {jsonl_path.name}"

    metadata = get_session_metadata(entries)
    assert metadata.get("message_count", 0) > 0, "message_count deve ser > 0"

    tool_calls = [tc for e in entries for tc in e.tool_calls]
    files_modified = [f for e in entries for f in e.files_modified]
    assert len(tool_calls) > 0 or len(files_modified) > 0, (
        "Esperado ao menos uma tool_call ou arquivo modificado"
    )
