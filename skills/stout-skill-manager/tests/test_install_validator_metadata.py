import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from install_validator import extract_frontmatter, validate  # noqa: E402


class InstallValidatorMetadataTests(unittest.TestCase):
    def test_metadata_version_satisfies_stout_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: fixture\n"
                "description: Use when validating a fixture skill.\n"
                "metadata:\n"
                "  version: 1.0.0\n"
                "  tier: 2\n"
                "  tools:\n"
                "    - python\n"
                "---\n",
                encoding="utf-8",
            )
            fields = extract_frontmatter(skill / "SKILL.md")
            self.assertIsInstance(fields["metadata"], dict)
            self.assertEqual(fields["metadata"]["version"], "1.0.0")
            self.assertEqual(fields["version"], "1.0.0")

            ok, errors, _ = validate(skill)
            self.assertTrue(ok, errors)


if __name__ == "__main__":
    unittest.main()
