# Diagnóstico de Falhas no Fluxo Wiki-LLM — v2 (com evidências)

## Pipeline Mapeado

```
Sessão Claude/Antigravity
    │
    ▼
context_manager.py save ──(step 10)──► wiki-stage.sh ──► vault/_raw/
    │                                                           │
    │ cria: session-NNN.md, ACTIVE_CONTEXT.md, MEMORY.md        │
    │ context.db, git commit + push                             ▼
    │                                                    /wiki-ingest (MANUAL)
    │                                                    raw mode: _raw/ → wiki pages
    ▼
    "Após o save, execute /wiki-ingest manualmente"
```

---

## Evidências Concretas Coletadas

### Estado real do sistema:

| Métrica | Valor |
|---------|-------|
| Sessões totais em `sessions/` | 392 |
| Sessões com formato `session-NNN-*` (sequencial) | 51 |
| Sessões com formato `session-YYYYMMDD-*` (timestamp, Claude) | 267 |
| Arquivos em `_raw/` aguardando ingest | **116 arquivos** (370 KB) |
| `cleaned/` (deveria estar vazio após wiki-stage) | Vazio (só `.gitkeep`) |
| Última modificação do `_raw/` mais antigo | 2026-05-06 (15 dias) |
| ACTIVE_CONTEXT.md — linhas | 149 (truncado no limite de 150) |
| `wiki-stage.sh` — depende de `bash.exe` PortableGit | PATH `C:/Users/victor.bernardi/PortableGit/bin/bash.exe` |
| `wiki-stage.sh` — `set -euo pipefail` | ✅ Aborta em erro |

---

## 🔴 CRÍTICAS — Quebram Silenciosamente

### 1. 🔴 **116 arquivos parados no `_raw/` — pipeline estagnado há 15 dias**

**Evidência:** `_raw/` contém 116 arquivos `.md`. O mais antigo (`0001-resilient-date-conversion-historical-sync.md`) é de **2026-05-06** — 15 dias atrás. Nenhum `/wiki-ingest` raw mode foi executado desde então.

**Causa:** O `/wiki-ingest` é manual por design. O wiki-stage.sh roda automático no `context_manager.py save`, mas ninguém executa o ingest. O arquivo `wiki-stage.sh` imprime `"[wiki-stage] Concluído. Execute /wiki-ingest para sincronizar o vault."` — mas isso vai para stdout do subprocess e é printado no console do context_manager, perdido entre outras mensagens.

**Arquivos afetados:** 116 arquivos, incluindo duplicatas (`_v2.md`, `_v3.md`), walkthroughs, specs, plans, concepts, e dados de negócio (orçamentos, relatórios, segmentações). Conteúdo inclui `v2_insight_engineering.md` (18 KB), `bup-auto-1-extrair-orcamentos-fabric.md` (16 KB), `seo-ge-scanner-v2.md` (15 KB).

**Impacto:** Conhecimento de 15 dias de sessões nunca chegou ao vault Obsidian. O `_raw/` é um cemitério de conhecimento não-destilado.

---

### 2. 🔴 **Duplicação massiva no ACTIVE_CONTEXT.md → truncamento silencioso**

**Evidência:** O arquivo está com **149 linhas** (limite é 150), e a última linha é o aviso de truncamento: `*[Contexto truncado — execute python context_manager.py maintain para otimizar]*`. Apesar do ACTIVE_CONTEXT.md ter 60 tarefas pendentes listadas, muitas são **quase-duplicatas** que escapam da deduplicação:

```
"Rodar /setup-matt-pocock-skills em projetos que precisem de configuração..." (session-133)
"Rodar /setup-matt-pocock-skills em projetos que precisem de issue tracker..." (session-134)
```
```
"Implementar Skill Sandboxing (V4.6), Iniciar V5.0 Distributed CDD" (session-121)
"Iniciar V4.3: Analytics Dashboard..."                               (session-120)
"Iniciar Fase 4: Integração de Skills..."                            (session-125)
```
```
"Refinar Matriz de Ação (Pág 3) com filtros de Popularidade..."      (session-107)
"Validar Lupas com Gerente de Estoque; Adicionar Executive Summary..."(session-109)
```

**Causa:** `update_active_context()` em `active_context.py:83-94` deduplica por `t.description == pt.description` (exato). Variações de uma palavra quebram a deduplicação. O `_extract_pending_tasks()` no `session_summary.py` filtra `**Step N:` via regex mas deixa passar ruído de planos, checklists, e tarefas repetidas com wording levemente diferente entre sessões.

**Impacto:** Arquivo lotado de ruído, truncado, tarefas reais de sessões recentes podem ter sido dropadas. O aviso de truncamento está lá mas ninguém age sobre ele.

---

### 3. 🔴 **Colisão de nomenclatura de sessões: 267 sessões Claude sem número sequencial**

**Evidência:** Das 392 sessões em `sessions/`:
- 51 têm formato `session-NNN-YYYYMMDD-HHMMSS-origem-uuid8.md` (ex: `session-174-20260521-151228-antigravity-4f63d0ee.md`)
- 267 têm formato `session-YYYYMMDD-HHMMSS-claude-uuid8.md` (ex: `session-20260507-100307-claude-17af7de8.md`)

As 267 sessões Claude **não têm número sequencial**. O `get_next_session_number()` em `session_summary.py:28-38` pula nomes com segundo segmento > 4 chars (detecta como data). Correto para não colidir, mas essas sessões nunca recebem um número.

**Impacto no ACTIVE_CONTEXT.md:** Todas as referências no ACTIVE_CONTEXT.md usam `session-NNN` com 3 dígitos. As sessões Claude são invisíveis nesse sistema. Exemplo: `"(desde session-132)"` referencia uma sessão com número, mas as 267 sessões Claude não podem ser referenciadas assim.

**Impacto na busca FTS5:** `index_session()` recebe `session_number` como parâmetro. Para sessões com número sequencial, recebe int. Para sessões timestamp, o código em `reindex_all()` tenta extrair `num` do nome do arquivo e pode receber string. O `search.py:49-50` tenta `int(row[0])` para display e falha silenciosamente com `ValueError`.

---

## 🟡 ALTAS — Degradam Progressivamente

### 4. 🟡 **`cleaned/` vazio: wiki-stage.sh NÃO está funcionando como esperado**

**Evidência:** O diretório `cleaned/` contém apenas `.gitkeep` (0 bytes). O `wiki-stage.sh` tem `set -euo pipefail` (aborta em erro), mas o fluxo deveria:
1. `superpowers_cleaner.py` → processa `Stout/docs/` e `Inova/**/docs/` → gera `.md` em `cleaned/`
2. `pending_to_ar9av_raw.py` → move `cleaned/*.md` → `vault/_raw/`

Se `cleaned/` está vazio, significa que **ou o cleaner não produz nada, ou o move esvaziou**. Como `_raw/` tem 116 arquivos, a teoria mais provável é que o move funciona mas o cleaner não está encontrando nada novo para processar — os docs do Stout/Inova já foram todos processados em execuções anteriores.

**Mas o problema real é outro:** Os 116 arquivos em `_raw/` vieram de execuções passadas do wiki-stage.sh. O pipeline funciona para **docs de projeto**, mas **não processa as sessões do context-agent** (`session-NNN.md`). As sessões nunca entram no `_raw/`.

**Causa raiz:** O `wiki-stage.sh` varre `Stout/docs/` e `Inova/**/docs/` — documentação de projetos. As sessões do context-agent (`session-NNN.md`, ACTIVE_CONTEXT.md) são um **caminho de dados completamente separado** que nunca é staged para o wiki.

**Gap de arquitetura:** Existem dois fluxos de conhecimento que nunca se encontram:
- **Docs de projeto** → `wiki-stage.sh` → `_raw/` → `/wiki-ingest` → wiki
- **Sessões do context-agent** → `session-NNN.md` → **beco sem saída**

As sessões contêm decisões, tarefas, descobertas — mas nunca são ingeridas no wiki.

---

### 5. 🟡 **Hardcoded paths quebram portabilidade**

**Evidência em `wiki-stage.sh`:**
```bash
STOUT_ROOT="${STOUT_ROOT:-/c/Projetos/Stout}"
VAULT="/c/Users/victor.bernardi/Documents/wiki-compiler-vault"
CLEANED_DIR="$HOME/.shared-ai-memory/context-agent/cleaned"
```

**Evidência em `context_manager.py:140-142`:**
```python
wiki_stage = Path("C:/Projetos/Stout/wiki-compiler/wiki-stage.sh")
bash_path = Path("C:/Users/victor.bernardi/PortableGit/bin/bash.exe")
```

**Evidência em `active_context.py:sync_to_memory()`:**
```python
header = (
    "<!-- Auto-generated by context-agent. Para detalhes: "
    "python C:\\Users\\victor.bernardi\\.shared-ai-memory\\.gemini\\skills\\context-agent\\scripts\\context_manager.py load -->\n\n"
)
```

Todos os paths são absolutos com nome de usuário hardcoded. Não funcionam em nenhuma outra máquina.

---

### 6. 🟡 **repo_root do Git é frágil (5 níveis de `parent`)**

**Evidência em `context_manager.py:173`:**
```python
repo_root = Path(__file__).parent.parent.parent.parent.parent
```

Isso assume que o arquivo está em `<repo>/antigravity/skills/process-context-agent/scripts/context_manager.py`. Se a estrutura mudar (ex: skill movida para `skills/` direto), o git sync opera no diretório errado.

---

### 7. 🟡 **Sem atomicidade no save — 10+ operações de filesystem**

**Evidência em `context_manager.py:89-178`:** O `cmd_save()` executa sequencialmente:
1. parse session → 2. generate summary → 3. save session file → 4. update project registry → 5. update active context → 6. sync MEMORY.md → 7. index FTS5 → 8. git sync → 9. wiki stage

Se crashar entre os steps 3 e 5, a sessão existe no disco mas o ACTIVE_CONTEXT.md está desatualizado. Nenhum rollback.

---

### 8. 🟡 **Parse de JSONL silencioso — dados perdidos sem warning**

**Evidência em `session_parser.py:14-19`:**
```python
with open(path, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue  # silencioso
```

Linhas com JSON inválido são simplesmente puladas. Nenhum contador, nenhum log, nenhum warning. Encoding issues usam `errors="replace"` que produz caracteres garbled em vez de falhar ruidosamente.

---

## 🟢 MÉDIAS — Inconvenientes e Riscos Latentes

### 9. 🟢 **`ARCHIVE_AFTER_SESSIONS=20` muito agressivo**

Com 392 sessões e `ARCHIVE_AFTER_SESSIONS=20`, sessões com mais de 20 números de distância da atual são arquivadas. Se a sessão atual é 174, sessões anteriores a 154 vão para archive comprimido. Mas as sessões Claude (sem número) não entram nessa contagem — então o cálculo de "20 sessões atrás" está distorcido.

### 10. 🟢 **Double-processing no raw mode**

Se um arquivo em `_raw/` é processado pelo `/wiki-ingest` mas o agente crasha antes de deletar o original, na próxima execução o arquivo será reingerido, criando páginas duplicadas no vault. O `pending_to_ar9av_raw.py` tem proteção (`if dst.exists(): dst.unlink()`), mas o wiki-ingest não tem checkpoint atômico.

### 11. 🟢 DRIFT detection frágil

`check_drift()` em `active_context.py:148-155` faz strip do header `<!-- Auto-generated... -->` do MEMORY.md para comparar. Se o MEMORY.md for editado manualmente (ex: adicionar notas), o drift detection quebra.

### 12. 🟢 Nenhum health check automático

`wiki_health_check.py` existe (`scripts/wiki_health_check.py`) mas é standalone — nunca chamado pelo pipeline. Nenhuma validação de que o vault está consistente após operações.

### 13. 🟢 `brain-watcher.py` — outro ponto de entrada não-documentado

O `brain-watcher.py` monitora `~/.gemini/antigravity/brain/` por mudanças em `implementation_plan.md` e `walkthrough.md` e dispara `stout_promote.py`. Isso é um terceiro caminho de ingest não documentado no fluxo principal.

---

## Diagrama de Fluxo Real (com gaps)

```
                    ┌─────────────────────────────────────┐
                    │        Sessão Claude/Antigravity      │
                    └────────┬────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    context_manager.py   Claude JSONL   brain-watcher.py
         save              (267 files)   (monitora brain/)
              │              │              │
              ▼              │              ▼
    session-NNN.md (51)     │     stout_promote.py
    ACTIVE_CONTEXT.md       │     → promove specs/plans
    MEMORY.md               │
    context.db              │
              │              │
              ▼              │
    wiki-stage.sh            │
    (varre Stout/Inova docs) │
              │              │
              ▼              │
         cleaned/            │
              │              │
              ▼              │
         vault/_raw/ ◄───────┘ (??? como as sessões chegam aqui?)
         (116 arquivos)
              │
              ▼
    /wiki-ingest (MANUAL — NUNCA EXECUTADO)
         (raw mode)
              │
              ▼
    wiki-compiler-vault/
    (concepts/, entities/, projects/, etc.)
```

**O gap central:** As sessões do context-agent (session-NNN.md) **nunca entram no pipeline do wiki**. O `wiki-stage.sh` só varre documentação de projetos. As sessões contêm o histórico real de decisões, tarefas e descobertas — mas esse conhecimento morre em `sessions/`.

---

## Recomendações por Prioridade

### 🚨 Imediato
1. **Rodar `/wiki-ingest` raw mode** para processar os 116 arquivos acumulados
2. **Rodar `context_manager.py maintain`** para limpar o ACTIVE_CONTEXT.md truncado

### 🔧 Curto prazo
3. **Adicionar `sessions/` ao escopo do wiki-stage.sh** ou criar um script separado `session-to-raw.sh` que transforma `session-NNN.md` → `_raw/`
4. **Criar alerta de backlog** — se `_raw/` tem > N arquivos ou arquivo mais antigo > M dias, emitir warning
5. **Normalizar nomenclatura de sessões** — decidir entre NNN sequencial ou timestamp; não manter os dois
6. **Substituir paths hardcoded** por env vars ou discovery relativo (`~/.shared-ai-memory/`)

### 📋 Médio prazo
7. **Adicionar `wiki_health_check.py` ao pipeline** como step pós-save
8. **Implementar checkpoint atômico no raw mode** do wiki-ingest
9. **Deduplicação semântica no ACTIVE_CONTEXT.md** — similaridade de texto, não igualdade exata
