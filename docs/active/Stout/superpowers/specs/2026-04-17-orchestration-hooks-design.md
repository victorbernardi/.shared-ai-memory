# Design: Ativação dos Ganchos de Orquestração e Auto-Reflexão

**Data:** 2026-04-17  
**Escopo:** Antigravity (Gemini CLI) — apenas  
**Abordagem:** Edição cirúrgica + protocolos globais (Opção C)

---

## Contexto

Victor trabalha em três domínios intensos e distintos:

| Domínio | Ferramentas principais |
|---------|----------------------|
| Inova (Dados) | Python, Excel, engines M0-M4, auditorias financeiras |
| Stout (Conhecimento/Skills) | Skills, workflows, Notion, portabilidade |
| Obsidian (Second Brain) | Notas, Wiki Compiler, Bibliotecário |

O objetivo é fazer com que as skills certas sejam chamadas automaticamente — invisíveis quando desnecessárias, automáticas quando críticas — sem burocracia nova.

---

## Fase 1 — Ganchos nos Workflows Existentes

### 1.1 `implement.md` — Fase 0 obrigatória

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\implement.md`  
**Ação:** Inserir antes do Step 0 atual ("Load the Plan")

```markdown
## Fase 0 — Briefing Pré-Execução (OBRIGATÓRIA)
1. Carregar `task-intelligence` → classificar tarefa (Simples/Moderada/Complexa/Crítica)
2. Se Complexa ou Crítica → carregar `blueprint` para plano de construção
3. Se ≥ 2 skills relevantes detectadas → carregar `dispatching-parallel-agents`
```

Nenhuma outra alteração no workflow.

---

### 1.2 `troubleshoot.md` — Decisão de paralelismo

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\troubleshoot.md`  
**Ação:** Inserir antes do "Gather" atual (passo 2 da seção "Before loading the skill")

```markdown
## Decisão de Paralelismo
Antes de iniciar: "Este problema envolve mais de um sistema independente? (S/N)"
- N → fluxo sequencial normal
- S → carregar `dispatching-parallel-agents`, 1 agente por domínio
```

---

### 1.3 `brainstorm.md` — Revisão adversarial visível

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\global_workflows\brainstorm.md`  
**Ação:** Inserir após geração de propostas, antes de apresentar ao usuário

```markdown
## Revisão Adversarial (obrigatória antes de entregar)
Para cada proposta, listar explicitamente ao usuário:
1. Fragilidade 1
2. Fragilidade 2
3. Fragilidade 3
Se alguma for crítica → reformular antes de apresentar.
Formato de entrega: proposta + as 3 fragilidades identificadas (sempre visível).
```

---

## Fase 2 — Memória de Sessão

### 2.1 `SESSION_START.md` — novo arquivo

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\SESSION_START.md`

```markdown
## Protocolo de Início de Sessão
1. Carregar `context-agent` → recuperar snapshot da sessão anterior
2. Emitir Briefing de Retomada (máx. 4 linhas):
   - Projeto ativo: [Inova | Stout | Obsidian | outro]
   - Em progresso: [tarefa]
   - Pendentes: [próximos passos]
   - Erros recentes: [se houver — senão omitir]
3. Se nenhum snapshot existir → iniciar sessão limpa sem aviso

Nota: `diary` NÃO é lido no início de sessão — apenas escrito ao final.
```

**Isolamento wiki-compiler:** O `context-agent` salva em `skills/context-agent/data/sessions/` — isolado de `brain/`. Não alimenta o pipeline automático do wiki-compiler.

---

### 2.2 `END_OF_TASK.md` — novo arquivo

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\END_OF_TASK.md`

```markdown
## Protocolo de Encerramento de Tarefa
1. Marcar tasks concluídas em task.md
2. Salvar snapshot via context-agent:
   python context_manager.py save
   → grava em data/sessions/ (NÃO em brain/)
3. Escrever entrada no diary:
   - O que foi feito
   - O que foi aprendido
   - Erros cometidos (se houver)

Encaminhamento para wiki-compiler permanece decisão manual do usuário.
```

---

## Fase 3 — Auto-Avaliação Global

### 3.1 Instrução global de `confidence-check`

**Arquivo:** `C:\Users\victor.bernardi\.gemini\GEMINI.md` (arquivo global existente — adicionar seção ao final)

```markdown
## Regra Global: confidence-check em Código de Dados
Antes de entregar qualquer bloco de código que toque dados
(Python, SQL, Excel, engines Inova), executar internamente:
1. Tenho certeza sobre os dados de entrada e seus tipos?
2. Há edge cases não tratados (nulos, duplicatas, datas faltando)?
3. O output pode ser verificado sem executar o código?
Se "Não" em qualquer ponto → sinalizar explicitamente antes de entregar.

Aplica-se em qualquer workflow ativo, sem exceção.
```

---

### 3.2 `diary/erros.md` — novo arquivo de log de erros

**Arquivo:** `C:\Users\victor.bernardi\.gemini\antigravity\diary\erros.md`

Formato fixo por entrada:
```
DATA | TIPO: [Densidade|Lógica|Contexto|Planejamento] | ERRO → CAUSA RAIZ → CORREÇÃO
```

Alimentado pelo modelo ao identificar um erro cometido na sessão. Sem automação.

---

### 3.3 Knowledge graph → Obsidian

Fora do escopo deste plano. Baixa prioridade — depende de validação das fases 1 e 2.

---

## Resumo de Arquivos

| Arquivo | Ação | Prioridade |
|---------|------|------------|
| `global_workflows/implement.md` | Editar — inserir Fase 0 | Alta |
| `global_workflows/troubleshoot.md` | Editar — inserir decisão de paralelismo | Alta |
| `global_workflows/brainstorm.md` | Editar — inserir revisão adversarial | Média |
| `SESSION_START.md` | Criar | Alta |
| `END_OF_TASK.md` | Criar | Média |
| `GEMINI.md` | Editar — adicionar seção confidence-check ao final | Alta |
| `diary/erros.md` | Criar | Média |

---

## Critérios de Sucesso

- Victor não precisa pedir que os ganchos sejam usados — disparam automaticamente
- Erros da sessão anterior não se repetem na sessão seguinte
- Código de dados sempre passa pelo confidence-check antes da entrega
- Tempo de retrabalho (como restauração de skills degradadas) cai a zero
