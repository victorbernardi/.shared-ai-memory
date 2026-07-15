#!/usr/bin/env python3
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from hybrid_validator import validate_source, validate_active_pipeline

SKILL_DIR = Path(__file__).parent.parent
CATALOG_PATH = SKILL_DIR / "config" / "platform_capabilities.yaml"
REFERENCES = SKILL_DIR / "references"
DRAFTER_AGENTS = [
    SKILL_DIR / "agents" / "code-drafter-agent.md",
    SKILL_DIR / "agents" / "code_drafter_agent.md",
]


def _load_catalog():
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


class TestHybridValidator(unittest.TestCase):
    def setUp(self):
        self.catalog = _load_catalog()
        self.base_dir = Path(tempfile.mkdtemp(prefix="stout-val-"))
        self.source_dir = self.base_dir / "demo-skill"
        self.source_dir.mkdir()
        (self.source_dir / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Use quando precisar testar.\n---\n# Demo\n",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def test_valid_source_passes(self) -> None:
        errors = validate_source(self.source_dir, self.catalog)
        self.assertEqual(errors, [])

    def test_missing_name_fails(self) -> None:
        (self.source_dir / "SKILL.md").write_text(
            "---\ndescription: Test\n---\n# Demo\n", encoding="utf-8"
        )
        errors = validate_source(self.source_dir, self.catalog)
        self.assertTrue(any("name" in e for e in errors))

    def test_missing_description_fails(self) -> None:
        (self.source_dir / "SKILL.md").write_text(
            "---\nname: demo-skill\n---\n# Demo\n", encoding="utf-8"
        )
        errors = validate_source(self.source_dir, self.catalog)
        self.assertTrue(any("description" in e for e in errors))

    def test_directory_name_mismatch_fails(self) -> None:
        mismatch_dir = self.base_dir / "wrong-name"
        mismatch_dir.mkdir()
        (mismatch_dir / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Test\n---\n# Demo\n",
            encoding="utf-8",
        )
        errors = validate_source(mismatch_dir, self.catalog)
        self.assertTrue(any("diretorio" in e for e in errors))
        shutil.rmtree(mismatch_dir)

    def test_required_unsupported_extension_blocks(self) -> None:
        (self.source_dir / "skill.platforms.yaml").write_text(
            yaml.dump({
                "targets": ["codex", "claude-code", "commandcode"],
                "extensions": [
                    {"id": "unknown.extension", "required": True, "value": {}},
                ],
            }),
            encoding="utf-8",
        )
        errors = validate_source(self.source_dir, self.catalog)
        self.assertTrue(any("obrigatoria" in e or "nao catalogada" in e for e in errors))

    def test_optional_extension_passes(self) -> None:
        (self.source_dir / "skill.platforms.yaml").write_text(
            yaml.dump({
                "targets": ["codex", "claude-code", "commandcode"],
                "extensions": [
                    {"id": "claude.allowed-tools", "required": False, "value": ["Read", "Grep"]},
                ],
            }),
            encoding="utf-8",
        )
        errors = validate_source(self.source_dir, self.catalog)
        self.assertEqual(errors, [])

    def test_wrong_value_type_fails(self) -> None:
        (self.source_dir / "skill.platforms.yaml").write_text(
            yaml.dump({
                "targets": ["codex", "claude-code", "commandcode"],
                "extensions": [
                    {"id": "claude.allowed-tools", "required": False, "value": "not-a-list"},
                ],
            }),
            encoding="utf-8",
        )
        errors = validate_source(self.source_dir, self.catalog)
        self.assertTrue(any("string_list" in e for e in errors))

    def test_active_legacy_scan_ignores_fixture_and_archive(self) -> None:
        active_roots = (Path(tempfile.mkdtemp(prefix="stout-active-")),)
        fixture_dir = active_roots[0] / "fixtures"
        fixture_dir.mkdir()
        (fixture_dir / "test.py").write_text(
            "<!-- @if platform=antigravity -->", encoding="utf-8"
        )
        archive_dir = active_roots[0] / "_archived"
        archive_dir.mkdir()
        (archive_dir / "old.py").write_text(
            "<!-- @if platform=antigravity -->", encoding="utf-8"
        )
        errors = validate_active_pipeline(active_roots)
        self.assertFalse(any("fixture" in e or "_archived" in e for e in errors))
        shutil.rmtree(active_roots[0])

    def test_active_legacy_detection(self) -> None:
        active_roots = (Path(tempfile.mkdtemp(prefix="stout-active-")),)
        active_roots[0].mkdir(parents=True, exist_ok=True)
        (active_roots[0] / "factory.py").write_text(
            "<!-- @if platform=antigravity -->", encoding="utf-8"
        )
        errors = validate_active_pipeline(active_roots)
        self.assertTrue(errors)
        shutil.rmtree(active_roots[0])

    def test_all_authoring_assets_name_the_multiformat_contract(self) -> None:
        for reference in ("platform-codex.md", "platform-claude.md", "platform-commandcode.md", "platform-hybrid.md"):
            self.assertTrue((REFERENCES / reference).exists(), f"Missing reference: {reference}")
        for agent in DRAFTER_AGENTS:
            if agent.exists():
                text = agent.read_text(encoding="utf-8")
                self.assertIn("platform-hybrid.md", text, f"{agent.name} missing platform-hybrid.md reference")
                self.assertIn("skill.platforms.yaml", text, f"{agent.name} missing skill.platforms.yaml reference")

    def test_no_active_antigravity_in_references(self) -> None:
        for ref in REFERENCES.glob("*.md"):
            if ref.name == "platform-hybrid.md":
                continue
            text = ref.read_text(encoding="utf-8")
            self.assertNotIn("antigravity", text.lower(), f"{ref.name} contains antigravity reference")

    def test_no_active_antigravity_in_templates(self) -> None:
        templates_dir = SKILL_DIR / "templates"
        for template in templates_dir.glob("*.md"):
            text = template.read_text(encoding="utf-8")
            self.assertNotIn("antigravity", text.lower(), f"{template.name} contains antigravity reference")


if __name__ == "__main__":
    unittest.main()
