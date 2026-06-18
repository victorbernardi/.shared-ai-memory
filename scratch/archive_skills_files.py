import os
import shutil

skills_dir = r"C:\Users\victor.bernardi\.shared-ai-memory\skills"
archive_dir = os.path.join(skills_dir, "_archived")

skills_to_archive = [
    "context-fundamentals",
    "audit-context-guardian",
    "audit-logging-system",
    "audit-verification",
    "audit-webapp-testing",
    "caveman",
    "cdd-governance",
    "code-documentation-code-explain",
    "code-documentation-doc-generate",
    "code-refactoring-context-restore",
    "code-refactoring-refactor-clean",
    "code-refactoring-tech-debt",
    "code-review-ai-ai-review",
    "code-review-checklist",
    "code-reviewer",
    "code-review-excellence",
    "code-simplifier",
    "context-agent",
    "context-degradation",
    "context-driven-development",
    "stout-finishing-a-development-branch",
    "context-guardian",
    "context-management",
    "context-manager",
    "context-optimization",
    "data-build-dashboard",
    "data-context-extractor",
    "data-create-viz",
    "data-explore-code",
    "data-explore-data",
    "data-insight-reporter",
    "data-statistical-analysis",
    "data-storytelling",
    "data-validate-data",
    "data-validation",
    "data-visualization",
    "design-antigravity-expert",
    "design-high-end-visual",
    "design-industrial-brutalist",
    "design-kpi-dashboard",
    "design-liquid-glass",
    "diagnose",
    "improve-codebase-architecture",
    "internal-comms",
    "process-brd-generator",
    "process-context-compression",
    "process-context-degradation",
    "process-context-driven-development",
    "process-context-fundamentals",
    "process-context-management",
    "process-context-manager",
    "process-context-optimization",
    "process-context-restore",
    "process-context-save",
    "process-deep-research",
    "process-doc-orchestrator",
    "process-internal-comms",
    "process-meeting-assistant",
    "process-superantigravity",
    "process-user-story",
    "prototype",
    "stout-brainstorming",
    "stout-cdd-orchestrator",
    "stout-commit",
    "stout-data-analyze",
    "stout-data-sql-queries",
    "stout-data-write-query",
    "stout-dev-tdd",
    "stout-executing-plans",
    "stout-immunity-gate",
    "tdd",
    "stout-improve-skill",
    "stout-spec-validation",
    "stout-subagent-driven-development",
    "stout-systematic-debugging",
    "stout-writing-plans",
    "systematic-debugging",
    "tag-taxonomy",
    "write-a-skill",
    "zoom-out"
]

# Ensure archive directory exists
os.makedirs(archive_dir, exist_ok=True)

moved_count = 0
not_found_count = 0
error_count = 0

for skill in skills_to_archive:
    src_path = os.path.join(skills_dir, skill)
    dst_path = os.path.join(archive_dir, skill)
    
    # Skip if trying to move the _archived directory itself
    if skill == "_archived":
        continue
        
    if not os.path.exists(src_path):
        # Check if already in _archived
        if os.path.exists(dst_path):
            print(f"Info: Skill '{skill}' already archived.")
        else:
            print(f"Warning: Skill folder '{skill}' not found at {src_path}")
            not_found_count += 1
        continue
        
    try:
        # If destination already exists, remove it first to avoid collision
        if os.path.exists(dst_path):
            print(f"Info: Destination '{dst_path}' already exists. Removing older archive...")
            if os.path.isdir(dst_path):
                shutil.rmtree(dst_path)
            else:
                os.remove(dst_path)
                
        # Move directory
        shutil.move(src_path, archive_dir)
        print(f"Success: Archived '{skill}'")
        moved_count += 1
    except Exception as e:
        print(f"Error: Failed to archive '{skill}'. Reason: {str(e)}")
        error_count += 1

print("\n--- Summary ---")
print(f"Successfully archived: {moved_count}")
print(f"Already archived/not found: {not_found_count}")
print(f"Errors: {error_count}")
