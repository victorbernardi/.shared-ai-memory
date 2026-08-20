from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "task-brief"
PYTHON_SCRIPT = SCRIPT.with_suffix(".py")


def _task_brief_module():
    if not PYTHON_SCRIPT.is_file():
        pytest.fail("task-brief.py is absent")
    spec = importlib.util.spec_from_file_location("task_brief_under_test", PYTHON_SCRIPT)
    if spec is None or spec.loader is None:
        pytest.fail("could not load task-brief.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bash() -> str:
    path = shutil.which("bash")
    if not path:
        pytest.skip("bash is required to execute scripts/task-brief")
    return path


def _run(plan: Path, task: int, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_bash(), str(SCRIPT), str(plan), str(task), str(output)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _run_python(
    plan: Path,
    task: int,
    output: Path | None = None,
    scope_json: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(PYTHON_SCRIPT), str(plan), str(task)]
    if output is not None:
        command.append(str(output))
    if scope_json is not None:
        command.extend(["--scope-json", str(scope_json)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "heading",
    (
        "## Task 3: English heading",
        "## Tarefa 3: Cabeçalho em português",
        "## 8. Tarefa 3: Cabeçalho numerado",
    ),
)
def test_extract_task_returns_exact_heading_and_ignores_fenced_headings(
    heading: str,
) -> None:
    module = _task_brief_module()
    plan = f"""# Plan

{heading}
Keep this task body exactly.

```markdown
## Task 3: fake heading inside a fence
## Task 99: another fake heading
```

### Step 1
This lower-level heading belongs to Task 3.

## Task 4: Next task
Do not include this text.
"""

    extracted_heading, body = module.extract_task(plan, 3)

    assert extracted_heading == heading
    assert "Keep this task body exactly." in body
    assert "fake heading inside a fence" in body
    assert "This lower-level heading belongs to Task 3." in body
    assert "Do not include this text." not in body
    assert not body.endswith("\n\n")


def test_extract_declared_files_is_deterministic_and_normalizes_separators() -> None:
    module = _task_brief_module()

    task = """## Task 3: Scope

**Files:**
- Modify: `src\\run.py`
- Test: `tests/test_run.py`

**Interfaces:**
The rest of the task is not a file declaration.
"""

    assert module.extract_declared_files(task) == (
        "src/run.py",
        "tests/test_run.py",
    )


@pytest.mark.parametrize(
    "files_section",
    (
        "- Modify: `/absolute/run.py`",
        "- Modify: `C:\\repo\\run.py`",
        "- Modify: `\\\\server\\share\\run.py`",
        "- Modify: `src/../run.py`",
        "- Modify: `src/*.py`",
        "- Modify: src/run.py",
        "This prose is not a declaration.",
    ),
)
def test_extract_declared_files_rejects_ambiguous_or_unsafe_entries(
    files_section: str,
) -> None:
    module = _task_brief_module()
    task = f"""## Task 3: Scope

**Files:**
{files_section}
"""

    with pytest.raises(ValueError):
        module.extract_declared_files(task)


def test_extract_declared_files_rejects_missing_section_and_conflicting_duplicates() -> None:
    module = _task_brief_module()

    with pytest.raises(ValueError):
        module.extract_declared_files("## Task 3\nNo Files section.\n")

    duplicate = """## Task 3: Scope

**Files:**
- Modify: `src/run.py`
- Test: `SRC\\RUN.PY`
"""
    if os.name == "nt":
        with pytest.raises(ValueError):
            module.extract_declared_files(duplicate)
    else:
        assert module.extract_declared_files(duplicate) == (
            "src/run.py",
            "SRC/RUN.PY",
        )


def test_python_cli_writes_scope_json_and_preserves_task_output_contract(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-3-brief.md"
    scope = tmp_path / "scope.json"
    plan.write_text(
        """# Plan

## Task 3
Implement the scoped task.

**Files:**
- Modify: `src/run.py`
- Teste: `tests/test_run.py`

## Task 4
Do not include this task.
""",
        encoding="utf-8",
    )

    result = _run_python(plan, 3, output, scope)

    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == (
        "## Task 3\nImplement the scoped task.\n\n"
        "**Files:**\n- Modify: `src/run.py`\n- Teste: `tests/test_run.py`\n"
    )
    assert json.loads(scope.read_text(encoding="utf-8")) == {
        "source": "task-files-section",
        "task_heading": "Task 3",
        "allowed_paths": ["src/run.py", "tests/test_run.py"],
    }


def test_python_cli_failure_does_not_replace_existing_output_or_scope(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-99-brief.md"
    scope = tmp_path / "scope.json"
    plan.write_text("# Plan\n\n## Task 1: Only task\n\nText.\n", encoding="utf-8")
    output.write_text("previous brief\n", encoding="utf-8")
    scope.write_text('{"previous": true}\n', encoding="utf-8")

    result = _run_python(plan, 99, output, scope)

    assert result.returncode == 3
    assert output.read_text(encoding="utf-8") == "previous brief\n"
    assert scope.read_text(encoding="utf-8") == '{"previous": true}\n'


def test_python_cli_rejects_missing_files_section_without_creating_scope(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-3-brief.md"
    scope = tmp_path / "scope.json"
    plan.write_text("# Plan\n\n## Task 3\nNo declared files.\n", encoding="utf-8")

    result = _run_python(plan, 3, output, scope)

    assert result.returncode == 2
    assert "Files" in result.stderr or "Arquivos" in result.stderr
    assert not output.exists()
    assert not scope.exists()


def test_task_brief_accepts_portuguese_numbered_heading(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-7-brief.md"
    plan.write_text(
        """# Plano

## 8. Tarefa 7: Preflight

Implementar a validação bilíngue.

```markdown
## Tarefa 7: fake heading inside a fence
```

## Tarefa 8: Próxima
Não incluir este texto.
""",
        encoding="utf-8",
    )

    result = _run(plan, 7, output)

    assert result.returncode == 0, result.stderr
    assert "Tarefa 7" in output.read_text(encoding="utf-8")
    assert "Implementar a validação bilíngue." in output.read_text(encoding="utf-8")
    assert "Tarefa 8" not in output.read_text(encoding="utf-8")
    assert "fake heading" in output.read_text(encoding="utf-8")


def test_task_brief_keeps_english_heading_compatibility(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-3-brief.md"
    plan.write_text(
        "# Plan\n\n### 2. Task 3: Existing task\n\nKeep this contract.\n",
        encoding="utf-8",
    )

    result = _run(plan, 3, output)

    assert result.returncode == 0, result.stderr
    assert "Keep this contract." in output.read_text(encoding="utf-8")


def test_task_brief_failure_does_not_destroy_existing_output(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "task-99-brief.md"
    plan.write_text("# Plan\n\n## Tarefa 1: Only task\n\nText.\n", encoding="utf-8")
    output.write_text("previous brief\n", encoding="utf-8")

    result = _run(plan, 99, output)

    assert result.returncode == 3
    assert "Task 99" in result.stderr or "Tarefa 99" in result.stderr
    assert output.read_text(encoding="utf-8") == "previous brief\n"


def test_task_brief_rejects_directory_output_without_mutation(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    output = tmp_path / "brief-output"
    plan.write_text("# Plan\n\n## Tarefa 1: Only task\n\nText.\n", encoding="utf-8")
    output.mkdir()

    result = _run(plan, 1, output)

    assert result.returncode == 2
    assert "not a regular file" in result.stderr
    assert list(output.iterdir()) == []
