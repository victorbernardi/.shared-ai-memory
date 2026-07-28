import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from superpowers_update import (  # noqa: E402
    SyncError,
    build_report,
    compare_skill,
    copy_skill_files,
    default_targets,
    discover_skill_dirs,
    emit_report,
    normalize_content,
    run_apply,
    run_check,
    snapshot_skill,
    sync_skill_to_targets,
)


def make_skill_tree(root: Path, files: dict[str, str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return root


class SuperpowersUpdateTests(unittest.TestCase):
    def test_normalize_content_handles_crlf_and_lone_cr(self):
        self.assertEqual(normalize_content(b"a\r\nb\rc\n"), b"a\nb\nc\n")

    def test_snapshot_skill_is_recursive_and_normalized(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "SKILL.md").write_bytes(b"skill\r\n")
            (root / "scripts").mkdir()
            (root / "scripts" / "run.py").write_bytes(b"print('x')\r\n")
            self.assertEqual(
                snapshot_skill(root),
                {"SKILL.md": b"skill\n", "scripts/run.py": b"print('x')\n"},
            )

    def test_compare_ignores_crlf_but_detects_content_change(self):
        source = {"SKILL.md": b"line 1\nline 2\n"}
        target = {"SKILL.md": b"line 1\r\nline 2\r\n"}
        self.assertTrue(compare_skill(source, target)["equal"])

        target["SKILL.md"] = b"line 1\r\nlegacy\r\n"
        result = compare_skill(source, target)
        self.assertEqual(result["changed"], ["SKILL.md"])
        self.assertFalse(result["equal"])

    def test_compare_reports_missing_and_extra_files(self):
        result = compare_skill(
            {"SKILL.md": b"current", "scripts/run.py": b"run"},
            {"SKILL.md": b"current", "legacy.md": b"keep"},
        )
        self.assertEqual(result["missing"], ["scripts/run.py"])
        self.assertEqual(result["extra"], ["legacy.md"])
        self.assertFalse(result["equal"])

    def test_compare_ignores_extra_files_when_canonical_files_match(self):
        result = compare_skill(
            {"SKILL.md": b"current"},
            {"SKILL.md": b"current", "legacy.md": b"keep"},
        )
        self.assertEqual(result["extra"], ["legacy.md"])
        self.assertTrue(result["equal"])

    def test_build_report_classifies_changes_and_noop(self):
        comparisons = {
            "canonical": {
                "new-skill": compare_skill({"SKILL.md": b"new"}, {}),
                "same-skill": compare_skill({"SKILL.md": b"same"}, {"SKILL.md": b"same"}),
                "removed-local": {
                    **compare_skill({}, {"SKILL.md": b"old"}),
                    "source_managed": True,
                },
            }
        }
        report = build_report("abc123", comparisons)
        self.assertEqual(report["status"], "CHANGES_AVAILABLE")
        self.assertEqual(report["source_sha"], "abc123")
        self.assertEqual(report["changed_skills"], ["new-skill"])
        self.assertEqual(report["new_skills"], ["new-skill"])
        self.assertEqual(report["modified_skills"], [])
        self.assertEqual(report["removed_skills"], ["removed-local"])
        self.assertEqual(report["comparisons"]["canonical"]["new-skill"]["classification"], "new")
        self.assertEqual(
            report["comparisons"]["canonical"]["same-skill"]["classification"], "equal"
        )

        extra = build_report(
            "abc123",
            {"canonical": {"local-skill": compare_skill({}, {"SKILL.md": b"local"})}},
        )
        self.assertEqual(extra["status"], "NO_OP")
        self.assertEqual(extra["removed_skills"], [])
        self.assertEqual(extra["extra_skills"], {"canonical": ["local-skill"]})

        noop = build_report(
            "abc123",
            {"canonical": {"same-skill": comparisons["canonical"]["same-skill"]}},
        )
        self.assertEqual(noop["status"], "NO_OP")

    def test_discover_only_skill_directories_with_skill_md(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_skill_tree(root / "skills" / "valid", {"SKILL.md": "x"})
            (root / "skills" / "not-a-skill").mkdir()
            self.assertEqual(list(discover_skill_dirs(root)), ["valid"])

    def test_default_targets_are_in_expected_order(self):
        home = Path("C:/Users/example")
        self.assertEqual(
            default_targets(home),
            [
                home / ".shared-ai-memory" / "skills",
                home / ".agents" / "skills",
                home / ".codex" / "skills",
                home / ".claude" / "skills",
                home / ".commandcode" / "skills",
            ],
        )

    def test_run_check_and_apply_update_only_divergent_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_root = root / "repo"
            make_skill_tree(source_root / "skills" / "changed", {"SKILL.md": "new"})
            make_skill_tree(source_root / "skills" / "same", {"SKILL.md": "same"})
            target_root = make_skill_tree(
                root / "target" / "changed",
                {"SKILL.md": "old", "legacy.md": "keep"},
            ).parent
            make_skill_tree(target_root / "same", {"SKILL.md": "same"})

            checked = run_check(source_root, [target_root], "sha-test")
            self.assertEqual(checked["status"], "CHANGES_AVAILABLE")
            self.assertEqual(checked["modified_skills"], ["changed"])
            self.assertEqual(checked["equal_skills"], ["same"])

            applied = run_apply(source_root, [target_root], "sha-test")
            self.assertEqual(applied["status"], "UPDATED")
            self.assertEqual((target_root / "changed" / "SKILL.md").read_text(encoding="utf-8"), "new")
            self.assertEqual(
                (target_root / "changed" / "legacy.md").read_text(encoding="utf-8"), "keep"
            )
            self.assertEqual((target_root / "same" / "SKILL.md").read_text(encoding="utf-8"), "same")

    def test_report_is_written_only_when_explicit_path_is_given(self):
        report = {"status": "NO_OP"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch("builtins.print"):
                emit_report(report, None)
            self.assertEqual(list(root.iterdir()), [])
            path = root / "report.json"
            emit_report(report, path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), report)

    def test_copy_skill_files_preserves_destination_only_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = make_skill_tree(root / "source", {"SKILL.md": "new", "scripts/run.py": "run"})
            target = make_skill_tree(root / "target", {"SKILL.md": "old", "legacy.md": "keep"})
            copy_skill_files(source, target)
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "new")
            self.assertEqual((target / "legacy.md").read_text(encoding="utf-8"), "keep")
            self.assertEqual((target / "scripts" / "run.py").read_text(encoding="utf-8"), "run")

    def test_apply_updates_changed_skill_and_preserves_extra(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = make_skill_tree(root / "source", {"SKILL.md": "new"})
            target = make_skill_tree(root / "target", {"SKILL.md": "old", "legacy.md": "keep"})
            sync_skill_to_targets(source, [target])
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "new")
            self.assertEqual((target / "legacy.md").read_text(encoding="utf-8"), "keep")

    def test_sync_rolls_back_previous_target_when_later_target_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = make_skill_tree(root / "source", {"SKILL.md": "new"})
            first = make_skill_tree(root / "first", {"SKILL.md": "old"})
            failing_target = root / "failing-file"
            failing_target.write_text("not a directory", encoding="utf-8")
            with self.assertRaises(SyncError):
                sync_skill_to_targets(source, [first, failing_target])
            self.assertEqual((first / "SKILL.md").read_text(encoding="utf-8"), "old")


if __name__ == "__main__":
    unittest.main()
