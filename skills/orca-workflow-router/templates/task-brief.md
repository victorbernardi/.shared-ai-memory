# Task Brief

An implementer receives only this minimum sufficient context:

```yaml
role: IMPLEMENTER
project_key: "sample-project"
run_id: "run-example"
task_id: "task-example"
dispatch_id: "dispatch-example"
run_charter_ref: "run-charter-example"
objective: "approved task objective"
required_sources: []
worktree: "C:\\Projects\\sample"
branch: "feature/sample"
owned_paths: []
protected_paths: []
pre_existing_dirty_paths: []
executor_policy:
  selected_by: victor
  value: agy | command-code
  automatic_fallback: false
  task_override: user_only
required_behavior: []
acceptance: []
plausible_wrong_implementation: "describe the tempting invalid shortcut"
focused_verification: []
project_closure_gates: []
forbidden_actions:
  - edit outside owned paths
  - read superior transcripts or broad project memory
  - create workers or change the executor
expected_completion_report: "completion-report.md"
```

The Task Brief contains no unrestricted Mem0, project graph, superior
transcript, or unrelated Run history. The implementer may edit only owned
paths and must report evidence rather than intent.
