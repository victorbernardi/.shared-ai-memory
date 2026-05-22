# Implementation Plan: Claude Memory Integration & Context Agent Fixes

## 1. Background & Motivation
The current memory architecture successfully captures conversational logs and decisions via `context-agent` into `MEMORY.md`. However, it misses the explicit, high-value conceptual memory files that Claude Code natively generates in its isolated `~/.claude/projects/<encoded-path>/memory/` directories. Additionally, a hardcoded path belonging to a previous user (`C:\Users\renat\...`) was found in the `context-agent` scripts, indicating a need for cleanup.

## 2. Objective
- Integrate Claude's native markdown memory files into the Stout documentation ecosystem.
- Clean up hardcoded paths in the `context-agent` infrastructure to ensure environment portability.

## 3. Implementation Steps

### Phase 1: Context Agent Cleanup
1. **Target File:** `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\context-agent\scripts\active_context.py`
2. **Action:** Replace the hardcoded string `"python C:\\Users\\renat\\skills\\context-agent\\scripts\\context_manager.py load"` with a dynamic path using the `__file__` reference or a generic environment-agnostic command (e.g., `python context_manager.py load`).

### Phase 2: Evolução do `stout_promote.py` (v2.2)
1. **Target File:** `C:\Users\victor.bernardi\.shared-ai-memory\scripts\stout_promote.py`
2. **Action:** Update the script to include a third source for artifacts: Claude's Native Memory.
   - **Path Encoding Logic:** Implement a function to convert the current `PROJECT_ROOT` path into the Claude directory format (e.g., replacing `:\` and `\` with `-`).
   - **Source Directory:** Target `~/.claude/projects/<encoded-path>/memory/`.
   - **Promotion Target:** Map `.md` files found in the Claude memory folder to the active project's `docs/concepts/` (or a dedicated `docs/claude_memory/` directory) to avoid cluttering `plans/` or `specs/`. Prefix the promoted files to indicate their origin (e.g., `concept_claude_<name>.md`).
   - **Syncing:** Ensure the copy mechanism checks for differences to avoid redundant copying.

### Phase 3: Rollout & Verification
1. **Apply Updates:** Distribute the updated `stout_promote.py` to the shared scripts folder.
2. **Test Run:** Execute the script within a project that has active Claude memory (e.g., `C:\Projetos\Inova`).
3. **Validate Obsidian Ingest:** Confirm that the promoted conceptual files are placed correctly in the project's `docs/` folder, allowing them to be ingested into the global memory via the existing `wiki-stage.sh` and Obsidian vault mechanisms.

## 4. Alternatives Considered
- *Wait for `claude-history-ingest` to run:* This skill ingests history directly to Obsidian, but promoting the files to the project's local `docs/` via `stout_promote.py` first keeps the project repository self-contained and allows the Gemini CLI to read them easily without querying the global vault.

## 5. Rollback Strategy
If the promotion creates too much noise, we can revert `stout_promote.py` to v2.1 and rely solely on the `claude-history-ingest` skill for global semantic memory.
