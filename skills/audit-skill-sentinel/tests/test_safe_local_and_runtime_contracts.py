import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SENTINEL_ROOT = Path(__file__).resolve().parents[1]
SENTINEL_SCRIPTS = SENTINEL_ROOT / "scripts"
sys.path.insert(0, str(SENTINEL_SCRIPTS))

from analyzers import code_quality, dependencies, governance_audit, security  # noqa: E402
from db import _build_insert_sql  # noqa: E402
import run_audit  # noqa: E402
from scanner import SkillScanner  # noqa: E402


class SafeLocalAnalyzerTests(unittest.TestCase):
    def _skill_data(self, root: Path, source: str, **metadata):
        script = root / "scripts" / "run.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(source, encoding="utf-8")
        return {
            "name": "fixture",
            "path": str(root),
            "python_files": ["scripts/run.py"],
            "file_count": 1,
            "requirements": [],
            **metadata,
        }

    def test_safe_local_profile_does_not_require_external_governance_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "import shutil\n\ndef remove_local(path):\n    shutil.rmtree(path)\n",
                sentinel_profile="safe-local",
            )
            score, findings = governance_audit.analyze(data)
            categories = {finding["category"] for finding in findings}
            self.assertEqual(score, 100.0)
            self.assertNotIn("no_governance", categories)
            self.assertNotIn("no_rate_limiting", categories)
            self.assertNotIn("no_confirmation", categories)

    def test_local_cleanup_is_not_classified_as_destructive_external_action(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "def remove_local(path):\n    return path\n",
            )
            _, findings = governance_audit.analyze(data)
            self.assertNotIn("no_confirmation", {finding["category"] for finding in findings})

    def test_stdlib_only_skill_does_not_require_requirements_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "from __future__ import annotations\nimport argparse\nfrom pathlib import Path\n",
            )
            score, findings = dependencies.analyze(data)
            self.assertEqual(score, 100.0)
            self.assertNotIn("missing_requirements", {finding["category"] for finding in findings})

    def test_reraised_broad_exception_is_not_reported_as_unhandled(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "def run():\n    try:\n        return 1\n    except Exception:\n        raise\n",
            )
            _, findings = code_quality.analyze(data)
            self.assertNotIn("broad_except", {finding["category"] for finding in findings})

    def test_sort_keys_is_not_a_secret_or_token_log(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "import json\nprint(json.dumps({'status': 'ok'}, sort_keys=True))\n",
            )
            _, findings = security.analyze(data)
            self.assertNotIn("token_in_log", {finding["category"] for finding in findings})

    def test_created_at_log_is_not_mistaken_for_sql_interpolation(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = self._skill_data(
                Path(temporary),
                "value = {'created_at': 'now'}\nprint(f\"created_at={value['created_at']}\")\n",
            )
            _, findings = security.analyze(data)
            self.assertNotIn("sql_injection", {finding["category"] for finding in findings})

    def test_dynamic_insert_identifiers_are_schema_validated(self):
        sql = _build_insert_sql("findings", ["audit_run_id", "title"])
        self.assertIn("INSERT INTO findings", sql)
        with self.assertRaises(ValueError):
            _build_insert_sql("findings", ["audit_run_id", "title; DROP TABLE findings"])

    def test_scanner_exposes_nested_sentinel_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: fixture\ndescription: Use when auditing.\n"
                "metadata:\n  sentinel_profile: safe-local\n---\n",
                encoding="utf-8",
            )
            info = SkillScanner(root)._analyze_skill(skill)
            self.assertEqual(info["sentinel_profile"], "safe-local")


class RuntimeContractTests(unittest.TestCase):
    def test_sentinel_configures_utf8_stdio_for_windows_runtimes(self):
        class FakeStream:
            def __init__(self):
                self.calls = []

            def reconfigure(self, **kwargs):
                self.calls.append(kwargs)

        stdout = FakeStream()
        stderr = FakeStream()
        original_stdout, original_stderr = run_audit.sys.stdout, run_audit.sys.stderr
        try:
            run_audit.sys.stdout = stdout
            run_audit.sys.stderr = stderr
            run_audit.configure_stdio()
        finally:
            run_audit.sys.stdout = original_stdout
            run_audit.sys.stderr = original_stderr
        self.assertEqual(stdout.calls, [{"encoding": "utf-8", "errors": "replace"}])
        self.assertEqual(stderr.calls, [{"encoding": "utf-8", "errors": "replace"}])

    def test_superpowers_skill_uses_codex_allowed_frontmatter_and_platform_metadata(self):
        skill_root = Path(__file__).parents[2] / "superpowers-update"
        content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        end = content.find("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        self.assertEqual(set(frontmatter) - {"name", "description", "metadata"}, set())
        metadata = frontmatter["metadata"]
        self.assertEqual(metadata["version"], "1.1.0")
        self.assertIn("codex", metadata["agents"])
        self.assertIn("commandcode", metadata["agents"])
        self.assertEqual(metadata["sentinel_profile"], "safe-local")

    def test_skill_sentinel_uses_codex_allowed_frontmatter_and_platform_metadata(self):
        skill_root = Path(__file__).parents[1]
        content = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        end = content.find("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        self.assertEqual(set(frontmatter) - {"name", "description", "metadata"}, set())
        metadata = frontmatter["metadata"]
        self.assertEqual(metadata["version"], "1.1.0")
        self.assertIn("codex", metadata["agents"])
        self.assertIn("commandcode", metadata["agents"])

    def test_superpowers_skill_has_codex_ui_metadata(self):
        skill_root = Path(__file__).parents[2] / "superpowers-update"
        interface = yaml.safe_load((skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))[
            "interface"
        ]
        self.assertTrue(interface["display_name"])
        self.assertGreaterEqual(len(interface["short_description"]), 25)
        self.assertLessEqual(len(interface["short_description"]), 64)
        self.assertIn("$superpowers-update", interface["default_prompt"])

    def test_skill_sentinel_has_codex_ui_metadata(self):
        skill_root = Path(__file__).parents[1]
        interface = yaml.safe_load((skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))["interface"]
        self.assertTrue(interface["display_name"])
        self.assertGreaterEqual(len(interface["short_description"]), 25)
        self.assertLessEqual(len(interface["short_description"]), 64)
        self.assertIn("$skill-sentinel", interface["default_prompt"])


if __name__ == "__main__":
    unittest.main()
