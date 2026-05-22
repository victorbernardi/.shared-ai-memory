# Spec Técnica — stout_promote v3.0

**Tipo:** spec  
**Branch:** `fix/stout-promote-antigravity-brain-path`  
**Data:** 2026-05-20  
**Versão:** v1  
**Status:** Aprovada para execução

---

## 1. Objetivo

Evoluir o `stout_promote.py` (v2.2 → v3.0) para que ele:

1. Detecte e promova **artefatos** de **todas as sessões** do projeto (não só a mais recente)
2. Adote **nomenclatura determinística baseada no nome da branch Git** como scope
3. Aplique **versionamento explícito** (`_v1`, `_v2`, ...) desde o primeiro arquivo
4. Cubra o tipo de documento **`spec.md`** que hoje não é mapeado
5. Classifique **artefatos** pelo **tipo declarado no conteúdo**, com fallback por nome de arquivo, não pela origem da sessão
6. Gere um **log estruturado JSON** de todas as promoções para rastreabilidade
7. Crie o script `post_approve.py` para **promoção automática** após aprovação de plano

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **artefato** | Arquivo `.md` gerado por IA no brain da sessão (`implementation_plan.md`, `spec.md`, `walkthrough.md`) |
| **documento** | Arquivo `.md` promovido e persistido na pasta `docs/` do projeto |

---

## 2. Contexto e Diagnóstico

### 2.1 Ambientes Antigravity (mapeamento empírico)

| Pasta | Descrição | Tem artefatos `.md`? | Ação do stout_promote |
|-------|-----------|----------------------|----------------------|
| `~/.gemini/antigravity-cli/brain/<id>/` | CLI — sessões interativas | ✅ Sim, na raiz | Promover |
| `~/.gemini/antigravity/brain/<id>/` | IDE/2.0 — editor integrado | ❌ Não (salva direto em `docs/`) | Ignorar |
| `~/.gemini/antigravity-ide/brain/<id>/` | IDE standalone | ❌ Não | Ignorar |
| `~/.shared-ai-memory/brain/<id>/artifacts/` | Legado | ✅ Sim, em subpasta `artifacts/` | Promover (fallback) |

### 2.2 Gaps identificados (v2.2)

| ID | Gap | Severidade |
|----|-----|-----------|
| G1 | `implementation_plan.md.resolved` — arquivo inexistente promovido | Baixa |
| G2 | Somente 1 sessão promovida por execução | Alta |
| G3 | Tipo de documento inferido pela origem, não pelo conteúdo | Média |
| G4 | Scope do nome gerado pelo LLM (não-determinístico) | Alta |
| G5 | Sanitização de nome incompleta (parênteses no slug) | Média |
| G6 | Primeiro arquivo sem `_v1` explícito (inconsistência) | Baixa |
| G7 | Claude memory varre todos os arquivos sem filtro de relevância | Média |
| G8 | Sem log de auditoria de promoções | Média |

---

## 3. Especificação de Comportamento

### 3.1 Formato de nomenclatura definitivo

```
{tipo}_{YYYY-MM-DD}_{branch-slug}_v{N}.md
```

**Componentes:**

| Campo | Regra |
|-------|-------|
| `{tipo}` | Detectado do conteúdo: `plan`, `spec`, `walkthrough`, `concept` |
| `{YYYY-MM-DD}` | Data de modificação do artefato de origem (não de promoção) |
| `{branch-slug}` | `git branch --show-current` com `/` → `-` e sem caracteres especiais. Máx 60 chars. Fallback: nome da pasta do projeto |
| `_v{N}` | Sempre explícito a partir de `v1`. Incrementa apenas se hash do conteúdo for diferente do arquivo mais recente |

**Exemplos:**
```
docs/plans/plan_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md
docs/plans/plan_2026-05-20_fix-stout-promote-antigravity-brain-path_v2.md   ← replaneio
docs/specs/spec_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md
docs/walkthroughs/walkthrough_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md
```

### 3.2 Detecção de tipo pelo conteúdo

Precedência estrita (CON-002):

| Prioridade | Mecanismo | Condição |
|-----------|-----------|----------|
| **1 — Conteúdo** | Inspeciona as primeiras 5 linhas do artefato buscando `TYPE_MARKERS` | Retorna o tipo assim que encontrar match |
| **2 — Nome de arquivo** | Usa o nome do arquivo de origem como hint | Somente se nenhum marcador for encontrado no conteúdo |
| **3 — Fallback** | Classifica como `concept` | Somente se prioridade 1 e 2 falharem |

```python
TYPE_MARKERS = {
    "plan":        ["tipo: plan", "type: plan", "# plano de implementação", "# implementation plan"],
    "spec":        ["tipo: spec", "type: spec", "# spec técnica", "# spec"],
    "walkthrough": ["tipo: walkthrough", "type: walkthrough", "# walkthrough"],
}

FILENAME_HINTS = {
    "implementation_plan": "plan",
    "spec":                 "spec",
    "walkthrough":          "walkthrough",
}
# Fallback final: "concept"
```

> **Nota:** Os marcadores de conteúdo devem ser verificados em lowercase e com strip de espaços.

### 3.3 Mapeamento de artefatos (destinos)

| Artefato de origem | Tipo detectado | Destino |
|-------------------|----------------|---------|
| `implementation_plan.md` | `plan` | `docs/plans/` |
| `spec.md` | `spec` | `docs/specs/` |
| `walkthrough.md` | `walkthrough` | `docs/walkthroughs/` |
| `task.md` | — | **Não promovido** |
| `implementation_plan.md.resolved` | — | **Ignorado** |
| `plan_*.md` (Gemini TMP) | `plan` | `docs/plans/` |
| `*.md` (Claude memory) | Detectado pelo conteúdo | Destino conforme tipo |

### 3.4 Sessões múltiplas

`get_all_brain_sessions()` substitui `get_latest_brain_session()`:
- Retorna **todas** as sessões onde `is_session_for_current_project()` retorna `True`
- O match usa **`PROJECT_ROOT.name` E `str(PROJECT_ROOT).lower()`** (path absoluto) para evitar colisões entre projetos com o mesmo nome de pasta em diretórios distintos (CON-004)
- Sessões ordenadas por data de modificação descendente
- Cada sessão é promovida independentemente
- O log de promoções impede duplicatas idênticas

### 3.5 Log de promoções (`docs/.promote_log.json`)

```json
[
  {
    "promoted_at": "2026-05-20T14:09:00",
    "session_id": "0d8c4d59-daff-4788-8607-6639d0ec7e02",
    "origin": "antigravity-cli",
    "branch": "fix/stout-promote-antigravity-brain-path",
    "files": [
      {
        "src": "implementation_plan.md",
        "dest": "docs/plans/plan_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md",
        "content_hash": "sha256:abc123..."
      }
    ]
  }
]
```

**Regra de deduplicação (CON-001):** antes de promover, calcula SHA-256 do arquivo de origem e compara com o `content_hash` de **qualquer registro anterior** no log para aquele `src` (campo `"src"`). Pula se o hash já constar em **qualquer** entrada do log — não apenas na mais recente. Isso garante que um artefato revertido ao conteúdo original não gere uma versão nova desnecessária.

### 3.6 `post_approve.py` — promoção automática

Script a ser executado pelo agente **imediatamente após aprovação do plano** pelo usuário:

```bash
python src/tools/post_approve.py           # promoção + commit
python src/tools/post_approve.py --dry-run # lista candidatos sem copiar nem commitar
```

Comportamento (modo padrão):
1. Chama `promote_artifacts()` do `stout_promote.py`
2. Executa `git add docs/`
3. Executa `git commit -m "docs: Promote {tipo}_{branch-slug}_v{N}"`
4. Imprime o path exato dos **documentos** promovidos

Comportamento (`--dry-run`):
- Lista os artefatos que seriam promovidos e seus destinos previstos
- Não copia arquivos
- Não cria commit
- Retorna exit code 0

**O agente deve incluir o path promovido na resposta ao usuário após a aprovação.**

### 3.7 Sanitização de slug

```python
import re

def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower()
    text = text.replace("/", "-").replace("\\", "-")
    text = re.sub(r"[^a-z0-9\-_]", "", text)
    text = re.sub(r"-{2,}", "-", text)   # colapsa hífens duplos
    return text[:max_len].strip("-")
```

---

## 4. Plano de Higiene (Arquivos Existentes)

Antes de fechar a branch, normalizar os arquivos gerados nesta sessão:

```
MANTER e RENOMEAR:
  docs/plans/plan_2026-05-20_03_potencial-(m3).md
    → docs/plans/plan_2026-05-20_fix-stout-promote-antigravity-brain-path_v1.md

DELETAR (duplicatas sem versionamento):
  docs/plans/plan_2026-05-20_03_potencial.md
  docs/walkthroughs/walkthrough_2026-05-20_03_potencial.md
  docs/walkthroughs/walkthrough_2026-05-20_03_potencial-(m3).md

MANTER (gerado antes do padrão, nome legível, histórico):
  docs/plans/plan_v1_governanca_recencia_m3.md
  docs/specs/spec_v1_governanca_recencia_m3.md
```

---

## 5. Arquivos a Modificar / Criar

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `src/tools/stout_promote.py` | MODIFY | v2.2 → v3.0 com todos os gaps resolvidos |
| `src/tools/post_approve.py` | NEW | Wrapper de promoção automática pós-aprovação |
| `GEMINI.md` (local) | MODIFY | Instruir o agente a rodar `post_approve.py` após aprovação |
| `docs/.promote_log.json` | NEW | Gerado automaticamente pelo script |

---

## 6. Não Está no Escopo

- Modificar o comportamento do Antigravity IDE (ele já salva em `docs/` corretamente)
- Promover arquivos `.py`, `.json` ou outros formatos além de `.md`
- Integração com CI/CD ou GitHub Actions

---

## 7. Critérios de Aceitação

- [ ] `python src/tools/stout_promote.py` promove todos os **artefatos** de **todas as sessões** do projeto com nome no padrão `{tipo}_{data}_{branch-slug}_v{N}.md`
- [ ] Executar duas vezes seguidas: segunda execução retorna `0 artefatos promovidos` (sem duplicatas) — CON-006
- [ ] Modificar `implementation_plan.md` no brain e rodar novamente: gera `_v2`
- [ ] Reverter `implementation_plan.md` ao conteúdo original e rodar novamente: NÃO gera `_v3` (hash já no log) — CON-001
- [ ] Criar `spec.md` mínimo no brain, rodar `stout_promote.py`: artefato promovido para `docs/specs/` — CON-008
- [ ] `docs/.promote_log.json` existe e contém o histórico correto com SHA-256
- [ ] `python src/tools/post_approve.py` promove + commita automaticamente
- [ ] `python src/tools/post_approve.py --dry-run` lista candidatos sem modificar `docs/` nem criar commit — CON-003
- [ ] Branch `fix/stout-promote-antigravity-brain-path` sem arquivos sujos (`git status` limpo)
