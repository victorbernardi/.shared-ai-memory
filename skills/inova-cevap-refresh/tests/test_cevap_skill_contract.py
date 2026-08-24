import json
from pathlib import Path


SKILL_DIR = Path(__file__).parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
REGISTRY_PATH = REPO_ROOT / "skills" / "stout-skill-registry" / "registry.json"


def _read_skill() -> str:
    skill_path = SKILL_DIR / "SKILL.md"
    assert skill_path.is_file(), f"missing CEVAP skill document: {skill_path}"
    return skill_path.read_text(encoding="utf-8")


def _read_json(path: Path):
    assert path.is_file(), f"missing CEVAP metadata: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_entries():
    registry = _read_json(REGISTRY_PATH)
    return {entry["name"]: entry for entry in registry["skills"]}


def test_cevap_document_uses_standalone_runtime_contract():
    skill = _read_skill()

    for required in (
        r"C:\Projetos\Inova.maquinas\motor-cevap",
        "CEVAP_BUP_PATH",
        "CEVAP_ONEDRIVE_PATH",
        "uv run --no-project",
        "scripts/consolidate_cevap.py",
        "test_inactivity_filter.py",
        "test_governance.py",
        "test_onedrive.py",
        "data/CEVAP_ATIVACAO.xlsx",
        "data/backups/CEVAP_ATIVACAO_backup_",
    ):
        assert required in skill

    assert "data/CEVAP_ATIVACAO_<" not in skill
    assert r"C:\Projetos\Inova\projects\motor-cevap" not in skill
    assert "Set-Location (Join-Path $repo \"projects\\motor-cevap\")" not in skill


def test_cevap_metadata_targets_all_active_platforms_and_delivered_files():
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
    assert blueprint["structure"] == [
        "SKILL.md",
        "tests/",
        "tests/test_cevap_skill_contract.py",
    ]


def test_cevap_registry_depends_on_bup_only():
    entries = _registry_entries()
    cevap = entries["inova-cevap-refresh"]

    assert cevap["path"] == "skills/inova-cevap-refresh"
    assert cevap["status"] == "active"
    assert cevap["dependencies"] == ["inova-bup-refresh"]
