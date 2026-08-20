from __future__ import annotations

import json
import os
import sys
import time
from typing import Any


MARKER = "SDD_CMDC_MOD_HOOK_OK"
HANDSHAKE = "SDD_CMDC_MOD_HOOK_HANDSHAKE"


def _value(argv: list[str], flag: str) -> str | None:
    try:
        index = argv.index(flag)
    except ValueError:
        return None
    if index + 1 >= len(argv):
        return None
    return argv[index + 1]


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def main() -> int:
    argv = sys.argv[1:]
    variant = os.environ.get("FAKE_CMDC_VARIANT", "success")
    resume = _value(argv, "--resume")
    max_turns = _value(argv, "--max-turns")
    if _value(argv, "--output-format") != "json" or max_turns is None:
        _emit(
            {
                "type": "result",
                "subtype": "error",
                "sessionId": "session-123",
                "stopReason": "invalid_flags",
                "result": "missing json output contract",
            }
        )
        return 2

    if variant == "stall":
        time.sleep(10)
        return 0
    if variant == "stderr":
        print("fake-stderr", file=sys.stderr, flush=True)

    if variant == "malformed":
        _emit(
            {
                "type": "event",
                "event": {"type": "assistant_progress", "turnNumber": 1},
            }
        )
        print("{not-json", flush=True)
    else:
        _emit(
            {
                "type": "event",
                "event": {
                    "type": "assistant_progress",
                    "turnNumber": 1,
                    "sessionId": resume or "session-123",
                },
            }
        )

    if _value(argv, "--mod"):
        _emit(
            {
                "type": "event",
                "event": {
                    "type": "tool_hook_blocked",
                    "toolName": "shell_command",
                    "hookOutput": HANDSHAKE,
                },
            }
        )

    if variant == "no_session":
        session_id = None
    else:
        session_id = resume or "session-123"
    result: dict[str, Any] = {
        "type": "result",
        "subtype": "max_turns" if variant == "max_turns" else ("error" if variant == "error" else "success"),
        "stopReason": "max_turns" if variant == "max_turns" else "end_turn",
        "result": "done",
    }
    if session_id is not None:
        result["sessionId"] = session_id
    _emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
