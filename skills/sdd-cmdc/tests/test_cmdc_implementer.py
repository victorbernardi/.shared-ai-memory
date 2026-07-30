from __future__ import annotations

import importlib.util
from types import SimpleNamespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "skills" / "sdd-cmdc" / "scripts" / "cmdc-implementer.py"
SPEC = importlib.util.spec_from_file_location("cmdc_implementer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_command_uses_fixed_model_and_edit_flags() -> None:
    command = MODULE.build_command(Path("cmdc"))

    assert command == [
        "cmdc",
        "-p",
        "--model",
        "deepseek/deepseek-v4-flash",
        "--max-turns",
        "20",
        "--trust",
        "--skip-onboarding",
        "--yolo",
    ]


def test_build_command_accepts_a_task_specific_turn_limit() -> None:
    command = MODULE.build_command(Path("cmdc"), max_turns=7)

    assert command[command.index("--max-turns") + 1] == "7"
    assert command[command.index("--model") + 1] == "deepseek/deepseek-v4-flash"


def test_classify_failure_reports_missing_command() -> None:
    diagnostic = MODULE.classify_failure(127, "", report_exists=False, cmd_found=False)

    assert diagnostic["BLOCKER_CODE"] == "CMD_NOT_FOUND"


def test_classify_failure_reports_authentication_requirement() -> None:
    diagnostic = MODULE.classify_failure(3, "not authenticated", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "AUTH_REQUIRED"


def test_classify_failure_reports_unavailable_model() -> None:
    diagnostic = MODULE.classify_failure(4, "MODEL_NOT_IN_PLAN", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "MODEL_UNAVAILABLE"


def test_classify_failure_reports_rate_limit() -> None:
    diagnostic = MODULE.classify_failure(5, "rate limited", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "RATE_LIMITED"


def test_classify_failure_reports_timeout() -> None:
    diagnostic = MODULE.classify_failure(8, "max turns reached", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "TIMEOUT"


def test_classify_failure_reports_generic_process_failure() -> None:
    diagnostic = MODULE.classify_failure(1, "unexpected failure", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "PROCESS_FAILED"


def test_classify_failure_reports_missing_report_after_success() -> None:
    diagnostic = MODULE.classify_failure(0, "", report_exists=False)

    assert diagnostic["BLOCKER_CODE"] == "REPORT_MISSING"


def test_render_blocked_emits_the_structured_contract() -> None:
    diagnostic = {
        "BLOCKER_CODE": "MODEL_UNAVAILABLE",
        "MESSAGE": "deepseek/deepseek-v4-flash não está disponível no plano atual",
        "COMMAND": "cmdc -p --model deepseek/deepseek-v4-flash",
        "EXIT_CODE": "4",
        "STDERR": "MODEL_NOT_IN_PLAN",
        "ACTION": "executar cmdc --list-models e interromper a tarefa",
    }

    assert MODULE.render_blocked(diagnostic) == "\n".join(
        [
            "STATUS: BLOCKED",
            "BLOCKER_CODE: MODEL_UNAVAILABLE",
            "MESSAGE: deepseek/deepseek-v4-flash não está disponível no plano atual",
            "COMMAND: cmdc -p --model deepseek/deepseek-v4-flash",
            "EXIT_CODE: 4",
            "STDERR: MODEL_NOT_IN_PLAN",
            "ACTION: executar cmdc --list-models e interromper a tarefa",
        ]
    )


def _write_prompt(tmp_path: Path, report_path: Path) -> Path:
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(
        f"Write your full report to {report_path}:\n",
        encoding="utf-8",
    )
    return prompt_path


def test_run_implementer_accepts_success_with_report(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    report_path = tmp_path / "report.md"
    report_path.write_text("STATUS: DONE\n", encoding="utf-8")
    prompt_path = _write_prompt(tmp_path, report_path)
    observed: dict[str, object] = {}

    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="worker output", stderr="")

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 0
    assert observed["command"] == MODULE.build_command(Path("cmdc"))
    assert capsys.readouterr().out == "worker output\n"


def test_run_implementer_preserves_failed_process_diagnostics(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda command, **kwargs: SimpleNamespace(
            returncode=4, stdout="partial output", stderr="MODEL_NOT_IN_PLAN"
        ),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path) == 4
    captured = capsys.readouterr()
    assert "partial output" in captured.out
    assert "BLOCKER_CODE: MODEL_UNAVAILABLE" in captured.err
    assert "STDERR: MODEL_NOT_IN_PLAN" in captured.err


def test_run_implementer_reports_missing_command(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")

    def missing_command(cmd_bin="cmdc"):
        raise FileNotFoundError("cmdc binary not found")

    monkeypatch.setattr(MODULE, "resolve_cmdc", missing_command)

    assert MODULE.run_implementer(tmp_path, prompt_path) == 127
    assert "BLOCKER_CODE: CMD_NOT_FOUND" in capsys.readouterr().err


def test_run_implementer_reports_missing_report_after_zero_exit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    prompt_path = _write_prompt(tmp_path, tmp_path / "missing-report.md")
    monkeypatch.setattr(MODULE, "resolve_cmdc", lambda cmd_bin="cmdc": Path("cmdc"))
    monkeypatch.setattr(
        MODULE.subprocess,
        "run",
        lambda command, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    assert MODULE.run_implementer(tmp_path, prompt_path) == 1
    assert "BLOCKER_CODE: REPORT_MISSING" in capsys.readouterr().err
