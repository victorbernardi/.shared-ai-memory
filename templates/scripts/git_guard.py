import subprocess
import sys
import re
from pathlib import Path

class GitGuard:
    """
    Barreira técnica que garante que o diretório de trabalho esteja limpo antes da execução.
    Modos:
        - block: Aborta a execução se houver arquivos não commitados.
        - prompt: Pergunta ao usuário se deseja commitar automaticamente.
        - auto: Commita automaticamente e prossegue.
    """
    def __init__(self, mode="block", watch_patterns=None):
        self.mode = mode
        self.watch_patterns = watch_patterns or ["*.py", "*.yaml", "*.json", "*.md"]

    def is_dirty(self):
        """Verifica se há mudanças pendentes no git."""
        try:
            # Verifica mudanças staged e unstaged
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def get_dirty_files(self):
        """Retorna a lista de arquivos com mudanças."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        return [line[3:] for line in result.stdout.splitlines()]

    def _get_context_message(self):
        """Tenta extrair o contexto do último checkpoint do GCC para a mensagem de commit."""
        try:
            gcc_path = Path(".GCC/branches")
            if not gcc_path.exists():
                return "auto-checkpoint: secured by GitGuard"

            # Pega o arquivo de checkpoint mais recente
            checkpoints = sorted(gcc_path.glob("checkpoint_*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
            if not checkpoints:
                return "auto-checkpoint: secured by GitGuard"

            latest = checkpoints[0]
            content = latest.read_text(encoding='utf-8')
            
            # Tenta extrair o título do checkpoint (Action)
            match_action = re.search(r'## 🔍 Context Graph.*?### 3. Ação \(Action\)\n- `(.*?)`', content, re.DOTALL)
            match_rationale = re.search(r'### 2. Lógica \(Rationale\)\n> (.*?)\n', content)
            
            action = match_action.group(1) if match_action else "working on implementation"
            rationale = match_rationale.group(1) if match_rationale else ""
            
            msg = f"checkpoint({action}): {rationale}" if rationale else f"checkpoint: {action}"
            return msg[:100] # Limita tamanho da mensagem
        except Exception:
            return "auto-checkpoint: secured by GitGuard"

    def assert_clean(self, context_name="Process"):
        """Ponto de checagem obrigatório."""
        if not self.is_dirty():
            return True

        dirty_files = self.get_dirty_files()
        
        # Filtra arquivos que não devem disparar o guarda se necessário
        # (ex: arquivos de log ou temporários)
        
        print(f"\n[!] GIT GUARD: Mudanças detectadas em {context_name}")
        for f in dirty_files:
            print(f"  - {f}")

        if self.mode == "block":
            print("\n[ABORT] Execução bloqueada. Por favor, faça o commit das mudanças antes de prosseguir.")
            print("Comando sugerido: git add . && git commit -m 'checkpoint: working on implementation'")
            sys.exit(1)
        
        elif self.mode == "auto":
            msg = self._get_context_message()
            print(f"\n[AUTO] Realizando auto-commit: {msg}")
            self._auto_commit(msg)
            return True
            
        elif self.mode == "prompt":
            choice = input("\n[PROMPT] Deseja realizar auto-commit agora? (y/n): ").lower()
            if choice == 'y':
                msg = self._get_context_message()
                self._auto_commit(msg)
                return True
            else:
                print("[ABORT] Execução cancelada pelo usuário.")
                sys.exit(1)

    def _auto_commit(self, message):
        """Executa o commit automático."""
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
            print(f"[SUCCESS] Commit realizado com sucesso.")
        except Exception as e:
            print(f"[ERROR] Falha no auto-commit: {e}")
            sys.exit(1)

# Singleton para uso global se necessário
git_guard = GitGuard(mode="block")
