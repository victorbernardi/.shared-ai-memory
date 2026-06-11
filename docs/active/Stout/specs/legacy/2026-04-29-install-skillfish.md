# Spec: Integração Skillfish (Stout Edition)

**Data:** 2026-04-29  
**Status:** Brainstorming Completo  
**ID:** SPEC-SKILLFISH-001

## 1. Objetivo
Sistematizar o gerenciamento de habilidades (Agent Skills) no Antigravity através da ferramenta Skillfish, permitindo que o agente instale, atualize e sincronize capacidades de forma autônoma e segura.

## 2. Requisitos

### Funcionais
- Instalação global do binário `skillfish`.
- Criação da habilidade `skill-manager` para interfacear comandos.
- Suporte aos comandos `add`, `update` e `list`.
- Redirecionamento obrigatório para `C:\Projetos\Stout\antigravity\skills`.

### Não-Funcionais
- **Qualidade:** Uso obrigatório da skill `writing-skills` para a criação do `SKILL.md`.
- **Segurança:** Integração pós-instalação com a `skill-sentinel` para auditoria de novas habilidades.
- **Isolamento:** Não deve interferir nas pastas globais do Gemini, focando apenas no diretório do projeto Stout.

## 3. Arquitetura Proposta

A solução opera em três camadas:
1. **Engine:** Binário `skillfish` instalado via NPM.
2. **Interface (Skill):** `skill-manager` atuando como dispatcher de comandos.
3. **Guardião:** `skill-sentinel` verificando a integridade do que foi baixado.

### Fluxo de Trabalho (Exemplo de Instalação)
1. Usuário solicita: "Adicione a skill X".
2. Agente ativa `skill-manager`.
3. `skill-manager` executa `skillfish add X --dir ...`.
4. `skill-manager` instrui o agente a invocar `skill-sentinel`.
5. `skill-sentinel` audita o arquivo `SKILL.md` recém-criado.

## 4. Plano de Validação
- **Teste 1:** Executar `skillfish --version` no terminal.
- **Teste 2:** Tentar listar as skills atuais via `skill-manager`.
- **Teste 3:** Simular a instalação de uma skill pública e verificar se a `skill-sentinel` é acionada.

## 5. Log de Decisões
- **DEC-001:** Nomeação como `skill-manager` para evitar sobrecarga na `skill-sentinel`.
- **DEC-002:** Uso da abordagem "Reativa" (Com Auditoria) para manter a disciplina Stout.
- **DEC-003:** Inclusão da `writing-skills` no processo de criação para garantir padrões de Tier 1.

---
**Próximo Passo:** Mover para a Fase 2: Estratégia (/plan).
