import os
import shutil
import subprocess

skills_dir = r"C:\Users\victor.bernardi\.shared-ai-memory\skills"
archive_dir = os.path.join(skills_dir, "_archived")
repo_dir = r"C:\Users\victor.bernardi\.shared-ai-memory"

skills_to_archive = ["audit-canary-deployment", "sync-wire"]

print("=== Starting Additional Skills Archiving & Git Sync ===")

# 1. Move folders physically
os.makedirs(archive_dir, exist_ok=True)
moved_folders = []

for skill in skills_to_archive:
    src_path = os.path.join(skills_dir, skill)
    dst_path = os.path.join(archive_dir, skill)
    
    if os.path.exists(src_path):
        try:
            if os.path.exists(dst_path):
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                else:
                    os.remove(dst_path)
            shutil.move(src_path, archive_dir)
            print(f"[+] Moved physically to archive: '{skill}'")
            moved_folders.append(skill)
        except Exception as e:
            print(f"[!] Error moving '{skill}': {str(e)}")
    else:
        if os.path.exists(dst_path):
            print(f"[~] '{skill}' already archived.")
            moved_folders.append(skill)
        else:
            print(f"[-] Folder '{skill}' not found.")

# Helper to run shell commands in repo dir
def run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[!] Git Command Failed: git {' '.join(args)}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        raise e

# 2. Git automation
try:
    # Get current branch
    current_branch = run_git(["branch", "--show-current"])
    print(f"[*] Current branch detected: '{current_branch}'")
    
    if not current_branch:
        print("[!] Not currently on a branch or detached HEAD. Aborting git operations.")
        exit(1)
        
    # Stage all changes (including the previous archiving changes and registry.json)
    print("[*] Staging changes...")
    run_git(["add", "-A"])
    
    # Commit changes
    print("[*] Committing changes...")
    commit_msg = "chore(skills): archive audit-canary-deployment and sync-wire"
    try:
        run_git(["commit", "-m", commit_msg])
        print(f"[+] Committed: '{commit_msg}'")
    except Exception:
        print("[~] No changes to commit (working tree clean).")
        
    # Determine the target main branch (main or master)
    branches = run_git(["branch"]).replace("*", "").split()
    target_branch = "master" if "master" in branches else ("main" if "main" in branches else None)
    
    if not target_branch:
        print("[!] Could not determine target main branch (neither 'master' nor 'main' found).")
        exit(1)
        
    print(f"[*] Target main branch: '{target_branch}'")
    
    if current_branch == target_branch:
        print(f"[*] Already on target branch '{target_branch}'. No merge needed.")
    else:
        # Checkout main/master branch
        print(f"[*] Checking out '{target_branch}'...")
        run_git(["checkout", target_branch])
        
        # Merge changes
        print(f"[*] Merging '{current_branch}' into '{target_branch}'...")
        run_git(["merge", current_branch, "--no-edit"])
        print(f"[+] Merged successfully into '{target_branch}'")
        
        # Go back to original branch
        print(f"[*] Checking back out to original branch '{current_branch}'...")
        run_git(["checkout", current_branch])
        
    print("\n=== Success! All skills archived and Git sync completed. ===")

except Exception as e:
    print(f"\n[!] Git automation failed: {str(e)}")
    print("[*] Please run the remaining git steps manually if needed.")
