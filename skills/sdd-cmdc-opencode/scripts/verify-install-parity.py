#!/usr/bin/env python3
"""Audit that one installed skill tree has exactly the source tree's bytes."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


IGNORED_DIRECTORIES = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def _files(root: Path) -> dict[Path, str]:
    """Return regular-file SHA-256 hashes keyed by root-relative paths."""
    result: dict[Path, str] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result[relative] = digest
    return result


def compare(source: Path, target: Path) -> list[str]:
    source_files = _files(source)
    target_files = _files(target)
    lines: list[str] = []
    for relative in sorted(source_files.keys() - target_files.keys(), key=str):
        lines.append(f"MISSING {relative.as_posix()}")
    for relative in sorted(target_files.keys() - source_files.keys(), key=str):
        lines.append(f"EXTRA {relative.as_posix()}")
    for relative in sorted(source_files.keys() & target_files.keys(), key=str):
        if source_files[relative] != target_files[relative]:
            lines.append(f"CHANGED {relative.as_posix()}")
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("targets", nargs="+", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_dir():
        print(f"source is not a directory: {source}", file=sys.stderr)
        return 2
    exit_code = 0
    for raw_target in args.targets:
        target = raw_target.expanduser().resolve()
        if not target.is_dir():
            print(f"TARGET {target}")
            print(f"MISSING_TARGET {target}")
            exit_code = 1
            continue
        differences = compare(source, target)
        print(f"TARGET {target}")
        if differences:
            for line in differences:
                print(line)
            exit_code = 1
        else:
            print("PARITY: OK")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
