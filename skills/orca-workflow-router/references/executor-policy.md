# Executor policy

```yaml
executor_policy:
  selected_by: victor
  value: agy | command-code
  automatic_fallback: false
  task_override: user_only
```

The Run Charter must contain one valid executor explicitly selected by
Victor. The conversational alias `cmdc` is normalized to `command-code` before
it is persisted or routed. For `TASK_READY`, if the executor is missing or
invalid, block only the dispatch and ask Victor for a new decision. Do not
choose a provider from availability, history, exit code, or a previous task.

## Routes

| Charter value | Capability |
|---|---|
| `agy` | `$delegate-to-agy` |
| `command-code` | `$commandcode-delegate` |

AgY failure never selects Command Code. Command Code failure never selects
AgY. Both failures preserve `EXECUTOR_UNAVAILABLE`, the original evidence,
and the current Run state; there is no automatic fallback.

The executor policy does not authorize a reviewer, a global instruction
change, publication, or a lifecycle record outside Orca. A task override is
valid only after a new explicit Victor decision.
