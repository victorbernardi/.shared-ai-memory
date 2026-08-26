---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch a code reviewer subagent to catch issues before they cascade. The
reviewer receives only the exact range and requirements needed for review; it
does not receive the coordinator's session history.

The review gate is separate from changing a PR to ready, merging, publishing,
or closing an issue. A missing or late reviewer report is an operational
failure of the review gate, not evidence that the reviewed code is defective.

## When to Request Review

**Mandatory:**

- After each task in subagent-driven development.
- After completing a major feature.
- Before merging to main.

**Optional but valuable:**

- When stuck and an independent diagnosis is useful.
- Before a risky refactor.
- After fixing a complex bug.

## How to Request

### 1. Freeze the review range

Record the repository, worktree, branch, `BASE_SHA`, `HEAD_SHA`, and the
timestamps before dispatch. Do not infer a range from a dirty checkout or from
an old handoff.

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or the explicitly approved merge base
HEAD_SHA=$(git rev-parse HEAD)
git status --short --branch
```

### 2. Select and preflight the reviewer route

Before dispatching, check whether the user selected a model, reasoning effort,
or service tier for this review in the current task. If no review-specific
selection exists, use this default route without asking a blocking question:

- `model="gpt-5.6-luna"`
- `reasoning_effort="max"`
- `service_tier="priority"`

An explicit selection in the current task overrides only the corresponding
default; unspecified fields remain `gpt-5.6-luna`, `max`, and `priority`. A
global `review_model`, a default model, or an earlier unrelated approval is not
an explicit selection for this review. `/review` is a separate Codex feature
and is not an implicit substitute for the spawned reviewer.

- With no override, request `model="gpt-5.6-luna"`,
  `reasoning_effort="max"`, and `service_tier="priority"`.
- With an explicit override, request the selected value and the defaults for
  any unspecified fields; record the actual requested values.
- If the runtime rejects the model or the requested `service_tier`, classify
  the dispatch as `SPAWN_FAILED`. Report the literal error and the available
  models/tiers when returned. Offer a concrete fallback and obtain permission
  before silently changing model or tier.
- Do not treat a configuration value such as `/fast` or `service_tier=fast` as
  proof that the runtime applied it. Record `effective_service_tier` only when
  the runtime exposes it; otherwise use `unknown`.

### 3. Dispatch one reviewer

Dispatch a `general-purpose` subagent with the template in
[`code-reviewer.md`](code-reviewer.md). Pass the selected model and reasoning
effort directly to the spawn call when supported, along with the requested
service tier. Preserve the exact returned `agent_id`; it is the identity for
every later poll.

Do not dispatch a second reviewer while the first agent is `QUEUED`, `RUNNING`,
or `POLL_TIMEOUT`. A polling timeout is not a dispatch failure.

### 4. Register the lifecycle record

Create a small record before the first wait and update it at every boundary:

```json
{
  "state": "QUEUED",
  "repository": "owner/name",
  "worktree": "absolute path",
  "base_sha": "BASE_SHA",
  "head_sha": "HEAD_SHA",
  "agent_id": "returned id",
  "requested_model": "model sent to spawn",
  "resolved_model": "runtime value or unknown",
  "reasoning_effort": "effort sent to spawn",
  "requested_service_tier": "tier sent to spawn",
  "effective_service_tier": "runtime value or unknown",
  "started_at": "ISO-8601",
  "finished_at": null,
  "last_observed_status": "QUEUED",
  "report": null,
  "error": null
}
```

The record must retain `agent_id`, requested/resolved model, reasoning effort,
requested/effective `service_tier`, timestamps, final status, report, and
error. Never claim that a model, priority, or service tier was effective when
the tool did not expose that fact.

## Lifecycle and Polling Contract

The controller must distinguish these states:

| State | Meaning | Next action |
| --- | --- | --- |
| `SPAWN_FAILED` | No agent was created; model, tier, capacity, or validation failed. | Record the literal error and obtain permission for any fallback. |
| `QUEUED` | Dispatch accepted but execution has not started. | Wait on the same `agent_id`. |
| `RUNNING` | The agent is still executing. | Wait on the same `agent_id`; never duplicate it. |
| `POLL_TIMEOUT` | A `wait_agent` call expired before a terminal status. | Retain the `agent_id`, do not interrupt, and wait again. |
| `READY` | The agent returned a non-empty final review report. | Validate the report and apply the review gate. |
| `FAILED` | The runtime returned a terminal error. | Record the error; classify the review as incomplete. |
| `INTERRUPTED` | An explicitly authorized close/interrupt ended the agent. | Record the reason; no report means incomplete. |
| `REVIEW INCOMPLETE` | The controller cannot prove a valid terminal report. | Do not approve, mark ready, merge, or close the issue. |

Use bounded waits and a finite overall deadline, but do not conflate the two:

1. Call `wait_agent` with a finite `timeout_ms`.
2. If it returns `timed_out=true` or an empty status, set `state=POLL_TIMEOUT`.
   This output does not prove that the child failed or stopped; preserve the
   same `agent_id` and all prior evidence.
3. Call `wait_agent` again for that same `agent_id`, using bounded backoff or a
   clearly recorded next deadline. A late `completed` result is valid and must
   be attached to the original lifecycle record.
4. If the status is `completed` but the report is null, empty, malformed, or
   absent, emit the explicit terminal error `REPORT_MISSING` and classify the
   gate as `REVIEW INCOMPLETE`. Missing output is never approval.
5. If the status is `errored`, classify `FAILED` and retain the runtime error.
6. If the status is `interrupted` or `shutdown`, classify `INTERRUPTED` and
   retain the interruption reason and any partial evidence.

`send_input`/follow-up is not a replacement for polling. Use it only when the
runtime explicitly supports it and the action is needed; record the submission
ID. It must never create a new reviewer or overwrite the original result.

## Explicit Interruption Policy

Never call `close_agent` or an interrupt operation solely because one
`wait_agent` timed out. Interrupt only after an explicit user decision or a
predeclared hard deadline, and record `interrupt_requested_at`, the prior
state, and the reason. If the runtime has no supported interruption operation,
leave the child state unresolved and report `REVIEW INCOMPLETE`; do not invent a
terminal result.

An interruption after `POLL_TIMEOUT` is therefore represented as
`INTERRUPTED`/`REVIEW INCOMPLETE`, not as `FAILED`, `READY`, or approval. The
reviewed PR remains unaffected by this operational classification.

## Terminal Review Gate

The only acceptable successful handoff is a structured final report containing
the exact range, files reviewed, tests/commands, findings by severity, and an
explicit assessment. A runtime `completed` status alone is insufficient.

Use this final payload shape, filling unknown runtime fields with `unknown`:

```json
{
  "state": "READY | FAILED | INTERRUPTED | REVIEW INCOMPLETE",
  "agent_id": "same id from spawn",
  "base_sha": "exact base",
  "head_sha": "exact head",
  "requested_model": "...",
  "resolved_model": "...",
  "reasoning_effort": "...",
  "requested_service_tier": "...",
  "effective_service_tier": "...",
  "started_at": "...",
  "finished_at": "...",
  "report": "final report or null",
  "error": "null or explicit terminal code/message"
}
```

`READY` does not itself approve a PR: the coordinator must validate the report
and findings. `POLL_TIMEOUT`, `REPORT_MISSING`, an absent report, a runtime
timeout, or an interrupted child always remains `REVIEW INCOMPLETE`.

## Example

```text
BASE_SHA=... HEAD_SHA=...
requested_model=gpt-5.6-luna reasoning_effort=max service_tier=priority
spawn -> agent_id=019... state=QUEUED
wait_agent(019..., 10000ms) -> timed_out=true state=POLL_TIMEOUT
wait_agent(019..., 60000ms) -> completed=final-report state=READY
```

The second line does not dispatch another reviewer. If the second wait also
expires, preserve the same ID and return `REVIEW INCOMPLETE`; do not interrupt
or approve implicitly.

## Acting on Feedback

- Fix Critical issues immediately.
- Fix Important issues before proceeding.
- Note Minor issues for later.
- Push back only with concrete technical reasoning and evidence.
- Keep review, code changes, ready-for-review, merge, publication, and cleanup
  as separate gates.

## Common Rationalizations

| Excuse | Reality |
| --- | --- |
| “The wait timed out, so the reviewer failed.” | `POLL_TIMEOUT` is intermediate; wait on the same ID again. |
| “I will dispatch another reviewer while this one is running.” | This creates duplicate reviews and loses lifecycle ownership. |
| “Closing the agent will make the timeout clean.” | It can discard a late report; interruption requires an explicit decision. |
| “The global review model or `/fast` proves the route.” | Record only values the runtime accepted and exposed. |
| “The agent completed, so the review passed.” | Validate the non-empty structured report and its assessment. |

## Red Flags

**Never:**

- Dispatch without applying the explicit review defaults or an explicit user
  override.
- Treat an empty `wait_agent` timeout as terminal failure or approval.
- Dispatch a duplicate while the original agent is non-terminal.
- Interrupt solely because polling timed out.
- Treat a missing report as a clean review.
- Merge, publish, or close the issue without a valid report and explicit
  authorization.
- Use OCR endpoints, `ocr review`, or `ocr llm test` as a substitute for this
  reviewer route.

See the template at [`code-reviewer.md`](code-reviewer.md).
