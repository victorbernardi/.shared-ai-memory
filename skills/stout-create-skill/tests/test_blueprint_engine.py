#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import yaml

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS = SKILL_DIR / "scripts"
BLUEPRINT_ENGINE = SCRIPTS / "blueprint_engine.py"
SUPPORTED_PLATFORMS = ("codex", "claude-code", "commandcode")


class TestBlueprintEngine(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(tempfile.mkdtemp(prefix="stout-test-"))
        self.skill_dir = SKILL_DIR

    def tearDown(self):
        import shutil
        shutil.rmtree(self.output_dir, ignore_errors=True)

    def _run_engine(self, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
        cmd = [
            sys.executable, str(BLUEPRINT_ENGINE),
            "--tier", "2",
            "--name", "demo-skill",
            "--description", "Use quando precisar testar a skill demo.",
            "--output-dir", str(self.output_dir),
        ]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.output_dir))

    def test_engine_requires_output_dir(self) -> None:
        cmd = [
            sys.executable, str(BLUEPRINT_ENGINE),
            "--tier", "2",
            "--name", "demo-skill",
            "--description", "Use quando precisar testar a skill demo.",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output-dir", result.stderr)

    def test_engine_writes_three_targets_and_default_manifest(self) -> None:
        result = self._run_engine()
        self.assertEqual(result.returncode, 0, result.stderr)

        blueprint = json.loads((self.output_dir / "blueprint.json").read_text(encoding="utf-8"))
        config = json.loads((self.output_dir / "skill.config.json").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((self.output_dir / "skill.platforms.yaml").read_text(encoding="utf-8"))

        self.assertEqual(blueprint["target_platforms"], list(SUPPORTED_PLATFORMS))
        self.assertEqual(list(config["platforms"]), list(SUPPORTED_PLATFORMS))
        self.assertEqual(manifest, {"targets": list(SUPPORTED_PLATFORMS), "extensions": []})

    def test_output_dir_must_be_specified(self) -> None:
        cmd = [
            sys.executable, str(BLUEPRINT_ENGINE),
            "--tier", "2",
            "--name", "demo-skill",
            "--description", "Test",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
