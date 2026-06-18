import sys
from pathlib import Path

# Adicionar scripts ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from active_context import sync_to_memory
from config import MEMORY_MD_PATH, ACTIVE_CONTEXT_PATH

def test_no_legacy_user_in_header():
    # 1. Garantir que o ACTIVE_CONTEXT existe
    if not ACTIVE_CONTEXT_PATH.exists():
        ACTIVE_CONTEXT_PATH.write_text("# Test Context", encoding="utf-8")
    
    # 2. Executar sync
    sync_to_memory()
    
    # 3. Validar conteúdo
    content = MEMORY_MD_PATH.read_text(encoding="utf-8")
    
    print(f"DEBUG: Header detectado: {content.splitlines()[0]}")
    
    if "Users\\renat" in content:
        print("FAIL: Path legado 'renat' ainda presente no header.")
        sys.exit(1)
    else:
        print("PASS: Path legado removido com sucesso.")
        sys.exit(0)

if __name__ == "__main__":
    test_no_legacy_user_in_header()
