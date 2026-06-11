# Spec: Robustez Transacional e Leitura de Esquemas (Session-Learning & Retrofit)

**Data:** 2026-05-27  
**Status:** Pronto para validação  
**Origem:** Incidente tático documentado em `notes/failure-log.md` (Sessão 216 e 173)  

---

## 1. Objetivo

Eliminar travamentos em cascata de bancos de dados locais e globais durante a consolidação retroativa (retrofit) e espelhamento de aprendizados. As falhas a serem sanadas ocorrem quando bancos SQLite locais corrompidos ou incompletos (como cascas vazias de scaffolding) quebram a transação global do módulo, deixando transações pendentes/zumbis e bloqueando inserções subsequentes com erros do tipo `cannot start a transaction within a transaction`.

---

## 2. Requisitos

### Funcionais

- **RF1 (Robustez no Espelhamento Central)**: O método `insert` de `SessionLearningDB` deve gerenciar erros na gravação do Golden DB central. Caso ocorra uma exceção (como PermissionError por restrições de sandbox), deve efetuar `g_conn.rollback()` de forma explícita e fechar a conexão `g_db.close()`, impedindo travamento do banco global físico.
- **RF2 (Controle Transacional no Retrofit)**: A função `run_retrofit` deve estabelecer uma transação explícita (`global_db.conn.execute("BEGIN IMMEDIATE TRANSACTION")`) para cada banco local SQLite processado. Em caso de sucesso, chama `global_db.conn.commit()`. Em caso de erro, realiza `global_db.conn.rollback()`, evitando o vazamento de transações que impedem inserções subsequentes.
- **RF3 (Verificação Prévia de Schema)**: A função `run_retrofit` deve consultar a tabela `sqlite_master` de cada banco de dados local antes de iniciar leituras. Caso as tabelas `session_learnings` ou `learning_facts` não existam, o processamento daquele banco específico deve ser abortado gracefulmente com uma mensagem de aviso no log, pulando para o próximo arquivo sem levantar exceções destrutivas.
- **RF4 (Princípio do Fechamento de Esteira)**: Sincronizar cirurgicamente as melhorias transacionais e de robustez no arquivo de template de ferramentas do `stout-init`: `skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py`.

### Não-funcionais

- **RNF1 (Compatibilidade Multiplataforma)**: O script deve operar de forma nativa e isolada no Windows (CMD e PowerShell), sem dependências adicionais externas além do Python 3.10+ stdlib e módulo `sqlite3` nativo.
- **RNF2 (Encoding UTF-8)**: Todas as transações e persistência de strings devem assegurar o formato UTF-8 puro (sem BOM) para evitar corrupção de caracteres em logs acentuados.
- **RNF3 (Performance no Ingest)**: O tempo de processamento por banco local sob transação imediata deve ser inferior a 100ms, otimizando o I/O síncrono.

---

## 3. Arquitetura

### Componentes

```text
skills/stout-session-learning/
└── scripts/
    └── stout-memory-capture.py       ← APLICA RF1, RF2, RF3 (Implementação principal)

skills/stout-init/
└── addons/cdd/templates/tools/
    └── stout_memory_capture.py       ← APLICA RF4 (Sincronização de Template)
```

### Matriz de Rastreabilidade

| Código Requisito | Componente / Função | Validação (Caso de Teste) |
|---|---|---|
| **RF1** | `SessionLearningDB.insert` | `test_double_persistence_writes_local_and_global` |
| **RF2** | `run_retrofit` (transações) | `test_retrofit_consolidates_and_deduplicates` |
| **RF3** | `run_retrofit` (check schema) | `test_retrofit_skips_corrupt_db_gracefully` |
| **RF4** | Addon CDD templates | Inspeção visual pós-stitching |

---

## 4. Validação

A eficácia técnica da especificação será assegurada por:
1. Suite de testes unitários local (`pytest tests/test_session_learning.py -v`).
2. Execução manual da ferramenta com flag de retrofit (`python skills/stout-session-learning/scripts/stout-memory-capture.py --retrofit`).
