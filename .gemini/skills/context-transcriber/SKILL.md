---
name: context-transcriber
description: Use when you need to transcribe audio files with high terminological accuracy, leveraging the project's local context (filenames, code, and documentation) to guide the Whisper engine and LLM refinement.
version: 1.0.0
metadata:
  category: content
  triggers: transcrição, áudio, m4a, mp3, whisper, ata, resumo contextual
---

# Context Transcriber (v1)

This skill automates audio-to-text transcription by integrating project-specific vocabulary directly into the transcription engine. It prevents common "hallucinations" of technical terms by reading the current directory's file structure before processing.

## When to Use
- Use when you have a meeting recording or audio note within a project folder and want a transcription that respects local naming conventions.
- Use when transcribing technical content where general-purpose models often fail on project-specific jargon (e.g., "Proteus", "Inova", "Fabric", "Stout").
- Use when you want the output automatically organized in \docs/transcricao/\.

## Workflow

### 1. Discovery & Context Loading
The skill must first list the files in the current workspace to identify potential keywords.
- **Action:** Run \ls\ or \dir\ to gather names of spreadsheets, scripts, and documentation.
- **Goal:** Build a comma-separated list of terms for the \initial_prompt\.

### 2. Transcription Execution
Call the internal script \	ranscribe_with_context.py\ located in the skill's \scripts/\ folder.
- **Parameters:**
  - \ile\: Path to the audio file.
  - \context_prompt\: The list of terms gathered in step 1.
  - \output_dir\: Default to \./docs/transcricao/\.

### 3. LLM Refinement (Mandatory)
After the raw \.md\ is generated, use the LLM to review the text against the project context.
- **Instruction:** "Review this transcription. Ensure that terms like [List of files/context] are correctly spelled and capitalized according to the project environment."

## Anti-Rationalization (Iron Rules)
| Excuse | Reality |
| :--- | :--- |
| "The audio is clear, I don't need context." | **False.** Context is mandatory to ensure naming consistency across the project. |
| "I'll save it in the root folder for speed." | **Prohibited.** All outputs MUST go to \docs/transcricao/\. |
| "I'll skip the LLM refinement to save tokens." | **Denied.** Refinement is the final gate for technical quality. |

## Success Criteria
- A Markdown file exists in \docs/transcricao/\ following the naming convention \YYYY-MM-DD_[Projeto-Assunto]_FULL.md\.
- The transcription correctly identifies project-specific terms.

---
*Framework Stout | Antigravity Edition*
