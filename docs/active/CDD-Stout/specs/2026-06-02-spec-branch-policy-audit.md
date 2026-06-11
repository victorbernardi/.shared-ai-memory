# Spec: Git Hooks and Branch Policy Validation Audit

**Data:** 2026-06-02
**Status:** Concluído (Fase de Pesquisa)
**Autor:** Antigravity (IA Coding Assistant)

---

## 1. Objetivo

Identificar se os repositórios ativos do ecossistema (Stout e Inova) contêm os scripts e hooks necessários para garantir as travas físicas locais de branch e formato de commit.

---

## 2. Diagnóstico Empírico (Fase de Research)

Realizamos uma auditoria manual no sistema de arquivos local (`C:\Projetos\`) e identificamos as seguintes conformidades e lacunas:

### A. Repositório Pai: `C:\Projetos\Stout`
* **Status:** **100% Conforme**
* **Detalhamento:** 
  * Repositório Git ativo.
  * Possui o validador central [branch_policy_validator.py](file:///C:/Projetos/Stout/branch_policy_validator.py) na raiz.
  * Possui `.git/hooks/pre-commit` e `.git/hooks/commit-msg` instalados e operacionais (redirecionando a validação para o arquivo central em Python).

### B. Repositório Pai: `C:\Projetos\Inova`
* **Status:** **Incompleto (Falha Silenciosa)**
* **Detalhamento:** 
  * Repositório Git ativo.
  * Possui `.git/hooks/pre-commit` e `.git/hooks/commit-msg` instalados.
  * **Lacuna:** O validador central `branch_policy_validator.py` **não existe** no diretório (nem na raiz, nem em `src/`, nem em `shared/`). O hook de pre-commit detecta a ausência do script e passa sem fazer nenhuma validação (falha silenciosa).

### C. Subprojeto Isolado: `C:\Projetos\Stout\Projetos\Configuration-Driven Development`
* **Status:** **Incompleto**
* **Detalhamento:**
  * Embora esteja na árvore de arquivos de `Stout`, este subprojeto é um repositório Git independente (possui `.git/` próprio).
  * **Lacuna:** Não possui os hooks `.git/hooks/pre-commit` ou `.git/hooks/commit-msg` instalados localmente. Também não possui o script `branch_policy_validator.py` em sua raiz ou em `src/`. Se os commits forem executados dentro desta pasta, nenhuma trava é acionada.

### D. Subprojeto Isolado: `C:\Projetos\Stout\Projetos\NotebookLM`
* **Status:** **Incompleto**
* **Detalhamento:**
  * Subprojeto com repositório Git independente (`.git/` próprio).
  * **Lacuna:** Sem hooks ativos e sem o script validador instalado localmente.

### E. Outros Subprojetos (`Skill-Folder-Pattern` e `Transcricoes`)
* **Status:** **Conforme (via Herança)**
* **Detalhamento:** Não possuem repositório Git isolado. Portanto, herdam diretamente o `.git/` e as travas configuradas no repositório pai de `C:\Projetos\Stout`.

---

## 3. Resumo de Ações Necessárias

Para padronizar e blindar completamente o ecossistema, o plano de estratégia deverá contemplar:

1. **Correção do Inova:** Copiar o `branch_policy_validator.py` para a raiz de `C:\Projetos\Inova`.
2. **Correção dos Subprojetos Git Isolados:** Instalar os hooks locais e o script do validador em `Configuration-Driven Development` e `NotebookLM` para assegurar a proteção de commits caso a IA ou o usuário trabalhe diretamente em suas pastas independentes.

---

## 4. Referências locais de hooks de template
* Configuração base do addon: [templates/cdd/hooks/pre-commit](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/templates/cdd/hooks/pre-commit)
* Lógica base do validador: [templates/cdd/src/branch_policy_validator.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/templates/cdd/src/branch_policy_validator.py)
