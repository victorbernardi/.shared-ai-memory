# Docs Active/Legacy Automation — Design

**Data:** 2026-05-07  
**Status:** Aprovado

---

## Objetivo

Automatizar a promoção e arquivamento de projetos em `~/.shared-ai-memory/docs/` baseado em atividade recente. Projetos sem modificação há 7+ dias vão para `legacy/`. Projetos modificados nos últimos 7 dias ficam (ou voltam) para `active/`.

---

## Estrutura de Diretórios

```
~/.shared-ai-memory/docs/
  active/                    ← projetos ativos
    NotebookLM/
      plans/                 ← filtrado pelo cleaner
      specs/                 ← filtrado pelo cleaner
      walkthroughs/          ← bypass (não influencia data de atividade)
      decisions/             ← bypass
      business/              ← bypass
    ecosystem-reorganization/
  legacy/                    ← projetos inativos
    context-agent/
    cortex/
  decisions/                 ← bypass global (raiz de docs)
  walkthroughs/              ← bypass global
  business/                  ← bypass global
```

---

## Regras

### Arquivamento (active → legacy)
- Varrer todas as pastas em `docs/active/`
- Para cada projeto: calcular data de modificação mais recente de qualquer arquivo, **excluindo** subpastas de bypass (`walkthroughs/`, `decisions/`, `business/`)
- Se data mais recente < 7 dias atrás → mover pasta inteira para `docs/legacy/`

### Reativação (legacy → active)
- Varrer todas as pastas em `docs/legacy/`
- Mesma lógica: se qualquer arquivo (excluindo bypass) foi modificado nos últimos 7 dias → mover para `docs/active/`

### Bypass
- Subpastas `walkthroughs/`, `decisions/`, `business/` dentro de qualquer projeto **não contam** para cálculo de data de atividade
- Seu conteúdo passa direto para o cleaner sem filtragem
- Pastas bypass na raiz de `docs/` nunca são arquivadas

### Projetos sem classificação
- Pastas na raiz de `docs/` que não estão em `active/` nem `legacy/` e não são bypass são tratadas como `active/` implicitamente — o script as move para `docs/active/` na primeira execução

---

## Implementação

### Onde vive o código

Novo comando `archive` adicionado ao `context_manager.py` existente em:
`~/.shared-ai-memory/skills/context-agent/scripts/context_manager.py`

Lógica de arquivamento extraída em módulo separado:
`~/.shared-ai-memory/skills/context-agent/scripts/docs_archiver.py`

### Interface

```bash
python context_manager.py archive
```

Output:
```
→ active/NotebookLM          (última modificação: 2026-05-06)
← legacy/cortex              (sem modificação há 14 dias)
→ active/ecosystem-reorganization (última modificação: 2026-05-07)

3 projetos verificados. 1 arquivado, 1 reativado.
```

### Integração com hooks

O hook de fim de sessão do context-agent chama `context_manager.py archive` automaticamente. Também pode ser chamado manualmente a qualquer momento.

---

## Constantes

```python
BYPASS_DIRS = {"decisions", "walkthroughs", "business"}
INACTIVE_DAYS = 7
DOCS_ROOT = USER_PROFILE / ".shared-ai-memory" / "docs"
ACTIVE_DIR = DOCS_ROOT / "active"
LEGACY_DIR = DOCS_ROOT / "legacy"
DOCS_ROOT_BYPASS = BYPASS_DIRS  # pastas na raiz de docs que nunca são arquivadas
```

---

## Casos de borda

- **Colisão de nomes:** projeto com mesmo nome em `active/` e `legacy/` → impossível pela lógica (um move o outro), mas se ocorrer: não mover e reportar erro
- **Projeto vazio:** sem arquivos além de bypass → tratar como inativo (ir para legacy)
- **Pasta raiz bypass:** `docs/decisions/`, `docs/walkthroughs/`, `docs/business/` nunca são tocadas
- **Projetos não classificados:** movidos para `active/` na primeira execução
