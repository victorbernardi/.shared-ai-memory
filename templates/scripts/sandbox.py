import os
import subprocess
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.config import config
from src.gcc_controller import gcc

class SkillSandbox:
    """
    Camada de isolamento para execução de scripts e ferramentas (Roadmap V4.9).
    Implementa Subprocess Whitelisting, Sanitização de Ambiente e Timeout.
    """

    def __init__(self):
        self.enabled = config.sandbox_enabled
        self.timeout = config.sandbox_timeout
        self.allowed_executables = config.sandbox_allowed_executables
        self.allowed_dirs = [Path(d).resolve() for d in config.sandbox_allowed_dirs]
        self.env_whitelist = config.sandbox_env_whitelist

    def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ação (script ou tool) dentro das restrições do sandbox.
        """
        action_type = action.get('type')
        target = action.get('target')
        params = action.get('params', {})
        
        # Se sandbox estiver desativado, faz um bypass direto (não recomendado)
        if not self.enabled:
            return self._unsafe_execute(action_type, target, params)

        try:
            # 1. Validação de Segurança
            self._validate_action(action_type, target)

            # 2. Preparação do Ambiente (Sanitização)
            env = self._get_sanitized_env()

            # 3. Construção do Comando
            cmd = self._build_command(action_type, target, params)

            # 4. Execução Controlada
            print(f"  [SANDBOX] Executando: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=params.get('timeout', self.timeout),
                cwd=str(Path.cwd())
            )

            outcome = "SUCCESS" if result.returncode == 0 else "FAILURE"
            
            # 5. Registro no GCC (SRAO)
            gcc.commit_milestone(
                action=f"sandbox_execute:{target}",
                rationale=f"Execução controlada de {action_type} via SkillSandbox.",
                context={
                    "action": action,
                    "exit_code": result.returncode,
                    "stdout_snippet": result.stdout[-500:] if result.stdout else "",
                    "stderr_snippet": result.stderr[-500:] if result.stderr else ""
                },
                outcome=outcome
            )

            return {
                "status": outcome,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired as e:
            error_msg = f"Tempo de execução excedido ({e.timeout}s)"
            self._log_failure(target, error_msg, action)
            return {"status": "TIMEOUT", "error": error_msg}
        
        except PermissionError as e:
            self._log_failure(target, str(e), action)
            return {"status": "BLOCKED", "error": str(e)}
        
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            self._log_failure(target, error_msg, action)
            return {"status": "ERROR", "error": error_msg}

    def _validate_action(self, action_type: str, target: str):
        """Valida se o comando e o caminho estão na whitelist."""
        # Se for script, valida o caminho
        if action_type in ['execute_script', 'execute_tool']:
            target_path = Path(target).resolve()
            
            # Valida se o arquivo existe
            if not target_path.exists():
                raise FileNotFoundError(f"Alvo não encontrado: {target}")

            # Valida se está em um diretório permitido
            is_allowed_dir = any(str(target_path).startswith(str(d)) for d in self.allowed_dirs)
            if not is_allowed_dir:
                raise PermissionError(f"Acesso negado ao diretório: {target_path.parent}")

            # Valida a extensão (apenas .py por enquanto no CDD)
            if target_path.suffix != '.py':
                 # Se não for .py, verificamos se é um dos executáveis permitidos se for uma chamada direta
                 pass 

    def _get_sanitized_env(self) -> Dict[str, str]:
        """Retorna um ambiente contendo apenas as variáveis permitidas."""
        sanitized = {}
        for key in self.env_whitelist:
            val = os.getenv(key)
            if val:
                sanitized[key] = val
        return sanitized

    def _build_command(self, action_type: str, target: str, params: Dict[str, Any]) -> List[str]:
        """Constrói a lista de argumentos para o subprocess."""
        cmd = []
        
        if target.endswith('.py'):
            cmd = [sys.executable, target]
        elif action_type == 'execute_tool' and target in self.allowed_executables:
            cmd = [target]
        else:
            # Fallback seguro: se não for .py e não estiver na whitelist de executáveis, bloqueia
            if target not in self.allowed_executables:
                raise PermissionError(f"Executável não permitido: {target}")
            cmd = [target]

        # Adiciona argumentos extras se existirem
        args = params.get('args', [])
        if isinstance(args, list):
            cmd.extend(args)
        elif isinstance(args, str):
            cmd.extend(args.split())
            
        return cmd

    def _log_failure(self, target: str, error: str, action: dict):
        """Registra falha de execução no GCC."""
        gcc.commit_milestone(
            action=f"sandbox_failure:{target}",
            rationale=f"Falha na execução do sandbox: {error}",
            context={"action": action, "error": error},
            outcome="FAILURE"
        )

    def _unsafe_execute(self, action_type: str, target: str, params: dict):
        """Execução direta sem proteção (legado)."""
        print(f"  [SANDBOX-BYPASS] Executando sem proteção: {target}")
        # Implementação minimalista para manter compatibilidade se desativado
        return {"status": "BYPASS", "message": "Sandbox is disabled"}

# Instância única para uso no projeto
sandbox = SkillSandbox()
