# ESPECIFICAÇÃO TÉCNICA (spec_v1_autodetect_concurrency.md)

> **STATUS:** APROVADO / CONFORMIDADE CDD
> **COMPONENTE:** `skills/stout-session-learning`
> **DATA DE CRIAÇÃO:** 2026-05-25

---

## 1. OBJETIVO E ENTENDIMENTO DO PROBLEMA

A skill `stout-session-learning` é responsável por consolidar de forma offline todo o aprendizado da sessão ativa (heurísticas, decisões e bugs mitigados), gravando-os em um banco de dados SQLite (`.stout/session_learning.db`) e mantendo a governança viva do projeto (`known_issues.md`, `evolution_backlog.md`, `aprendizados_sessao.md`).

### O Gargalo

No fluxo tradicional, o script programático central `stout-memory-capture.py` tentava ler dados da pasta `.stout/session_memory/raw`. Como esta pasta permanece vazia durante sessões puras do Antigravity CLI (cujos transcripts são gravados em logs centrais do AppData), a execução abortava silenciosamente:

```text
[stout-memory] Nenhuma raw memory ou transcript encontrado. Abortando.
```text

Isso resultava na não persistência dos aprendizados, falha de rastreabilidade de bugs conhecidos e quebra silenciosa da governança cognitiva ao final da sessão.

---

## 2. PROPOSTA DE ARQUITETURA E FLUXO DE DADOS

Para sanar este problema de forma totalmente autônoma, robusta a concorrência e livre de digitação manual de caminhos complexos, a especificação técnica prevê duas principais inovações arquiteturais:

### A. Hierarquia Inteligente de Resolução de Transcript

O script programático `stout-memory-capture.py` tentará localizar o `transcript.jsonl` da sessão ativa de forma dinâmica, seguindo a hierarquia abaixo:

1. **CLI Flag (`--conversation-id` / `--conv-id`)**: Se informado de forma explícita pelo console.
2. **Env Vars de Sessão (`GEMINI_CONVERSATION_ID` / `CONVERSATION_ID`)**: Injetadas no terminal ativo gerenciado pelo Antigravity CLI.
3. **Persistência Local do Projeto (`.stout/active/session.meta`)**: Arquivo JSON que registra localmente no projeto qual ID de sessão está ativo.
4. **Varredura Inteligente por Recência**: Filtra todos os transcripts na pasta `~/.gemini/antigravity-cli/brain/` modificados nas últimas 24 horas, elegendo o mais recente (com aviso de concorrência se múltiplos logs forem modificados nos últimos 10 minutos).

### B. Mecanismo de Auto-Registro (Self-Recording Session)

Na primeira execução da skill em cada turno (orquestrada nativamente pelo motor de regras CDD onde as variáveis de ambiente estão populadas), o script extrai o ID ativo e **grava localmente no projeto** o arquivo `.stout/active/session.meta` no formato:

```json
{
  "conversation_id": "f201be5c-cd94-4f0a-bca3-20a411a021d5",
  "updated_at": "2026-05-25T20:25:23Z"
}
```text

Isso permite que qualquer chamada manual posterior em terminais comuns (neutros, sem variáveis de ambiente) saiba exatamente a qual transcript no AppData aquela pasta local de projeto está vinculada.

---

## 3. ESPECIFICAÇÃO DE MUDANÇAS FÍSICAS

A modificação cirúrgica afeta dois scripts:

1. A skill local ativa: `skills/stout-session-learning/scripts/stout-memory-capture.py`
2. O template de inicialização de projetos: `skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py`

### Funções a serem Adicionadas/Modificadas

#### `persist_session_id(active_dir: str, conv_id: str)`

Escreve de forma idempotente e atômica o arquivo `session.meta` no diretório informado.

#### `autodetect_transcript(active_dir: str, specified_conv_id: Optional[str] = None) -> Optional[str]`

Executa a busca hierárquica pelo transcript no sistema local. Implementa um scanner que lê `Path.home() / ".gemini" / "antigravity-cli" / "brain"`.
Inclui o log defensivo caso detecte mais de 1 transcript modificado nos últimos 10 minutos (concorrência).

#### Modificação no CLI Parser

Adição do argumento `--conversation-id` (ou `--conv-id`).

---

## 4. CRITÉRIOS DE ACEITAÇÃO E VALIDAÇÃO BDD

### Cenário 1: Primeira execução da skill na sessão CLI

* **Dado que** o script roda no terminal do Antigravity CLI (onde `CONVERSATION_ID` está preenchido)
* **Quando** for executado sem parâmetros de entrada
* **Então** ele deve persistir o ID em `.stout/active/session.meta`
* **E** processar o transcript do AppData correspondente com sucesso.

### Cenário 2: Execuções manuais subsequentes em console comum

* **Dado que** o arquivo `.stout/active/session.meta` já foi gerado no projeto
* **E** o script é chamado em um console comum sem variáveis de ambiente
* **Quando** for executado sem parâmetros de entrada
* **Então** ele deve ler o ID persistido no arquivo local
* **E** carregar o transcript do AppData correspondente de forma totalmente automática.

### Cenário 3: Resolução de Concorrência ativa

* **Dado que** existam múltiplos transcripts modificados nos últimos 10 minutos
* **E** o script não encontre registro local nem variáveis de ambiente
* **Quando** for executado sem parâmetros de entrada
* **Então** ele deve emitir um log de alerta `[stout-memory] ⚠️ MÚLTIPLAS SESSÕES ATIVAS DETECTADAS!` listando os IDs
* **E** assumir o mais recente por data de modificação como fallback seguro.

### Cenário 4: Forçamento Manual por ID

* **Dado que** existam múltiplas sessões
* **Quando** o script for executado passando a flag `--conversation-id <id>`
* **Então** ele deve ignorar fallbacks e carregar o transcript exato da sessão especificada.

---

## 5. PLANO DE VALIDAÇÃO TÉCNICA

1. **Cenário de Testes E2E**: Rodar a suite geral do projeto via:

   `python -m pytest tests/ -v`

2. **Execução Local**: Validar a execução no projeto atual, certificando-se de que a indexação no SQLite (`.stout/session_learning.db`) e o Markdown (`aprendizados_sessao.md`) são criados/atualizados com sucesso.
