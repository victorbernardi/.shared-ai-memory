# SEO_GE Interactive Scanner Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Criar um scanner interativo e autônomo para validação de grupos econômicos, integrando múltiplos elos de solda e suporte híbrido a dados (Cache/Fabric).

**Architecture:** 
- Script modular `scripts/seo_ge_scanner.py` com separação entre I/O e lógica de decisão.
- Implementação de um Score de Confiança Multidimensional para veredictos automáticos.
- Integração nativa com `negative_welds.json` e `expert_welds.json`.

**Tech Stack:** Python 3.x, Pandas, NetworkX, JSON.

---

### Task 1: Boilerplate e Inicialização
**Files:**
- Create: `scripts/seo_ge_scanner.py`

**Step 1: Criar a estrutura básica do script com suporte a UTF-8 e parsing de argumentos.**
```python
import sys
import os
import json
import pandas as pd
import argparse

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="SEO_GE Interactive Scanner v1.0")
    parser.add_argument("--busca", help="Termo de busca (Nome ou CNPJ)")
    parser.add_argument("--mode", choices=['cache', 'fabric'], default='cache')
    parser.add_argument("--auto", action='store_true', help="Modo Autônomo para Agente AI")
    args = parser.parse_args()
    print("SEO_GE Scanner Inicializado.")

if __name__ == "__main__":
    main()
```
**Step 2: Verificar execução inicial.**
Run: `python scripts/seo_ge_scanner.py`
Expected: "SEO_GE Scanner Inicializado."

---

### Task 2: Lógica de Carregamento Híbrido
**Files:**
- Modify: `scripts/seo_ge_scanner.py`

**Step 1: Implementar `get_motor_status()` e `load_master_data()`.**
O script deve ler o `GEMINI.md` para validar o status e carregar o `dataset_ouro_v11_7.xlsx`.

---

### Task 3: Menu Interativo e Seleção
**Files:**
- Modify: `scripts/seo_ge_scanner.py`

**Step 1: Implementar o fluxo de exibição de integrantes do grupo e lista de sugestões preditivas.**
Uso da lógica do `seo_ge_diagnostic.py` para listar potenciais vizinhos com números (1, 2, 3...).

---

### Task 4: Motor de Veredicto Multidimensional
**Files:**
- Modify: `scripts/seo_ge_scanner.py`

**Step 1: Implementar `calculate_verdict_score(id_a, id_b)`.**
Comparar:
- CEP (Exato)
- Endereço (Fuzzy)
- Email (Domínio corporativo)
- Sobrenome (Extração de DNA)
- Telefone (Limpo)

---

### Task 5: Persistência e Modo Autônomo
**Files:**
- Modify: `scripts/seo_ge_scanner.py`

**Step 1: Implementar a gravação automática em `negative_welds.json` ou `expert_welds.json` quando o modo `--auto` for detectado.**

---

### Task 6: Verificação Final
**Step 1: Rodar teste real com o grupo RIVELLI em modo interativo.**
**Step 2: Rodar teste real com o grupo JOSE RONALDO em modo `--auto`.**
