from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "sdd-cmdc-opencode" / "scripts" / "task-brief"


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
