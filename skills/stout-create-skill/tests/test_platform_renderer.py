#!/usr/bin/env python3
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from platform_contract import SUPPORTED_PLATFORMS, load_catalog
from platform_renderer import render_source

SKILL_DIR = Path(__file__).parent.parent
CATALOG_PATH = SKILL_DIR / "config" / "platform_capabilities.yaml"


class TestPlatformRenderer(unittest.TestCase):
    def setUp(self):
        self.source = Path(tempfile.mkdtemp(prefix="stout-src-"))
        self.output = Path(tempfile.mkdtemp(prefix="stout-out-"))
        self.catalog = load_catalog(CATALOG_PATH)

        (self.source / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Test\n---\n# Demo\n", encoding="utf-8"
        )
        (self.source / "scripts").mkdir()
        (self.source / "scripts" / "check.py").write_text("print('ok')", encoding="utf-8")
        (self.source / "tests").mkdir()
        (self.source / "tests" / "__init__.py").write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.source, ignore_errors=True)
        shutil.rmtree(self.output, ignore_errors=True)

    def test_renderer_copies_common_files_to_each_target(self) -> None:
        report = render_source(self.source, self.output, self.catalog)
        for platform in SUPPORTED_PLATFORMS:
            artifact = self.output / "rendered" / platform / "demo-skill"
            self.assertTrue((artifact / "SKILL.md").exists(), f"SKILL.md missing for {platform}")
            self.assertTrue((artifact / "scripts" / "check.py").exists(), f"scripts/check.py missing for {platform}")

    def test_skips_manifest_and_install_file(self) -> None:
        (self.source / "skill.platforms.yaml").write_text("targets: [codex]", encoding="utf-8")
        (self.source / ".stout-install.json").write_text("{}", encoding="utf-8")
        render_source(self.source, self.output, self.catalog)
        for platform in SUPPORTED_PLATFORMS:
            artifact = self.output / "rendered" / platform / "demo-skill"
            self.assertFalse((artifact / "skill.platforms.yaml").exists())
            self.assertFalse((artifact / ".stout-install.json").exists())

    def test_manifest_codex_only_renders_only_codex(self) -> None:
        manifest = {"targets": ["codex"], "extensions": []}
        (self.source / "skill.platforms.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        report = render_source(self.source, self.output, self.catalog)
        self.assertTrue((self.output / "rendered" / "codex" / "demo-skill" / "SKILL.md").exists())
        self.assertFalse((self.output / "rendered" / "claude-code" / "demo-skill").exists())
        self.assertFalse((self.output / "rendered" / "commandcode" / "demo-skill").exists())

    def test_no_manifest_renders_all_platforms(self) -> None:
        report = render_source(self.source, self.output, self.catalog)
        for platform in SUPPORTED_PLATFORMS:
            self.assertTrue((self.output / "rendered" / platform / "demo-skill").exists())

    def test_claude_extension_applies_frontmatter_only_to_claude(self) -> None:
        manifest = {
            "targets": ["codex", "claude-code", "commandcode"],
            "extensions": [
                {"id": "claude.allowed-tools", "required": False, "value": ["Read", "Grep"]},
            ],
        }
        (self.source / "skill.platforms.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        report = render_source(self.source, self.output, self.catalog)

        statuses = {(item.extension_id, item.platform, item.status) for item in report}
        self.assertIn(("claude.allowed-tools", "claude-code", "included"), statuses)
        self.assertIn(("claude.allowed-tools", "codex", "skipped"), statuses)
        self.assertIn(("claude.allowed-tools", "commandcode", "skipped"), statuses)

        claude_fm = (self.output / "rendered" / "claude-code" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("allowed-tools", claude_fm)

        codex_fm = (self.output / "rendered" / "codex" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("allowed-tools", codex_fm)

    def test_codex_file_extension_creates_file_only_in_codex(self) -> None:
        manifest = {
            "targets": ["codex", "claude-code", "commandcode"],
            "extensions": [
                {"id": "codex.openai-ui-metadata", "required": False, "value": {"type": "skill"}},
            ],
        }
        (self.source / "skill.platforms.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        render_source(self.source, self.output, self.catalog)

        codex_file = self.output / "rendered" / "codex" / "demo-skill" / "agents" / "openai.yaml"
        self.assertTrue(codex_file.exists(), "agents/openai.yaml should exist for codex")

        claude_file = self.output / "rendered" / "claude-code" / "demo-skill" / "agents" / "openai.yaml"
        self.assertFalse(claude_file.exists(), "agents/openai.yaml should NOT exist for claude-code")

    def test_report_only_contains_requested_extensions(self) -> None:
        manifest = {
            "targets": ["codex", "claude-code"],
            "extensions": [
                {"id": "claude.allowed-tools", "required": False, "value": ["Read"]},
            ],
        }
        (self.source / "skill.platforms.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        report = render_source(self.source, self.output, self.catalog)
        reported_ids = {item.extension_id for item in report}
        self.assertEqual(reported_ids, {"claude.allowed-tools"})

    def test_unsupported_required_extension_produces_error(self) -> None:
        manifest = {
            "targets": ["codex", "claude-code", "commandcode"],
            "extensions": [
                {"id": "unknown.extension", "required": True, "value": {}},
            ],
        }
        (self.source / "skill.platforms.yaml").write_text(
            yaml.dump(manifest), encoding="utf-8"
        )
        report = render_source(self.source, self.output, self.catalog)
        errors = [item for item in report if item.status == "error"]
        self.assertTrue(len(errors) > 0, "Should report error for unknown extension")


if __name__ == "__main__":
    unittest.main()
