# Plano de Implementação: Limpeza e Enriquecimento de Orçamentos

## 1. Background & Motivation
O pipeline atual extrai orçamentos abertos via scraper (Power BI) e orçamentos cancelados via Fabric. Conforme detalhado no handoff do projeto, o próximo passo essencial é limpar os dados brutos e enriquecer os orçamentos abertos cruzando-os com informações consolidadas do Microsoft Fabric (como dados de clientes, vendedores e peças) para gerar uma visão final de alto valor para inteligência comercial.

## 2. Scope & Impact
* **Arquivos Afetados:**
  * `src/transform.py` (Novo arquivo a ser criado)
  * `run.py` (Atualizado para orquestrar extração + transformação)
* **Impacto:** O arquivo final `data.xlsx` (orçamentos abertos) passará a conter informações mais ricas vindas do banco de dados, melhorando a análise de potencial. Os DataFrames serão tipificados e limpos de forma consistente antes de serem salvos.

## 3. Proposed Solution
Criar um novo módulo `transform.py` que atuará como a camada de limpeza e integração (enrichment).

## 4. Phased Implementation Plan

### Fase 1: Módulo de Transformação e Limpeza
* Criar `src/transform.py`.
* Implementar `limpar_orcamentos_abertos(df: pd.DataFrame)`: Normalizar nomes de colunas, tipar datas e valores numéricos.
* Implementar `limpar_orcamentos_cancelados(df: pd.DataFrame)`: Garantir conformidade de tipos e limpar strings.

### Fase 2: Enriquecimento via Fabric
* Implementar `enriquecer_orcamentos_abertos(df: pd.DataFrame)` dentro de `src/transform.py`.
* **Lógica:** Conectar ao Fabric via `shared.fabric_db.ConexaoFabric`, buscar informações complementares (ex: Razão Social do Cliente a partir da tabela SA1, e detalhes do vendedor na tabela padrão) fazendo match pelo Número do Orçamento e Filial.
* Fazer o merge (Left Join) do DataFrame raspado do Power BI com o DataFrame complementar do Fabric.

### Fase 3: Integração no Orquestrador
* Atualizar `run.py` para injetar filtros de data (Jan/2025 até o momento atual) nas chamadas de extração, conforme handoff e teste de carga.
* Chamar as rotinas de `transform.py` após a extração, garantindo que o arquivo Excel salvo em `data/output/` seja a versão processada e enriquecida.

## 5. Verification
* Executar `run.py` localmente.
* Verificar se o log indica sucesso nas conexões e merges.
* Inspecionar o arquivo resultante `data/output/data_enriquecida.xlsx` usando um snippet Python para confirmar as novas colunas adicionadas e a corretude dos tipos de dados.

## 6. Migration & Rollback
* O script original `run.py` será focado em encadear os processos de forma modular. Caso o enriquecimento falhe no Fabric (timeout ou esquema alterado), a função deverá prever um `try/except` que preserve os dados originais raspados, garantindo que o pipeline não quebre por completo.