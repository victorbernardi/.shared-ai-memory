---
name: sync-wire
description: >-
  Use when you need to communicate with the Antigravity agent or Gemini CLI, resolve context asymmetry, or align analytical premises via SYNC_WIRE.md.
metadata:
  category: discipline
  triggers: sync_wire, communication, context alignment, inter-agent, close_session
---

# Sync-Wire Communication Discipline

## Iron Law

**Communication is NOT optional when context asymmetry is detected; never assume the other agent's state without empirical alignment.**

Violating the letter IS violating the spirit.

## The Rule

1. **ALWAYS** verify that background monitors (`sync_wire_monitor.py` and `brain-watcher.py`) are active before starting the session.
2. **ALWAYS** explicitly invoke this skill before or during any dialogue in `SYNC_WIRE.md`.
3. **ALWAYS** use the mandatory header format: `### [YYYY-MM-DD HH:MM:SS] [Agent Name]`.
4. **ALWAYS** respond promptly to queries (type: query) from the other agent.
5. **ALWAYS** finalize the communication by sending the `CLOSE_SESSION` command to clear the channel and terminate the monitor.

## Violations

Dialogue without headers? **Delete it. Start over.**
Assuming state without sync? **Discard investigation. Re-align.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "It's just a quick check" | Quick checks without traces lead to poisoned memory. |
| "I'll clean the file later" | Later = never. Use CLOSE_SESSION now. |
| "The other agent will see the file change" | Monitors rely on explicit formatting for reliability. |

## Red Flags - STOP

- "I think the Antigravity already knows..." -> **STOP.** Ask via Sync-Wire.
- "The SYNC_WIRE.md is getting messy" -> **STOP.** Use CLOSE_SESSION to reset.

## Valid Exceptions

- Local-only infrastructure tasks that do not impact analytical premises.
- Emergency recovery where the monitor script itself is broken (fix the monitor first).

**Everything else:** Follow the rule.
