# Walkthrough - Migração de Data Skills (Stout Premium)

Concluímos com sucesso a migração e conversão de **10 skills de análise de dados** do repositório `knowledge-work-plugins` para o ambiente local do projeto **Stout**.

## O que foi realizado

### 1. Conversão Premium
Cada skill foi reescrita seguindo os padrões de excelência da **Stout Edition**:
- **Gatilhos Bilíngues**: Suporte a comandos em Português e Inglês (ex: `explore data` / `explorar dados`).
- **Metadados Estruturados**: Adição de `risk`, `source`, `date_added` e categorias.
- **Operating Modes**: Definição clara do papel do agente (ex: Senior Data Scientist, Data Auditor).

### 2. Suporte Nativo a Microsoft Fabric
Identificamos que o ambiente utiliza o dialeto **T-SQL** via conector JDBC. Customizamos as skills de SQL (`data-sql-queries` e `data-write-query`) para priorizar:
- Sintaxe `SELECT TOP (n)` em vez de `LIMIT`.
- Funções `DATETRUNC`, `DATEDIFF` e `JSON_VALUE`.
- Otimização para o conector local em `Documents\Fabric_Database_Connector`.

### 3. Protocolo Canary Deployment
Todas as modificações foram realizadas de forma atômica e segura, com registros de auditoria em:
- [canary-log.md](file:///C:/Users/victor.bernardi/.gemini/antigravity/diary/canary-log.md)

## Skills Instaladas (Checklist Final)

- [x] **Fase 1: `data-analyze`** - Fluxo completo de análise estruturada.
- [x] **Fase 2: `data-build-dashboard`** - Geração de dashboards HTML/JS Premium.
- [x] **Fase 3: `data-create-viz`** - Visualizações Python de alta qualidade.
- [x] **Fase 4: `data-data-context-extractor`** - Descoberta de contexto de warehouse.
- [x] **Fase 5: `data-data-visualization`** - Princípios de design e acessibilidade.
- [x] **Fase 6: `data-explore-data`** - Scanner de integridade e qualidade de dados.
- [x] **Fase 7: `data-sql-queries`** - Enciclopédia de dialetos (com Patch Fabric).
- [x] **Fase 8: `data-statistical-analysis`** - Rigor matemático e detecção de vieses.
- [x] **Fase 9: `data-validate-data`** - Auditoria de relatórios e QA de queries.
- [x] **Fase 10: `data-write-query`** - Motor de tradução NL to SQL (com Patch Fabric).

## Como utilizar as novas skills
Você pode chamar as novas funcionalidades diretamente via chat ou usando o prefixo `/data-`.
Exemplos:
- `/data-explore-data minha_tabela`
- `/data-write-query top 10 produtos por venda no Fabric`
- `/data-validate-data [copiar seu relatorio aqui]`

---
**Missão cumprida: O Antigravity agora possui um arsenal completo e personalizado para análise de dados no Microsoft Fabric.**
