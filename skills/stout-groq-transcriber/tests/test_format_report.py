#!/usr/bin/env python3
"""Regression tests for format_report.py import safety."""

import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


class FormatReportImportTests(unittest.TestCase):
    def test_module_import_is_side_effect_free(self) -> None:
        script_path = (
            Path(__file__).resolve().parents[1] / "scripts" / "format_report.py"
        )

        self.assertTrue(script_path.is_file())

        spec = spec_from_file_location("format_report", script_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertTrue(callable(module.main))
        self.assertTrue(callable(module.build_report))
        self.assertEqual(module.DEFAULT_CLEANUP_MODEL, "openai/gpt-oss-120b")


if __name__ == "__main__":
    unittest.main()
