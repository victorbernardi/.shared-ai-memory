# Spec: Unificação de Governança e Blindagem Técnica (v5)

## 1. Objetivo
Unificar os manifestos estratégicos (`GEMINI.md`) sem retroceder nas regras técnicas estabelecidas em `gemini-tools.md`. Integrar o *Agentic Design Framework* como a camada de raciocínio superior que justifica e potencializa as regras de ferramentas existentes.

## 2. Diagnóstico de Riscos e Melhorias (Based on User Feedback)
- **Risco de Retrocesso Técnico:** O mapeamento de ferramentas Claude Code -> Gemini e as regras de "Ausência de Subagentes Genéricos" são vitais. A unificação NÃO pode diluir essas instruções.
- **Divergência de Ferramentas:** O arquivo `gemini-tools.md` em `.antigravity` e `C:\Motores-LLM` deve ser a âncora técnica. O manifesto estratégico deve atuar como o "Diretor Criativo" (Strategic Master) que aponta para este "Manual de Engenharia".
- **Melhoria (Não apenas Mudança):** Integrar o conceito de "Mastery of Context" do framework para reforçar por que usamos `grep_search` e `context7` em vez de leituras massivas.

## 3. Requisitos de Governança Atualizados
- **Preservação Integral:** As seções de "Mapeamento de Ferramentas" e "Regras de Ouro" de `gemini-tools.md` devem ser mantidas e referenciadas no novo `GEMINI.md`.
- **Sincronização Golden Copy:** Manter a regra de que alterações no Stout devem ser promovidas para `C:\Motores-LLM` via `canary-deployment`.
- **Hierarquia de Documentos:**
  1.  **`GEMINI.md` (Root):** O Manifesto Estratégico (O Quê e Por Quê).
  2.  **`gemini-tools.md`:** O Manual Técnico (Como).
  3.  **`MEMORY.md`:** Memória Dinâmica (Onde estamos).

## 4. Arquitetura de Solução (v5)
1.  **Consolidação de "The Strategic":** Adicionar os 4 pilares do *Agentic Design Framework* ao início do root `GEMINI.md`.
2.  **Referência Técnica Blindada:** O novo `GEMINI.md` terá uma seção de "Engenharia de Ferramentas" que espelha as regras de `gemini-tools.md`, garantindo que o agente tenha esse contexto em qualquer leitura do manifesto.
3.  **Link de Alta Fidelidade:** Garantir que o link para `gemini-tools.md` aponte para a versão oficial em `C:\Motores-LLM` (Golden Copy) ou para a versão local sincronizada.

## 5. Plano de Validação
- **Checklist de Equivalência:** O agente deve demonstrar que ainda sabe traduzir `Read` para `view_file`.
- **Handshake de Contexto:** Validar se o agente aplica o "Mastery of Context" ao realizar buscas.
- **Conformidade Stout:** Planos e Specs continuam versionados.

---
*Status: Spec v5 Blindada e Aprimorada*
