# 🗺️ Roadmap: Configuration-Driven Development (CDD) - Skill Edition [LEGACY]

Este projeto segue a metodologia Stout Lab para desacoplar regras de negócio da execução técnica, agora integrado ao **Padrão de Pasta de Skills**.

## ✅ Fase 1 & 2: Inicialização e Pesquisa (CONCLUÍDO)

- [x] Scaffolding do projeto (`stout-init`).
- [x] Implementação do **Shared Core Engine** (Level 3 - Execução) em `C:\Projetos\Stout\scripts\core`.
- [x] Criação do `src/config.py` com suporte a multi-ambiente.
- [x] Validação do ciclo básico (Regra -> Motor -> Resultado).

## 🚀 Fase 3: Maturidade de Skills e Metadados (CONCLUÍDO)

- [x] **3.1 - Expansão do Motor (engine.py):** Suporte a roteamento baseado no contexto de Skills.
- [x] **3.2 - Validação JSON Schema:** Garantir que os catálogos de skills e regras sigam o contrato.
- [x] **3.3 - Catálogo de Skills (Prompts):** Migrar `prompts.yaml` para um formato de `skills_catalog.yaml` que siga o Padrão de Pasta (Level 1 & 2).

## 🧠 Fase 4: Skill Routing & Orquestração (CONCLUÍDO)

- [x] **4.1 - Skill Router Inteligente:** Integrar o motor de regras com o catálogo de skills.
- [x] **4.2 - Seleção Dinâmica de Recursos:** Decidir quais referências (Level 3) carregar baseado na regra ativada.
- [x] **4.2b - Arquitetura Multi-Tier:** Suporte a repositórios de skills Globais e Locais com sobreposição.
- [x] **4.3 - Traceability GCC:** Implementar o Context Controller para registrar marcos lógicos (Commit/Context).
- [x] **4.4 - Arquitetura de Eventos (Hooks CDD):** Implementação de pré/pós ações validadas.

## 🛡️ Fase 5: Governança e Imunidade a Erros (CONCLUÍDO)

- [x] **5.1 - Protocolo de Imunidade (stout-immunity-gate):** Implementação do Audit Gate e Sentinel v5.
- [x] **5.2 - Imutabilidade (CLI Protocol):** Refatoração para forçar o uso de `replace` sobre `write_file`.
- [x] **5.3 - Documentação Stout:** ADR-0006, Walkthrough e registros de Failure-Log.
- [x] **5.4 - Integração Inova/Stout:** Garantir que o motor carregue skills de `.agent/skills/` ou `~/.gemini/skills/`.
- [x] **5.5 - CLI de Gestão de Skills:** Comandos para testar ativação de skills sem rodar o projeto todo.

---
*Roadmap V2.0 concluído com sucesso em 2026-05-14.*

## 🛡️ Roadmap V3.0: Ecossistema Blindado e Sincronizado (PRÓXIMA ETAPA)

### Fase 9: Resiliência Extrema & Guardrails (Hardening)

*   **9.1 - Validação Preventiva:** Integrar validação de schema no Agente Sentinela.
*   **9.2 - Skill Sandboxing:** Implementar camadas de permissões por skill no `ADDON.md`.
*   **9.3 - Auto-Recovery:** Restauração automática de configurações estáveis via GCC.

### Fase 10: Testabilidade & QA Agêntico

*   **10.1 - Rule Simulator:** Relatório automático de cobertura de intenções.
*   **10.2 - Unit Testing de Skills:** Testes isolados para scripts de Level 3.

### Fase 11: Governança de Distribuição (Scale)

*   **11.1 - Skill Semantic Versioning:** Controle de versão para evolução de habilidades.
*   **11.2 - Stout Central Registry:** Sincronização de melhorias entre múltiplos projetos.
