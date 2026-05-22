# Spec: Governança de Sessões e Sincronização GitHub (v1)

## 1. Problema
As sessões de trabalho (geradas pelo `context-agent`) e as modificações estruturais do ecossistema Stout não estão sendo sincronizadas com o GitHub de forma consistente.

### Sintomas Detectados:
- **Backlog de Commits:** 22 commits locais não enviados ao `origin`.
- **Sessões Órfãs:** Arquivos de `session-012.md` a `session-033.md` estão como *untracked*.
- **Desalinhamento Estrutural:** Mudanças significativas em pastas de skills (renomeações para prefixos `process-`, `audit-`, `data-`) estão pendentes no Git (deletions e untracked folders).
- **Falta de Automação:** O encerramento de sessão não inclui uma etapa de persistência remota (Git Push).

---

## 2. Objetivos
1. **Consolidação:** Limpar o estado atual do repositório, rastreando todas as sessões órfãs e confirmando a nova estrutura de pastas.
2. **Protocolo de Encerramento:** Implementar um fluxo (ou comando) que garanta que o `context-agent save` seja seguido de `git commit` e `git push`.
3. **Visibilidade:** Garantir que o `origin/master` reflita exatamente o estado do `source of truth` (Stout local).

---

## 3. Pesquisa e Diagnóstico (Brainstorming)

### Hipóteses:
- **H1:** O `context-agent` não tem permissão ou instrução para gerenciar o Git.
- **H2:** A mudança de estrutura de pastas (refactoring de skills) causou confusão no rastreamento do Git.
- **H3:** O fluxo de trabalho atual depende de ação manual do usuário para o push, que é frequentemente esquecida.

### Requisitos Iniciais:
- **Funcional:** Automação do ciclo `Save -> Commit -> Push`.
- **Segurança:** Não automatizar o push se houver conflitos ou erros de linting (opcional, Stout é root).
- **Rastreabilidade:** Mensagens de commit devem referenciar o ID da sessão.

---

## 5. Análise de Riscos e Protocolo de Segurança
Operações massivas no Git em um ecossistema complexo como o Stout exigem salvaguardas rigorosas para evitar perda de dados.

### 5.1. Matriz de Riscos
| Risco | Descrição | Gravidade | Mitigação |
| :--- | :--- | :--- | :--- |
| **Remoção de Junctions** | Git interpretar link simbólico como pasta vazia e deletar conteúdo original. | **CRÍTICA** | Proibir comandos destrutivos (`clean`, `checkout`, `restore`) sem verificação de links. |
| **Desincronização Local/Remoto** | Conflitos ao tentar push automático com mudanças no origin. | Média | Implementar `pull --rebase` obrigatório no fluxo de sync. |
| **Backlog Gigante** | Commits massivos dificultam o debug de quando um erro foi introduzido. | Média | Priorizar commits granulares por módulo/projeto. |

### 5.2. Protocolo de Segurança de Execução
1. **Snapshot de Memória:** Realizar backup da pasta `memory/` antes de operações globais.
2. **Validação de Links:** Comando `dir /al` para garantir que Junctions estão intactos.
3. **Commit Granular:** Em vez de `git add -A`, realizar staging pasta por pasta para revisão.
4. **Verificação Humana:** Apresentar a lista de arquivos a serem deletados antes da confirmação.
