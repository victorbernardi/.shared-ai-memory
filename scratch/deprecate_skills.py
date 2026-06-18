import json
import os
from datetime import datetime

registry_path = r"C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json"

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

if not os.path.exists(registry_path):
    print(f"Error: Registry file not found at {registry_path}")
    exit(1)

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

print(f"Success: Updated {updated_count} skills in registry.json")
