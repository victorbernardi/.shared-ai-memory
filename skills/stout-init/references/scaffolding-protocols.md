---
id: 'stout-init'
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

### Phase 2: Core Scaffolding (ICM)

Crie a estrutura ICM usando os templates de `../_shared-icm-templates/`:

```
<projeto>/
  CLAUDE.md          ← Layer 0: copiar de CLAUDE.md.template e personalizar
  AGENTS.md          ← ponteiro fino: copiar de AGENTS.md.template
  CONTEXT.md         ← Layer 1 pipeline: copiar de CONTEXT.pipeline.md e preencher estágios
  00_research/
    CONTEXT.md       ← copiar de CONTEXT.00_research.md
    references/
  <NN>_<estagio>/    ← um diretório por estágio operacional (ex: 01_extrair/)
    CONTEXT.md       ← copiar de CONTEXT.stage.md e preencher as 8 seções
    output/
    scripts/
  shared/            ← scripts reutilizados entre estágios (Layer 3)
  _config/           ← preenchido pelo addon CDD (se selecionado)
  tests/             ← cobertura cross-cutting
  .gitignore
  .env.example
```

**NÃO gerar** `GEMINI.md`, `ANTIGRAVITY.md` nem junction `docs/`.

**Confirmar lista de estágios com o operador** antes de criar os diretórios `NN_<estagio>/`.

**Bootstrap Python/uv (obrigatório para projetos Python):**

1. Criar `requirements.txt` com as dependências do projeto (ou `pyproject.toml` se build system).
2. Criar `.venv` isolado:

```powershell
cd <raiz-do-projeto>
uv venv --python 3.12
uv pip install -r requirements.txt
```

1. Validar:

```powershell
uv run python -c "import sys; print(f'Python {sys.version[:5]} OK')"
```

**NÃO assumir** que o Anaconda está disponível. Todo projeto nasce com `uv` como runtime.

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
