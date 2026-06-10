import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def test_commandcode_session_dir_default():
    """COMMANDCODE_SESSION_DIR padrão deve apontar para ~/.commandcode/projects."""
    import importlib
    import config as cfg
    importlib.reload(cfg)

    user_profile = Path(os.getenv("USERPROFILE", str(Path.home())))
    expected = user_profile / ".commandcode" / "projects"
    assert cfg.COMMANDCODE_SESSION_DIR == expected, (
        f"Esperado {expected}, obtido {cfg.COMMANDCODE_SESSION_DIR}"
    )


def test_commandcode_origin_redirects_claude_session_dir():
    """SESSION_ORIGIN=commandcode deve direcionar CLAUDE_SESSION_DIR para COMMANDCODE_SESSION_DIR."""
    import importlib
    original = os.environ.get("CONTEXT_AGENT_ORIGIN")
    try:
        os.environ["CONTEXT_AGENT_ORIGIN"] = "commandcode"
        import config as cfg
        importlib.reload(cfg)

        user_profile = Path(os.getenv("USERPROFILE", str(Path.home())))
        expected = user_profile / ".commandcode" / "projects"
        assert cfg.CLAUDE_SESSION_DIR == expected, (
            f"Esperado {expected}, obtido {cfg.CLAUDE_SESSION_DIR}"
        )
    finally:
        if original is None:
            os.environ.pop("CONTEXT_AGENT_ORIGIN", None)
        else:
            os.environ["CONTEXT_AGENT_ORIGIN"] = original


def test_claude_origin_redirects_to_claude_projects():
    """SESSION_ORIGIN=claude deve direcionar CLAUDE_SESSION_DIR para ~/.claude/projects."""
    import importlib
    original = os.environ.get("CONTEXT_AGENT_ORIGIN")
    try:
        os.environ["CONTEXT_AGENT_ORIGIN"] = "claude"
        import config as cfg
        importlib.reload(cfg)

        user_profile = Path(os.getenv("USERPROFILE", str(Path.home())))
        expected = user_profile / ".claude" / "projects"
        assert cfg.CLAUDE_SESSION_DIR == expected, (
            f"Esperado {expected}, obtido {cfg.CLAUDE_SESSION_DIR}"
        )
    finally:
        if original is None:
            os.environ.pop("CONTEXT_AGENT_ORIGIN", None)
        else:
            os.environ["CONTEXT_AGENT_ORIGIN"] = original
