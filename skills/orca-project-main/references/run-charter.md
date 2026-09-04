# Run Charter and Control handoff

Victor approves the objective and explicitly selects the executor before a
Run Charter is handed to Control. The v1 charter payload is frozen to the
exact top-level fields shown below: observed Git identity (`repository`,
`branch`, `base_sha`, `head_sha`, `worktree`, `dirty_baseline`) plus one
nested `executor_policy`. Its values are selected by `victor`, `agy` or
`command-code`, `automatic_fallback: false`, and `task_override: user_only`.
The conversational alias `cmdc` is normalized to `command-code` before
persistence or routing. No alternate nesting or aliases are accepted in this
contract; any compatibility change requires an explicitly recorded decision
that preserves these exact fields.

```yaml
run_charter:
  schema_version: 1
  run_id: ""
  project_key: ""
  work_slug: ""             # project/work identity slug
  objective: ""
  why_now: ""
  repository: ""            # canonical repo path/URL
  branch: ""
  base_sha: ""
  head_sha: ""
  worktree: ""              # path
  dirty_baseline: {}        # pre-existing dirty state at charter time
  executor_policy:
    selected_by: victor
    value: agy | command-code
    automatic_fallback: false
    task_override: user_only
  relevant_memory: []       # directed Mem0 results with confidence notes
  relevant_decisions: []
  in_scope: []
  out_of_scope: []
  protected_paths: []       # native Orca skills remain protected
  acceptance: []            # fresh review via open-code-review-delegate
  verification: []
  rollback: []
```

Every newly created Run objective must begin with exactly:

```text
[project:<project_key>] [work:<work_slug>] <objective>
```

This marker form agrees with the Control protocol marker requirement: the
objective starts with the bracketed project key, then the bracketed work slug,
then the plain-language objective text.

## Curated Control handoff

Use `$orca-cli` to start a new Control session and provide only the
Run-bound `CONTROL_BOOTSTRAP` plus this Run Charter. Control receives the
selected Run detail and a minimal collision index for branch, worktree, path,
writer, coordinator, and concurrent integration collisions. It remains
read-only over candidate files and does not receive the Project Lead
transcript or broad memory.

The Project Lead does not create implementation Tasks or Dispatches. Control
owns those lifecycle actions through `$orchestration` and the workflow router.
