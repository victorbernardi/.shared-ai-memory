# Protocolo Universal de Governança e Imutabilidade V2.0 (Stout Edition)

> [!CAUTION]
> **[STOUT-IMMUTABLE]** — Este documento é protegido por trava física.
> O uso de `write_file` é BLOQUEADO pelo Guardrail V2.0. Use apenas `replace`.

Este documento é a **Fonte de Verdade Única** para o uso de ferramentas no ecossistema Antigravity/Gemini CLI.
 A adesão a este protocolo é obrigatória e monitorada deterministicamente pelo Guardrail do sistema.

## 1. Regra de Ouro: O Fluxo de Imutabilidade

A integridade do código e a eficiência de tokens dependem do cumprimento rigoroso do fluxo **Check-Read-Edit**.

### 🔄 Fluxo Obrigatório Antes de Qualquer Ação
1.  **Verificação de Existência:** Executar `list_dir` (Antigravity) ou `list_directory` (Gemini CLI) para validar o estado do arquivo.
2.  **Aquisição de Contexto (Obrigatório se existir):** Executar `view_file` (Antigravity) ou `read_file` (Gemini CLI).
    -   **Regra de Eficiência (200 Linhas):** Para arquivos com mais de 200 linhas, é OBRIGATÓRIO o uso de leitura cirúrgica (`start_line`, `end_line`).
3.  **Execução de Edição:** Aplicar a alteração via `replace` ou `multi_replace`.

---

## 2. Matriz de Ferramentas Bilíngue

O sistema opera em modo bilíngue. O Guardrail traduz e valida as intenções em ambos os ambientes:

| Categoria | Gemini CLI | Antigravity | Regra de Governança |
| :--- | :--- | :--- | :--- |
| **Pesquisa** | `grep_search` | `grep_search` | Livre para descoberta de padrões. |
| **Navegação** | `list_directory` / `glob` | `list_dir` | **Obrigatória** antes de criar novos arquivos. |
| **Leitura** | `read_file` | `view_file` | **Obrigatória** antes de edições. Respeitar limite de 200 linhas. |
| **Escrita** | `write_file` | `write_to_file` | **BLOQUEADA** se o arquivo já existir. |
| **Edição** | `replace` / `multi_replace` | `replace_file_content` | Permitida apenas após leitura comprovada. |
| **Execução** | `run_shell_command` | `run_command` | Gera log em `failure-log.md` se Exit Code != 0. |

---

## 3. Whitelist de Exceção (Livre Parcialmente)

O Protocolo de Imutabilidade (bloqueio de `write_file`) **NÃO** se aplica aos seguintes casos, permitindo agilidade em telemetria e diagnóstico:

-   Diretório `notes/` (Logs de falha, métricas, dashboards).
-   Arquivos e pastas com prefixo `temp_`.
-   Arquivos com extensão `*.log`.
-   Diretório `.GCC/` (Gestão de ramos e checkpoints).

---

## 4. Camadas de Defesa (Guardrail)

O cumprimento deste protocolo é garantido por três camadas:

1.  **Camada Cognitiva:** Este documento e as instruções no `GEMINI.md`.
2.  **Camada de Runtime (Python):** Script `src/core/guardrail.py` que intercepta e bloqueia ações fora do padrão.
3.  **Camada de Shell (PowerShell):** Script `src/core/write_guard.ps1` que atua como última barreira física no sistema operacional.

---

## 5. Padrão Ouro de Migração (Copy Folder + Replace)

Para evoluir ou "Stout-ificar" skills globais sem perda de inteligência ou infraestrutura, o agente DEVE seguir este protocolo:

-   **PROIBIDO:** Migrar apenas o arquivo `SKILL.md` (alto risco de transformar a skill em uma "casca vazia").
-   **OBRIGATÓRIO:** 
    1.  **Discovery:** Listar recursivamente o diretório de origem para identificar subpastas (`/scripts`, `/references`, `/addons`).
    2.  **Cópia Integral:** Copiar a PASTA INTEIRA da skill global para o novo diretório local.
    3.  **Refatoração:** Utilizar EXCLUSIVAMENTE a ferramenta `replace` para modificações cirúrgicas.
    4.  **Selo:** Injetar o selo `[STOUT-IMMUTABLE]` em todos os documentos críticos da nova pasta.

---

> [!CAUTION]
> A violação persistente deste protocolo ou falha no validador físico resultará na criação do `.audit_gate`, travando o sistema para auditoria humana.
