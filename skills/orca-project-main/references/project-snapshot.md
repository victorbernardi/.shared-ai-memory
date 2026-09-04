# Project Snapshot contract

The snapshot is compact and evidence-bearing. Live Orca supplies Run/Task/
Dispatch status; live Git supplies branch, worktree, dirty state, and `HEAD`.
Memory and reports never override those observations.

```yaml
project_snapshot:
  project_key: "sample-project"
  repositories: []
  related_projects: []
  memory:
    provider: mem0 | unavailable
    relevant_preferences: []
    relevant_decisions: []
    confidence_notes: []
  runs:
    - id: "run-example"
      objective: "sample objective"
      status: "observed-status"
      coordinator: "observed-coordinator"
      candidate_head: null
      next_safe_action: "read-only next step"
  worktrees:
    - path: "C:\\Projects\\sample"
      branch: "feature/sample"
      head: "exact-observed-head"
      dirty: false
      classification: active | paused | blocked | completed | abandoned | superseded | legacy | experimental | unmanaged
      evidence: []
  open_questions: []
  recommended_next_objectives: []
```

## Classification rules

Use only the enumerated classifications. `legacy`, `abandoned`, and
`superseded` require explicit evidence such as a decision, marker, or live
artifact; age or inactivity alone is not evidence. Record the reason and
evidence reference. If evidence is insufficient, keep the item active,
paused, blocked, experimental, or unmanaged as appropriate and state the
uncertainty.

Facts, inferences, and open questions must be visibly separated. A snapshot
with an unavailable memory provider remains valid when its Orca/Git facts are
fresh and its semantic context is marked degraded.

