# Plano de Implementação: Correção de Falhas Transacionais e Robustez no Session-Learning e Retrofit

> **ID de Governança**: stout_session_learning_robustness  
> **Status**: [Aguardando Aprovação Humana]  
> **Autor**: Engenheiro Stout / Gemini CLI  
> **Data**: 2026-05-27  

---

## 1. Contexto & Diagnóstico

Recentemente, a suite de testes e a esteira de governança local do Stout registraram os seguintes incidentes em `notes/failure-log.md`:
1. `cannot start a transaction within a transaction` ao fazer retrofit de markdowns históricos em ambientes de testes e de host.
2. `no such table: session_learnings` ao ingerir bancos locais inativos ou incompletos (ex: `pricewatch-jd`).

### Causa Raiz:
- **Transação Zumbi no Central**: Ao tentar espelhar a sessão local no Golden DB central (`GLOBAL_DB_PATH`) dentro do método `insert`, caso ocorra um erro (como PermissionError por restrições do sandbox padrão), o bloco `except` do central loga o erro mas **não realiza rollback** nem **fecha a conexão**. Isso deixa a transação zumbi pendente na conexão.
- **Auto-commit no Loop de Ingestão**: O loop consolidado retroativo (`run_retrofit`) consome e edita os bancos SQLite locais diretamente na conexão global. Se algum banco local falhar com `no such table: session_learnings` (por estar corrompido ou vazio), a exceção aborta a iteração pulando o `global_db.conn.commit()`. Sem rollback, a transação implícita ou estado transacional do SQLite continuam ativos, fazendo com que iterações e chamadas subsequentes a `insert` (como as de processamento de markdowns avulsos) falhem com `cannot start a transaction within a transaction` ao tentar abrir um `BEGIN IMMEDIATE TRANSACTION`.

---

## 2. Proposta Técnica (Mudanças Cirúrgicas)

### A. Correções em `skills/stout-session-learning/scripts/stout-memory-capture.py`

#### 1. Robustez do Espelhamento Central (`insert`):
No método `insert`, caso ocorra qualquer erro no bloco central:
```python
            except Exception as e:
                try:
                    g_conn.rollback()
                except Exception:
                    pass
                try:
                    g_db.close()
                except Exception:
                    pass
                _log_failure(f"Falha ao espelhar no banco de dados central: {e}")
```

#### 2. Transações Explícitas e Tratamento de Exceções no Retrofit (`run_retrofit`):
Modificar a ingestão de bancos SQLite locais para:
- Iniciar uma transação explícita com `global_db.conn.execute("BEGIN IMMEDIATE TRANSACTION")` no início de cada ingestão de banco de dados.
- Concluir com `global_db.conn.commit()` ao término do processamento de cada banco de dados.
- Realizar rollback seguro em caso de exceções:
```python
        except Exception as e:
            try:
                global_db.conn.rollback()
            except Exception:
                pass
            _log_failure(f"Erro ao processar retrofit do banco {sq_path}: {e}")
```

#### 3. Verificação de Integridade Pré-leitura:
Antes de ler tabelas nos bancos locais SQLite do retrofit, validar a presença das tabelas `session_learnings` e `learning_facts` via `sqlite_master`:
```python
            # Verifica se as tabelas existem no banco local
            tables = [r[0] for r in local_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "session_learnings" not in tables or "learning_facts" not in tables:
                print(f"[stout-retrofit] Aviso: Banco local {sq_path} não possui o schema necessário. Pulando.")
                local_conn.close()
                continue
```

### B. Correções no Template do `stout-init`
Replicar as exatas alterações no arquivo de template de ferramentas:
`skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py`.

---

## 3. Plano de Verificação

### Testes Automatizados
- Executar os testes locais de Session-Learning:
  `pytest tests/test_session_learning.py -v`

### Validação Manual
- Rodar varredura manual com flag `--retrofit` no host:
  `python skills/stout-session-learning/scripts/stout-memory-capture.py --retrofit`
