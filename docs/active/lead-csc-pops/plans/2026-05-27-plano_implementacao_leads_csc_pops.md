# Plano de Implementação Técnica (Stout Execution Strategy)

## Campanha de Leads Preventivos de Pós-Vendas (FPS & Material Rodante)

> **Identidade do Documento:** `./docs/plans/2026-05-27-plano_implementacao_leads_csc_pops.md`  
> **Data:** 27/05/2026  
> **Status:** Pronto para Execução / Aguardando Início de Build  
> **Projeto:** Inova Máquinas | Leads CSC Pops  
> **Stack:** Python 3.11, PowerShell 5.1, openpyxl, jaydebeapi

---

## 🎯 1. Escopo & Arquitetura Proposta

Este plano detalha o roteiro técnico de engenharia para implementar o motor modular de cálculo de alertas e relatórios gerenciais diários, seguindo rigorosamente os padrões de modularidade de 4 camadas da Inova Máquinas (conforme `CLAUDE.md`).

Os componentes serão criados de forma isolada e auto-contida em: `C:\Projetos\Inova\projects\lead-csc-pops\`.

---

## ⚙️ 2. Componentes e Estrutura de Código

### Camada 1: Extração (extract.py)

* **Objetivo:** I/O puro e conexões externas.
* **Mapeamento físico:** `src/extract.py`
* **Lógica:**
  * Carrega a base ativa de equipamentos em `shared/data/Product_details_full.xlsx`.
  * Carrega as tratativas e orçamentos comerciais do Excel no OneDrive.
  * Realiza a consulta no Fabric DW (`LH_Consumo`) para buscar as capas de orçamentos da tabela `VS1010` e cruzar com o cadastro de chassis da `VV1010` (Auditoria).
  * **Regra de Cache:** Força o uso de cache local `.parquet` em `/cache` com `use_cache=True` na fase de desenvolvimento e validações lógicas.

### Camada 2: Transformação (transform.py)

* **Objetivo:** Lógica de negócio pura (funções puras, sem efeitos colaterais de I/O, disco ou rede).
* **Mapeamento físico:** `src/transform.py`
* **Lógica:**
  * Calcula a diferença de horímetro (`Horimetro_Atual - Horimetro_Base`).
  * Dispara os alertas inteligentes baseados nas regras de negócio de desgaste:
    * FPS global: a cada 200h acumuladas adicionais.
    * Rodante Tratores (700J, 750J, 850J, 1050K): a cada 1.500h acumuladas adicionais.
    * Rodante Escavadeiras (130G a 350ZX): a cada 3.000h acumuladas adicionais.
  * Lógica do **Gatilho de Reentrada:** Atualiza o `Horimetro_Base` para os chassis cujo status comercial do feedback da planilha no OneDrive foi marcado como "Tratado" (`Venda` ou `Venda Perdida`).
  * Lógica da **Ponte da Verdade:** Efetua o cruzamento dos chassis dos alertas com as propostas físicas de fato abertas no Protheus (trazidas do Fabric).
  * Consolida os KPIs diários da campanha (Adesão Comercial, Conversão Real, Aderência de Propostas, Aging de leads, Pipeline em Negociação).

### Camada 3: Carga & Publicação (load.py)

* **Objetivo:** Escrita física e segurança.
* **Mapeamento físico:** `src/load.py`
* **Lógica:**
  * Salva semanalmente a base de leads atualizada no OneDrive (`.xlsx`).
  * Utiliza `openpyxl` para aplicar bloqueio de células por senha nas colunas estruturais de origem e habilita edição e dropdown com opções de tratativa (`Venda`, `Venda Perdida`, `Sem Contato`) apenas nas colunas de feedback comercial.
  * Gera a visualização do painel diário de KPIs em HTML para envio por e-mail.

### Camada 4: Orquestrador (run.py)

* **Objetivo:** Ponto de entrada (Entrypoint) do motor.
* **Mapeamento físico:** `run.py`
* **Lógica:**
  * Resolve caminhos relativos e importa as conexões e credenciais do Fabric centralizadas em `C:\Projetos\Inova\shared\config.py` de forma dinâmica.
  * Executa a esteira em ordem: `extract` ➔ `transform` ➔ `load`.
  * Garante asserções fail-fast rígidas para validação de dados em memória antes da escrita (Regra 5).

### Camada 5: Agendador e Report (PowerShell)

* **Objetivo:** Automação operacional Windows.
* **Mapeamento físico:** `scripts/scheduler_daily.ps1`
* **Lógica:**
  * Orquestra a execução diária em background.
  * Carrega os parâmetros de rede SMTP e credenciais seguras do arquivo `.env` local.
  * Envia o e-mail diário com o report HTML gerado de KPIs para o Roberto e para a Gabriela.
  * Cria o agendamento oficial da tarefa no Windows Task Scheduler.

---

## 🧪 3. Plano de Validação & Testes

* **Testes de Unidade (TDD):** Implementação de testes em `tests/test_transform.py` usando `pytest`. Os testes cobrirão:
  * O cálculo correto de delta de horímetro.
  * O acionamento preciso de alertas de FPS (200h) e Material Rodante (1.500h/3.000h).
  * O fluxo de reentrada e zeramento do horímetro base após feedback de fechamento.
* **Validação de Estilo e Segurança:** Teste físico abrindo a planilha no Excel para garantir que as colunas estruturais estejam de fato travadas por senha.
* **Pre-flight Check:** Dry-run completo com dados falsificados e cache de rede para certificar que o pipeline roda de ponta a ponta sem falhas.

---
*Plano de engenharia preparado para início de codificação na fase de Build.*
