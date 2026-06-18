import os
import shutil
import json

registry_path = r"C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json"
skills_dir = r"C:\Users\victor.bernardi\.shared-ai-memory\skills"
archive_dir = os.path.join(skills_dir, "_archived")

skills_to_deprecate = {
    "stout-brainstorming",
    "stout-cdd-orchestrator",
    "stout-commit",
    "stout-data-analyze",
    "stout-data-sql-queries",
    "stout-data-write-query",
    "stout-dev-tdd",
    "stout-executing-plans",
    "stout-finishing-a-development-branch",
    "stout-immunity-gate",
    "stout-improve-skill",
    "stout-spec-validation",
    "stout-subagent-driven-development",
    "stout-systematic-debugging",
    "stout-writing-plans"
}

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

print("=== Starting Stout Skills Archiving Process ===")

# 1. Update registry.json
if os.path.exists(registry_path):
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        updated_count = 0
        for skill in data.get("skills", []):
            name = skill.get("name")
            if name in skills_to_deprecate:
                skill["status"] = "deprecated"
                skill["updated_at"] = "2026-06-18"
                skill["notes"] = "Arquivado em lote em 2026-06-18 a pedido do usuário."
                updated_count += 1

        data["last_updated"] = "2026-06-18"

        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[1/2] Success: Deprecated {updated_count} skills in registry.json")
    except Exception as e:
        print(f"[1/2] Error updating registry.json: {str(e)}")
else:
    print(f"[1/2] Warning: registry.json not found at {registry_path}")

# 2. Move files physically
os.makedirs(archive_dir, exist_ok=True)
moved_count = 0
already_archived = 0
error_count = 0

for skill in skills_to_archive:
    src_path = os.path.join(skills_dir, skill)
    dst_path = os.path.join(archive_dir, skill)
    
    if skill == "_archived":
        continue
        
    if not os.path.exists(src_path):
        if os.path.exists(dst_path):
            already_archived += 1
        else:
            print(f"[-] Skill '{skill}' not found in skills directory.")
        continue
        
    try:
        if os.path.exists(dst_path):
            if os.path.isdir(dst_path):
                shutil.rmtree(dst_path)
            else:
                os.remove(dst_path)
        
        shutil.move(src_path, archive_dir)
        print(f"[+] Archived: '{skill}'")
        moved_count += 1
    except Exception as e:
        print(f"[!] Error archiving '{skill}': {str(e)}")
        error_count += 1

print("\n=== Archiving Process Completed ===")
print(f"Successfully archived: {moved_count}")
print(f"Already archived/not found: {already_archived}")
print(f"Errors encountered: {error_count}")
