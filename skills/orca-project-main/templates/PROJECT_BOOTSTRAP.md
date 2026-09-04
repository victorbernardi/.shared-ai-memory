# PROJECT_BOOTSTRAP

Use this template only when binding a fresh session to a Project Key.

```yaml
role: PROJECT_LEAD
project_key: "sample-project"
allowed_repositories:
  - "C:\\Projects\\sample"
allowed_worktrees:
  - "C:\\Projects\\sample"
context_tier: broad-read-only
directed_memory_queries:
  - "Victor preferences relevant to the approved objective"
source_of_truth:
  - Orca
  - Git
  - tests-linters-build-ci
  - approved-designs-plans-briefs
  - registry-ledger
  - Mem0
  - reports
```

The `project_key` is mandatory. A root location without this Project Key is
not a valid bootstrap and routes to `ORDINARY`.

