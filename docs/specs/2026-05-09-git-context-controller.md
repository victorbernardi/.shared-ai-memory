# Especificação: Git-Context-Controller (GCC)

> **Fase:** Research / Brainstorming (Read-Only)
> **Data:** 2026-05-09
> **Autor:** Antigravity + Victor Bernardi
> **Status:** ⏳ AGUARDANDO APROVAÇÃO HUMANA

---

## 1. Objetivo

Criar uma skill mecânica e automatizada chamada **`git-context-controller`** (GCC) que implemente a **REGRA 3 do manifesto GEMINI.md** — a blindagem contra Memória Envenenada dentro da Muralha de Contexto.

### O Problema

Os modelos de linguagem mantêm um registro estritamente **linear** de eventos. Se o agente comete um erro de raciocínio no passo 10 de uma execução de 50 passos, essa falha permanece **indelevelmente gravada** no histórico. O agente se torna:

1. **Incapaz de retroceder** o estado da memória para antes da falha
2. **Perpetuamente ancorado** em conclusões equivocadas
3. **Construtor inevitável** de soluções disfuncionais baseadas em premissas corrompidas

### A Solução Conceitual (já documentada)

A REGRA 3 do `GEMINI.md` define que o contexto do agente deve funcionar como um **Sistema de Arquivos Versionado** através de 3 operações:

| Operação | Analogia Git | Propósito |
|----------|-------------|-----------|
| `BRANCH` | `git checkout -b` | Criar ramo experimental isolado para testar hipótese |
| `DISCARD` | `git branch -D` | Descartar branch envenenado, limpar o veneno |
| `MERGE` | `git merge` | Consolidar aprendizado validado de volta à raiz |

### O que falta

**Uma skill materializada** que execute essas operações mecanicamente, integrando-se ao ecossistema existente (`context-agent`, `context-guardian`).

---

## 2. Análise do Ecossistema Existente

### 2.1 Skills Internas (Stout)

| Skill | O que faz | Lacuna para o GCC |
|-------|-----------|-------------------|
| `context-degradation` | Documenta cientificamente os padrões de degradação (poisoning, lost-in-middle, distraction) | Apenas **teoria**, sem automação |
| `context-guardian` | Snapshots PRÉ-compactação com 3 camadas de redundância (P0/P1/P2) e briefing de transição | Atua **linearmente** (append-only). Sem conceito de branches |
| `context-agent` | Persistência entre sessões (save/load/search via FTS5) | **Sem versionamento**. Cada save é um snapshot flat, não uma árvore |
| `context-optimization` | Compaction, observation masking, KV-cache, partitioning | Foco em **eficiência de tokens**, não em isolamento de raciocínio |

### 2.2 Skills Externas (Skillfish)

| Skill | O que faz | Relevância |
|-------|-----------|------------|
| **Savepoint Rollback** | Reverte estado do **projeto (arquivos)** para um savepoint | ⭐⭐⭐ Mecânica de rollback mais próxima. Mas opera em **código**, não em **contexto cognitivo** |
| **Savepoint Snapshot Manager** | Cria snapshots versionados do estado do projeto | ⭐⭐⭐ Bom modelo de referência para a estrutura de dados |
| **Context Canary** | Monitora saúde do contexto após compactação | ⭐⭐ Detecção, não prevenção |
| **MCP Context Isolation** | Isola resultados de MCP em subcontextos | ⭐⭐ Isolamento de dados, não de raciocínio |
| **Maestro Agent Context Isolation** | Isola outputs de sub-agentes | ⭐⭐ Bom padrão, mas depende de subagentes |

### 2.3 Conclusão da Análise

> **Nenhuma skill existente (interna ou externa) resolve o problema completo.**
>
> As skills de **Savepoint** são as mais próximas mecanicamente, mas operam sobre **arquivos de código** (git stash/restore), não sobre o **estado cognitivo** do agente.
>
> O GCC precisa ser construído como uma peça **nova e original** do ecossistema Stout, usando os patterns já validados internamente.

---

## 3. Requisitos

### 3.1 Funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-01 | `gcc branch <nome>`: Criar snapshot nomeado do estado cognitivo atual (ACTIVE_CONTEXT.md + MEMORY.md + sessão ativa) | P0 |
| RF-02 | `gcc discard <nome>`: Descartar branch e restaurar estado ao ponto pré-branch | P0 |
| RF-03 | `gcc merge <nome>`: Consolidar aprendizado do branch de volta ao tronco principal | P0 |
| RF-04 | `gcc status`: Listar branches ativos com metadata (criação, tamanho, motivo) | P1 |
| RF-05 | `gcc diff <nome>`: Mostrar diferenças entre branch e tronco atual | P1 |
| RF-06 | Integração com `context-agent save` para persistência automática | P1 |
| RF-07 | Integração com `context-guardian` para snapshots P0 antes de branch | P2 |

### 3.2 Não-Funcionais

| ID | Requisito | Critério |
|----|-----------|----------|
| RNF-01 | Execução rápida | Cada comando deve completar em < 5 segundos |
| RNF-02 | Sem dependências externas | Apenas Python stdlib + arquivos locais |
| RNF-03 | Idempotência | Executar `gcc branch X` duas vezes não deve criar duplicatas |
| RNF-04 | Auditabilidade | Toda operação deve gerar log em `gcc/logs/` |
| RNF-05 | Isolamento total | Um branch não deve contaminar o tronco ou outros branches |

---

## 4. Arquitetura Proposta — 3 Abordagens

### Abordagem A: File-System Branching (RECOMENDADA)

**Conceito:** Cada branch é uma **pasta isolada** contendo cópias dos arquivos de estado cognitivo. O "merge" é uma operação de cópia seletiva de volta ao tronco.

```
~/.shared-ai-memory/context-agent/
├── trunk/                          # Estado principal (atual)
│   ├── ACTIVE_CONTEXT.md
│   ├── MEMORY.md
│   └── session-current.md
├── branches/                       # Branches isolados
│   ├── tese-migracao/
│   │   ├── ACTIVE_CONTEXT.md       # Snapshot no momento do branch
│   │   ├── MEMORY.md
│   │   ├── session-branch.md       # Histórico do branch
│   │   ├── learnings.md            # Aprendizados extraídos (para merge)
│   │   └── metadata.json           # Timestamp, motivo, status
│   └── refactor-api/
│       └── ...
├── logs/                           # Audit trail
│   └── gcc-2026-05-09T02-12.log
└── gcc.json                        # Estado global (branch ativo, histórico)
```

**Prós:**

- Simples de implementar (file I/O puro)
- Fácil de auditar (pastas legíveis)
- Integra naturalmente com `context-agent` (mesma raiz)
- Zero dependências

**Contras:**

- Não versiona o **histórico de conversa** real (apenas os arquivos de estado)
- O "veneno" na memória linear do LLM persiste até nova sessão

**Mitigação do contra:** O GCC não pode apagar tokens já processados pelo LLM. O que ele pode fazer é:

1. Ao fazer `BRANCH`: salvar estado limpo como checkpoint
2. Ao fazer `DISCARD`: **instruir o agente a ignorar tudo após o branch** via prompt injection no topo do contexto + restaurar arquivos de estado para o snapshot
3. Ao fazer `MERGE`: extrair apenas os learnings validados e injetá-los no contexto limpo

### Abordagem B: Session-Based Branching

**Conceito:** Cada branch é uma **sessão separada** do Antigravity. O merge é uma operação de extração cross-sessão.

**Prós:** Isolamento real da memória linear do LLM

**Contras:** Complexo de automatizar, requer múltiplas instâncias do Antigravity

### Abordagem C: Git Real sobre Context Files

**Conceito:** Usar git real (`git init`, `git branch`, `git stash`) sobre o diretório `context-agent/`.

**Prós:** Mecânica de branching já implementada e robusta

**Contras:** Overhead de manter um repo git dentro do context-agent, conflitos com o git do projeto principal

---

## 5. Decision Log

| # | Decisão | Alternativas | Motivo |
|---|---------|-------------|--------|
| D1 | Abordagem A (File-System Branching) | B (Session), C (Git Real) | Menor complexidade, zero dependências, integração natural com ecossistema existente |
| D2 | Python como linguagem | Bash, Node | Consistência com `context_manager.py` existente |
| D3 | Storage em `~/.shared-ai-memory/context-agent/` | Diretório separado | Reutilizar infraestrutura e paths já configurados |
| D4 | Cada branch contém `learnings.md` | Merge automático | Forçar o agente a sintetizar aprendizados antes do merge previne injeção de veneno no tronco |
| D5 | Prompt injection no discard | Apenas restaurar arquivos | Restaurar arquivos sozinho não limpa o veneno da memória linear; o prompt injection instrui o LLM a desconsiderar o trecho envenenado |
| D6 | Snapshot = apenas ACTIVE_CONTEXT.md + MEMORY.md | Incluir session-NNN.md | Leve e cirúrgico (~20KB). Sessions já são persistidas pelo context-agent via FTS5, copiar seria redundância sem valor |
| D7 | Merge NÃO trigga wiki-compiler | Trigger automático | Merge é momento arriscado; manter pipeline de qualidade manual (`/wiki-ingest`) preserva validação humana |
| D8 | Output terminal + indicator no MEMORY.md | Badge VS Code | Combo elegante: terminal para consulta ativa, MEMORY.md para consciência passiva do agente. Zero overhead |

---

## 6. Assumptions (Pressupostos)

1. O ecossistema Antigravity continuará usando `ACTIVE_CONTEXT.md` e `MEMORY.md` como fontes de verdade do estado cognitivo
2. O `context-agent` manterá compatibilidade com a estrutura atual de diretórios
3. O agente (LLM) consegue seguir instruções de "ignorar contexto anterior ao checkpoint X" quando recebe um prompt injection claro
4. Múltiplos branches simultâneos são raros (caso de uso principal: 1 branch experimental por vez)

---

## 7. Riscos Conhecidos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| LLM ignora o prompt injection do `discard` e continua envenenado | Alto | Complementar com restart de sessão quando discard falhar |
| Branch esquecido consome espaço | Baixo | Cleanup automático de branches > 7 dias via `maintain` |
| Conflito de merge quando trunk evoluiu durante o branch | Médio | Merge manual com diff side-by-side |

---

## 8. Plano de Validação (Como provaremos que funciona)

| Teste | Cenário | Critério de Sucesso |
|-------|---------|-------------------|
| T1 | `gcc branch tese-1` → verificar que snapshot foi criado | Pasta `branches/tese-1/` existe com cópias fiéis |
| T2 | Modificar ACTIVE_CONTEXT.md → `gcc discard tese-1` → verificar restauração | ACTIVE_CONTEXT.md volta ao estado pré-branch |
| T3 | `gcc branch tese-2` → escrever learnings → `gcc merge tese-2` → verificar consolidação | Learnings aparecem no ACTIVE_CONTEXT.md do trunk |
| T4 | `gcc status` → verificar listagem | Mostra branches com metadata correta |
| T5 | `gcc branch X` executado 2x → verificar idempotência | Sem duplicata, sem erro |

---

## 9. Open Questions (RESOLVIDAS ✅)

1. ~~**Escopo do snapshot:**~~ → Apenas `ACTIVE_CONTEXT.md` + `MEMORY.md` (D6)
2. ~~**Integração com wiki-compiler:**~~ → Não triggar automaticamente (D7)
3. ~~**Notificação visual:**~~ → Terminal + indicator no MEMORY.md (D8)

---

## 10. Understanding Lock ✅

### O que está sendo construído
- Skill `git-context-controller` (GCC): ferramenta CLI Python para blindagem contra Memória Envenenada

### Por que existe
- Materializar a REGRA 3 do manifesto GEMINI.md que hoje é apenas comportamental

### Para quem
- Agentes LLM operando no ecossistema Stout/Antigravity

### Restrições
- Python stdlib only, sem dependências externas
- Integrar com infraestrutura existente (context-agent, MEMORY.md)
- Snapshot leve (~20KB, apenas arquivos de estado cognitivo)

### Não-objetivos
- NÃO versiona o histórico de conversa real (tokens processados)
- NÃO substitui o context-agent ou context-guardian
- NÃO trigga wiki-compiler automaticamente

---

> **FASE 1 CONCLUÍDA.** Todas as questões resolvidas, Understanding Lock confirmado. Pronto para `/plan` ou `/build`.
