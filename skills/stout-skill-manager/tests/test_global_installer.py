#!/usr/bin/env python3
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from global_installer import (
    GlobalTarget,
    install_artifacts,
    load_global_targets,
)


class TestGlobalInstaller(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(tempfile.mkdtemp(prefix="stout-inst-"))
        self.source_dir = self.base_dir / "source" / "demo-skill"
        self.source_dir.mkdir(parents=True)
        (self.source_dir / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")

        self.artifacts_dir = self.base_dir / "artifacts" / "demo-skill"
        for platform in ("codex", "claude-code", "commandcode"):
            rendered = self.artifacts_dir / "rendered" / platform / "demo-skill"
            rendered.mkdir(parents=True)
            (rendered / "SKILL.md").write_text(f"---\nname: demo\nplatform: {platform}\n---\n", encoding="utf-8")
            (rendered / "scripts").mkdir()
            (rendered / "scripts" / "run.py").write_text(f"print('{platform}')", encoding="utf-8")

        self.dest_base = self.base_dir / "global"
        self.global_targets = {
            "codex": GlobalTarget("codex", self.dest_base / "codex" / "skills"),
            "claude-code": GlobalTarget("claude-code", self.dest_base / "claude" / "skills"),
            "commandcode": GlobalTarget("commandcode", self.dest_base / "commandcode" / "skills"),
        }
        for target in self.global_targets.values():
            target.path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def test_install_creates_all_targets(self) -> None:
        result = install_artifacts(
            self.source_dir, self.artifacts_dir,
            ("codex", "claude-code", "commandcode"),
            replace=False, global_targets=self.global_targets,
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["installed"]), 3)
        for platform in ("codex", "claude-code", "commandcode"):
            dest = self.global_targets[platform].path / "demo-skill"
            self.assertTrue((dest / "SKILL.md").exists(), f"SKILL.md missing for {platform}")

    def test_collision_requires_replace(self) -> None:
        for platform in ("codex",):
            dest = self.global_targets[platform].path / "demo-skill"
            dest.mkdir()
            (dest / "SKILL.md").write_text("old", encoding="utf-8")

        result = install_artifacts(
            self.source_dir, self.artifacts_dir,
            ("codex",), replace=False, global_targets=self.global_targets,
        )
        self.assertEqual(result["status"], "collision")
        dest = self.global_targets["codex"].path / "demo-skill"
        self.assertEqual((dest / "SKILL.md").read_text(encoding="utf-8"), "old")

    def test_replace_overwrites_existing(self) -> None:
        dest = self.global_targets["codex"].path / "demo-skill"
        dest.mkdir()
        (dest / "SKILL.md").write_text("old", encoding="utf-8")

        result = install_artifacts(
            self.source_dir, self.artifacts_dir,
            ("codex",), replace=True, global_targets=self.global_targets,
        )
        self.assertEqual(result["status"], "ok")
        content = (dest / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("platform: codex", content)

    def test_second_copy_failure_restores_first_target(self) -> None:
        dest_codex = self.global_targets["codex"].path / "demo-skill"
        dest_codex.mkdir()
        (dest_codex / "SKILL.md").write_text("old-codex", encoding="utf-8")

        dest_claude = self.global_targets["claude-code"].path / "demo-skill"
        dest_claude.mkdir()
        (dest_claude / "SKILL.md").write_text("old-claude", encoding="utf-8")

        broken_artifacts = self.base_dir / "broken" / "demo-skill"
        broken_artifacts.mkdir(parents=True)
        (broken_artifacts / "rendered" / "codex" / "demo-skill").mkdir(parents=True)
        shutil.copy2(
            self.artifacts_dir / "rendered" / "codex" / "demo-skill" / "SKILL.md",
            broken_artifacts / "rendered" / "codex" / "demo-skill" / "SKILL.md",
        )
        (broken_artifacts / "rendered" / "claude-code").mkdir(parents=True)

        failing_targets = {
            "codex": GlobalTarget("codex", self.dest_base / "codex" / "skills"),
            "claude-code": GlobalTarget("claude-code", self.dest_base / "claude" / "skills"),
        }

        result = install_artifacts(
            self.source_dir, broken_artifacts,
            ("codex", "claude-code"), replace=True, global_targets=failing_targets,
        )

        self.assertEqual(result["status"], "error")
        self.assertTrue(result["rolled_back"])

    def test_stout_install_json_written(self) -> None:
        result = install_artifacts(
            self.source_dir, self.artifacts_dir,
            ("codex",), replace=False, global_targets=self.global_targets,
        )
        self.assertEqual(result["status"], "ok")
        install_json = self.source_dir / ".stout-install.json"
        self.assertTrue(install_json.exists())
        data = __import__("json").loads(install_json.read_text(encoding="utf-8"))
        self.assertEqual(data["skill_name"], "demo-skill")
        self.assertIn("codex", data["targets"])


class TestGlobalTargets(unittest.TestCase):
    def test_load_returns_three_targets(self) -> None:
        config_path = Path(__file__).parent.parent / "config" / "global_targets.yaml"
        targets = load_global_targets(config_path)
        self.assertEqual(set(targets.keys()), {"codex", "claude-code", "commandcode"})
        for platform, target in targets.items():
            self.assertEqual(target.platform, platform)


if __name__ == "__main__":
    unittest.main()
