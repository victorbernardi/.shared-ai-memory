# PLANO DE IMPLEMENTAÇÃO - v1.0
## Atualização de Dados e Automação de Recência Inova/BUP

Este plano detalha as etapas para realizar o download dos dados em tempo real (sem cache), executar a unificação de clientes e grupos econômicos através do Motor Identidade, gerar o relatório de recência e automatizar todo o fluxo de atualização.

---

## 🏁 Metas de Execução

1. **Auditoria de Conexão:** (Concluído com Sucesso! SA1010, VV1010 e VO1010 estão conectando e operacionais).
2. **Ingestão Lógica Estrita (Sem Cache):**
   - Implementar `scripts/seo_ge_ingest_fabric.py` com validações estruturais Fail-Fast (assertivas de schema e não-vazio) para sobrescrever os arquivos físicos de cache com dados atualizados.
3. **Execução do Batch M0 (v11.7):**
   - Rodar o pipeline `scripts/seo_ge_batch_v11_7.py` para recalcular elos e QSA, gerando a nova Golden Copy final `dataset_ouro_identidade.parquet` no diretório compartilhado.
4. **Relatório de Recência:**
   - Rodar `C:\Projetos\Inova\shared\generate_recency_report.py` para consolidar o status de recência de todas as bases em `C:\Projetos\Inova\shared\recency_status.md`.
5. **Orquestração Polyglot (PowerShell):**
   - Criar o script `scripts/seo_ge_update_pipeline.ps1` que encadeia as três execuções (`seo_ge_ingest_fabric.py` -> `seo_ge_batch_v11_7.py` -> `generate_recency_report.py`) com logs robustos em UTF-8 e controle de erros.

---

## 🛠️ Detalhamento dos Componentes

### 1. Ingestão Lógica (`[NEW] scripts/seo_ge_ingest_fabric.py`)
Um utilitário dedicado que usa `ConexaoFabric` central para baixar as tabelas cruas do Protheus sem cache (`use_cache=False`) e salvá-las nos arquivos exatos esperados pelo Batch M0.

#### Validações Fail-Fast (Regra 5):
- `assert not df.empty, "Tabela SA1010 vazia"`
- Checagem das colunas críticas do schema.
- Em caso de falha de conexão ou validação de schema, o script dispara `sys.exit(1)` imediatamente para interromper a orquestração e evitar a contaminação do pipeline.

### 2. Processador de Unificação (`scripts/seo_ge_batch_v11_7.py`)
Execução do motor atual v11.7 de soldagem e unificação de grupos econômicos, que lê os caches atualizados e gera a Golden Copy `dataset_ouro_identidade.parquet` em `shared/data/`.

### 3. Emissor do Relatório de Recência (`C:\Projetos\Inova\shared\generate_recency_report.py`)
Disparo do script central para recalcular a recência e atualizar o arquivo de status markdown na pasta compartilhada.

### 4. Orquestrador PowerShell (`[NEW] scripts/seo_ge_update_pipeline.ps1`)
Criaremos um script PowerShell para orquestrar e agendar no Windows Task Scheduler. O script lidará com:
- Definição do encoding UTF-8 na console.
- Execução sequencial dos passos com verificação do código de retorno (exit code) de cada etapa.
- Logs limpos salvos em um arquivo de auditoria física.

---

## 📋 Checklist de Execução

- `[ ]` Criar script de ingestão `scripts/seo_ge_ingest_fabric.py`.
- `[ ]` Rodar `scripts/seo_ge_ingest_fabric.py` para baixar dados frescos sem cache.
- `[ ]` Executar o Batch de Unificação `scripts/seo_ge_batch_v11_7.py` para gerar a Golden Copy.
- `[ ]` Disparar `C:\Projetos\Inova\shared\generate_recency_report.py` para atualizar o relatório de recência em `shared/recency_status.md`.
- `[ ]` Criar o script de orquestração `scripts/seo_ge_update_pipeline.ps1` para automações futuras.
- `[ ]` Validar a integridade física de todos os artefatos modificados.

---

## 🧪 Plano de Verificação

### Verificação Automatizada/Empírica:
1. Executar o pipeline e monitorar o console para garantir `exit code 0`.
2. Verificar que a data de modificação física de `dataset_ouro_identidade.parquet` corresponde à hora do teste.
3. Verificar se `shared/recency_status.md` foi atualizado hoje e exibe `🟢 Atualizado Hoje` para as bases correspondentes.
