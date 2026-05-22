"""
Busca full-text via SQLite FTS5 no histórico de sessões.
"""

import sqlite3
from pathlib import Path

from config import DB_PATH, MAX_SEARCH_RESULTS
from models import SearchResult


def _get_connection() -> sqlite3.Connection:
    """Retorna conexão SQLite com FTS5."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_search_db():
    """Cria tabela FTS5 se não existir."""
    conn = _get_connection()
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS session_search USING fts5(
            session_id,
            date,
            section,
            content,
            tokenize='unicode61'
        )
    """)
    conn.commit()
    conn.close()


def index_session(session_id: int, date: str, sections: dict[str, str]):
    """
    Indexa conteúdo de uma sessão.
    sections: {"topics": "texto", "decisions": "texto", ...}
    """
    conn = _get_connection()
    # Remove entradas antigas da mesma sessão
    conn.execute(
        "DELETE FROM session_search WHERE session_id = ?",
        (str(session_id),),
    )
    for section_name, content in sections.items():
        if content.strip():
            conn.execute(
                "INSERT INTO session_search (session_id, date, section, content) VALUES (?, ?, ?, ?)",
                (str(session_id), date, section_name, content),
            )
    conn.commit()
    conn.close()


def search(query: str, limit: int = MAX_SEARCH_RESULTS) -> list[SearchResult]:
    """Busca full-text no histórico."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            """
            SELECT session_id, date, section, snippet(session_search, 3, '>>>', '<<<', '...', 40)
            FROM session_search
            WHERE session_search MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        ).fetchall()
    except sqlite3.OperationalError:
        # Tabela não existe ou query inválida
        return []
    finally:
        conn.close()

    results = []
    for row in rows:
        # Tentar extrair o número da sessão. Se for formato longo (Claude), usa 0 como fallback.
        try:
            session_id_str = row[0]
            if session_id_str.startswith("session-"):
                # Formato longo: session-20260504-175336-claude-f2851171
                session_num = 0
            else:
                session_num = int(session_id_str)
        except (ValueError, TypeError):
            session_num = 0

        results.append(SearchResult(
            session_number=session_num,
            date=row[1],
            section=row[2],
            snippet=row[3],
        ))
    return results


def reindex_all(sessions_dir: Path):
    """Reconstrói índice a partir dos arquivos de sessão."""
    conn = _get_connection()
    conn.execute("DELETE FROM session_search")
    conn.commit()
    conn.close()

    for session_file in sorted(sessions_dir.glob("session-*.md")):
        # Detectar ID da sessão pelo nome do arquivo
        # Formato 1: session-001-antigravity.md -> 1
        # Formato 2: session-20260504-claude-f2851171.md -> 0 (ou extrair data)
        parts = session_file.stem.split("-")
        try:
            if len(parts[1]) <= 3:
                num = int(parts[1])
            else:
                # Sessão legada ou formato longo
                num = session_file.stem  # Usar a string completa como ID
        except (IndexError, ValueError):
            num = session_file.stem

        text = session_file.read_text(encoding="utf-8")
        date = ""
        sections = {}
        current_section = "general"

        for line in text.splitlines():
            if line.startswith("# Sessão") and "—" in line:
                date = line.split("—")[-1].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip().lower()
            else:
                sections.setdefault(current_section, "")
                sections[current_section] += line + "\n"

        index_session(num, date, sections)
