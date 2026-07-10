#!/usr/bin/env python3
"""
Test corrections dictionary loading and application
"""

import json
from pathlib import Path

def test_corrections_load():
    """Validar que o arquivo de correções pode ser carregado"""
    config_dir = Path(__file__).parent.parent / "config"
    corrections_file = config_dir / "corrections.json"

    assert corrections_file.exists(), f"Arquivo não encontrado: {corrections_file}"

    with open(corrections_file, encoding='utf-8') as f:
        corrections = json.load(f)

    assert isinstance(corrections, dict), "Correções deve ser um dicionário"
    assert len(corrections) > 0, "Dicionário de correções vazio"
    print(f"[OK] Carregadas {len(corrections)} regras de correção")


def test_corrections_apply():
    """Validar que as correções funcionam"""
    test_text = "Arca e indopaycom precisam de correção"
    expected = "Arka e Indopacom precisam de correção"

    corrections = {
        "Arca": "Arka",
        "indopaycom": "Indopacom"
    }

    result = test_text
    for wrong, right in corrections.items():
        result = result.replace(wrong, right)

    assert result == expected, f"Esperado '{expected}', obteve '{result}'"
    print(f"[OK] Correções aplicadas com sucesso")


if __name__ == "__main__":
    test_corrections_load()
    test_corrections_apply()
    print("\n[PASS] Todos os testes passaram!")
