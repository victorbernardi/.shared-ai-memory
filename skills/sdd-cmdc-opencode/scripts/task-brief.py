#!/usr/bin/env python3
"""Extract a task brief and its deterministic file scope from a Markdown plan."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Iterable


class TaskBriefError(ValueError):
    """The plan or its declared scope does not satisfy the helper contract."""


class TaskNotFoundError(TaskBriefError):
    """The requested task heading is not present in the plan."""


_HEADING_RE = re.compile(r"^(?P<marks>#{1,6})[ \t]+(?P<text>.*?)\s*$")
_TASK_RE = re.compile(
    r"^(?:(?:[0-9]+)[.)]?[ \t]+)?"
    r"(?P<kind>Task|Tarefa)[ \t]+(?P<number>[0-9]+)"
    r"(?=$|[ \t:.)-])",
    re.IGNORECASE,
)
_FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
_FILES_SECTION_RE = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]+)?(?:\*\*|__)?[ \t]*"
    r"(?P<name>Files|Arquivos)[ \t]*:[ \t]*"
    r"(?:\*\*|__)?[ \t]*$",
    re.IGNORECASE,
)
_LABEL_BOUNDARY_RE = re.compile(
    r"^[ \t]*(?:\*\*|__)[^*_\r\n]+(?:\*\*|__)[ \t]*:?\s*$"
)
_ACTION_RE = re.compile(
    r"^[ \t]*[-+*][ \t]*"
    r"(?:(?:\*\*|__)[ \t]*)?"
    r"(?P<action>Create|Modify|Test|Delete|Criar|Modificar|Teste|Excluir)"
    r"(?:[ \t]*(?:\*\*|__))?[ \t]*:[ \t]*"
    r"(?P<value>.*?)\s*$",
    re.IGNORECASE,
)
_CODE_SPAN_RE = re.compile(r"`([^`\r\n]+)`")
_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_WILDCARD_CHARS = frozenset("*?[]")


def _without_line_ending(line: str) -> str:
    return line[:-2] if line.endswith("\r\n") else line.rstrip("\n\r")


def _heading_records(lines: list[str]) -> Iterable[tuple[int, int, str, re.Match[str]]]:
    in_fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        fence_match = _FENCE_RE.match(line)
        if in_fence is not None:
            if fence_match:
                marker = fence_match.group("fence")
                if marker[0] == in_fence[0] and len(marker) >= in_fence[1]:
                    remainder = line[fence_match.end() :].strip()
                    if not remainder:
                        in_fence = None
            continue
        if fence_match:
            marker = fence_match.group("fence")
            in_fence = (marker[0], len(marker))
            continue
        heading_match = _HEADING_RE.match(_without_line_ending(line))
        if heading_match:
            yield (
                index,
                len(heading_match.group("marks")),
                heading_match.group("text"),
                heading_match,
            )


def _task_number(heading_text: str) -> int | None:
    match = _TASK_RE.match(heading_text.strip())
    if not match:
        return None
    return int(match.group("number"))


def extract_task(plan_text: str, task_number: int) -> tuple[str, str]:
    """Return the exact Markdown heading and body for one task.

    Task headings inside fenced code are ignored. A later task heading ends the
    body only when it is at the same or a higher Markdown level.
    """

    if isinstance(task_number, bool) or not isinstance(task_number, int) or task_number < 1:
        raise TaskBriefError("task number must be a positive integer")

    lines = plan_text.splitlines(keepends=True)
    records = list(_heading_records(lines))
    target: tuple[int, int, str, re.Match[str]] | None = None
    for record in records:
        if _task_number(record[2]) == task_number:
            target = record
            break
    if target is None:
        raise TaskNotFoundError(f"task {task_number} not found")

    start, level, _, _ = target
    end = len(lines)
    for index, candidate_level, candidate_text, _ in records:
        if index <= start:
            continue
        if candidate_level <= level and _task_number(candidate_text) is not None:
            end = index
            break

    heading = _without_line_ending(lines[start])
    body = "".join(lines[start + 1 : end])
    if body:
        body = body.rstrip("\r\n") + "\n"
    return heading, body


def _is_section_boundary(line: str) -> bool:
    stripped = line.strip()
    return bool(_HEADING_RE.match(stripped) or _LABEL_BOUNDARY_RE.match(line))


def _normalize_declared_path(raw_path: str) -> str:
    normalized = unicodedata.normalize("NFC", raw_path.strip()).replace("\\", "/")
    if not normalized:
        raise TaskBriefError("declared path is empty")
    if normalized.startswith("/") or _DRIVE_RE.match(normalized):
        raise TaskBriefError(f"declared path is not repository-relative: {raw_path}")
    if any(character in normalized for character in _WILDCARD_CHARS):
        raise TaskBriefError(f"declared path contains a wildcard: {raw_path}")

    has_trailing_separator = normalized.endswith("/")
    parts: list[str] = []
    for part in normalized.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise TaskBriefError(f"declared path contains '..': {raw_path}")
        parts.append(part)
    if not parts:
        raise TaskBriefError(f"declared path is empty: {raw_path}")
    result = "/".join(parts)
    return result + "/" if has_trailing_separator else result


def extract_declared_files(task_text: str) -> tuple[str, ...]:
    """Extract strict repository-relative paths from a task-local Files section."""

    lines = task_text.splitlines(keepends=True)
    section_start: int | None = None
    for index, line in enumerate(lines):
        if _FILES_SECTION_RE.match(_without_line_ending(line)):
            section_start = index + 1
            break
    if section_start is None:
        raise TaskBriefError("task has no Files/Arquivos section")

    paths: list[str] = []
    seen_exact: set[str] = set()
    seen_casefolded: set[str] = set()
    found_boundary = False
    for line in lines[section_start:]:
        if _is_section_boundary(line):
            found_boundary = True
            break
        if not line.strip():
            continue
        action_match = _ACTION_RE.match(_without_line_ending(line))
        if action_match is None:
            raise TaskBriefError(
                "Files/Arquivos entries must use a recognized action and backtick path"
            )
        value = action_match.group("value").strip()
        spans = list(_CODE_SPAN_RE.finditer(value))
        if len(spans) != 1 or value[: spans[0].start()].strip() or value[spans[0].end() :].strip():
            raise TaskBriefError(
                "Files/Arquivos entries must contain exactly one backtick path"
            )
        path = _normalize_declared_path(spans[0].group(1))
        if path in seen_exact:
            continue
        if os.name == "nt":
            casefolded = path.casefold()
            if casefolded in seen_casefolded:
                raise TaskBriefError(f"duplicate path with conflicting spelling: {path}")
            seen_casefolded.add(casefolded)
        seen_exact.add(path)
        paths.append(path)

    if not found_boundary and section_start == len(lines):
        found_boundary = True
    if not paths:
        raise TaskBriefError("Files/Arquivos section contains no declared paths")
    return tuple(paths)


def _read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _validate_output_path(path: Path, label: str) -> None:
    if path.exists() and not path.is_file():
        raise TaskBriefError(f"{label} path is not a regular file: {path}")
    if not path.parent.is_dir():
        raise TaskBriefError(f"output directory does not exist: {path.parent}")


def _atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=str(path.parent),
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _git_root(start: Path) -> Path:
    completed = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise TaskBriefError("could not resolve the repository root for the default output")
    return Path(completed.stdout.strip()).resolve()


def _default_output(plan_path: Path, task_number: int) -> Path:
    root = _git_root(plan_path.parent)
    workspace_root = root / ".superpowers" / "sdd"
    workspace = workspace_root / plan_path.stem
    workspace.mkdir(parents=True, exist_ok=True)
    gitignore = workspace_root / ".gitignore"
    if not gitignore.exists():
        _atomic_write(gitignore, "*\n")
    return workspace / f"task-{task_number}-brief.md"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract one task and optionally derive its declared file scope."
    )
    parser.add_argument("plan_file")
    parser.add_argument("task_number")
    parser.add_argument("outfile", nargs="?")
    parser.add_argument("--scope-json", dest="scope_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if not re.fullmatch(r"[0-9]+", args.task_number):
            raise TaskBriefError(f"task number must be numeric: {args.task_number}")
        task_number = int(args.task_number)
        if task_number < 1:
            raise TaskBriefError("task number must be a positive integer")

        plan_path = Path(args.plan_file)
        if not plan_path.is_file():
            raise TaskBriefError(f"no such plan file: {plan_path}")
        output_path = (
            Path(args.outfile)
            if args.outfile
            else _default_output(plan_path, task_number)
        )
        scope_path = Path(args.scope_json) if args.scope_json else None
        _validate_output_path(output_path, "output")
        if scope_path is not None:
            _validate_output_path(scope_path, "scope output")
            if scope_path == output_path:
                raise TaskBriefError("output and scope JSON paths must differ")

        heading, body = extract_task(_read_text(plan_path), task_number)
        scope_content: str | None = None
        if scope_path is not None:
            allowed_paths = extract_declared_files(heading + "\n" + body)
            scope_content = json.dumps(
                {
                    "source": "task-files-section",
                    "task_heading": re.sub(r"^#{1,6}[ \t]+", "", heading),
                    "allowed_paths": list(allowed_paths),
                },
                ensure_ascii=False,
                indent=2,
            ) + "\n"

        output_content = heading + "\n" + body
        _atomic_write(output_path, output_content)
        if scope_path is not None and scope_content is not None:
            _atomic_write(scope_path, scope_content)
        print(f"wrote {output_path}: {len(output_content.splitlines())} lines")
        return 0
    except TaskNotFoundError as error:
        print(f"Task {args.task_number} not found in {args.plan_file}", file=sys.stderr)
        return 3
    except (OSError, TaskBriefError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
