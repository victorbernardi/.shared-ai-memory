#!/usr/bin/env python3
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

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

        (self.source / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Test\n---\n# Demo\n", encoding="utf-8")
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
        self.assertEqual({item.status for item in report}, {"included", "skipped"})

    def test_skips_manifest_and_install_file(self) -> None:
        (self.source / "skill.platforms.yaml").write_text("targets: [codex]", encoding="utf-8")
        (self.source / ".stout-install.json").write_text("{}", encoding="utf-8")
        render_source(self.source, self.output, self.catalog)
        for platform in SUPPORTED_PLATFORMS:
            artifact = self.output / "rendered" / platform / "demo-skill"
            self.assertFalse((artifact / "skill.platforms.yaml").exists())
            self.assertFalse((artifact / ".stout-install.json").exists())

    def test_optional_claude_extension_is_skipped_elsewhere(self) -> None:
        report = render_source(self.source, self.output, self.catalog)
        statuses = {(item.platform, item.status) for item in report}
        self.assertIn(("claude-code", "included"), statuses)
        self.assertIn(("codex", "skipped"), statuses)
        self.assertIn(("commandcode", "skipped"), statuses)


if __name__ == "__main__":
    unittest.main()
