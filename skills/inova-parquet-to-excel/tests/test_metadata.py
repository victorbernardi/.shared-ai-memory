import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_skill_metadata_is_valid():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "name: inova-parquet-to-excel" in text
    assert "parquet" in text.lower() and "xlsx" in text.lower()
    config = json.loads((ROOT / "skill.config.json").read_text(encoding="utf-8"))
    assert config["body"]["source"] == "SKILL.md"
    assert all(config["platforms"][p]["enabled"] for p in ("codex", "claude-code", "commandcode"))
