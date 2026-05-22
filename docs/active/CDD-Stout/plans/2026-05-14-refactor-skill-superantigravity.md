# PLAN: Evolução do Orquestrador Superantigravity (Stout Standard v5)

## 1. OBJETIVO
Elevar a skill `using-superantigravity` ao selo de qualidade Stout, integrando o **Protocolo de Imunidade a Erros** e a **Arquitetura de Delegação (Context Wall)**. O objetivo é garantir que o orquestrador permaneça LEAN, delegando falhas para a skill `systematic-debugging` e validando conhecimentos via `context7`.

## 2. ARQUITETURA DE GOVERNANÇA
Seguindo os princípios de CDD e Context Wall:

### A. Camada de Consciência (Orquestrador)
- **Skill:** `using-superantigravity`
- **Responsabilidade:** Monitorar o estado do projeto.
- **Nova Regra:** Bloqueio imediato se `.audit_gate` existir.
- **Ação em Falha:** Invocar `systematic-debugging` em vez de tentar correções ad-hoc.

### B. Camada de Resolução (Executor)
- **Skill:** `systematic-debugging`
- **Responsabilidade:** Analisar a falha cientificamente.
- **Dependência:** Consulta obrigatória à MCP `context7` (SOP Diagnóstico).
- **Entregável:** Atualização do `failure-log.md` e do `Implementation Plan`.

### C. Camada de Imutabilidade (Ferramentas)
- **Referência:** `docs/governance/protocolo_ferramentas_cli.md`
- **Regra:** Proibido `write_file` em arquivos existentes (exceto logs/notes).
- **Proteção:** Injeção de check de gate no `engine_wrapper.py`.

## 3. COMPONENTES TÉCNICOS
1.  **Audit Gate (.audit_gate):** Arquivo trava físico para impedir modificações não auditadas.
2.  **Sentinel Agent:** Monitor de processos que cria o gate em caso de `Exit Code != 0`.
3.  **Stout Quality Seal (.stout_seal.json):** Registro centralizado de metadados de governança (substitui headers no código).

## 4. ANÁLISE DE RISCOS E MITIGAÇÃO
- **Risco de Deadlock:** Implementação da flag `--bypass-gate` restrita ao diretório `src/core/`.
- **Falsos-Positivos:** Lista branca de comandos seguros (read-only) no Sentinel.
- **Sobrecarga da Skill:** Manter a `using-superantigravity` apenas como decisora de fluxo, nunca como ferramenta de debug.

## 5. WORKFLOW REFINADO (THE STOUT LOOP)
1.  **Erro Detectado** -> Sentinel cria `.audit_gate`.
2.  **Orquestrador** detecta trava -> Ativa `systematic-debugging`.
3.  **Debugger** valida via `context7` -> Escreve no `failure-log.md`.
4.  **Debugger** atualiza o plano estratégico.
5.  **Agente** aplica a correção via `replace` (respeitando imutabilidade).
6.  **Sentinel** remove o gate após verificação de sucesso.

## 6. ROADMAP DE IMPLEMENTAÇÃO
- **Etapa 1:** Registro da decisão arquitetural (**ADR-0006**). [CONCLUÍDO]
- **Etapa 2 (Hardening Preflight):** 
    - Injetar `_check_audit_gate()` no `src/core/preflight.py`.
    - Garantir que o boot retorne `valid: False` se o gate existir.
- **Etapa 3 (Hardening Sentinel):**
    - Atualizar `src/tools/sentinel_agent.py` para criar o gate em falhas reais.
    - Implementar whitelist de comandos seguros.
- **Etapa 4:** Refatoração da `SKILL.md` global.
- **Etapa 5:** Criação do `Walkthrough` final.
