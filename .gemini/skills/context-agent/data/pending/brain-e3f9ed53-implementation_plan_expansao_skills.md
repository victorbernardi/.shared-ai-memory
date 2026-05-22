# Plano de Implementação: Expansão do Ecossistema de Documentação

Este plano descreve o processo de instalação, refinamento e auditoria de 5 novas habilidades para o ambiente **Stout (Desenvolvimento)**, focando em documentação técnica e de negócio para projetos de dados.

## Objetivo
Estabelecer um toolkit de documentação de alta performance em `C:\Projetos\Stout\antigravity\skills`, garantindo que todas as habilidades sigam os padrões Tier 1 da `writing-skills` e obtenham score > 80 no `skill-sentinel`.

## Habilidades Alvo

### 🧬 Orquestração e Fluxo
6.  **`doc-workflow-orchestrator`** [NOVA]: Uma skill de Tier 1 que define a sequência lógica de uso das habilidades (BRD -> ADR -> Spec -> Insight), garantindo que elas se complementem sem alterar sua lógica original.

---

## Fluxo de Trabalho por Skill (Protocolo de Excelência)

Para cada uma das habilidades, seguiremos este rito:

### 1. Aquisição e Extração
- Download via `skillfish` ou extração do bundle `claude-config` já clonado.
- Deploy inicial em `C:\Projetos\Stout\antigravity\skills/[nome-da-skill]`.

### 2. Refinamento via `writing-skills`
Aplicaremos os seguintes padrões em cada `SKILL.md`:
- **YAML Frontmatter:** Inclusão obrigatória de `name`, `version`, `category` e `triggers`.
- **CSO (Search Optimization):** Otimização da `description` começando com "Use when..." e inclusão de 3+ triggers bilíngues (PT-BR e EN).
- **Cross-References:** Adição de uma seção "Related Skills" para conectar as peças do workflow.
- **Anti-Rationalization:** Adição de regras de disciplina que o agente não deve ignorar.

### 3. Criação da Orquestradora
- Desenvolver a `doc-workflow-orchestrator` como um guia de processo (Tier 1).

### 4. Auditoria Sentinel
- Execução de `python run_audit.py --skill [nome-da-skill]`.
- Correção imediata de qualquer finding de severidade **High** ou **Medium**.

---

## Plano de Execução

### Fase 1: Documentação Técnica (Batch 1)
- [ ] Instalação e Refinamento de `explore`.
- [ ] Instalação e Refinamento de `spec-validation`.

### Fase 2: Documentação de Negócio (Batch 2)
- [ ] Instalação e Refinamento de `brd-generator`.
- [ ] Instalação e Refinamento de `user-story-expert`.
- [ ] Instalação e Refinamento de `data-insight-reporter`.

### Fase 3: Validação Final
- [ ] Auditoria completa do ecossistema de documentação.
- [ ] Geração do Walkthrough final.

---

## Riscos e Mitigações
- **Incompatibilidade Windows:** Alguns scripts podem ser Bash (.sh). **Mitigação:** Adaptaremos para PowerShell ou instruções puras de Markdown se necessário.
- **Sincronização Indesejada:** Manteremos o isolamento absoluto entre o workspace `c:\Motores-LLM` e o destino `C:\Projetos\Stout`.

## User Review Required
> [!IMPORTANT]
> As habilidades de Negócio (`brd-generator`, etc.) podem exigir templates específicos da sua empresa. Usaremos os templates padrão da comunidade a menos que você forneça modelos customizados.

**Aprovação do Plano:** Digite "Aprovo" para iniciarmos a Fase 1.
