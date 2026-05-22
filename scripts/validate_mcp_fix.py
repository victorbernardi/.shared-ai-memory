import subprocess
import sys
import importlib

def test_mcp_integrity():
    print("--- Iniciando Validação Stout (TDD Post-Fix) ---")
    
    # 1. Verificar colisão de pacotes
    print("[1/3] Verificando colisão de pacotes...")
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    if "notebooklm-mcp-server" in result.stdout:
        print("FALHA: Pacote conflitante 'notebooklm-mcp-server' ainda presente.")
        return False
    print("OK: Sem pacotes conflitantes.")

    # 2. Verificar importação da classe vital
    print("[2/3] Verificando importação de NotebookLMFastMCP...")
    try:
        # Forçar reload do módulo para garantir que estamos testando o estado atual
        import notebooklm_mcp.server
        importlib.reload(notebooklm_mcp.server)
        from notebooklm_mcp.server import NotebookLMFastMCP
        print("OK: Classe NotebookLMFastMCP importada com sucesso.")
    except ImportError as e:
        print(f"FALHA: Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"FALHA: Erro inesperado: {e}")
        return False

    # 3. Verificar execução do CLI
    print("[3/3] Verificando execução do comando help...")
    result = subprocess.run(["notebooklm-mcp", "--help"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FALHA: CLI retornou erro {result.returncode}")
        return False
    print("OK: CLI funcional.")

    print("\nVERIFICAÇÃO CONCLUÍDA: AMBIENTE ÍNTEGRO.")
    return True

if __name__ == "__main__":
    if not test_mcp_integrity():
        sys.exit(1)
