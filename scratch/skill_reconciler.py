import os
import shutil
import yaml
from pathlib import Path

# Paths to check
LOCAL_SKILLS = Path(r"C:\Users\victor.bernardi\.gemini\skills")
SHARED_SKILLS = Path(r"C:\Users\victor.bernardi\.shared-ai-memory\skills")
BACKUP_DIR = Path(r"C:\Users\victor.bernardi\.gemini\skills_backup")

def get_skill_name(skill_md_path):
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    return metadata.get('name')
    except Exception as e:
        print(f"Error reading {skill_md_path}: {e}")
    return None

def main():
    skill_map = {} # name -> list of paths
    
    all_paths = [LOCAL_SKILLS, SHARED_SKILLS]
    
    for base_path in all_paths:
        if not base_path.exists():
            continue
        for root, dirs, files in os.walk(base_path):
            if "SKILL.md" in files:
                skill_path = Path(root) / "SKILL.md"
                name = get_skill_name(skill_path)
                if name:
                    if name not in skill_map:
                        skill_map[name] = []
                    skill_map[name].append(skill_path)

    conflicts = {name: paths for name, paths in skill_map.items() if len(paths) > 1}
    
    if not conflicts:
        print("No skill conflicts found.")
        return

    print(f"Found {len(conflicts)} skill conflicts:")
    for name, paths in conflicts.items():
        print(f"\nSkill: {name}")
        for p in paths:
            print(f"  - {p}")

    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        print(f"\nCreated backup directory: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
