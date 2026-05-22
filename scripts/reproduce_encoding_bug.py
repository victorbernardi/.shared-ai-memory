import os
from pathlib import Path

def reproduce():
    test_file = Path("scripts/test_mojibake.md")
    original_text = "animações rápidas e corações ágeis"
    
    print(f"--- REPRODUÇÃO DE BUG (MOJIBAKE) ---")
    print(f"Original: {original_text}")

    # SIMULANDO O BUG: Escrita sem encoding (assumindo padrão do sistema Windows CP1252)
    try:
        with open(test_file, "w") as f:
            f.write(original_text)
        
        # Leitura simulando o processo falho
        with open(test_file, "r") as f:
            read_text = f.read()
        
        print(f"Lido (Bug): {read_text}")
        
        if read_text != original_text:
            print("[FAIL] Bug reproduzido! O texto foi corrompido.")
        else:
            print("[PASS] O sistema não corrompeu o texto automaticamente (ambiente seguro?).")
            
    finally:
        if test_file.exists():
            os.remove(test_file)

def vaccine_test():
    test_file = Path("scripts/test_vaccine.md")
    original_text = "animações rápidas e corações ágeis"
    
    print(f"\n--- TESTE DA VACINA (UTF-8 EXPLÍCITO) ---")
    
    try:
        # APLICAÇÃO DA VACINA: Escrita com UTF-8 explícito
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(original_text)
            
        # Leitura com UTF-8 explícito
        with open(test_file, "r", encoding="utf-8") as f:
            read_text = f.read()
            
        print(f"Lido (Vacina): {read_text}")
        
        if read_text == original_text:
            print("[SUCCESS] Vacina validada! Caracteres preservados.")
        else:
            print("[FAIL] Erro inesperado na vacina.")
            
    finally:
        if test_file.exists():
            os.remove(test_file)

if __name__ == "__main__":
    reproduce()
    vaccine_test()
