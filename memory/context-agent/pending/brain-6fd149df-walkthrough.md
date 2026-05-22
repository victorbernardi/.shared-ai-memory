# Walkthrough - Fixing `opencode.jsonc` Configuration

I have updated the configuration file to resolve the linter issues identified.

## Changes Made

### Configuration Adjustments

#### [opencode.jsonc](file:///c:/Users/victor.bernardi/.opencode/opencode.jsonc)

-   **Log Level**: Changed `"info"` to `"INFO"` to match the required uppercase format.
-   **Model Identifiers**:
    -   Updated `plan` agent model from `google/gemini-3.1-pro` to `google/gemini-3.1-pro-preview`.
    -   Updated `wiki-llm` agent model from `moonshot/kimi-k2-turbo` to `moonshotai/kimi-k2-turbo-preview`.

## Verification Results

### Automated Tests
-   Cross-referenced updated values with the "Valid values" list provided by the IDE linter.
-   Verified that the file structure remains valid JSONC.

### Manual Verification
-   The configuration now adheres to the schema constraints for `logLevel` and `model` fields as reported by the `@current_problems` metadata.
