"""
Parser dos logs JSONL do Claude Code.
Lê arquivos de sessão e extrai informações estruturadas.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import CLAUDE_SESSION_DIR, FILE_MODIFYING_TOOLS
from models import SessionEntry


def parse_session_file(path: Path) -> list[SessionEntry]:
    """Lê um arquivo JSONL e retorna lista de SessionEntry."""
    session_id = path.stem
    mtime_ts = datetime.fromtimestamp(path.stat().st_mtime).isoformat()

    entries = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                entry = _parse_raw_entry(raw)
                if entry:
                    if not entry.session_id:
                        entry.session_id = session_id
                    if not entry.timestamp:
                        entry.timestamp = mtime_ts
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def _parse_commandcode_entry(raw: dict) -> Optional[SessionEntry]:
    """Parseia uma entrada no formato Command Code (Anthropic Messages API variante)."""
    role = raw["role"]
    if role == "system":
        return None

    timestamp = raw.get("timestamp", "")
    session_id = raw.get("sessionId", "")
    content_raw = raw.get("content", "")
    text_parts: list[str] = []
    tool_calls: list[dict] = []
    files_modified: list[dict] = []

    if isinstance(content_raw, str):
        text_parts.append(content_raw)
    elif isinstance(content_raw, list):
        for block in content_raw:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            if btype in ("text", "reasoning"):
                text = block.get("text", "")
                if text:
                    text_parts.append(text)
            elif btype in ("tool_use", "tool-call"):
                # tool_use: name + input  |  tool-call: toolName + input
                tool_name = block.get("name") or block.get("toolName", "")
                tool_input = block.get("input", {})
                tc = {"name": tool_name, "input": tool_input}
                tool_calls.append(tc)
                if tool_name in FILE_MODIFYING_TOOLS:
                    fp = (
                        tool_input.get("file_path")
                        or tool_input.get("filePath")
                        or tool_input.get("path", "")
                    )
                    if fp:
                        files_modified.append({"path": fp, "action": tool_name})
            elif btype in ("tool_result", "tool-result"):
                # tool_result: content field  |  tool-result: output field
                rc = block.get("content") or block.get("output", "")
                if isinstance(rc, str):
                    text_parts.append(rc)
                elif isinstance(rc, dict) and rc.get("type") == "text":
                    text_parts.append(rc.get("value", rc.get("text", "")))
                elif isinstance(rc, list):
                    for rb in rc:
                        if isinstance(rb, dict) and rb.get("type") == "text":
                            text_parts.append(rb.get("text", ""))

    return SessionEntry(
        type=role,
        role=role,
        timestamp=timestamp,
        session_id=session_id,
        content="\n".join(text_parts),
        tool_calls=tool_calls,
        files_modified=files_modified,
    )


def _parse_raw_entry(raw: dict) -> Optional[SessionEntry]:
    """Converte um dict JSON bruto em SessionEntry."""
    entry_type = raw.get("type", "")

    if entry_type == "queue-operation":
        return SessionEntry(
            type="queue",
            timestamp=raw.get("timestamp", ""),
            session_id=raw.get("sessionId", ""),
            content=raw.get("content", ""),
        )

    # Formato Command Code (Anthropic Messages API) — role sem type
    if "role" in raw and "type" not in raw:
        return _parse_commandcode_entry(raw)

    if entry_type not in ("user", "assistant", "USER_INPUT", "PLANNER_RESPONSE"):
        return None

    # Mapeamento de tipos Antigravity para tipos padrão do agente
    mapped_type = entry_type
    if entry_type == "USER_INPUT":
        mapped_type = "user"
    elif entry_type == "PLANNER_RESPONSE":
        mapped_type = "assistant"

    msg = raw.get("message", {})
    role = msg.get("role", mapped_type)
    slug = raw.get("slug", "")
    session_id = raw.get("sessionId", raw.get("step_index", ""))
    timestamp = raw.get("timestamp", raw.get("created_at", ""))

    # Extrair texto e tool_calls do content
    text_parts = []
    tool_calls_list = raw.get("tool_calls", [])
    tool_calls = []
    files_modified = []
    model = msg.get("model", "")

    # Processar tool_calls do Antigravity
    for tc in tool_calls_list:
        name = tc.get("name", "")
        args = tc.get("args", tc.get("input", {}))
        tool_calls.append({"name": name, "input": args})
        if name in FILE_MODIFYING_TOOLS:
            fp = args.get("file_path", args.get("TargetFile", ""))
            if fp and isinstance(fp, str):
                fp = fp.strip().strip('"').strip("'")
                files_modified.append({"path": fp, "action": name.lower()})

    content = raw.get("content", "")
    if not content and msg:
        content = msg.get("content", "")
    if isinstance(content, str):
        text_parts.append(content)
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "")
            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                tool_name = block.get("name", "")
                tool_input = block.get("input", block.get("args", {}))
                tool_calls.append({"name": tool_name, "input": tool_input})
                # Detectar arquivos modificados
                if tool_name in FILE_MODIFYING_TOOLS:
                    fp = tool_input.get("file_path", tool_input.get("TargetFile", ""))
                    if fp and isinstance(fp, str):
                        # Limpar aspas escapadas e whitespace
                        fp = fp.strip().strip('"').strip("'")
                        files_modified.append({"path": fp, "action": tool_name.lower()})
            elif block_type == "tool_result":
                # Resultados de ferramentas (em mensagens do user)
                result_content = block.get("content", "")
                if isinstance(result_content, list):
                    for rc in result_content:
                        if isinstance(rc, dict) and rc.get("type") == "text":
                            text_parts.append(rc.get("text", ""))
                elif isinstance(result_content, str):
                    text_parts.append(result_content)

    # Token usage
    usage = msg.get("usage", {})
    token_usage = {}
    if usage:
        token_usage = {
            "input": usage.get("input_tokens", 0),
            "output": usage.get("output_tokens", 0),
            "cache_read": usage.get("cache_read_input_tokens", 0),
            "cache_creation": usage.get("cache_creation_input_tokens", 0),
        }

    return SessionEntry(
        type=entry_type,
        timestamp=timestamp,
        session_id=session_id,
        slug=slug,
        role=role,
        content="\n".join(text_parts),
        tool_calls=tool_calls,
        token_usage=token_usage,
        model=model,
        files_modified=files_modified,
    )


def extract_user_messages(entries: list[SessionEntry]) -> list[str]:
    """Extrai apenas o texto das mensagens do usuário."""
    return [e.content for e in entries if e.role == "user" and e.content.strip()]


def extract_assistant_messages(entries: list[SessionEntry]) -> list[str]:
    """Extrai apenas o texto das respostas do assistente."""
    return [e.content for e in entries if e.role == "assistant" and e.content.strip()]


def extract_tool_calls(entries: list[SessionEntry]) -> list[dict]:
    """Extrai todas as chamadas de ferramentas."""
    calls = []
    for e in entries:
        calls.extend(e.tool_calls)
    return calls


def extract_files_modified(entries: list[SessionEntry]) -> list[dict]:
    """Extrai lista de arquivos modificados (sem duplicatas)."""
    seen = set()
    files = []
    for e in entries:
        for f in e.files_modified:
            key = f["path"]
            if key not in seen:
                seen.add(key)
                files.append(f)
    return files


def get_session_metadata(entries: list[SessionEntry]) -> dict:
    """Extrai metadados da sessão: slug, timestamps, modelo, tokens."""
    if not entries:
        return {}

    timestamps = [e.timestamp for e in entries if e.timestamp]
    slugs = [e.slug for e in entries if e.slug]
    models = [e.model for e in entries if e.model]

    total_input = sum(e.token_usage.get("input", 0) for e in entries)
    total_output = sum(e.token_usage.get("output", 0) for e in entries)
    total_cache = sum(e.token_usage.get("cache_read", 0) for e in entries)

    user_msgs = [e for e in entries if e.role == "user"]
    assistant_msgs = [e for e in entries if e.role == "assistant"]

    # Calcular duração
    duration_minutes = 0
    if len(timestamps) >= 2:
        try:
            t_start = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            t_end = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            duration_minutes = int((t_end - t_start).total_seconds() / 60)
        except (ValueError, IndexError):
            pass

    return {
        "slug": slugs[0] if slugs else "",
        "session_id": entries[0].session_id if entries else "",
        "start_time": timestamps[0] if timestamps else "",
        "end_time": timestamps[-1] if timestamps else "",
        "duration_minutes": duration_minutes,
        "model": models[0] if models else "",
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cache_tokens": total_cache,
        "message_count": len(user_msgs) + len(assistant_msgs),
        "tool_call_count": sum(len(e.tool_calls) for e in entries),
    }


def _discover_session_files() -> list[Path]:
    """Descobre arquivos de sessão independente do motor.

    Claude Code: <project>/<uuid>.jsonl (flat)
    Antigravity/Gemini: <uuid>/.system_generated/logs/overview.txt (nested NDJSON)
    """
    if not CLAUDE_SESSION_DIR.exists():
        return []
    flat = list(CLAUDE_SESSION_DIR.glob("*.jsonl"))
    if flat:
        return sorted(flat, key=lambda p: p.stat().st_mtime, reverse=True)
    nested = list(CLAUDE_SESSION_DIR.glob("*/.system_generated/logs/overview.txt"))
    return sorted(nested, key=lambda p: p.stat().st_mtime, reverse=True)


def get_latest_session_file() -> Optional[Path]:
    """Encontra o arquivo de sessão mais recente (JSONL ou overview.txt)."""
    files = _discover_session_files()
    return files[0] if files else None


def get_all_session_files() -> list[Path]:
    """Retorna todos os arquivos de sessão ordenados por mtime desc."""
    return _discover_session_files()
