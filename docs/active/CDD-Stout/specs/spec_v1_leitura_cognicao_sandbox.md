# 📑 Especificação Técnica: Resolução de Caminhos Globais no Sandbox (Leituras de Cognição)

> **Status:** READY FOR DEV (Certificado por stout-spec-validation)
> **Versão:** Spec v2.0
> **ID da Spec:** `spec_v1_leitura_cognicao_sandbox`
> **Projeto:** Stout Lab CDD (Motor CDD)
> **Data:** 2026-05-28
> **Autor:** Gemini CLI CDD Architect
> **Herança:** [Roadmap Consolidado V4.9 / V5.0](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/docs/plans/roadmap_consolidado.md)

---

## 🎯 1. Objetivo e Motivação

Durante a execução de regras de negócio que envolvem a **Camada de Cognição Ativa** e o salvamento unificado de sessões (ex: integração do `ContextAgent` global em `~/.shared-ai-memory` ou acionamento de skills em `~/.gemini`), o motor CDD lança uma exceção de segurança (`PermissionError`) por violação de fronteira do `SkillSandbox` (V4.9).

Essa falha ocorre porque a whitelist de diretórios permitidos em `src/config.py` (`sandbox_allowed_dirs`) está restrita apenas ao escopo do workspace local e não suporta a resolução dinâmica de caminhos globais referenciando a pasta home (`~` ou `%USERPROFILE%`) do desenvolvedor no Windows.

Esta especificação define a ampliação segura e a resolução de caminhos dinâmicos no sandbox para reabilitar as interações cognitivas globais.

---

## 📋 2. Declaração de Requisitos (SOW / AC)

Para fins de rastreabilidade e governança técnica, definimos os seguintes Critérios de Aceitação (SOW):
* **AC-1:** O motor CDD deve ser capaz de salvar e ler dados legítimos da Camada de Cognição Ativa localizados no diretório global do desenvolvedor (`~/.shared-ai-memory` e `~/.gemini/config/skills`).
* **AC-2:** A proteção de isolamento (`SkillSandbox`) deve permanecer ativada e bloqueando ativamente tentativas de path traversal ou acesso a caminhos não-permitidos a partir das novas raízes adicionadas.

---

## 🛠️ 3. Requisitos Funcionais (FR)

* **FR-001:** O `SkillSandbox` deve suportar a especificação de caminhos relativos ao home directory (usando `~` ou `%USERPROFILE%`) em sua lista de diretórios autorizados.
  * *Implements:* AC-1
* **FR-002:** O sandbox deve expandir e resolver dinamicamente esses caminhos na inicialização para mapear o home directory real do Windows (`C:\Users\victor.bernardi`).
  * *Implements:* AC-1
* **FR-003:** O motor CDD deve ser capaz de executar com sucesso a sincronização do Context Agent (`context_manager.py`) localizado fora do workspace sem disparar bloqueios.
  * *Implements:* AC-1

---

## 🛡️ 4. Requisitos Não-Funcionais (NFR)

* **NFR-001:** O sandbox de execução deve continuar ativo e impondo restrições rígidas a diretórios e binários não autorizados.
  * *Validates:* AC-2
  * *Rationale:* Evitar overreach agêntico ou execução de scripts maliciosos fora das fronteiras delimitadas.
* **NFR-002:** A expansão de caminhos dinâmicos deve ser compatível com a formatação do sistema operacional Windows (normalização de barras e caminhos absolutos).
  * *Validates:* AC-1
  * *Rationale:* Garantir interoperabilidade sem requerer alterações no runtime nativo.
* **NFR-003:** A resolução de caminhos no sandbox deve ser tolerante a diretórios inexistentes em tempo de compilação ou inicialização (`strict=False`).
  * *Validates:* AC-1
  * *Rationale:* Evitar que o motor sofra falhas catastróficas em sua inicialização em novos workspaces ou ambientes efêmeros.

---

## 🔍 5. Matriz de Rastreabilidade

| SOW (Acceptance Criteria) | Functional Requirement (FR) | Test Scenario (Test) | Non-Functional Req (NFR) |
| :--- | :--- | :--- | :--- |
| **AC-1** | FR-001, FR-002, FR-003 | T-001, T-003 | NFR-002, NFR-003 |
| **AC-2** | - | T-002 | NFR-001 |

---

## 🏗️ 6. Arquitetura e Mudanças Propostas

### 6.1. Whitelist Declarativa
No arquivo [src/config.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/src/config.py), os diretórios globais de cognição serão adicionados à lista `sandbox_allowed_dirs`:

```python
sandbox_allowed_dirs: List[str] = [
    "src/tools", 
    "Research", 
    "tests", 
    "src/distributed",
    "~/.shared-ai-memory",
    "~/.gemini"
]
```

### 6.2. Resolução Dinâmica de Diretórios Permitidos
No construtor `__init__` da classe `SkillSandbox` em [src/core/sandbox.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/src/core/sandbox.py), alteramos a inicialização de `self.allowed_dirs` para expandir o home directory e resolver os caminhos absolutos de forma tolerante (`strict=False`):

```python
self.allowed_dirs = [Path(d).expanduser().resolve(strict=False) for d in config.sandbox_allowed_dirs]
```

---

## 🧪 7. Plano de Testes e Validação

### T-001: Validação de Permissão em Caminho Global
* **Tipo:** Unidade / Automatizado
* **FR Associado:** FR-001, FR-002
* **Objetivo:** Garantir que o `SkillSandbox` permite executar scripts válidos localizados dentro de caminhos globais contendo `~`.
* **Comando:** `pytest tests/test_sandbox.py::test_sandbox_allows_expanded_global_paths`

### T-002: Bloqueio de Path Traversal
* **Tipo:** Unidade / Automatizado
* **FR Associado:** NFR-001
* **Objetivo:** Garantir que tentativas de usar caminhos relativos de fuga (`..`) a partir das pastas globais whitelistadas continuam levantando `PermissionError`.
* **Comando:** `pytest tests/test_sandbox.py::test_sandbox_blocks_path_traversal_on_expanded_paths`

### T-003: Validação de Regressão CDD
* **Tipo:** Integração / E2E
* **FR Associado:** FR-003, NFR-003
* **Objetivo:** Garantir que a baseline histórica de 32 cenários E2E permanece estável e livre de falhas de regressão.
* **Comando:** `pytest tests/ -v`

