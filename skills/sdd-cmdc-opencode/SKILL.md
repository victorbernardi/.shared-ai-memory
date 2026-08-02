---
description: Use when executing implementation plans with independent tasks in the current session and delegating implementation tasks to Command Code
name: sdd-cmdc-opencode
---

# SDD via Command Code with delegated Open Code Review

Implementation scaffold for the sdd-cmdc-opencode workflow.

This placeholder is committed with Task 2 only. The full delegated review workflow is implemented in Task 3.

**Delegated review:** every review in this workflow must use the `open-code-review-delegate` subskill, running `ocr delegate preview` followed by `ocr delegate rule` on the exact repository and range.

**Review states:** a review is only complete when the delegate reports REVIEW CLEAN; anything else is REVIEW INCOMPLETE and blocks the task. Timeout, partial preview, excluded files without justification, or an unresolved rule never produce approval, and the task is marked BLOCKED until the scope is complete. Fix rounds run against FIX_BASE.

**No fallback:** quando o OCR delegado falhar, não substituir a revisão por uma revisão Codex comum — nunca substituir o fluxo delegado por qualquer outro mecanismo de revisão.
