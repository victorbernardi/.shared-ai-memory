import sys
from pathlib import Path

def encode_claude_path(path_str):
    # Simula o comportamento do Claude Code para codificar diretórios
    # Substitui :\ e \ por -
    return path_str.replace(":\\", "--").replace("\\", "-").replace(":", "--").replace("/", "-")

def test_encoding():
    # Caso 1: Raiz de Inova
    p1 = r"C:\Projetos\Inova"
    # Esperado: C--Projetos-Inova (conforme listagem real vista no diretório .claude/projects)
    res1 = encode_claude_path(p1)
    print(f"DEBUG: {p1} -> {res1}")
    assert res1 == "C--Projetos-Inova"
    
    # Caso 2: Projeto aninhado
    p2 = r"C:\Projetos\Inova\projects\Historico-de-Vendas"
    res2 = encode_claude_path(p2)
    print(f"DEBUG: {p2} -> {res2}")
    # O Claude costuma codificar o path absoluto
    assert res2 == "C--Projetos-Inova-projects-Historico-de-Vendas"

if __name__ == "__main__":
    try:
        test_encoding()
        print("PASS: Codificação do Claude validada.")
    except AssertionError as e:
        print("FAIL: Codificação divergente.")
        sys.exit(1)
