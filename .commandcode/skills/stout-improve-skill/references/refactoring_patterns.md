# Padrões de Refatoração Stout (Elite V1.2.0)

Este documento contém trechos de código e padrões arquiteturais que devem ser seguidos durante as operações da `stout-improve-skill`.

## 1. Concorrência e Locks (Escrita em JSON)

Sempre que uma skill escrever em um arquivo compartilhado, utilize o padrão de Lock:

```python
import threading
from pathlib import Path

_file_lock = threading.Lock()

def atomic_write(path: Path, data: dict):
    with _file_lock:
        temp_file = path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_file.replace(path)
```

## 2. Versionamento Semântico Robusto

Substitua `version.split('.')` pelo uso da biblioteca `packaging`.

```python
from packaging import version

def is_upgrade_valid(current: str, proposed: str) -> bool:
    return version.parse(proposed) > version.parse(current)
```

## 3. Otimização de Busca O(1)

Evite iterar em listas para encontrar objetos se o ID for conhecido.

```python
# ANTES (O(n))
skill = next((s for s in registry["skills"] if s["name"] == name), None)

# DEPOIS (O(1))
# Mantenha um mapeamento durante o load_registry
skills_map = {s["name"]: s for s in registry["skills"]}
skill = skills_map.get(name)
```

## 4. Tratamento de Erros Resiliente

Sempre capture exceções específicas e forneça contexto.

```python
try:
    source = filepath.read_text(encoding="utf-8")
except PermissionError:
    print(f"[ERRO] Sem permissão para ler {filepath.name}")
except FileNotFoundError:
    print(f"[ERRO] Arquivo não encontrado: {filepath.name}")
```

## 5. Frontmatter Ouro (SKILL.md)

Padrão obrigatório para conformidade de elite:

```yaml
---
name: stout-exemplo
description: "Use quando... NÃO use para..."
tier: 3
category: meta-governance
source: custom
date_added: '2026-05-15'
author: Victor
---
```