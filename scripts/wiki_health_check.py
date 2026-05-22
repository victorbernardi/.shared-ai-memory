import os
import re

VAULT_PATH = r'C:\Users\victor.bernardi\Documents\wiki-compiler-vault'
INDEX_PATH = os.path.join(VAULT_PATH, 'index.md')

def main():
    # 1. Check Index Consistency
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    files_on_disk = []
    for root, dirs, files in os.walk(VAULT_PATH):
        if '.obsidian' in root or '_archives' in root or '_raw' in root: continue
        for f in files:
            if f.endswith('.md') and f not in ['index.md', 'log.md', 'hot.md', 'GEMINI.md', 'CLAUDE.md', 'ANTIGRAVITY.md']:
                rel_dir = os.path.relpath(root, VAULT_PATH)
                if rel_dir == '.':
                    files_on_disk.append(f.replace('.md', ''))
                else:
                    files_on_disk.append(f"{rel_dir.replace(os.sep, '/')}/{f.replace('.md', '')}")

    links_in_index = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', index_content)
    
    missing_in_index = [f for f in files_on_disk if f not in links_in_index]
    broken_in_index = [l for l in links_in_index if l not in files_on_disk and not l.startswith('http')]

    print(f"Total files on disk (filtered): {len(files_on_disk)}")
    print(f"Links found in index: {len(links_in_index)}")
    print(f"Missing in index: {len(missing_in_index)}")
    print(f"Broken in index: {len(broken_in_index)}")
    
    if broken_in_index:
        print("\nBroken links in index:")
        for bl in broken_in_index[:10]: print(f"  - {bl}")
        
    if missing_in_index:
        print("\nMissing files in index:")
        for mi in missing_in_index[:10]: print(f"  - {mi}")

if __name__ == "__main__":
    main()
