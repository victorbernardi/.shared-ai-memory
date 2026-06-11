# Plan: Branch Policy and Git Hooks Remediation

**Data:** 2026-06-02
**Status:** Aguardando Aprovação Humana (Fase de Strategy)
**Autor:** Antigravity (IA Coding Assistant)

---

## 1. Contexto de Repositórios (Monorepo vs. Repositórios Isolados)

A auditoria identificou que a proteção dos subprojetos funciona em dois níveis:

1. **Nível Monorepo (Centralizado):**
   * Os repositórios pais `C:\Projetos\Inova` e `C:\Projetos\Stout` monitoram todos os subprojetos que não possuem `.git` local (como `02_Faturamento`, `Skill-Folder-Pattern`, `Transcricoes`, etc.).
   * A ativação dos hooks nas raízes pais protege automaticamente estes subprojetos dependentes.

2. **Nível Isolado (Individual):**
   * Subprojetos inicializados com repositório Git próprio (como `Configuration-Driven Development` e `NotebookLM`) ignoram os hooks da raiz pai. Eles necessitam de hooks locais instalados em seus respectivos diretórios `.git`.

---

## 2. Detalhamento das Tarefas de Remediação

### TASK-01 — Ativação no Repositório Pai `Inova` (Cobrindo todos os subprojetos de Inova)
* **Objetivo:** Ativar a trava de branch para todos os subprojetos do monorepo Inova (ex: `02_Faturamento`, `pricewatch-jd`, etc.).
* **Ações:**
  * Copiar o validador base do CDD localizado em [branch_policy_validator.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/templates/cdd/src/branch_policy_validator.py) para a raiz do repositório em `C:\Projetos\Inova\branch_policy_validator.py`.
* **Critério de Aceitação:** Arquivo presente na raiz do Inova; tentativa de commit em subprojeto com branch errada bloqueada pelo hook.

### TASK-02 — Configuração de Hooks no Subprojeto Git Isolado `Configuration-Driven Development`
* **Objetivo:** Proteger o repositório isolado do próprio CDD.
* **Ações:**
  * Copiar o hook [pre-commit](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/templates/cdd/hooks/pre-commit) para `C:\Projetos\Stout\Projetos\Configuration-Driven Development\.git\hooks\pre-commit`.
  * Copiar o hook [commit-msg](file:///C:/Projetos/Stout/.git/hooks/commit-msg) para `C:\Projetos\Stout\Projetos\Configuration-Driven Development\.git\hooks\commit-msg`.
  * Copiar o validador [branch_policy_validator.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/templates/cdd/src/branch_policy_validator.py) para `C:\Projetos\Stout\Projetos\Configuration-Driven Development\src\branch_policy_validator.py`.
* **Critério de Aceitação:** Hooks instalados e operacionais.

### TASK-03 — Configuração de Hooks no Subprojeto Git Isolado `NotebookLM`
* **Objetivo:** Proteger o repositório isolado do subprojeto NotebookLM.
* **Ações:**
  * Copiar o hook `pre-commit` para `C:\Projetos\Stout\Projetos\NotebookLM\.git\hooks\pre-commit`.
  * Copiar o hook `commit-msg` para `C:\Projetos\Stout\Projetos\NotebookLM\.git\hooks\commit-msg`.
  * Copiar o validador `branch_policy_validator.py` para `C:\Projetos\Stout\Projetos\NotebookLM\src\branch_policy_validator.py`.
* **Critério de Aceitação:** Hooks instalados e operacionais.

### TASK-04 — Validação Prática e Homologação
* **Objetivo:** Testar e comprovar a segurança em todos os níveis.
* **Ações:**
  * Simular commits com branches incorretas nos repositórios `Inova` (pai), `CDD` (isolado) e `NotebookLM` (isolado).
  * Confirmar exibição do feedback e interrupção do commit.

---

## 3. Plano de Rollback

* A remoção do arquivo `pre-commit` do diretório `.git/hooks/` de qualquer repositório desativa instantaneamente as travas físicas sem risco de corromper o repositório.
