import os
from pathlib import Path

def reproduce_real_fail():
    test_file = Path("scripts/test_fail.md")
    original_text = "animações rápidas e corações ágeis"
    
    print(f"--- SIMULANDO CAUSA RAIZ (UTF-8 lido como CP1252) ---")
    
    try:
        # 1. Alguém escreve certo (UTF-8)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(original_text)
            
        # 2. O Script de Promoção lê SEM especificar encoding (assumindo CP1252 no Windows)
        # Note: encoding="cp1252" is the default for open() on many Windows systems.
        with open(test_file, "r", encoding="cp1252") as f:
            corrupted_text = f.read()
            
        print(f"Texto corrompido na leitura: {corrupted_text}")
        
        # 3. O Script de Promoção escreve esse lixo de volta (Mojibake gerado)
        if "Ã§" in corrupted_text or "Ã¡" in corrupted_text:
            print("[SUCCESS] Causa raiz confirmada! O Mojibake foi gerado.")
        else:
            print("[FAIL] Não foi possível simular a corrupção conforme esperado.")
            
    finally:
        if test_file.exists():
            os.remove(test_file)

if __name__ == "__main__":
    reproduce_real_fail()
