# 📝 Plano de Execução: Migração e Estruturação ICM - Detalhamento Peças

> **Versão:** v2.0.0  
> **Status:** Em Standby (Aguardando Aprovação Humana)  
> **Referência Spec:** `docs/specs/spec_v2_migration_to_detalhamento_pecas.md`  
> **Data:** 2026-06-02  
> **Autor:** Gemini CLI (Engenheiro de Software)  

---

## 🚦 FASES DE IMPLEMENTAÇÃO

### Fase 1: Scaffolding e Infraestrutura do Novo Projeto
- [ ] **Tarefa 1.1 — Criação da Árvore de Diretórios ICM:**
  - **O que fazer:** Criar as pastas do projeto `C:\Projetos\Inova\projects\Detalhamento-Pecas` e sua estrutura ICM (`00_research`, `01_export`, `02_audit`, `src`, `notes`, `browser_state`, `output`, `docs`).
  - **Critério de Sucesso:** Diretórios criados fisicamente.
  
- [ ] **Tarefa 1.2 — Configuração e Cópia de Dependências Base:**
  - **O que fazer:** Copiar `requirements.txt`, `src/config.py` e os cookies persistentes de `browser_state/state.json` para o novo projeto.
  - **Critério de Sucesso:** Arquivos copiados e confirmados.

### Fase 2: Migração de Scripts e Ajustes Internos
- [ ] **Tarefa 2.1 — Refatoração e Mapeamento de Estágios (ICM-ization):**
  - **O que fazer:** Mover e adaptar o script de exportação para `01_export/scripts/export_sales.py`. Copiar `src/01_login.py` para `src/login.py` (mantendo o utilitário comum).
  - **Critério de Sucesso:** Scripts presentes em suas pastas específicas do ICM.

- [ ] **Tarefa 2.2 — Criação do Módulo de Auditoria (GATE):**
  - **O que fazer:** Mover e refatorar `scratch/check_final_file.py` para `02_audit/scripts/audit_file.py` de modo a validar o Excel de vendas de Janeiro de 2025 e gerar um output `output/audit_status.json` com o status do GATE.
  - **Critério de Sucesso:** Script de auditoria gerado no estágio 02 com verificação ativa.

### Fase 3: Documentação e Contratos do Pipeline
- [ ] **Tarefa 3.1 — Criação dos Contratos CONTEXT.md:**
  - **O que fazer:** Escrever os arquivos `CONTEXT.md` na raiz do projeto (contrato geral do pipeline), em `00_research/`, `01_export/` e `02_audit/` definindo escopos e responsabilidades.
  - **Critério de Sucesso:** 4 arquivos `CONTEXT.md` gerados no novo projeto em Português.

- [ ] **Tarefa 3.2 — Geração de Identidade (GEMINI.md & ANTIGRAVITY.md):**
  - **O que fazer:** Criar e configurar as identidades locais do novo projeto `GEMINI.md` (regras e KPIs de Peças) e `ANTIGRAVITY.md` (memória agêntica).
  - **Critério de Sucesso:** Identidades locais configuradas.

### Fase 4: Validação Empírica & Cleanup
- [ ] **Tarefa 4.1 — Validação Ponta a Ponta:**
  - **O que fazer:** Rodar a exportação na nova pasta (`python 01_export/scripts/export_sales.py`) e em seguida o gate de auditoria (`python 02_audit/scripts/audit_file.py`), certificando o sucesso completo da cadeia.
  - **Critério de Sucesso:** Robô de exportação e auditoria executados com sucesso e arquivo Excel gerado na pasta final `C:\Projetos\Inova\shared\data\`.

- [ ] **Tarefa 4.2 — Limpeza do Projeto de Origem:**
  - **O que fazer:** Apagar os arquivos de Peças legados de `dashboard-inova-data-export` (`src/07_export_sales.py`, specs e plans de vendas).
  - **Critério de Sucesso:** Arquivos removidos da origem, mantendo-a limpa para próximas exportações.

---

## 🔒 TRAVA DE SEGURANÇA (STANDBY MODE)

Este plano de migração modular foi gerado de acordo com as diretrizes do ecossistema Stout. 
Nenhuma alteração física ou cópia foi efetuada nos diretórios.

**Aguardando aprovação humana explícita do Victor no chat para avançar à fase de Execução da Migração (`/build`).**
