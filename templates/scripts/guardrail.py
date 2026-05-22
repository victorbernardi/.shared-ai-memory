import os
import sys
from pathlib import Path

def validate_write_op(file_path: str, action: str = 'write_file'):
    """
    Valida se uma operação de escrita é segura de acordo com o Protocolo de Imunidade V2.0.
    """
    abs_path = Path(file_path).resolve()
    
    # 1. Verificação de Selo de Imutabilidade (Hard Lockdown)
    if abs_path.exists():
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(500) # Lê o topo do arquivo
                if "[STOUT-IMMUTABLE]" in head and action in ['write_file', 'write_to_file']:
                    error_msg = (
                        f"🔒 LOCKDOWN DE SEGURANÇA (STOUT-IMMUTABLE):\n"
                        f"O arquivo '{file_path}' possui um SELO DE IMUTABILIDADE.\n"
                        f"→ O uso de '{action}' é TERMINANTEMENTE PROIBIDO neste documento.\n"
                        f"→ Ação ÚNICA permitida: Edição cirúrgica via 'replace'."
                    )
                    print(error_msg, file=sys.stderr)
                    return False, error_msg
        except:
            pass

    # 2. Verificação de Whitelist (Liberdade Parcial)
    # Isenção por diretório ou extensão
    whitelist_dirs = ['notes', 'temp_', '.GCC']
    is_whitelisted = any(part in str(abs_path) for part in whitelist_dirs) or abs_path.suffix == '.log'
    
    if is_whitelisted:
        return True, "Operação segura (Whitelist/Telemetry)."

    # 2. Detecção de Ambiente e Ferramentas Proibidas
    mode = os.getenv("STOUT_CLI_MODE", "GEMINI").upper()
    
    forbidden_tools = {
        "GEMINI": ["write_file"],
        "ANTIGRAVITY": ["write_to_file"]
    }
    
    suggested_tools = {
        "GEMINI": "replace",
        "ANTIGRAVITY": "replace_file_content"
    }

    # Se a ferramenta usada for uma ferramenta de "Escrita Total" e o arquivo existir
    current_forbidden = forbidden_tools.get(mode, forbidden_tools["GEMINI"])
    
    if action in current_forbidden and abs_path.exists():
        suggestion = suggested_tools.get(mode, suggested_tools["GEMINI"])
        error_msg = (
            f"🚫 BLOQUEIO DE SEGURANÇA (GUARDRAIL V2.0):\n"
            f"Tentativa de usar '{action}' no arquivo EXISTENTE: '{file_path}'\n"
            f"Ambiente Detectado: {mode}\n"
            f"→ VIOLAÇÃO DO PROTOCOLO DE IMUTABILIDADE.\n"
            f"→ Ação CORRETA: Use a ferramenta '{suggestion}' para edições cirúrgicas.\n"
            f"→ Regra de Ouro: Check (list_dir) -> Read (read_file) -> Edit ({suggestion})."
        )
        print(error_msg, file=sys.stderr)
        return False, error_msg
    
    return True, "Operação segura."

import json

SESSION_READS_PATH = Path("temp_/.session_reads.json")

def register_read(file_path: str):
    """Registra que um arquivo foi lido na sessão atual."""
    SESSION_READS_PATH.parent.mkdir(parents=True, exist_ok=True)
    reads = []
    if SESSION_READS_PATH.exists():
        try:
            with open(SESSION_READS_PATH, 'r') as f:
                reads = json.load(f)
        except:
            reads = []
    
    abs_path = str(Path(file_path).resolve())
    if abs_path not in reads:
        reads.append(abs_path)
        with open(SESSION_READS_PATH, 'w') as f:
            json.dump(reads, f)

def validate_edit_op(file_path: str, action: str = 'replace'):
    """
    Valida se uma operação de edição possui contexto prévio.
    Regra: 'replace' exige 'read_file' na mesma sessão.
    """
    abs_path = str(Path(file_path).resolve())
    
    # Isenção para novos arquivos
    if not Path(file_path).exists():
        return True, "Arquivo novo."

    # Verifica histórico de leitura
    reads = []
    if SESSION_READS_PATH.exists():
        try:
            with open(SESSION_READS_PATH, 'r') as f:
                reads = json.load(f)
        except:
            pass

    if abs_path not in reads:
        error_msg = (
            f"🚫 BLOQUEIO DE GOVERNANÇA (GUARDRAIL V2.0):\n"
            f"Risco de EDIÇÃO CEGA no arquivo: '{file_path}'\n"
            f"→ O agente tentou '{action}' sem executar uma leitura prévia.\n"
            f"→ Fluxo Obrigatório: list_dir -> read_file -> replace.\n"
            f"→ Por favor, leia o arquivo antes de tentar editá-lo."
        )
        print(error_msg, file=sys.stderr)
        return False, error_msg

    return True, "Contexto validado."

def validate_read_op(file_path: str, start_line: int = None, end_line: int = None):
    """
    Valida se uma operação de leitura é eficiente (Economia de Contexto).
    
    Regra: Arquivos > 200 linhas EXIGEM leitura cirúrgica (start_line/end_line).
    """
    abs_path = Path(file_path).resolve()
    if not abs_path.exists():
        return True, "Arquivo novo (leitura ignorada)."

    try:
        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f)
        
        if line_count > 200 and start_line is None:
            error_msg = (
                f"⚠️ ALERTA DE EFICIÊNCIA DE CONTEXTO (GUARDRAIL V2.0):\n"
                f"O arquivo '{file_path}' possui {line_count} linhas.\n"
                f"→ Leituras integrais de arquivos grandes são proibidas para economizar tokens.\n"
                f"→ Ação CORRETA: Use parâmetros 'start_line' e 'end_line' para leitura cirúrgica."
            )
            print(error_msg, file=sys.stderr)
            return False, error_msg
            
    except Exception as e:
        return True, f"Erro ao validar leitura (ignorado): {e}"
        
    return True, "Operação eficiente."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python guardrail.py <caminho_do_arquivo> [acao] [start_line] [end_line]")
        sys.exit(1)
        
    path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else 'write_file'
    
    # Detecção de ação de leitura
    if action in ['read_file', 'view_file']:
        start = int(sys.argv[3]) if len(sys.argv) > 3 else None
        end = int(sys.argv[4]) if len(sys.argv) > 4 else None
        success, msg = validate_read_op(path, start, end)
        if success:
            register_read(path) # Registra leitura bem sucedida
    elif action in ['replace', 'multi_replace', 'replace_file_content', 'multi_replace_file_content']:
        success, msg = validate_edit_op(path, action)
    else:
        success, msg = validate_write_op(path, action)
        
    if not success:
        # Cria um Audit Gate para travar o sistema em caso de violação
        with open(".audit_gate", "w", encoding="utf-8") as f:
            f.write(f"Violação de Guardrail: {msg}")
        sys.exit(1)
    
    print(msg)
    sys.exit(0)
