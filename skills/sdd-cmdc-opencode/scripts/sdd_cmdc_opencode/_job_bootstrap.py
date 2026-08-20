from __future__ import annotations

import json
import subprocess
import sys
import threading
from typing import BinaryIO


GO_LINE = b"SDD_CMDC_GO\n"


def _emit(payload: dict[str, object]) -> None:
    output = json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"\n"
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()


def _forward(source: BinaryIO, destination: BinaryIO) -> None:
    try:
        read_chunk = getattr(source, "read1", source.read)
        while True:
            chunk = read_chunk(65536)
            if not chunk:
                return
            destination.write(chunk)
            destination.flush()
    except (BrokenPipeError, OSError):
        return
    finally:
        try:
            source.close()
        except OSError:
            pass


def main() -> int:
    try:
        separator = sys.argv.index("--")
    except ValueError:
        return 2
    target_command = sys.argv[separator + 1 :]
    if not target_command:
        return 2

    if sys.stdin.buffer.readline() != GO_LINE:
        return 2

    try:
        target = subprocess.Popen(
            target_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except OSError as exc:
        _emit({"type": "target_spawn_failed", "error": str(exc)})
        return 127

    _emit({"type": "target_spawned", "pid": target.pid})
    assert target.stdin is not None
    assert target.stdout is not None
    assert target.stderr is not None

    stdout_thread = threading.Thread(
        target=_forward,
        args=(target.stdout, sys.stdout.buffer),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_forward,
        args=(target.stderr, sys.stderr.buffer),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    try:
        while True:
            chunk = sys.stdin.buffer.read(65536)
            if not chunk:
                break
            target.stdin.write(chunk)
            target.stdin.flush()
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            target.stdin.close()
        except OSError:
            pass

    returncode = target.wait()
    stdout_thread.join()
    stderr_thread.join()
    return returncode if returncode >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
