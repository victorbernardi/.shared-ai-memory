---
id: 'stout-init-v2'
name: 'stout-init V2.0 (Modular Scaffolding)'
description: 'Inicializa projetos com arquitetura modular, permitindo a injeção de addons (como CDD) e governança Stout.'
level: 3
---

# 🚀 SKILL: STOUT-INIT V2.0 — Scaffolding Modular de Alta Maturidade

## Propósito
Garantir que todo novo projeto nasça com uma base técnica sólida, governança clara e arquitetura expansível via Addons.

---

## 🛠️ Padrão Universal de Encoding (Corta o mal pela raiz)
Todo script Python gerado por esta skill ou seus addons DEVE conter o seguinte cabeçalho para garantir compatibilidade total no Windows:

```python
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

## 🛠️ Pipeline de Execução (4 Fases)

### Phase 1: Discovery & Configuration
1. **Coleta de Metadados:** Nome, Domínio, Objetivo, KPI, Stack.
2. **Seleção de Addons:** Pergunte ao usuário: "Quais addons deseja injetar? [ ] cdd (Recomendado), [ ] outros..."

### Phase 2: Core Scaffolding
Crie a estrutura base física: `src/`, `data/`, `docs/`, `tests/`, `notes/`.
Arquivos Base: `GEMINI.md`, `ANTIGRAVITY.md`, `README.md`, `.env.example`, `.gitignore`.

### Phase 3: Addon Injection (Orquestração Declarativa)
Para cada addon selecionado, leia o `ADDON.md` e execute as instruções de instalação e costura (Stitching).

### Phase 4: Finalization & Quality
1. **Sanitização:** Execute obrigatoriamente o script de auto-fix:
   `python C:\Users\victor.bernardi\.shared-ai-memory\scripts\markdown_auto_fixer_v1.py .`
2. **Manifesto:** Gere um `stout-manifest.json` com os metadados.

---

## Regras de Ouro
1. **Modularidade Total:** O orchestrator nunca deve ter lógica específica de um addon.
2. **Qualidade First:** Nenhum projeto é entregue sem passar pelo `markdown_auto_fixer_v1.py`.
3. **UTF-8 Mandatório:** Todos os arquivos DEVEM ser salvos em UTF-8 sem BOM.
