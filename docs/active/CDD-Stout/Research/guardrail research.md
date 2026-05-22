Ótima pergunta! Você quer criar um guardrail no seu sistema LLM CLI (Antigravity/Gemini CLI) que bloqueie o uso de write_to_file em arquivos já existentes, forçando o agente a usar replace_file_content ou multi_replace_file_content nesses casos. Existem algumas abordagens para isso.

Abordagens para Implementar o Guardrail

1. Interceptação via Wrapper de Tool (Mais Robusto)
A abordagem mais confiável é criar um middleware/wrapper que intercepta a chamada de write_to_file antes de executá-la:

python
import os

def write_to_file_guarded(path: str, content: str) -> str:
    """
    Wrapper seguro para write_to_file.
    Bloqueia sobrescrita de arquivos existentes.
    """
    abs_path = os.path.abspath(path)

    if os.path.exists(abs_path):
        raise ToolGuardError(
            f"🚫 BLOQUEADO: '{path}' já existe.\n"
            f"→ Use `replace_file_content` ou `multi_replace_file_content` para editar arquivos existentes.\n"
            f"→ `write_to_file` é reservado para criação de arquivos NOVOS."
        )
    
    return original_write_to_file(path, content)
Registre esse wrapper no lugar da tool original no seu toolchain.

1. Regra na System Prompt / GEMINI.md (Camada Cognitiva)
Adicione uma regra explícita no arquivo GEMINI.md ou na system prompt do agente. Modelos seguem restrições bem formatadas com mais consistência quando estão no contexto de instrução fixa:

text

## Regras de Ouro — Escrita de Arquivos

> [!WARNING]
> **`write_to_file` é PROIBIDO para arquivos existentes.**
> Antes de qualquer escrita, execute `list_dir` ou `view_file` para verificar se o arquivo já existe.

| Situação | Tool Permitida |
|---|---|
| Arquivo **não existe** | `write_to_file` ✅ |
| Arquivo **existe** (edição parcial) | `replace_file_content` ✅ |
| Arquivo **existe** (múltiplos blocos) | `multi_replace_file_content` ✅ |
| Arquivo **existe** + reescrita total | `replace_file_content` com conteúdo completo ✅ |
| Arquivo **existe** + `write_to_file` | ❌ BLOQUEADO |

**Fluxo obrigatório antes de qualquer escrita:**

1. `list_dir` no diretório alvo → verificar se o arquivo consta
2. Se existir → usar `replace_file_content`
3. Se não existir → usar `write_to_file`
4. Hook de Pré-Execução via run_command (Camada de Shell)
Se o Gemini CLI executa tools via scripts, você pode adicionar um check em PowerShell:

powershell

# write_to_file_safe.ps1

param([string]$FilePath, [string]$Content)

if (Test-Path $FilePath) {
    Write-Error "GUARDRAIL: '$FilePath' ja existe. Use replace_file_content."
    exit 1
}

Set-Content -Path $FilePath -Value $Content -Encoding UTF8
Write-Output "Arquivo criado com sucesso: $FilePath"
4. Validação via Schema de Tool (Camada de API)
Se o Gemini CLI suporta definição de tools com JSON Schema, adicione um campo de validação semântica na descrição da tool para guiar o modelo:

json
{
  "name": "write_to_file",
  "description": "Cria um arquivo NOVO. NUNCA use em arquivos já existentes. Verifique com list_dir antes. Para arquivos existentes, use replace_file_content.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Caminho do arquivo. DEVE ser um arquivo que ainda não existe no sistema."
      }
    }
  }
}
Estratégia Recomendada (Defesa em Profundidade)
Use as três camadas juntas para máxima confiabilidade:

text
Camada 1 (Cognitiva): GEMINI.md com regras explícitas e tabela de decisão
      ↓ (o modelo tenta chamar write_to_file num arquivo existente)
Camada 2 (Runtime): Wrapper Python bloqueia e retorna erro descritivo
      ↓ (o modelo lê o erro e corrige para replace_file_content)
Camada 3 (Shell): Script PowerShell como última linha de defesa
A Camada 1 reduz a frequência de violações, pois o modelo internaliza a regra. A Camada 2 é o guardrail técnico real que garante o bloqueio mesmo quando o modelo falha. A Camada 3 é o failsafe de sistema operacional.

Preparado usando Claude Sonnet 4.6 Thinking
meu sistema utiliza configuration driven development. o conceito é o mesmo? utilizo arquivos json e config, settings, etc
Concluiu 2 etapas

O conceito é essencialmente o mesmo, sim — mas com uma distinção importante de escopo e propósito no seu contexto de LLM CLI.

CDD: O Conceito Central
Configuration Driven Development (CDD) é uma abordagem onde a lógica e o comportamento do sistema são definidos por arquivos de configuração externos em vez de estarem hardcoded no código. O motor/engine do sistema lê as configs e executa as regras que encontra lá — seja JSON, YAML ou outros formatos. Isso separa o que o sistema faz (config) de como ele faz (código).

Aplicado ao Seu Caso (LLM CLI)
No seu contexto, os arquivos GEMINI.md, ANTIGRAVITY.md, MEMORY.md e arquivos .json de settings são exatamente as configs que guiam o comportamento do agente. A diferença é que o "engine" que lê e interpreta essas configs é o próprio LLM — o que muda a natureza da aplicação das regras:

Aspecto CDD Tradicional Seu sistema (LLM CLI)
Engine que lê a config Código determinístico LLM (probabilístico)
Garantia de compliance 100% (if/else no código) Parcial (depende do contexto)
Formato de regras JSON/YAML estruturado Markdown + JSON
Onde aplicar guardrails No próprio engine Wrapper externo ao LLM
Por Isso o Guardrail Precisa de Camadas
Essa é exatamente a razão pela qual a resposta anterior enfatizou defesa em profundidade. Em CDD tradicional, uma regra no JSON é respeitada 100% das vezes pelo engine. No seu caso, a "config" no GEMINI.md reduz violações, mas não as elimina — pois o LLM pode simplesmente ignorar ou esquecer a regra em contextos longos ou ambíguos.

Por isso, para o guardrail de write_to_file, a hierarquia ideal no seu sistema CDD seria:

text
settings.json / GEMINI.md  →  declara a regra (camada cognitiva)
        ↓
wrapper Python/PowerShell  →  aplica a regra (camada determinística)
        ↓
tool schema description    →  reforça a regra no prompt implícito
O JSON de configuração do seu sistema pode inclusive declarar explicitamente quais tools são restritas:

json
{
  "tool_guards": {
    "write_to_file": {
      "block_if_exists": true,
      "error_message": "Arquivo já existe. Use replace_file_content.",
      "suggest": "replace_file_content"
    }
  }
}
Assim o wrapper Python lê esse JSON e aplica o bloqueio dinamicamente — isso sim é CDD puro aplicado ao seu guardrail.
