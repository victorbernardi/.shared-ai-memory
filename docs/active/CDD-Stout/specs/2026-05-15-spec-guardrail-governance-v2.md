# Especificação Técnica: Guardrail de Governança Bilíngue V2.0

**Data:** 2026-05-15
**Status:** Validado via Brainstorming
**Ramo GCC:** `guardrail_v2_dev`

## 1. Objetivo
Implementar uma Camada de Governança e Tradução Universal que padroniza o uso de ferramentas entre Gemini CLI e Antigravity, garantindo imutabilidade de arquivos, leitura contextual obrigatória e eficiência de tokens.

## 2. Requisitos Funcionais

### 2.1. Matriz de Mapeamento Bilíngue
O sistema deve reconhecer e validar as ferramentas equivalentes:

| Categoria | Gemini CLI | Antigravity | Regra de Governança |
| :--- | :--- | :--- | :--- |
| **Pesquisa** | `grep_search` | `grep_search` | Livre |
| **Navegação** | `list_directory` | `list_dir` | **Mandatória** antes de criar arquivos |
| **Leitura** | `read_file` | `view_file` | **Mandatória** antes de editar. Otimizar se > 200 linhas. |
| **Escrita** | `write_file` | `write_to_file` | **BLOQUEADA** se o arquivo já existir. |
| **Edição** | `replace` | `replace_file_content` | Permitida apenas após leitura comprovada. |
| **Execução** | `run_shell_command` | `run_command` | Gera log automático em caso de erro (Exit Code != 0). |

### 2.2. Protocolo de Imutabilidade (Hardened)
- Bloqueio determinístico de ferramentas de "Escrita Total" em arquivos existentes.
- **Exceção (Whitelist):** Diretórios `notes/`, `temp_` e arquivos `*.log` são isentos de trava.

### 2.3. Otimização de Contexto (Token Efficiency)
- Para arquivos com **mais de 200 linhas**, o agente DEVE usar leitura cirúrgica (`start_line`, `end_line`) em vez de leitura integral.
- O Guardrail emitirá um aviso se uma leitura integral de arquivo grande for detectada.

### 2.4. Fluxo de Trabalho Obrigatório
1. `Verificar Existência` (`list_dir` / `list_directory`).
2. `Ler Contexto` (`view_file` / `read_file`) -> *Obrigatório para arquivos existentes.*
3. `Editar` (`replace` / `replace_file_content`).

## 3. Arquitetura e Implementação

### 3.1. Detecção de Ambiente
O sistema utilizará a variável `STOUT_CLI_MODE` (valores: `GEMINI` ou `ANTIGRAVITY`). Na ausência da variável, tentará detectar ferramentas nativas no PATH.

### 3.2. Camadas de Defesa
1. **Cognitiva:** Atualização do `GEMINI.md` com as novas regras.
2. **Runtime (Python):** Refatoração do `src/core/guardrail.py` para suportar a matriz completa e a lógica de 200 linhas.
3. **Shell (PowerShell):** Implementação de `src/core/write_guard.ps1` como última linha de defesa física.

## 4. Plano de Validação (Testes)
- [ ] Testar bloqueio de `write_file` em arquivo `.py` existente.
- [ ] Testar permissão de `write_file` em `notes/test.log`.
- [ ] Testar se o sistema reconhece comandos Antigravity e aplica as mesmas travas.
- [ ] Validar aviso de eficiência em arquivo de 300 linhas.

## 5. Log de Decisões
- **Decisão:** Liberdade parcial para logs e temporários para evitar deadlocks de telemetria.
- **Decisão:** Limite de 200 linhas para leitura cirúrgica visando economia de tokens em contextos longos.
- **Decisão:** Uso de Branch GCC para isolamento de testes.
