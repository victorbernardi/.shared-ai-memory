---
name: spec-validation
version: 1.0.0
description: Use when you need to validate consistency between SOW and Specs. Valida a consistência entre SOW (Statement of Work) e especificações técnicas, garantindo rastreabilidade e ausência de contradições.
when_to_use: validar especificação, consistência, rastreabilidade, validação de requisitos, spec validation, consistency check, requirements traceability, AC to FR mapping
allowed-tools: [Read, Grep, Glob]
---

# Workflow: SOW/Spec Validation

## ID System

| Document | Prefix  | Links To         |
| -------- | ------- | ---------------- |
| SOW      | AC-N    | -                |
| Spec     | FR-NNN  | Implements: AC-N |
| Spec     | T-NNN   | FR: FR-NNN       |
| Spec     | NFR-NNN | Validates: AC-N  |
| Spec     | AS-NNN  | -                |

Priority levels (P0/P1/P2) and the Gate rule are defined by the `reviewer-spec` agent.
Each check below assigns priority per finding type.

## Checks

Run P0-producing checks (1-3) first. If any P0 is raised, downstream checks may
be skipped. The gate will already be NotReady.

### 1. AC→FR Traceability [P0 candidate]

Each `AC-N` must have ≥1 FR with `Implements: AC-N`.

| Finding                                       | Priority |
| --------------------------------------------- | -------- |
| AC has no FR implementing it                  | P0       |
| Orphan FR implements non-existent AC          | P1       |

### 2. FR→Test Coverage [P0 candidate]

Each `FR-NNN` must have ≥1 `T-NNN` with matching FR reference.

| Finding                               | Priority |
| ------------------------------------- | -------- |
| FR has no test scenario               | P0       |
| Test references non-existent FR       | P1       |

### 3. Traceability Matrix Integrity [P0 candidate]

| Column | Must exist in             |
| ------ | ------------------------- |
| AC     | SOW Acceptance Criteria   |
| FR     | Spec Functional Req table |
| Test   | Spec Test Scenarios       |
| NFR    | Spec NFR table            |

| Finding                                 | Priority |
| --------------------------------------- | -------- |
| Matrix row references non-existent ID   | P0       |
| Matrix row missing expected column      | P1       |

### 4. Scope↔Implementation [P1 candidate]

SOW In-Scope targets must appear in Spec phases. Extra files → P2.

### 5. Contradiction Detection [P0/P1 candidate]

Cross-check SOW↔Spec for technology mismatches, numeric conflicts.

| Finding                                   | Priority |
| ----------------------------------------- | -------- |
| SOW and Spec specify conflicting tech     | P0       |
| SOW and Spec specify conflicting numerics | P0       |
| Terminology used inconsistently           | P1       |

### 6. Ambiguous Expressions [P0 candidate]

| Language | Patterns                                                                           |
| -------- | ---------------------------------------------------------------------------------- |
| PT       | adequadamente, sempre que possível, razoável, TBD, rápido (sem métrica), considerar |
| EN       | appropriately, as much as possible, reasonable, adequate, TBD, fast (no metric)     |

| Finding                                           | Priority |
| ------------------------------------------------- | -------- |
| Ambiguous term inside a SHALL clause (FR)         | P0       |
| Ambiguous term in NFR Target                      | P0       |
| Ambiguous term elsewhere                          | P1       |

### 7. Terminology Consistency [P1 candidate]

Same concept must use same term across documents.

| Finding                                          | Priority |
| ------------------------------------------------ | -------- |
| Synonym mixing (user/member) in same role        | P1       |
| Abbreviation mixing (DB/database)                | P2       |

### 8. Column Completeness [P0/P1/P2 candidate]

| Finding                                          | Priority |
| ------------------------------------------------ | -------- |
| AC Observable signal column empty (SOW)          | P0       |
| In Scope Observable outcome column empty (SOW)   | P1       |
| NFR Rationale column empty                       | P1       |
| Assumption Impact-if-broken column empty         | P1       |
| Dependency Purpose column empty                  | P2       |

Risks column rules (Probability/Mitigation × Impact): delegated to
`reviewer-spec` Risks Completeness section.

### 9. Phase Dependency [P1 candidate]

Implementation table must declare `Depends`. Empty Depends blocks parallel
scheduling judgment.

| Finding                                          | Priority |
| ------------------------------------------------ | -------- |
| Phase Depends column empty                       | P1       |

### 10. YAGNI Compliance [P2]

With YAGNI Checklist: verify Spec excludes checked items. Flag over-engineering.

### 11. Scope Integrity [P0/P1 candidate]

SOW In Scope and Out of Scope must not overlap. ACs must target only In Scope.

| Finding                                             | Priority |
| --------------------------------------------------- | -------- |
| In Scope target also listed in Out of Scope         | P0       |
| AC references a target absent from In Scope         | P1       |
| Out of Scope lacks `Why not` justification          | P2       |

## Output

Markdown appended to reviewer findings:

```markdown
## Consistency Findings

| CON-001 | P0/P1/P2 | check name | sow.md:section / spec.md:section | What CC will do when it reads this | Concrete rewrite, not "clarify this" |
```

Finding format and Gate contribution follow the `reviewer-spec` agent.

## Related Skills

- **explore**: Explore the codebase to verify if the implementation matches the validated spec.
- **adr**: Decisions that impact the spec should be recorded as ADRs.
- **doc-workflow-orchestrator**: Master guide for the documentation lifecycle.

## Instalação

Habilidade baseada em regras de análise estática de documentos Markdown.
```bash
# Instalado via skill-manager no ambiente Stout
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/spec-validation` | Inicia a auditoria de consistência SOW/Spec |

## Governança e Segurança

- **Nível de Governança:** 2 (Review).
- **Segurança:** Acesso apenas para leitura de documentos. Não modifica arquivos sem aprovação.
