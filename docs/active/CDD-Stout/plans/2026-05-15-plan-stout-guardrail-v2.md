# Implementation Plan: Guardrail de Imutabilidade V2.0

**Data:** 2026-05-15
**Status:** Aguardando Aprovação
**Autor:** Gemini CLI Builder

## 1. Problema e Justificativa
O sistema atual permite o uso indiscriminado de `write_file`, o que sobrescreve arquivos existentes de forma não cirúrgica, causando perda de histórico, fragmentação de código e retrabalho manual. O primeiro Guardrail implementado foi incompleto por não contemplar todas as ferramentas de edição válidas.

## 2. Objetivos
- Implementar um bloqueio determinístico que impede o uso de `write_file` em arquivos que já existem.
- Permitir explicitamente as ferramentas de edição cirúrgica: `replace` e `multi_replace`.
- **Garantir a integridade contextual:** Impor a leitura obrigatória (`read_file`) de QUALQUER arquivo antes de uma tentativa de edição.
- Garantir que a falha de processo (pular o plano) seja corrigida com documentação robusta.

## 3. Matriz de Decisão de Ferramentas

| Situação | Ferramenta Permitida | Status Guardrail |
| :--- | :--- | :--- |
| Arquivo **NÃO EXISTE** | `write_file` | ✅ PERMITIDO |
| Arquivo **EXISTE** (Edição simples) | `replace` | ✅ PERMITIDO (Após `read_file`) |
| Arquivo **EXISTE** (Edição múltipla) | `multi_replace` | ✅ PERMITIDO (Após `read_file`) |
| Arquivo **EXISTE** (Reescrita total) | `replace` (com conteúdo completo) | ✅ PERMITIDO (Após `read_file`) |
| Arquivo **EXISTE** + `write_file` | `write_file` | ❌ BLOQUEADO |

> [!IMPORTANT]
> **Obrigação de Contexto:** Antes de qualquer alteração (`replace`/`multi_replace`), o agente DEVE obrigatoriamente executar `read_file` (mesmo que parcial) para confirmar o estado atual do código. Isso evita edições baseadas em contexto obsoleto.

### 🔄 Fluxo Obrigatório Antes de Qualquer Escrita

1. **Verificação de Existência:** Executar `list_dir` no diretório alvo.
2. **Aquisição de Contexto (Se o arquivo existe):** Executar OBRIGATORIAMENTE `read_file` para ler o bloco a ser alterado.
3. **Decisão de Ferramenta:**
   - **Arquivo EXISTE:** Usar `replace_file_content` ou `multi_replace_file_content`.
   - **Arquivo NÃO EXISTE:** Usar `write_to_file`.

## 4. Etapas de Implementação

### 4.1. Camada de Runtime: Refatoração do Script de Guardrail (`src/core/guardrail.py`)
- Atualizar a lógica para aceitar uma lista de ferramentas permitidas.
- Bloquear deterministicamente `write_file` (ou `write_to_file`) se o arquivo existir.

### 4.2. Camada de Shell: Hook de Pré-Execução (PowerShell)
- Implementar um script `src/core/write_guard.ps1` que atua como última linha de defesa.
- Este script será chamado via `run_shell_command` para validações físicas em tempo real antes de escritas críticas.

```powershell
# Exemplo de lógica para o write_guard.ps1
param([string]$FilePath)
if (Test-Path $FilePath) {
    Write-Error "GUARDRAIL: '$FilePath' já existe. Use replace_file_content."
    exit 1
}
```

### 4.3. Atualização da Governança (Documentação)
- Atualizar `GEMINI.md` e o Protocolo de Ferramentas com as camadas de defesa.

### 4.4. Refino das Regras CDD (`data/config/rules.yaml`)
- Integrar os hooks de pré-execução no motor de regras.

## 5. Estratégia de Defesa em Profundidade
1. **Camada 1 (Cognitiva):** GEMINI.md com regras e fluxo de verificação.
2. **Camada 2 (Runtime):** Script Python bloqueia e retorna erro descritivo.
3. **Camada 3 (Shell):** Script PowerShell como última linha de defesa.

## 5. Estratégia de Teste
- **Cenário 1:** Tentar `write_file` em arquivo novo -> Sucesso.
- **Cenário 2:** Tentar `write_file` em arquivo existente -> Bloqueio + Audit Gate.
- **Cenário 3:** Tentar `replace` em arquivo existente -> Sucesso.
- **Cenário 4:** Tentar `multi_replace` em arquivo existente -> Sucesso.

## 6. Próximos Passos
Após aprovação, proceder com a execução cirúrgica.
