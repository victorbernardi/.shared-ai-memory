# Stout Groq Transcriber Output Spec

Date: 2026-07-08
Topic: output contract cleanup for `stout-groq-transcriber`
Status: approved for planning, not yet implemented

## SOW

### Problem Statement

The current transcription workflow writes a mix of final artifacts and intermediate files into the project root. This creates operational clutter and makes the supported output contract unclear.

### In Scope

| Target | Observable outcome |
| --- | --- |
| Clean output mode | Running the skill in default mode produces exactly one final Markdown file in the expected destination. |
| Destination auto-resolution | The skill writes to `research/` when that directory exists, otherwise to `transcriptions/`. |
| Debug and archive isolation | Non-clean modes store artifacts under a per-session directory in `transcriptions/`. |
| Filename normalization | Final output filename matches the input `.mp4` basename with `.md` extension. |
| CLI contract | Output behavior is controlled by explicit flags with deterministic defaults. |
| Final document structure | The final Markdown file carries a fixed, ordered set of sections. |
| CLI failure contract | Every failing precondition exits non-zero with an error naming the precondition. |

### Out of Scope

| Target | Why not |
| --- | --- |
| Prompt redesign for transcription quality | This change addresses artifact placement and output contract, not model prompt quality. |
| Model migration or provider changes | The problem is independent of Groq model selection. |
| Cleanup of historical loose files already present in repositories | This spec governs future writes only. |
| Multi-file final outputs in clean mode | The user explicitly wants one canonical final artifact. |

### Acceptance Criteria

| ID | Acceptance criterion | Observable signal |
| --- | --- | --- |
| AC-1 | Default execution SHALL use `clean` mode. | Running without `--mode` resolves to `clean`. |
| AC-2 | In `clean`, the skill SHALL generate exactly one final Markdown file and no intermediate root-level artifacts. | Only one new `.md` file appears in the clean destination; no `raw`, `chunk`, `corrected`, or temp files are written to project root. |
| AC-3 | If `research/` exists in the resolved project root and `--out-dir` is not provided, `clean` SHALL write directly to `research/<session>.md`. | A run from a project containing `research/` produces the file in that directory. |
| AC-4 | If `research/` does not exist and `--out-dir` is not provided, `clean` SHALL write directly to `transcriptions/<session>.md`. | A run from a project without `research/` produces the file in `transcriptions/`. |
| AC-5 | In `debug`, artifacts SHALL be isolated under `transcriptions/<session>/debug/`. | Final and intermediate files appear only under that session path. |
| AC-6 | In `archive`, artifacts SHALL be isolated under `transcriptions/<session>/archive/<timestamp>/`. | A timestamped directory is created and populated under the session path. |
| AC-7 | Absent `--session-name`, the final output filename SHALL be derived from the input `.mp4` basename and use the `.md` extension. | Input `phx_review_prd_alertas.mp4` produces `phx_review_prd_alertas.md`. |
| AC-8 | `--out-dir` SHALL override the base destination rules for all modes. | Outputs are written under the user-supplied base directory. |
| AC-9 | `--session-name` SHALL override the derived session name for session paths and final filename when explicitly provided. | Session folder and final filename reflect the override. |
| AC-10 | `--keep-source-copy` SHALL only create additional source-copy artifacts in `debug` or `archive`, not in default `clean`. | Clean mode still emits only one final `.md` and warns on stderr that the flag has no effect; non-clean modes may also include the copied source file. |
| AC-11 | The final Markdown output SHALL contain stable sections for title, minimal metadata, meeting summary, key action items, and full transcript. | Generated `.md` includes all required sections in order. |
| AC-12 | The CLI SHALL fail when input is missing, output path cannot be created, final file cannot be written, or Groq API key is absent. | The process exits non-zero and the error message names the failing precondition and the path or variable involved. |

## Technical Spec

### Architecture Summary

The implementation will introduce a dedicated artifact-management layer around the existing transcription pipeline. The pipeline remains responsible for transcription and cleanup content generation. The artifact-management layer becomes solely responsible for resolving destination paths, naming outputs, and deciding which artifacts may be written in each mode.

### Assumptions

| ID | Assumption | Impact if broken |
| --- | --- | --- |
| AS-001 | The target project is a Git repository, so that project-root resolution (FR-013) terminates at a `.git` directory. | Project-root resolution falls back to the current working directory, and destination auto-resolution may select the wrong directory. |
| AS-002 | The primary input is an `.mp4` file or an input path whose basename can be deterministically transformed into a Markdown filename. | Filename derivation rules may need extension-agnostic fallback handling. |
| AS-003 | Existing downstream consumers can accept the Markdown file as the canonical final artifact instead of a `.txt` transcript. | A compatibility bridge may be required temporarily. |
| AS-004 | `research/` and `transcriptions/` are project-local directories, not external storage mounts with custom write behavior. | Path creation and write semantics may vary and need explicit handling. |

### Functional Requirements

| ID | Requirement | Implements |
| --- | --- | --- |
| FR-001 | The CLI SHALL resolve `clean` as the default mode when `--mode` is not provided. | AC-1 |
| FR-002 | In `clean`, the artifact manager SHALL allow writing exactly one final Markdown file into the project tree and SHALL suppress debug, raw, corrected, chunked, and temporary artifact writes into the project tree. Transient chunk data MAY be written to a system temporary directory outside the project tree, and SHALL be removed before the process exits. | AC-2 |
| FR-003 | In `clean`, if `research/` exists in the resolved project root and `--out-dir` is not provided, the final Markdown path SHALL be `research/<session>.md`. | AC-3 |
| FR-004 | In `clean`, if `research/` does not exist in the resolved project root and `--out-dir` is not provided, the final Markdown path SHALL be `transcriptions/<session>.md`. | AC-4 |
| FR-005 | In `debug`, the artifact manager SHALL write artifacts only under `transcriptions/<session>/debug/` unless `--out-dir` overrides the base destination. | AC-5, AC-8, AC-9 |
| FR-006 | In `archive`, the artifact manager SHALL write artifacts only under `transcriptions/<session>/archive/<timestamp>/` unless `--out-dir` overrides the base destination. The timestamp SHALL use the format `YYYYMMDD-HHMMSS`; if the resulting directory already exists, a numeric suffix `-NN` SHALL be appended, starting at `-01`. | AC-6, AC-8, AC-9 |
| FR-007 | The basename SHALL be derived from the input filename stem. The session name SHALL default to the basename, and the final filename SHALL be `<session>.md` in every mode. | AC-7 |
| FR-008 | When `--out-dir` is provided, the artifact manager SHALL use that directory as the base output root for all modes. | AC-8 |
| FR-009 | When `--session-name` is provided, the artifact manager SHALL use it as the effective session name and final filename stem. | AC-9 |
| FR-010 | `--keep-source-copy` SHALL be ignored in `clean`, and the CLI SHALL emit a warning to stderr stating that the flag has no effect in `clean`. It SHALL only create a source-file copy in `debug` or `archive`. | AC-10 |
| FR-011 | The final artifact writer SHALL emit a single Markdown document with sections for title, minimal metadata, meeting summary, key action items, and full transcript, in that order. | AC-11 |
| FR-012 | The CLI SHALL validate input existence, destination creation, final write success, and API key availability before reporting success, and on failure SHALL exit non-zero with a message naming the failing precondition and the path or variable involved. | AC-12 |
| FR-013 | The artifact manager SHALL resolve the project root by walking upward from the current working directory until a directory containing `.git` is found; if none is found, the current working directory SHALL be used as the project root. | AC-3, AC-4 |

### Non-Functional Requirements

| ID | Requirement | Validates | Rationale |
| --- | --- | --- | --- |
| NFR-001 | Output path and filename resolution SHALL be deterministic for the same inputs and filesystem state. Archive paths are exempt by design, because they embed a wall-clock timestamp; see FR-006. | AC-2, AC-3, AC-4, AC-5, AC-7, AC-8, AC-9 | Predictable output placement is the primary objective of this change. |
| NFR-002 | The supported workflow SHALL not write intermediate artifacts to the project root in any mode. | AC-2, AC-5, AC-6 | Root-level clutter is the operational defect being corrected. |
| NFR-003 | Each CLI error message SHALL name the failing precondition and the path or variable involved. | AC-12 | Failures need to be actionable during repeated manual use. |
| NFR-004 | The `clean` path SHALL require zero flags beyond the input file. | AC-1, AC-2, AC-3, AC-4 | The default path must stay low-friction. |

### Interfaces and Internal Units

| Unit | Responsibility |
| --- | --- |
| `resolve_mode(args)` | Resolve effective mode, defaulting to `clean`. |
| `resolve_project_root(cwd)` | Walk upward from `cwd` to the nearest `.git` directory; fall back to `cwd`. |
| `derive_session_name(input_path, session_name_override)` | Produce the session name used for session paths and final filename. |
| `resolve_base_output_dir(project_root, mode, out_dir_override)` | Resolve `research/`, `transcriptions/`, or override base destination. |
| `build_output_plan(...)` | Produce the final artifact path and any allowed auxiliary artifact paths. |
| `write_final_markdown(...)` | Write the canonical Markdown artifact. |
| `write_debug_artifact(...)` | Write non-final artifacts only in modes that permit them. |

### Dependencies

| Dependency | Purpose |
| --- | --- |
| Groq API (Whisper v3, LLaMA) | Transcription and summary generation; unchanged by this spec. |
| `ffmpeg` | Audio extraction and chunking of long inputs prior to transcription. |
| Python `pathlib` | Project-root walk and path construction (FR-013). |
| Python `tempfile` | Out-of-tree storage for transient chunk data (FR-002). |
| Git working tree | Marker used by project-root resolution (FR-013, AS-001). |

### Risks

| ID | Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| R-001 | Project-root walk escapes the intended project when the skill is run from a nested Git repository or submodule. | Medium | Output lands in the wrong repository. | `--out-dir` overrides resolution entirely; T-015 pins the subdirectory case. |
| R-002 | Existing downstream consumers still read the legacy `.txt` transcript. | Medium | Silent breakage of dependent workflows. | AS-003 tracks this; audit consumers before the implementation plan is approved. |
| R-003 | Transient chunk files leak into the project tree when the process is killed mid-run. | Low | Reintroduces the clutter this spec removes. | Write chunks under `tempfile`, outside the project tree; T-017 asserts the tree is clean. |
| R-004 | `research/` exists but is not the intended destination for a given project. | Low | Output placed in an unexpected directory. | Documented in AS-004; `--out-dir` provides the escape hatch. |

### Implementation Phases

| Phase | Targets | Depends |
| --- | --- | --- |
| P1 — Path resolution core | `resolve_project_root`, `resolve_base_output_dir`, `derive_session_name` (FR-003, FR-004, FR-007, FR-008, FR-009, FR-013) | — |
| P2 — Artifact manager and mode gating | `build_output_plan`, `write_final_markdown`, `write_debug_artifact` (FR-002, FR-005, FR-006, FR-010) | P1 |
| P3 — CLI contract | Flag parsing, mode default, failure contract (FR-001, FR-012) | P1, P2 |
| P4 — Final document structure | Markdown section writer (FR-011) | P2 |

## Test Scenarios

| ID | Scenario | FR |
| --- | --- | --- |
| T-001 | Run the CLI without `--mode` and assert the resolved mode is `clean`. | FR-001 |
| T-002 | Run `clean` in a fixture project with `research/` present and assert exactly one file is created at `research/<session>.md`. | FR-002, FR-003, FR-007, FR-011 |
| T-003 | Run `clean` in a fixture project without `research/` and assert exactly one file is created at `transcriptions/<session>.md`. | FR-002, FR-004, FR-007, FR-011 |
| T-004 | Run `clean` and assert no root-level `raw`, `corrected`, `chunk`, or temporary files are created. | FR-002 |
| T-005 | Run `debug` and assert artifacts are written only under `transcriptions/<session>/debug/`. | FR-005, FR-007 |
| T-006 | Run `archive` twice with a frozen clock and assert the second run creates a `-01`-suffixed directory rather than overwriting the first. | FR-006, FR-007 |
| T-007 | Run with `--out-dir custom-output` in each mode and assert all artifacts are rooted under `custom-output`. | FR-003, FR-004, FR-005, FR-006, FR-008 |
| T-008 | Run with `--session-name custom-name` and assert the final filename and session directory use `custom-name`. | FR-005, FR-006, FR-009 |
| T-009 | Run `clean` with `--keep-source-copy` and assert no source copy is created and a warning is written to stderr. | FR-010 |
| T-010 | Run `debug` or `archive` with `--keep-source-copy` and assert the original media file is copied into the session tree. | FR-010 |
| T-011 | Inspect the generated Markdown and assert it contains title, minimal metadata, meeting summary, key action items, and full transcript sections, in that order. | FR-011 |
| T-012 | Run with a missing input file and assert a non-zero exit and an error naming the missing input path. | FR-012 |
| T-013 | Run with missing API key and assert a non-zero exit and an error naming the absent environment variable. | FR-012 |
| T-014 | Simulate output-directory creation or file-write failure and assert a non-zero exit and an error naming the unwritable path. | FR-012 |
| T-015 | Run `clean` from a subdirectory of a fixture Git project containing `research/` and assert the file is created at `<project-root>/research/<session>.md`, not under the subdirectory. | FR-003, FR-013 |
| T-016 | Run `clean` from a fixture directory with no `.git` ancestor and assert the current working directory is used as the project root. | FR-004, FR-013 |
| T-017 | Run `clean` on a long input requiring chunking and assert no transient chunk files remain anywhere in the project tree after exit. | FR-002 |

## Traceability Matrix

| AC | FR | Test | NFR |
| --- | --- | --- | --- |
| AC-1 | FR-001 | T-001 | NFR-004 |
| AC-2 | FR-002 | T-002, T-003, T-004, T-017 | NFR-001, NFR-002 |
| AC-3 | FR-003, FR-013 | T-002, T-007, T-015 | NFR-001, NFR-004 |
| AC-4 | FR-004, FR-013 | T-003, T-007, T-016 | NFR-001, NFR-004 |
| AC-5 | FR-005 | T-005 | NFR-001, NFR-002 |
| AC-6 | FR-006 | T-006 | NFR-002 |
| AC-7 | FR-007 | T-002, T-003, T-005, T-006 | NFR-001 |
| AC-8 | FR-005, FR-006, FR-008 | T-007 | NFR-001 |
| AC-9 | FR-005, FR-006, FR-009 | T-008 | NFR-001 |
| AC-10 | FR-010 | T-009, T-010 | NFR-002 |
| AC-11 | FR-011 | T-002, T-003, T-011 | — |
| AC-12 | FR-012 | T-012, T-013, T-014 | NFR-003 |

## Consistency Notes

- Every acceptance criterion maps to at least one functional requirement, and every functional requirement maps to at least one test scenario. The Traceability Matrix is the authoritative view; the `Implements` and `FR` columns must agree with it.
- `basename` designates exclusively the stem derived from the input filename. `session` designates the effective session name, which equals `basename` unless `--session-name` overrides it. Session paths and the final filename always use `session`.
- `project root` designates the directory resolved by FR-013, which is not necessarily the current working directory.
- The spec uses stable terminology: `clean`, `debug`, `archive`, `session`, `basename`, `project root`, `final Markdown file`.
- The spec intentionally avoids ambiguous terms such as `adequately`, `reasonable`, `fast`, or `TBD` in requirement clauses.
- NFR-001 deliberately excludes AC-6: archive paths embed a wall-clock timestamp and are therefore non-deterministic by design.
- AC-11 has no governing NFR: it constrains document structure, not path resolution, error text, or invocation friction.

## Implementation Boundary

This spec is approved for planning only. No implementation should begin until a separate implementation plan is written and reviewed.
