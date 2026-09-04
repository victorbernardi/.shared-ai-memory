---
name: orca-workflow-router
description: Use when a valid Run-bound CONTROL session must route an Orca workflow event or lifecycle transition.
metadata:
  version: "1.0.0"
  tier: "3"
  category: orchestration
---

# orca-workflow-router

## Entry condition and responsibility

Load this skill only from a valid `CONTROL` session bound to one Run by a
`CONTROL_BOOTSTRAP` and Run Charter. It consumes one live Run event and
returns the next existing capability. `$orchestration` owns Run, Task,
Dispatch, gate, and worker lifecycle state. `$orca-cli` is used only for
placement, terminal, and worktree operations when required.

This router does not implement a Task, review a candidate, copy OCR logic,
or persist a parallel lifecycle store. It does not infer role from a title,
root, transcript, or terminal. Ambiguous input is read-only and the dependent
transition is blocked.

## Routing contract

1. Validate the Run-bound Control bootstrap and read the exact Run Charter.
2. Read the executor selected by Victor: `agy` or `command-code`.
3. Route `TASK_READY` through `references/executor-policy.md`.
4. After `worker_done`, require identity, fresh Git state, artifact/diff, and
   validation before accepting an implementation report.
5. Route verification, fresh review, findings, remediation, final review, and
   finishing through the existing skills listed in the references.
6. Preserve live Orca state when an executor or reviewer is unavailable; do
   not substitute a route automatically.

Read the complete [event table](references/events-and-transitions.md),
[executor policy](references/executor-policy.md), and [review
routing](references/review-routing.md) before acting. The Task Brief, Review
Brief, and Completion Report templates define the minimum context that may
cross each boundary.

## Protected boundaries

`$orca-cli` and `$orchestration` are protected native skills and are not
modified or copied. `$delegate-to-agy`, `$commandcode-delegate`,
`$verification-before-completion`, `$open-code-review-delegate`,
`$receiving-code-review`, and `$finishing-a-development-branch` remain
separate capabilities. The legacy `$sdd-cmdc-opencode` route and Pi are not
adopted. No second lifecycle store, service, daemon, or paid executor is
introduced.
