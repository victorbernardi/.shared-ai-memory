# Semantic memory and durable project metadata

## Mem0 policy

Mem0 is a semantic provider. Directed queries may retrieve Victor preferences,
accepted or rejected decisions and their reasons, project relations, explicit
legacy/superseded markers, and recurring workflow conventions. Do not ingest
the full history without a directed question.

Mem0 must not be used as the source of truth for Orca Run/Task/Dispatch
status, branch, worktree, dirty state, `HEAD`, worker liveness, current review
acceptance, or CI. Orca and Git remain authoritative for those facts.

Automatic writes require an explicit Victor declaration, an explicitly
accepted architectural decision, a confirmed project relation, an explicit
legacy/superseded/abandoned classification, or an explicitly approved
workflow. Model inferences remain candidates. Never delete or silently
replace older memory; record a `supersedes` relation when a decision changes.

## Unavailable provider

When Mem0 is unavailable, mark the snapshot as `provider: unavailable` and
semantic context as `degraded`. Continue factual discovery from Orca, Git,
approved artifacts, and compliant durable examples. Do not invent memory, do
not install another memory framework, and do not block the entire project only
because Mem0 is unavailable.

## Registry and Work Ledger boundary

Reuse a compliant existing Registry or Work Ledger when one is found. If none
exists, the minimum file-backed location is:

```text
%USERPROFILE%\\.codex\\project-memory\\
  registry.yaml
  projects\\<project_key>.yaml
```

The repository contains schemas and synthetic examples only. Registry/Ledger
entries may record relations, classifications, evidence references, and
recommended next steps, but live Orca and Git override them. They are not a
second lifecycle store.

## Privacy

Do not store credentials, tokens, authenticated URLs, raw PII, or private
user data in memory queries copied to artifacts. Redact before writing a
report. A semantic confidence note must say when a fact is inferred or when
the provider is unavailable.
