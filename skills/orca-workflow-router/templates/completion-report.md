# Completion Report

The implementer reports facts in this shape; an absent or empty report is not
acceptance.

```yaml
role: IMPLEMENTER
project_key: "sample-project"
run_id: "run-example"
task_id: "task-example"
dispatch_id: "dispatch-example"
repository: "C:\\Projects\\sample"
worktree: "C:\\Projects\\sample"
branch: "feature/sample"
head_sha: "exact-observed-head"
outcome: succeeded | failed
changed_files: []
validation:
  - command: "python -m pytest tests/example.py -q"
    result: "fresh observed result"
worker_done: true
blockers: []
evidence_refs: []
claim_policy: "no completion claim without identity, diff, validation, and fresh evidence"
```

`outcome` is required and accepts only `succeeded` or `failed`. A failed outcome
reports blockers and evidence and is not acceptance; a succeeded
outcome still requires the identity, diff, validation, and fresh evidence
listed above.

The report must not contain credentials, tokens, authenticated URLs, raw PII,
or private user data. Orca lifecycle state and Git observations remain the
authoritative sources.
