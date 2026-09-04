# Context scope for `orca-project-main`

## Classification precedence

Every session starts as `UNCLASSIFIED`. Apply these checks in order:

1. A current valid Orca Dispatch preamble establishes `IMPLEMENTER`,
   `REVIEWER`, or `INVESTIGATOR`.
2. A valid Run-bound `CONTROL_BOOTSTRAP` establishes `CONTROL`.
3. A valid Project-Key-bound `PROJECT_BOOTSTRAP` establishes `PROJECT_LEAD`.
4. Without those proofs, the session is `ORDINARY` and receives no broad
   project memory by default.

The Dispatch preamble takes precedence over bootstrap history. Ambiguity is
read-only. A root path, title, first session, Codex usage, broad context, or
another terminal is not evidence of `PROJECT_LEAD` or `CONTROL`.

## Minimum-sufficient context matrix

| Context | PROJECT_LEAD | CONTROL | IMPLEMENTER | REVIEWER | INVESTIGATOR | ORDINARY |
|---|---|---|---|---|---|---|
| Victor preferences | broad, directed | only selected Charter items | none | none | named scope only | none |
| Mem0 | directed broad query | not by default | no Mem0 | no Mem0 | only named source | none |
| Project relations | broad read-only | only collision-relevant | none | review-relevant only | brief-defined | none |
| All relevant Runs | yes, read-only | index of selected Run and collisions | no | no | named scope | no |
| Run detail | as needed | selected Run plus Charter | only Task/Dispatch | only review brief | only investigation brief | no |
| Branches/worktrees | all observed | selected Run and conflicts | assigned only | candidate only | named scope | no |
| Transcript from superior session | never transfer | never receive | no transcript | no transcript | no transcript | no |
| Candidate edit permission | none | none | owned paths only | none | none | only when explicitly requested outside a Run |
| Task/Dispatch creation | none | one Run only | none | none | none | none |

`PROJECT_LEAD` is the only role with broad context. Every worker receives
minimum sufficient context. `CONTROL` receives a
selected Run, its Run Charter, and a minimal collision index; it does not
receive the full history of every Run. Workers receive minimum sufficient
context, no Mem0, no project graph, and no transcript from a superior role.
Project Lead may use directed Mem0 queries only for semantic context.

## Safety rules

- Protected skills remain unchanged and are not copied.
- Context is evidence-scoped, not inferred from session order.
- A missing provider degrades semantic context but does not create facts.
- The six roles are mutually explicit: `PROJECT_LEAD`, `CONTROL`,
  `IMPLEMENTER`, `REVIEWER`, `INVESTIGATOR`, and `ORDINARY`.
