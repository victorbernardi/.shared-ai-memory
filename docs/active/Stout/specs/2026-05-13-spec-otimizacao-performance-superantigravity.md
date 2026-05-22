# Especificação Técnica: Otimização de Performance - Skill using-superantigravity (Stout Edition)

**Data:** 2026-05-13  
**Status:** Validado  
**Versão:** 1.0  
**Autor:** Gemini CLI (Antigravity Architect)

---

## 1. Objetivo
Reduzir o tempo de carregamento da sessão e o consumo inicial de tokens ao ativar a skill `using-superantigravity`. A solução aplica a **Regra 1 (Progressive Disclosure)** do ecossistema Stout, transformando a skill de um monólito denso em um orquestrador minimalista baseado em referências sob demanda.

## 2. Requisitos

### Funcionais
- Fragmentar o conteúdo da skill em 3 níveis estritos de refrigeração.
- Manter a inicialização automática do `brain-watcher.py` (essencial para automação).
- Garantir que toda a "Golden Copy" (filosofia, infraestrutura e ciclo de vida) permaneça acessível em arquivos de referência.

### Não-Funcionais
- **Performance:** Redução de >50% no tamanho do arquivo `SKILL.md` principal.
- **Eficiência de Contexto:** Evitar o carregamento proativo do histórico de sessões (`ACTIVE_CONTEXT.md`) antes da fase de Research.

## 3. Arquitetura Proposta (Design de 3 Níveis)

### Nível 1: Discovery (SKILL.md - Frontmatter)
O `SKILL.md` principal conterá apenas:
- Metadados YAML.
- Gatilho visual (Description).
- Comando mandatório de background (`brain-watcher.py`).
- Instruções de "Launcher" (como carregar os próximos níveis).

### Nível 2: Activation (references/stout-lifecycle.md)
Arquivo isolado contendo as diretrizes de execução das fases:
- `/brainstorm` (Research)
- `/plan` (Strategy)
- `/build` (Execution)

### Nível 3: Cold Storage (references/*.md)
- `philosophy.md`: Red Flags, Core Philosophy e diagramas DOT.
- `infrastructure.md`: Hierarquia de busca, clonagem de skills e comandos globais.

## 4. Plano de Validação
1. **Teste de Carga:** Medir a latência percebida ao acionar `activate_skill using-superantigravity` após a refatoração.
2. **Teste de Continuidade:** Verificar se o agente consegue carregar as instruções de ciclo de vida corretamente via `read_file` ao iniciar um brainstorming.
3. **Persistência de Automação:** Confirmar se o `brain-watcher.py` inicia corretamente em background.

## 5. Log de Decisões
- **Decisão:** Mover as instruções do ciclo de vida para `references/` em vez de mantê-las no corpo.
- **Motivo:** Evitar que o agente processe as regras de "como pesquisar" enquanto o CLI ainda está indexando o projeto, mitigando o gargalo de contexto inicial.
- **Alternativa Considerada:** Apenas remover os gráficos DOT. Rejeitada por não atacar a causa raiz da densidade processual.

---
*Documento gerado conforme protocolo de Brainstorming Stout Edition.*
