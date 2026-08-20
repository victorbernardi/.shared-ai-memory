# SDD Command Code execution context

This context defines the operational language used by `sdd-cmdc-opencode` to coordinate governed implementation and review through local Command Code.

## Language

**Orchestrator**:
The Codex control plane that prepares work, dispatches implementation and review, evaluates evidence, and advances the plan.
_Avoid_: implementer, reviewer, worker

**Run**:
One governed implementation attempt for one task, identified by an immutable `run_id`.
_Avoid_: invocation, round, session

**Run Contract**:
The immutable JSON input that identifies a Run and declares its plan provenance, workspace, scope, execution policy, and success criteria.
_Avoid_: prompt configuration, runner options

**Run Record**:
The persisted transaction history for a Run, including its contract, events, checkpoints, session identity, and result.
_Avoid_: state file, log bundle

**Command Code Session**:
The durable local Command Code conversation identified by the session ID emitted by `cmdc-local`.
_Avoid_: Run, Fix Round

**Checkpoint**:
An append-only snapshot that ties a Run state to its contract, Git baseline, known workspace changes, and Command Code Session.
_Avoid_: backup, save point

**Recovery**:
Continuation of the same Run from a verified Checkpoint using the same Command Code Session.
_Avoid_: retry, restart

**Result**:
The current structured JSON outcome for a Run, with prior invocation outcomes retained in its append-only Run Record.
_Avoid_: report, final message

**Implementer Report**:
The human-readable Markdown account of work performed by the Command Code implementer.
_Avoid_: Result, ledger

**Review Transaction**:
One persisted review lifecycle over an exact Git range, identified by a stable `review_id`.
_Avoid_: review attempt, reviewer session

**Fix Round**:
An explicitly authorized Run that addresses findings from a Review Transaction using a new Command Code Session.
_Avoid_: Recovery, automatic retry

**Ledger**:
The plan-scoped human-readable recovery map that records task decisions, blockers, commits, reviews, and completion.
_Avoid_: Run Record, event log

## Relationships

- The **Orchestrator** creates exactly one **Run Contract** for each **Run**.
- A **Run** owns exactly one **Run Record** and may produce many **Checkpoints**.
- A **Recovery** continues the same **Run** and the same **Command Code Session**.
- A **Run** produces one structured **Result** and may update one **Implementer Report**.
- A **Review Transaction** consumes only a successful **Result** and an exact Git range.
- A **Review Transaction** may authorize zero or more **Fix Rounds**.
- Every **Fix Round** uses a new **Command Code Session** and produces its own **Result**.
- The **Ledger** links Runs, Review Transactions, findings, and operator decisions for one plan.

## Example dialogue

> **Developer:** "The worker reached its turn limit. Should I start another Run?"
> **Domain expert:** "No. If the Checkpoint is valid, use Recovery to resume the same Run and Command Code Session. A new Run is reserved for an authorized Fix Round or a different task."

## Flagged ambiguities

- "resume" previously meant either continuing implementation or polling a reviewer; use **Recovery** for a Run and "resume review polling" for a **Review Transaction**.
- "report" previously mixed human narrative with approval evidence; the **Implementer Report** is Markdown, while the **Result** is the transactional JSON authority.
- "retry" previously covered both continuation and corrective work; **Recovery** preserves the session, while a **Fix Round** always creates a new session.
- "backend" may suggest interchangeable implementers; `cmdc-local` is the only operational implementation backend until a second Adapter satisfies the complete Run contract.
