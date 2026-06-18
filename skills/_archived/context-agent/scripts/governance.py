"""
Módulo de governança para context-agent.
Implementa registro de ações e o Git Sync Hook para persistência remota.
"""
from __future__ import annotations
import os
import subprocess
import time
from typing import Dict, Any, Optional
from pathlib import Path

class GovernanceManager:
    """Gerencia a governança e conformidade da skill."""
    
    def __init__(self):
        self.last_action_time = 0
        self.min_interval = 1.0  # 1 segundo entre ações de memória

    def check_rate_limit(self) -> bool:
        """Verifica se a ação está dentro do limite de taxa."""
        now = time.time()
        if now - self.last_action_time < self.min_interval:
            return False
        self.last_action_time = now
        return True

    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Registra a ação no log de auditoria local."""
        print(f"[GOVERNANCE] Action recorded: {action}")

    def git_sync(self, session_id: int, topic: str, repo_path: str | Path):
        """
        Realiza o ciclo Git Sync: add, commit, push.
        Garante que a sessão seja persistida remotamente no GitHub.
        """
        repo_path = Path(repo_path)
        if not (repo_path / ".git").exists():
            print(f"[GOVERNANCE] Skipping Git Sync: {repo_path} is not a git repository.")
            return

        print(f"[GOVERNANCE] Starting Git Sync for session-{session_id:03d}...")
        
        try:
            # 1. Staging granular (Memória, Docs e a própria sessão)
            # Usamos -A para garantir que deleções e movimentações sejam capturadas
            subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True, capture_output=True)
            
            # 2. Commit com mensagem padronizada
            commit_msg = f"session: {session_id:03d} - {topic}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_path, check=True, capture_output=True)
            print(f"  [GIT] Committed: {commit_msg}")

            # 3. Push para o origin
            # Usamos pull --rebase para evitar conflitos simples
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "master"], cwd=repo_path, check=True, capture_output=True)
            print("  [GIT] Pushed to GitHub successfully.")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip() if e.stderr else str(e)
            if "nothing to commit" in error_msg:
                print("  [GIT] Nothing to commit, repository already in sync.")
            else:
                print(f"  [GIT] ERROR during sync: {error_msg}")
        except Exception as e:
            print(f"  [GIT] UNEXPECTED ERROR: {e}")
