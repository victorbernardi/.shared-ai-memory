# Mapeamento de Ferramentas Nativas Antigravity

Este documento é a referência oficial das ferramentas nativas (tools) disponíveis para o agente no ecossistema Antigravity. Ao escrever ou executar planos no Stout, utilize APENAS estas ferramentas para interagir com o sistema.

## Mapeamento Claude Code -> Gemini (Antigravity)

Caso encontre referências a ferramentas do Claude Code nas skills legadas, utilize a equivalência abaixo para a nossa API real atual:

| Referência na Skill (Claude) | Equivalente Antigravity Nativo |
|-----------------------------|-------------------------------|
| `Read` (file reading)       | `view_file` |
| `Write` (file creation)     | `write_to_file` |
| `Edit` (file editing)       | `replace_file_content` / `multi_replace_file_content` |
| `Bash` (run commands)       | `run_command` |
| `Grep` (search file content)| `grep_search` |
| `Glob` (search files by name) | `list_dir` (Navegação estruturada) |
| `TodoWrite` (task tracking) | Artefato `task` e arquivos em `./docs` |
| `Skill` tool (invoke a skill)| `view_file` em arquivos `.md` na pasta `skills/` |
| `WebSearch`                 | `search_web` (Fallback) |
| `WebFetch`                  | `read_url_content` |

## Ausência de Subagentes Genéricos
O ecossistema Antigravity **não possui suporte** nativo à delegação genérica de subagentes (como a tool `Task` do Claude ou subagentes como `codebase_investigator` ou `generalist`). 
Skills que dependam de despacho para subagentes devem fazer **fallback para execução em sessão única** através do sistema de planejamento (`/plan`). A única exceção é o `browser_subagent` para navegação visual web automatizada.

## Catálogo de Ferramentas e Regras de Ouro

### 1. Pesquisa e Navegação (Context Efficiency)
- `list_dir`: Lista arquivos e subpastas de um diretório absoluto.
- `grep_search`: Busca de texto super rápida e otimizada (via ripgrep). Suporta regex. **Sempre prefira isso no lugar de `view_file` para buscar onde uma variável é usada.**

### 2. Leitura e Edição (Cirúrgica)
- `view_file`: Lê conteúdo de arquivos.
- `write_to_file`: Sobrescreve ou cria arquivos completos. (Melhor para arquivos novos, curtos, ou criação de artefatos).
- `replace_file_content`: Substituição estrita exigindo bloco único idêntico. Use para manter a integridade de arquivos grandes sem reescrevê-los.
- `multi_replace_file_content`: Permite substituir múltiplos blocos não adjacentes em uma única chamada.

### 3. Execução de Comandos
- `run_command`: Executa scripts no Powershell.
  - **Regra de ouro:** Sempre utilize flags silenciosas (`--silent`, `-q`, `--no-pager`).
  - Retorna um background job ID se parametrizado com delay.
  - Pode interagir com jobs abertos usando `command_status` e `send_command_input`.

### 4. Memória, Web e Contexto Avançado

> [!IMPORTANT]
> **Arquitetura de Memória:**
> - **`GEMINI.md`**: Reservado para o CLI (telemetria e fatos nativos). **NÃO use `save_memory`**.
> - **`ANTIGRAVITY.md`**: Fonte de verdade estática do projeto (Bíblia).
> - **`MEMORY.md`**: Memória dinâmica gerida pelo `context-agent` (Use `context-agent save`).

- **Pesquisa Profissional (Tavily):** Utilize obrigatoriamente o servidor MCP `tavily-search`. A ferramenta nativa `search_web` é estritamente para fallback.
- **Documentação Técnica Avançada (Context7):** Utilize o servidor MCP `context7` para ingestão de documentação técnica externa de alta fidelidade. O uso de `read_url_content` deve ser evitado para documentação densa.
- **Gestão de Memória (Suíte Context-Agent):** Toda persistência de fatos e decisões de longo prazo deve ser orquestrada por esta suíte para garantir compressão e recuperação inteligente. 
- **Preservação de Contexto:** Utilize as skills de `context-management` para evitar a degradação da janela de contexto em sessões longas no Stout.
