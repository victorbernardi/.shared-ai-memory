# ESPECIFICAÇÃO TÉCNICA (spec_v2_autodetect_concurrency_multiagent.md)

> **STATUS:** 🟢 **READY FOR DEV** (Conformidade Stout Spec Validation 100% Validada)  
> **COMPONENTE:** `skills/stout-session-learning`  
> **DATA DE ATUALIZAÇÃO:** 2026-05-26  

---

## 1. ESCOPO E ARQUITETURA MULTICLIENTE

Esta especificação estende a governança cognitiva da skill `stout-session-learning` para operar de forma unificada e transparente em três interfaces distintas do ecossistema: **Antigravity CLI (antigo Gemini CLI)**, **CommandCode** e **Claude Desktop**. 

O motor programático `stout-memory-capture.py` atuará como um **parser polimórfico**, capaz de converter múltiplos formatos de logs e transcripts em uma estrutura de destilação neutra de aprendizados e bugs de sessão.

---

## 2. CRITÉRIOS DE ACEITAÇÃO (SOW Acceptance Criteria)

* **AC-1 [Detecção Automática e Parsing Polimórfico]**: O motor deve identificar automaticamente o cliente de IA ativo (Antigravity CLI, CommandCode ou Claude Desktop) e converter com sucesso logs JSONL estruturados e arrays de blocos em textos lineares limpos, sem estourar exceções.
* **AC-2 [Isolamento e Resiliência em Sandbox]**: O motor deve rodar em ambientes restritos (Sandboxes locais) usando o cache local `.stout/session_memory/raw/transcript.jsonl`. Se o host for acessível (Bypass ativo), o motor fará a varredura e cópia dinâmica sem interferência ou travamentos.
* **AC-3 [Persistência Dupla e Auto-Healing de Backlogs]**: Toda sessão destilada deve persistir fatos cognitivos no SQLite local do projeto e espelhar concorrentemente na Golden Copy central SQLite. Adicionalmente, markdowns locais em `/docs/governance/` devem ser auto-gerados e preenchidos com cabeçalhos de tabela rígidos caso estejam vazios ou ausentes, seguidos por escrita dupla na central global.
* **AC-4 [Retrofit e Consolidação Retroativa]**: A flag `--retrofit` deve vasculhar recursivamente múltiplos projetos no host, ingerir bancos SQLite e markdowns históricos contendo `aprendizado` ou `learning`, processar e deduplicar semântica e logicamente com similaridade $\ge 85\%$ e consolidar tudo na Golden Copy.

---

## 3. REQUISITOS FUNCIONAIS (Functional Requirements)

### A. Detecção e Parsing de Clientes

* **FR-001 [Parser Antigravity CLI]**: Lê objetos JSON do transcript em `~/.gemini/antigravity-cli/brain/<conv-id>/.system_generated/logs/transcript.jsonl`, extraindo linearmente os campos `source` e `content` textuais.  
  * *Implements*: AC-1
* **FR-002 [Parser CommandCode]**: Lê arquivos JSONL em `~/.commandcode/projects/<slug-do-projeto>/<session-id>.jsonl` e processa a chave `content` que é estruturada como um array de blocos. Concatena os subcampos `text` de todos os blocos de texto no array.  
  * *Implements*: AC-1
* **FR-003 [Parser Claude Desktop]**: Lê arquivos Markdown recentes (`.md`) no diretório global `~/.claude/projects/<slug-do-projeto>/memory/` (onde o slug do projeto é codificado com hífens duplos `--`).  
  * *Implements*: AC-1

### B. Isolamento e Sandbox (Ponte Cognitiva)

* **FR-004 [Mecanismo Local Path Priority]**: O script tenta prioritariamente abrir o cache local do projeto em `.stout/session_memory/raw/transcript.jsonl` quando executado dentro de sandboxes restritas.  
  * *Implements*: AC-2
* **FR-005 [Mecanismo Fallback & Copy]**: Se o cache local estiver vazio ou ausente e o Bypass de Sandbox estiver ativo, o script varre a home do host (`Path.home()`), detectando o cliente ativo via variáveis de ambiente (`COMMANDCODE_SESSION_ID`, `GEMINI_CONVERSATION_ID`, `CONVERSATION_ID`) ou mtime de arquivos modificado nos últimos 10 minutos (600 segundos). Copia o transcript de forma transparente para `.stout/session_memory/raw/transcript.jsonl`.  
  * *Implements*: AC-2

### C. Persistência Dupla e Auto-Healing

* **FR-006 [SQLite Local do Projeto]**: Grava os fatos e bugs destilados no SQLite local do projeto localizado em `.stout/session_learning.db` (Tabela `learning_facts`).  
  * *Implements*: AC-3
* **FR-007 [Golden SQLite Central]**: Espelha concorrentemente e de forma idempotente todos os fatos destilados para a base de longo prazo `C:\Users\victor.bernardi\.shared-ai-memory\session_learning_golden.db`.  
  * *Implements*: AC-3
* **FR-008 [Auto-Healing de Tabelas Locais]**: Se os arquivos `known_issues.md` ou `evolution_backlog.md` não existirem em `docs/governance/` (ou estiverem vazios), o script gera-os automaticamente com os cabeçalhos Markdown rígidos oficiais:
  * *Cabeçalho de Bugs (`known_issues.md`)*: `| Bug ID | Categoria | Descrição | Ocorrências | Workaround | Resolução | Status |`
  * *Cabeçalho de Melhorias (`evolution_backlog.md`)*: `| ID | Data | Origem (Sessão) | Proposta | Impacto | Prioridade | Status |`  
  * *Implements*: AC-3
* **FR-009 [Escrita Dupla e Auto-Healing Central Wiki]**: Atualiza a base de markdowns globais na Wiki em `C:\Users\victor.bernardi\.shared-ai-memory\docs\governance\known_issues_golden.md` e `evolution_backlog_golden.md`, auto-cicatrizando os cabeçalhos oficiais rígidos se necessário.  
  * *Implements*: AC-3

### D. Ingestão e Consolidação Retroativa (Retrofit)

* **FR-010 [Mecanismo Retrofit Varredura]**: Ao receber o argumento `--retrofit`, o script realiza varredura recursiva sob `C:\Projetos\` mapeando bancos SQLite locais `.stout/session_learning.db` e arquivos de aprendizados contendo padrões textuais `aprendizado` ou `learning` no nome.  
  * *Implements*: AC-4
* **FR-011 [Destilação Offline e Deduplicação Shingle]**: Ingere arquivos Markdown legados textuais avulsos acionando a lógica local da classe `OfflineDistiller` para estruturar fatos brutos. Deduplica logicamente os fatos agregados com base em similaridade de Shingle ($\ge 85\%$) antes de salvar na base consolidada, evitando repetições de fatos idênticos.  
  * *Implements*: AC-4
* **FR-012 [Git Hygiene & Propagação de Cópias]**: Garante de forma automatizada que a pasta local `.stout/` esteja registrada no arquivo `.gitignore` do repositório. Sincroniza e propaga as alterações do script para todas as 19 localizações físicas registradas.  
  * *Implements*: AC-3, AC-4

---

## 4. REQUISITOS NÃO-FUNCIONAIS (Non-Functional Requirements)

* **NFR-001 [Tempo de Resposta de Ingestão]**: A rotina padrão de ingestão e gravação de uma sessão ativa deve rodar em menos de **1.5 segundos**.  
  * *Validates*: AC-1
* **NFR-002 [Limite de Memória Heap]**: A rotina pesada de `--retrofit` recursivo no disco deve controlar o consumo de memória heap, não excedendo **256 MB** de pico no host Windows.  
  * *Validates*: AC-2, AC-4
* **NFR-003 [Segurança Concorrente SQLite]**: Toda gravação dupla concorrente na Golden Copy SQLite central deve utilizar transações isoladas (`IMMEDIATE` transaction mode) com tratamento explícito de exceção `sqlite3.OperationalError` (Database locked) e um timeout transacional máximo de **30 segundos** antes de retornar falha.  
  * *Validates*: AC-3
* **NFR-004 [Encoding Hardened & Falha Silenciosa]**: Toda leitura/escrita de arquivos deve forçar codificação de caracteres **UTF-8**. Erros de encoding ou caminhos inacessíveis devem ser capturados de forma robusta e persistidos silenciosamente em `notes/failure-log.md` (também em UTF-8) sem estourar exceções ou interromper a execução do fluxo de IA.  
  * *Validates*: AC-3, AC-4

---

## 5. PREMISSAS E SUPOSIÇÕES (Assumptions)

* **AS-001 [Acesso a Shared Memory Host]**: Assume-se que o diretório global da Shared Memory `C:\Users\victor.bernardi\.shared-ai-memory` está configurado corretamente e possui permissões de leitura/escrita habilitadas no host do usuário.
* **AS-002 [Runtime SQLite Nativo]**: Assume-se que o interpretador Python em uso no host possui o módulo nativo `sqlite3` compilado com suporte padrão a concorrência a nível de thread.

---

## 6. MATRIZ DE RASTREABILIDADE (Traceability Matrix)

| ID do AC | Requisito Funcional (FR) | Requisito Não-Funcional (NFR) | Caso de Teste (T) | Premissa / Suposição (AS) |
| :--- | :--- | :--- | :--- | :--- |
| **AC-1** | FR-001, FR-002, FR-003 | NFR-001 | T-001 | AS-001 |
| **AC-2** | FR-004, FR-005 | NFR-002 | T-002 | AS-001 |
| **AC-3** | FR-006, FR-007, FR-008, FR-009, FR-012 | NFR-003, NFR-004 | T-003, T-004 | AS-001, AS-002 |
| **AC-4** | FR-010, FR-011, FR-012 | NFR-002, NFR-004 | T-005 | AS-001, AS-002 |

---

## 7. CENÁRIOS DE TESTE BDD (Test Scenarios)

* **T-001 [Parser Polimórfico - CC vs AG]**:  
  * **Dado** arquivos de logs mockados do Antigravity (`transcript.jsonl` com `source`/`content`) e do CommandCode (`session.jsonl` com `role`/`content` array de blocos),  
  * **Quando** o parser polimórfico é executado sobre ambos,  
  * **Então** o texto de conversa deve ser extraído linearmente com sucesso e ambos os transcripts devem gerar fatos cognitivos corretos idênticos.  
  * *FR*: FR-001, FR-002
* **T-002 [Isolamento em Sandbox Restrita]**:  
  * **Dado** uma execução em contêiner de sandbox sem bypass onde a pasta de home do host é inacessível,  
  * **Quando** existe o arquivo local `.stout/session_memory/raw/transcript.jsonl`,  
  * **Então** o script deve rodar perfeitamente extraindo a conversa a partir do cache local, sem tentar varrer o host ou causar exceções de sistema.  
  * *FR*: FR-004
* **T-003 [Resiliência Concorrente Central SQLite]**:  
  * **Dado** duas instâncias simultâneas concorrentes do motor de captura tentando gravar fatos no banco central `session_learning_golden.db` no mesmo instante,  
  * **Quando** as transações concorrentes entram em contenção de locks,  
  * **Então** a biblioteca deve gerenciar a concorrência de forma limpa usando retentativas com timeout de 30s, completando ambas as gravações com sucesso sem corromper a base SQLite.  
  * *FR*: FR-007
* **T-004 [Auto-Healing de Markdowns Locais e Globais]**:  
  * **Dado** que os arquivos locais `known_issues.md` e `evolution_backlog.md` foram deletados de `docs/governance/`,  
  * **Quando** a rotina de sincronização é acionada,  
  * **Então** os arquivos devem ser gerados novamente com cabeçalhos Markdown idênticos e compatíveis, preenchendo as tabelas sem falhas de "replace".  
  * *FR*: FR-008, FR-009
* **T-005 [Varredura e Deduplicação do Retrofit]**:  
  * **Dado** uma pasta de testes contendo 3 arquivos Markdown legados com aprendizados avulsos redundantes sobre os mesmos bugs,  
  * **Quando** a rotina `python stout-memory-capture.py --retrofit` é executada,  
  * **Então** o script deve consolidar os arquivos deduplicando fatos com $\ge 85\%$ de similaridade, gerando apenas 1 registro único limpo no Golden DB e markdowns consolidados.  
  * *FR*: FR-010, FR-011

---

## 8. DEPENDÊNCIAS DE FASES DE EXECUÇÃO

| Fase da Implementação | Escopo Técnico | Depende de (Fases) |
| :--- | :--- | :--- |
| **Fase 1: Higiene Git** | Registro de `.stout/` no `.gitignore` | Nenhuma (Independente) |
| **Fase 2: Parsers Polimórficos** | Desenvolvimento de FR-001, FR-002, FR-003, FR-004 e FR-005 | Fase 1 |
| **Fase 3: Auto-Healing MDs** | Implementação de FR-008 e FR-009 | Fase 2 |
| **Fase 4: Gravação Dupla & Retrofit**| Implementação de FR-006, FR-007, FR-010, FR-011 | Fase 3 |
| **Fase 5: Sincronização Geral** | Propagação automatizada de scripts (FR-012) | Fase 4 |

---

## 9. REGRAS DE HIGIENE DO GIT

* O diretório `.stout/` (incluindo o SQLite local `.stout/session_learning.db` e as sessões ativas `.stout/active/`) é inserido no `.gitignore` e considerado **estritamente local**.
* Somente os markdowns declarativos e legíveis (`aprendizados_sessao.md` e os arquivos na pasta `docs/`) são versionados no Git do repositório do projeto.

m sucesso os fatos cognitivos locais de múltiplos diretórios de projetos na base central `session_learning_golden.db` sem gerar registros duplicados.
