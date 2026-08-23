import json
from pathlib import Path


SKILL_DIR = Path(__file__).parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
REGISTRY_PATH = REPO_ROOT / "skills" / "stout-skill-registry" / "registry.json"


def _read_skill() -> str:
    skill_path = SKILL_DIR / "SKILL.md"
    assert skill_path.is_file(), f"missing BUP skill document: {skill_path}"
    return skill_path.read_text(encoding="utf-8")


def _read_json(path: Path):
    assert path.is_file(), f"missing BUP metadata: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_entries():
    registry = _read_json(REGISTRY_PATH)
    return {entry["name"]: entry for entry in registry["skills"]}


def test_bup_document_uses_governed_monorepo_contract():
    skill = _read_skill()

    for required in (
        r"C:\Projetos\Inova",
        "refresh_governance.json",
        "dependency_governance.py",
        r".venv\Scripts\python.exe",
        "test_bup_scheduler_log.py",
        "test_bup_output_invariants.py",
        "BUP_POS_VENDA.xlsx",
    ):
        assert required in skill


def test_bup_metadata_targets_all_active_platforms_and_delivered_files():
    config = _read_json(SKILL_DIR / "skill.config.json")
    blueprint = _read_json(SKILL_DIR / "blueprint.json")

    assert set(config["platforms"]) == {
        "claude-code",
        "antigravity",
        "commandcode",
        "codex",
    }
    assert config["platforms"]["codex"]["output"] == ".codex/skills"
    assert set(blueprint["target_platforms"]) == set(config["platforms"])
    assert blueprint["structure"] == ["SKILL.md", "tests/"]


def test_bup_registry_entry_declares_only_real_upstream_dependencies():
    entries = _registry_entries()
    bup = entries["inova-bup-refresh"]

    assert bup["path"] == "skills/inova-bup-refresh"
    assert bup["status"] == "active"
    assert bup["dependencies"] == [
        "inova-pipeline-01",
        "inova-motor-faturamento",
        "inova-motor-orcamentos",
    ]
