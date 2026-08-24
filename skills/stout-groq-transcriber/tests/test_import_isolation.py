"""Regression tests for running the globally installed skill from a project."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = SKILL_ROOT / "scripts" / "run.py"
TRANSCRIBE_SCRIPT = SKILL_ROOT / "scripts" / "transcribe.py"


def _write_fake_dependencies(root: Path) -> Path:
    dependencies = root / "dependencies"
    (dependencies / "dotenv").mkdir(parents=True)
    (dependencies / "groq").mkdir(parents=True)
    (dependencies / "dotenv" / "__init__.py").write_text(
        "def load_dotenv(*args, **kwargs):\n    return False\n",
        encoding="utf-8",
    )
    (dependencies / "groq" / "__init__.py").write_text(
        "class Groq:\n"
        "    def __init__(self, **kwargs):\n"
        "        pass\n"
        "    class audio:\n"
        "        class transcriptions:\n"
        "            @staticmethod\n"
        "            def create(**kwargs):\n"
        "                return 'fala crua'\n"
        "    class chat:\n"
        "        class completions:\n"
        "            @staticmethod\n"
        "            def create(**kwargs):\n"
        "                class Message:\n"
        "                    content = 'Speaker 1: fala organizada'\n"
        "                class Choice:\n"
        "                    message = Message()\n"
        "                class Response:\n"
        "                    choices = [Choice()]\n"
        "                return Response()\n",
        encoding="utf-8",
    )
    return dependencies


def _write_foreign_transcriber_modules(root: Path) -> Path:
    scripts = root / "foreign" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "__init__.py").write_text("", encoding="utf-8")
    (scripts / "extract.py").write_text(
        "DEFAULT_WHISPER_MODEL = 'foreign-model'\n"
        "transcribe_audio = lambda *args: 'foreign transcript'\n",
        encoding="utf-8",
    )
    (scripts / "run.py").write_text(
        "DEFAULT_CLEANUP_MODEL = 'foreign-model'\n"
        "main = parse_args = run_transcription_pipeline = transcribe_main = lambda *args, **kwargs: 0\n",
        encoding="utf-8",
    )
    (scripts / "transform.py").write_text(
        "apply_corrections = lambda text: text\n"
        "cleanup_with_groq = lambda text, client: text\n"
        "configured_model = lambda *args, **kwargs: 'foreign-model'\n"
        "count_speakers = lambda *args, **kwargs: 1\n"
        "render_report = lambda *args, **kwargs: ''\n"
        "structure_minutes = lambda *args, **kwargs: ''\n",
        encoding="utf-8",
    )
    (scripts / "load.py").write_text(
        "load_report = load_transcription = lambda *args, **kwargs: None\n",
        encoding="utf-8",
    )
    (scripts / "output_contract.py").write_text(
        "def build_output_plan(*args, **kwargs):\n"
        "    raise RuntimeError('foreign project module imported')\n"
        "render_markdown = lambda *args, **kwargs: ''\n"
        "resolve_mode = lambda mode: mode or 'clean'\n",
        encoding="utf-8",
    )
    return scripts.parent


def _run_probe(script: Path, *, project: Path, dependency_path: Path, foreign_path: Path) -> subprocess.CompletedProcess[str]:
    probe = project / "probe.py"
    probe.write_text(
        "import runpy\n"
        "import sys\n"
        f"sys.path[:] = {[str(foreign_path), str(dependency_path), str(project)]!r} + [\n"
        "    entry for entry in sys.path\n"
        f"    if entry not in {[str(foreign_path), str(dependency_path), str(project)]!r}\n"
        "]\n"
        f"namespace = runpy.run_path({str(script)!r}, run_name='skill_probe')\n"
        "print(namespace.get('DEFAULT_WHISPER_MODEL', '<missing>'))\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(probe)],
        cwd=project,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )


def test_transcribe_ignores_a_foreign_scripts_package(tmp_path: Path) -> None:
    dependency_path = _write_fake_dependencies(tmp_path)
    foreign_path = _write_foreign_transcriber_modules(tmp_path)

    result = _run_probe(
        TRANSCRIBE_SCRIPT,
        project=tmp_path,
        dependency_path=dependency_path,
        foreign_path=foreign_path,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "whisper-large-v3"


def test_official_entrypoint_writes_only_one_clean_output_in_project(
    tmp_path: Path,
) -> None:
    dependency_path = _write_fake_dependencies(tmp_path)
    foreign_path = _write_foreign_transcriber_modules(tmp_path)
    project = tmp_path / "project"
    (project / ".git").mkdir(parents=True)
    (project / "research").mkdir()
    audio_path = project / "meeting.mp3"
    audio_path.write_bytes(b"audio")

    # A real project may contain its own generic ``scripts`` package. The
    # global skill must still load its own ETL modules and keep output in the
    # project's working tree.
    project_scripts = project / "scripts"
    project_scripts.mkdir()
    for module in ("__init__.py", "extract.py", "load.py", "output_contract.py", "transform.py"):
        (project_scripts / module).write_text(
            "raise RuntimeError('foreign project module imported')\n",
            encoding="utf-8",
        )

    probe = project / "run_probe.py"
    probe.write_text(
        "import runpy\n"
        "import sys\n"
        f"sys.argv = ['run.py', {str(audio_path)!r}]\n"
        f"sys.path[:] = {[str(foreign_path), str(dependency_path), str(project)]!r} + [\n"
        "    entry for entry in sys.path\n"
        f"    if entry not in {[str(foreign_path), str(dependency_path), str(project)]!r}\n"
        "]\n"
        f"runpy.run_path({str(RUN_SCRIPT)!r}, run_name='__main__')\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["GROQ_API_KEY"] = "test-key"
    result = subprocess.run(
        [sys.executable, str(probe)],
        cwd=project,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    generated = sorted(
        path.relative_to(project)
        for path in project.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path != audio_path
        and path != probe
        and "scripts" not in path.parts
    )
    assert generated == [Path("research/meeting.md")]
