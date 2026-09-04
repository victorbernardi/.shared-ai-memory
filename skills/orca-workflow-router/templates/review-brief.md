# Review Brief

```yaml
role: REVIEWER
review_skill: open-code-review-delegate
project_id: "sample-project"
run_id: "run-example"
implementation_id: "task-example"
review_id: "review-task-example"
implementation_dispatch_id: "dispatch-example"
review_dispatch_id: "review-dispatch-example"
repository: "C:\\Projects\\sample"
worktree: "C:\\Projects\\sample"
branch: "feature/sample"
base_sha: "exact-base-sha"
head_sha: "exact-head-sha"
business_context: []
contract_refs: []
verification_evidence: []
forbidden_actions:
  - edit candidate files
  - widen scope
  - create workers
  - approve without accounting for every reviewable file
disposition: ACCEPT | CHANGES_REQUESTED | BLOCKED
```

The reviewer is fresh, did not implement the candidate, and must account for
every reviewable file. If `HEAD` changes after this brief is frozen, the final
review is stale and cannot authorize finishing.
