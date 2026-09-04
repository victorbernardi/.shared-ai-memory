# CONTROL_BOOTSTRAP

This template binds one Control session to one Run.

```yaml
role: CONTROL
run_id: "run-example"
project_key: "sample-project"
run_charter: "path-or-embedded-approved-run-charter"
selected_run_detail: "live selected Run only"
collision_index:
  branch: []
  worktree: []
  path: []
  writer: []
  coordinator: []
  integration: []
context_tier: selected-run-and-minimal-collision-index
read_only_over_candidates: true
one_control_per_run: true
```

The Control session receives no broad project transcript, full history of
other Runs, or unrestricted Mem0 context. It may inspect other Runs only for
the listed collision classes. A missing `run_id`, missing Run Charter, or
ambiguous binding is invalid and remains read-only.

