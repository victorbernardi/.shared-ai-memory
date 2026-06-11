# LLM Wiki — Reforma (Z Híbrido)

**Data:** 2026-04-23
**Status:** Em revisão
**Escopo:** Reformar o ecossistema wiki existente: trocar motor de compilação por Ar9av/obsidian-wiki, unificar context-agent nos 4 agentes, centralizar camada de peneira, preservar contratos externos.

---

## Problema

O wiki-compiler atual (Gemini CLI + `SCHEMA.md`, especificado em 2026-04-15) está parado por acúmulo de "sujeira" — conteúdo cru entrando por múltiplas vias sem filtragem adequada. Sintomas:

- Fragmentos de terminal, paths e comandos aparecem como tópicos do wiki
- Wikilinks órfãos ou inconsistentes entre páginas
- Páginas duplicadas com variações de nome
- Context-agent só roda consistentemente no Antigravity; OpenCode tem instalação parcial; Claude Code e Gemini CLI não estão integrados ao pipeline

Três caminhos não filtrados alimentam `raw/_pending/`: `harvest_brain.sh` (Antigravity brain), Bibliotecário via Trigger Gamma, e fragmentos NotebookLM tagged `nlm-synthesis`. Cada um tem suas próprias regras e formato, dificultando manutenção.

---

## Visão Geral — Z Híbrido

Trocar o motor, preservar os contratos externos.

- **Motor novo:** Ar9av/obsidian-wiki substitui `SCHEMA.md` + Gemini CLI como compilador
- **Contratos preservados:** `raw/_pending/` continua sendo o ponto único de entrada; `SUGESTOES-HOJE.md`, `PENDENCIAS.md`, `suggestion_ignore.md`, `AUDIT_REPORT.md` mantêm nomes e semântica; vault permanece em `Obsidian-Victor-Global/wiki/` (flat, kebab-case)
- **Peneira centralizada:** context-agent unificado vira a única camada de filtragem de input (sessões + spec/plan Superpowers)
- **Input único de agentes:** os 4 agentes (Claude Code, OpenCode, Gemini CLI, Antigravity) deixam de escrever direto no pending — passam a usar context-agent como middleware
- **Reset + rebuild:** conteúdo atual do wiki é reprocessado pela peneira nova junto com histórico de sessões/specs disponíveis

### Fluxo

```
Claude Code   ─┐
OpenCode      ─┤
Gemini CLI    ─┼──► context-agent (4 instalações, storage unificado)
Antigravity   ─┘       │
                        │
Superpowers docs ──► context-agent (cleanup spec/plan)
(docs/superpowers/)     │
                        ▼
                  raw/_pending/
                        │
                        ▼
                  Ar9av compiler + audit engine existente
                        │
                        ▼
                  Review gate (batch diff aprovado pelo usuário)
                        │
                        ▼
                  wiki/ (flat, kebab-case) — repo git dedicado
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
    CLI agents     SUGESTOES-       Auto-sync para
    (via INDEX)    HOJE.md +        NotebookLM
                   NLM research     (notebook fixo)
```

---

## Fase 1 — Unificar context-agent nos 4 agentes

**Objetivo:** context-agent funcional em todos os agentes, escrevendo numa única pasta.

| Agente | Ação |
|---|---|
| Antigravity | Ajustar `config.py` para apontar paths unificados; corrigir SKILL.md (remover referências obsoletas ao `~/.gemini/antigravity/`) |
| Gemini CLI | Compartilha skill com Antigravity — ação acima resolve |
| OpenCode | Completar instalação: adicionar `config.py`, `context_manager.py`, `session_parser.py`, `project_registry.py`, `active_context.py`, `search.py` (disponíveis no worktree `.worktrees/context-agent/`) |
| Claude Code | Instalar do zero usando worktree como base; hook `Stop` em `~/.claude/settings.json` aciona `context_manager.py save` |

**Storage unificado:** `C:\Projetos\Stout\memory\context-agent\`
- `sessions/` — saídas de todos os agentes (nome inclui origem: `session-NNN-claude.md`, etc.)
- `archive/` — sessões antigas
- `ACTIVE_CONTEXT.md`, `PROJECT_REGISTRY.md`, `context.db` (SQLite FTS5)

**Trigger:** mecanismo manual (`encerrar sessão` reconhecido pelo agente) é padrão inicial. Claude Code adiciona hook `Stop` automático. Migração para hooks em outros agentes é pós-fase (não-bloqueante).

**Entrega:** os 4 agentes gravam sessões filtradas no mesmo storage.

---

## Fase 2 — Limpeza de spec/plan do Superpowers

Novo módulo do context-agent: `superpowers_cleaner.py`.

**Escopo:** ler arquivos `.md` em `docs/superpowers/specs/` e `docs/superpowers/plans/` nas 3 instalações Superpowers (Claude Code, OpenCode, Gemini+Antigravity).

**Regras de limpeza (Layer 2):**

| Descarta | Preserva |
|---|---|
| YAML frontmatter da skill | Título e data |
| Seção "Checklist" de processo | Seção "Problema" / "Solução" |
| Placeholders (`TBD`, `TODO`, `<slug>`) | Decisões registradas |
| Referências a skills (`use X skill`) | Arquitetura, fluxos, diagramas |
| Metainformação de aprovação (`Status: Aprovado`) | Aprendizados e tradeoffs |
| Seção "Out of scope" | Seção "In scope" |

**Output:** `memory/context-agent/cleaned/spec-<slug>.md`, `plan-<slug>.md`.

**Integração:** cleaned → copia para `raw/_pending/` junto com sessões.

**Entrega:** specs/plans viram input limpo do wiki.

---

## Fase 3 — Adotar Ar9av/obsidian-wiki como motor

**Fork e adaptação** do projeto `Ar9av/obsidian-wiki` em `C:\Projetos\Stout\wiki-compiler\compiler\`.

**Adapters a criar** (`C:\Projetos\Stout\wiki-compiler\adapters\`):
- `sessions_to_pending.py` — lê de `memory/context-agent/sessions/` e copia para `raw/_pending/` conforme disparo de compile
- `cleaned_to_pending.py` — lê de `memory/context-agent/cleaned/` e copia para `raw/_pending/`

**Audit engine existente** (`C:\Projetos\Stout\wiki-compiler\audit\`) é integrado ao pipeline. Remover check de NLM (NLM deixa de ser input).

**Deprecações** (mantidas em tree, marcadas como obsoletas; remover após 2 semanas de validação):
- `harvest_brain.sh` — captura direta do Antigravity brain, substituída por context-agent
- Escrita do Bibliotecário em `raw/_pending/` via Trigger Gamma — substituída por context-agent na instalação Antigravity

**Entry point:** `run_wiki_work.sh` mantém a assinatura e orquestra: adapters → Ar9av ingest → audit → review gate → commit no vault.

**Entrega:** motor novo, mesmos contratos externos, mesmo formato de saída.

---

## Fase 4 — Reset + Rebuild

**Pré-condição:** Fases 1-3 validadas (context-agent gravando sessões limpas, Ar9av compilando raw/_pending/ corretamente em ambiente de teste).

**Passos:**

1. **Backup** completo do vault atual em `Obsidian-Victor-Global/wiki/` para `backup/wiki-pre-reforma-YYYY-MM-DD/` (fora do vault)
2. **Git init** no path do vault atual (`git init` em `Obsidian-Victor-Global/wiki/`); primeiro commit = snapshot do estado atual; criar remoto privado no GitHub
3. **Esvaziar** páginas `.md` do vault (mantém estrutura `raw/_pending/`, `suggestion_ignore.md`)
4. **Re-seed híbrido:** alimentar `raw/_pending/` com:
   - Conteúdo do backup (páginas wiki atuais)
   - Histórico de sessões em `memory/context-agent/sessions/` (das últimas 4 semanas)
   - Spec/plan limpos pela Fase 2
5. **Rodar** pipeline completo: Ar9av consolida duplicatas (merge por similaridade Jaccard ≥ 0.6), audit engine valida integridade
6. **Revisão manual** de amostra (10 páginas aleatórias + 100% das páginas técnicas críticas) antes do commit final
7. **Commit atômico** no repo dedicado do vault

**Entrega:** wiki limpo, links saudáveis, conteúdo reconsolidado pela peneira nova.

---

## Fase 5 — Wiki como input para CLIs + sync NotebookLM

### INDEX.md — ponto de entrada para agentes

Gerado pelo compiler após cada run (nunca editado à mão).

```markdown
# Wiki Index — YYYY-MM-DD
<N> páginas · <X> #tech · <Y> #negocio

## Tecnologia
- [[slug-da-pagina]] — Descrição curta da página

## Negócio
- [[slug-da-pagina]] — Descrição curta da página
```

**Integração:** cada agente referencia `INDEX.md` no seu system prompt base (`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, instructions do Antigravity). Agentes leem INDEX na inicialização e aprofundam em páginas específicas sob demanda.

### Feedback loop — sugestões persistentes + research NLM

**Mudança de comportamento:** `SUGESTOES-HOJE.md` passa a ser **acumulativo**, não sobrescrito.

```
Compile run gera sugestão nova em tópico X
  ├─► notebook_list() filtra notebooks com "estudo" no título
  ├─► cross_notebook_query([matches], "pesquisa sobre X: ...")
  ├─► resposta com citações vira sub-seção "Embasamento" da sugestão
  ├─► dedupe Jaccard 0.6 com sugestões existentes (evita repetir)
  └─► append em SUGESTOES-HOJE.md

Lifecycle da sugestão:
  - "ignorar" → suggestion_ignore.md
  - "concluído" → suggestion_ignore.md
  - caso contrário → permanece indefinidamente
```

**Formato de cada sugestão:**
```markdown
### [título] — [[página-wiki-origem]]
**Data:** YYYY-MM-DD · **Status:** ativa

[descrição curta]

#### Embasamento (via NotebookLM)
[resposta do NLM com citações]
```

**Leitura:** todos os 4 agentes (não só Bibliotecário) ganham capacidade de ler `SUGESTOES-HOJE.md` quando o usuário menciona "wiki", "sugestão", "recomenda". Diretiva portada do `librarian_policy.md` para skill Superpowers compartilhada.

### Sync automático para NotebookLM

Ao final de cada compile run:
- Detecta páginas wiki novas/alteradas desde último sync (via manifesto local `wiki/.nlm_sync_manifest.json`)
- `source_add(notebook_id="987bb91c-86a3-4a9a-a3db-4dbaa150bd18", source_type="file", file_path=...)` para cada página
- Atualiza manifesto
- Respeita pruning manual: se o usuário deletar um source no NLM UI, o manifesto detecta (na próxima validação) e não re-upa

**Dependência:** MCP `notebooklm-mcp` operacional (requer `nlm login` quando cair).

**Entrega:** wiki fecha o ciclo — serve como input para os agentes via INDEX, responde a feedback com sugestões embasadas, e mantém NotebookLM sincronizado automaticamente.

---

## Storage layout consolidado

```
C:\Projetos\Stout\memory\context-agent\          ← storage unificado
├── sessions\                                    ← saídas dos 4 agentes
├── cleaned\                                     ← spec/plan limpos
├── archive\
├── ACTIVE_CONTEXT.md
├── PROJECT_REGISTRY.md
└── context.db

C:\Projetos\Stout\wiki-compiler\                 ← código reformado
├── compiler\                                    ← Ar9av adaptado
├── adapters\
│   ├── sessions_to_pending.py
│   └── cleaned_to_pending.py
├── audit\                                       ← preservado
├── tests\
└── run_wiki_work.sh                             ← entry point preservado

C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\wiki\   ← vault (repo git dedicado, git init na Fase 4)
├── raw\
│   ├── _pending\                                ← contrato preservado
│   └── inbox\                                   ← futuro
├── SUGESTOES-HOJE.md                            ← acumulativo na nova versão
├── PENDENCIAS.md
├── suggestion_ignore.md
├── AUDIT_REPORT.md
├── INDEX.md                                     ← NOVO
├── .nlm_sync_manifest.json                      ← NOVO
└── *.md                                         ← páginas (flat, kebab-case)
```

---

## Peneira — 4 camadas

| Layer | Momento | Responsável | Função |
|---|---|---|---|
| 1 — Session clean | save time | context-agent `session_summary.py` | Remove shell noise, paths, comandos, hashes, mensagens >2000 chars |
| 2 — Spec/plan clean | save time | context-agent `superpowers_cleaner.py` (novo) | Remove frontmatter, checklists, placeholders, meta-info; preserva decisões e arquitetura |
| 3 — Ingest + audit | compile time | Ar9av + audit engine | Dedupe Jaccard, merge vs create, detecção de órfãos/duplicatas/conflitos |
| 4 — Review gate | compile time | Humano (você) | Aprovação batch do diff plan antes do commit |

**Principio:** wiki silencioso é melhor que wiki poluído. Sessão sem sinal → nada em pending. Spec puramente processual → nada em pending.

---

## O que NÃO muda

- Path do vault (`Obsidian-Victor-Global/wiki/`)
- Estrutura flat kebab-case
- Contrato `raw/_pending/` como ponto único de input
- Nomes e semântica de `SUGESTOES-HOJE.md`, `PENDENCIAS.md`, `suggestion_ignore.md`, `AUDIT_REPORT.md`
- Audit engine existente (exceto remoção do check NLM)
- Capacidade dos agentes de ler SUGESTOES e responder a "pendente/concluído/ignora"

## O que é removido ou deprecado

- `SCHEMA.md` + Gemini CLI como compilador (substituído por Ar9av)
- `harvest_brain.sh` (deprecado; remover após 2 semanas)
- Escrita do Bibliotecário em `raw/_pending/` via Trigger Gamma (deprecado; Antigravity agora usa context-agent)
- Check NLM no audit engine (NLM não é mais input)
- Fragmentos `nlm-synthesis` em `raw/_pending/` (não geradas mais)
- Sobrescrita de `SUGESTOES-HOJE.md` a cada run (vira acumulativo)

---

## Dependências e riscos

**Dependências externas:**
- MCP `notebooklm-mcp` operacional (research + sync automático)
- Credenciais de GitHub para criar repo privado do vault (Fase 4)
- Ar9av/obsidian-wiki como upstream (fork para mitigar risco de abandono)

**Riscos identificados:**

| Risco | Mitigação |
|---|---|
| NLM MCP instável/cai (como ocorreu hoje) | Design degrada graciosamente: sugestões sem embasamento se NLM inacessível; sync NLM fica pendente em buffer até reconexão |
| Dedupe Jaccard gera falsos positivos/negativos | Threshold já existe em 0.6 (calibrado); review gate humano captura casos divergentes |
| Ar9av upstream diverge ou abandona | Fork do projeto desde o início, versionado no monorepo Stout |
| Re-seed da Fase 4 produz wiki muito diferente do atual | Revisão manual de amostra é obrigatória antes do commit; backup preservado para reverter |
| Superpowers compartilhado (Gemini+Antigravity) causa conflito de instalação do context-agent | Única fonte em `C:\Projetos\Stout\antigravity\skills\` já é verdade; home dir é symlink/mirror (validado) |

---

## Fora de escopo (pós-reforma)

- Migração para hooks automáticos nos 4 agentes (Claude Code já tem; outros ficam manuais por ora)
- Integração Pilsen/VMS via `raw/inbox/` (referenciada mas não implementada)
- Expansão do INDEX.md com metadata adicional (tags secundárias, prioridade de leitura)
- Cross-notebook query com ranking de relevância (versão inicial faz query simples)
- Export de pacotes temáticos para NotebookLM (sync automático cobre o caso geral; export manual fica para depois se necessário)

---

## Sequência de entrega recomendada

1. **Fase 1** — unificar context-agent (sem tocar no wiki ainda; baixo risco, desbloqueia tudo)
2. **Fase 2** — superpowers_cleaner (pode rodar em paralelo com Fase 3)
3. **Fase 3** — Ar9av em ambiente isolado (compila em vault de teste, valida output)
4. **Fase 4** — reset + rebuild (única fase destrutiva; backup obrigatório)
5. **Fase 5** — INDEX + NLM sync + feedback persistente (sobre wiki já reconstruído)

Cada fase recebe seu próprio plano de implementação detalhado via skill `writing-plans`.
