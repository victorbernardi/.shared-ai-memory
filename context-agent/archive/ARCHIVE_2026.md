# Arquivo Consolidado — 2026

### Sessão 049 — 2026-05-05
  - Prioridade em clientes inativos (90 dias+), uso de horímetros para prospecção preventiva e planos de integração via API com sistema Simonete.

### Sessão 050 — 2026-05-05
  - Prioridade em clientes inativos (90 dias+), uso de horímetros para prospecção preventiva e planos de integração via API com sistema Simonete.

### Sessão 051 — 2026-05-05
  - Prioridade em clientes inativos (90 dias+), uso de horímetros para prospecção preventiva e planos de integração via API com sistema Simonete.

### Sessão 052 — 2026-05-05
  - Updated NotebookLM MCP to version 0.1.14. Used automatic authentication mode to bypass local Chrome 147 vs ChromeDriver 148 mismatch. Updated settings.json executable path.

### Sessão 053 — 2026-05-05
  - Desinstalar pacotes notebooklm-mcp e notebooklm-mcp-server do Anaconda para evitar conflitos de binários; Unificar todos os clientes MCP para usar o executável em .local/bin; Utilizar 'nlm' wrapper para comandos CLI e 'notebooklm-mcp.exe' exclusivamente para servidores MCP stdio.

### Sessão 054 — 2026-05-05
  - Confirmada integridade de gemini-tools.md como fonte da verdade.

### Sessão 055 — 2026-05-05
  - Manter nomes de ferramentas de abstração nas skills Antigravity e nomes reais nas chamadas de ferramenta do Gemini CLI; gemini-tools.md serve como manual de tradução.

### Sessão 056 — 2026-05-05
  - Confirmada a integridade dos scripts de busca FTS5 e o fluxo híbrido de salvamento.

### Sessão 057 — 2026-05-05
  - Processamento em batches via sub-agentes; Limpeza do _raw/ pós-promoção; Normalização do .manifest.json.

### Sessão 058 — 2026-05-05
  - Clonagem local de skills; Hierarquia Global vs Local; Soberania da Golden Copy.

### Sessão 059 — 2026-05-05
  - Soberania do faturamento sobre segmentação; Joins via CNPJ Raiz.

### Sessão 060 — 2026-05-06
  - Utilizar COALESCE com múltiplos TRY_CONVERT no SQL; Unificar vw_VENDAS com f_vendas_hist31102025.

### Sessão 061 — 2026-05-06
  - A inatividade deve ser consolidada por Grupo Econômico (Raiz 8).

### Sessão 062 — 2026-05-06
  - Usar MCP local nativo em vez de wrapper de API; Adotar LESSONS_LEARNED.md obrigatório na governança.

### Sessão 063 — 2026-05-06
  - Utilização de Playwright para lidar com renderização Next.js; Normalização automatizada para padrão Gold Standard; Registro de histórico via Comet ML.

### Sessão 064 — 2026-05-06
  - Manter bypass do Motor M3 via base bruta para garantir integridade de datas; Remover apenas orçamentos abertos recentemente (< 90 dias); Preservar clientes A1/A2 sem faturamento recente.

### Sessão 065 — 2026-05-07
  - Manter padrão 'process-' para todas as skills de workflow.
  - 2. **MD012 (Excesso de espaços):** A documentação reprova explicitamente `\n\n\n` (múltiplas linhas em branco). Vamos usar Regex para colapsar qualquer espaço extra em apenas `\n\n`.

### Sessão 066 — 2026-05-07
  - Documentação de baixa qualidade agora é considerada falha técnica grave (Regra #9). Centralização da Golden Copy em templates/markdown-quality.
  - 2. **MD012 (Excesso de espaços):** A documentação reprova explicitamente `\n\n\n` (múltiplas linhas em branco). Vamos usar Regex para colapsar qualquer espaço extra em apenas `\n\n`.

### Sessão 067 — 2026-05-07
  - Implementar state-tracking em md-sanitize.py; Priorizar 'Quality First' na scaffold stout-init.

### Sessão 068 — 2026-05-08

### Sessão 069 — 2026-05-08

### Sessão 070 — 2026-05-08
  - Cancelamento da implementacao do promote-to-prod.ps1 devido a restricoes de admin; Manutencao da fonte da verdade em shared-ai-memory.

### Sessão 071 — 2026-05-09
  - 1. Manifestos passam a usar comandos restritivos (NUNCA/SEMPRE). 2. Laboratório Stout possui regra de Air Gap e criação de Vacinas. 3. Projeto Inova focado estritamente em Conector Fabric, KPIs e Next Best Action.

### Sessão 072 — 2026-05-09

### Sessão 073 — 2026-05-09

### Sessão 074 — 2026-05-09
  - Rebatizar o agente para SEO Grupo Econômico; Migrar todos os scripts para /scripts/ com lógica modular em /engine/; Utilizar NetworkX para unificação transitiva; Implementar Soberania Digital e Societária com score 100; Adicionar coluna NOME_GRUPO ao Dataset Ouro.

### Sessão 075 — 2026-05-11
  - Rebatizado para SEO Grupo Econômico; Centralizado em /scripts/; Unificação transitiva via NetworkX; Aplicação de Soberania Digital (C8) e Societária (C9).

### Sessão 076 — 2026-05-11

### Sessão 077 — 2026-05-11
  - Priorizar OAuth2 sobre Service Account para evitar invalid_grant.

### Sessão 078 — 2026-05-11

### Sessão 079 — 2026-05-11
  - Correcao de CNPJ float/cientifico: usar int(float(x)) antes de str() no _load_master. Busca por raiz CNPJ usa regex de 8 digitos sem zfill. Routing Fabric: condicao corrigida para aceitar PROD ou FABRIC. Proibido emojis em qualquer log/print de scripts Python (regra GEMINI.md).

### Sessão 080 — 2026-05-11
  - Usar scripts com flags --auto para evitar travamentos de input; Formalizar seo_ge_audit_tool.py como padrão no GEMINI.md.

### Sessão 081 — 2026-05-11
  - Priorizar ferramentas com flags --auto em ambientes automatizados; Utilizar HEREDOC ou Python -c para escrita de arquivos complexos no Windows.

### Sessão 082 — 2026-05-11
  - Utilizar rich para layout CLI; Formalizar motor de veredito baseado em CEP/Logradouro/Email/Telefone.

### Sessão 083 — 2026-05-11
  - Manter o scanner em background com gotejamento de 1.5s; Interface CLI validada para auditorias manuais.

### Sessão 084 — 2026-05-11
  - Manter modo híbrido (Argumentos vs Loop); Persistir carregamento do dataset em memória durante a sessão interativa.

### Sessão 085 — 2026-05-11
  - Estrutura: pipelines/, projects/, shared/. Shared data = parquets consumidos por 2+ projetos. Stage data = caches internos com hash MD5. scripts/ + data/ + docs/ para todos os projects. parents[N] para resolucao de paths relativa ao script.

### Sessão 086 — 2026-05-11
  - Cada motor sera dividido em 4 arquivos: extract.py (queries SQL + cache Fabric), transform.py (logica Pandas e regras de negocio), load.py (exportacao parquet/xlsx), run.py (orquestrador). Isso separa responsabilidades e facilita testes unitarios por camada.

### Sessão 087 — 2026-05-11

### Sessão 088 — 2026-05-11
  - Usar Double Export (Local/Shared), Implementar Schema Ouro de 11 colunas, Resolução híbrida de caminhos para cache e POPS.

### Sessão 089 — 2026-05-11
  - Removida hierarquia de prioridade do POPS; caminho fixado em shared/data/Product_details_full.xlsx.

### Sessão 090 — 2026-05-12
  - Usar CNPJ_GRUPO como chave unica de agregacao no M3 para evitar fragmentacao; Priorizar nomes do M0 no output final; Criar arquivo de feedback para expansao da base M0.

### Sessão 091 — 2026-05-12
  - Uso de watchdog.py para gerenciar resiliencia do crawler. Remocao de emojis/acentos em logs de console Windows.

### Sessão 092 — 2026-05-12
  - fabric_db.py em Documents/Fabric_Database_Connector mantido em sincronia com shared/fabric_db.py

### Sessão 093 — 2026-05-12

### Sessão 094 — 2026-05-12
  - 01_DNA lê dataset_ouro_dna_maquinas_v1.parquet (novo nome); 03_Potencial aponta para o mesmo arquivo novo; parque removido do 03_Potencial (dead code); dedup de PINs por maior Potencial Total antes do assert

### Sessão 095 — 2026-05-12
  - Vault at C:\Users\victor.bernardi\Documents\wiki-compiler-vault is now trusted for wiki-ingest operations.

### Sessão 096 — 2026-05-12
  - 05_Segmentacao: pot_total no auditoria inclui orfaos D1/D2 para paridade com M4

### Sessão 097 — 2026-05-12
  - Arquivos _pre_migration em quarentena: 02_Faturamento liberado a partir de 2026-05-26, demais a definir apos testes em producao

### Sessão 098 — 2026-05-12
  - Decisao A: schema slim do faturamento
  - Decisao B: modulos shared devem estar em shared/
  - Decisao C: baseline atualizado junto com schema

### Sessão 099 — 2026-05-12
  - dataset_ouro_faturamento_v1.parquet tem schema definitivo de 2 colunas: CNPJ_RAIZ + CAL2025_PECAS — stages downstream fazem join de identidade via dataset_ouro_identidade_v1.parquet
  - segmentation_logic.py e inova_audit_core.py: source of truth em 00_Cerebro_Inova/, copia obrigatoria em shared/ para o pipeline importar via parents[N]
  - Baseline de validate_pipeline.py deve ser atualizado no mesmo commit de refatoracao que mude schema de parquet — divergencia cascata em stages downstream e esperada e documentada
  - Arquivos _pre_migration em quarentena: 02_Faturamento liberado a partir de 2026-05-26, demais stages a definir apos testes em producao
  - context-agent --decisions e --tasks agora suportam multiplos flags (action=append) — cada flag acumula na lista em vez de sobrescrever

### Sessão 100 — 2026-05-12

### Sessão 101 — 2026-05-12

### Sessão 102 — 2026-05-12

### Sessão 103 — 2026-05-13
  - Scan QSA marcado como concluído; prioridade alterada para BATCH FINAL.

### Sessão 104 — 2026-05-13
  - Priorizar CNPJ da Filial como chave primária de herança de feedback (fallback para ID/Nome de Grupo); Adotar validação de volumetria de observações como check obrigatório pré-exportação.

### Sessão 105 — 2026-05-13
  - Implementação de filtragem física total de convertidos (<90 dias); Migração do relatório de alertas Excel para Log JSON acumulativo (conversao_audit.json); Saneamento sistêmico de encoding UTF-8 em todo o projeto.
  - 1.  **Brainstorming:** Escolhemos a abordagem executiva **"Onde as vendas perderam fôlego?"** para substituir a afirmação imprecisa de que as vendas haviam parado.

### Sessão 106 — 2026-05-13
  - Substituir similaridade de string por mapeamento de CNPJ Grupo via M0 para listas de exceção; Integrar listas estratégicas permanentemente no código fonte do motor.
  - 1.  **Brainstorming:** Escolhemos a abordagem executiva **"Onde as vendas perderam fôlego?"** para substituir a afirmação imprecisa de que as vendas haviam parado.

### Sessão 107 — 2026-05-13
  - Adoção inegociável de safras anuais discretas de 12 meses (23/24, 24/25, 25/26) para integridade financeira.
  - A lógica de safras foi corrigida para **Valores Discretos** e a decisão foi devidamente documentada no repositório para consulta futura.

### Sessão 108 — 2026-05-13
  - Remover fallback de vendedor do cadastro (SA1) para garantir integridade do CRM do Pos-Venda. Priorizar VS1010 para identificacao de pipeline ativo.

### Sessão 109 — 2026-05-13
  - Agregacao centralizada por SKU no data_loader.py; Storytelling dividido em 5 scripts em src/analyses/; Visao regional separada por df_raw.

### Sessão 110 — 2026-05-13
  - Substituído 'prompts.yaml' por 'skills_catalog.yaml' para alinhar com o Padrão de Pasta de Skills. Implementada validação de schema JSON no src/config.py.

### Sessão 111 — 2026-05-13

### Sessão 112 — 2026-05-13
  - Utilizar Folder Pattern para skills; Implementar Progressive Disclosure no Router; Usar Junction para skills globais; Adotar padrão GCC para checkpoints.

### Sessão 113 — 2026-05-13
  - Implementada prioridade absoluta de configuracao (JSON) sobre o Protheus (SA3010) para evitar ruido de IDs compartilhados.

### Sessão 114 — 2026-05-14
  - Uso de whitelist dinâmica via segment_rules.json; Migração total para M0 (Identidade Ouro)

### Sessão 115 — 2026-05-14
  - Migração para arquitetura modular de addons no stout-init; Adoção de proteção global de UTF-8 em todos os entry points; Uso de GCC Context Graph como fonte para analytics.

### Sessão 116 — 2026-05-14
  - Outcome: SUCCESS_VERIFIED | Context: {"test_id": "integration_001", "scope": "full_orchestration"}

### Sessão 117 — 2026-05-14
  - Outcome: SUCCESS | Context: {}

### Sessão 118 — 2026-05-14
  - Uso do GCC para mensagens de commit; Inicialização via Startup do Windows.

### Sessão 119 — 2026-05-14
  - Roadmap V4 aprovado. Skill Sandboxing em standby.

### Sessão 120 — 2026-05-14
  - Hooks integrados via engine.py e main.py; Protocolo de segurança contra latência (limite de iterações + log para arquivo) implementado.

### Sessão 121 — 2026-05-14

### Sessão 122 — 2026-05-14
  - N/A

### Sessão 123 — 2026-05-14
  - Descartar MCPs não oficiais para Perplexity devido à instabilidade e fragilidade. Instituir o SOP Search-Before-Code como regra imutável para correções de erro.

### Sessão 124 — 2026-05-14
  - Descartar MCPs não oficiais para Perplexity devido à instabilidade e fragilidade. Instituir o SOP Search-Before-Code como regra imutável para correções de erro.

### Sessão 125 — 2026-05-14
  - Adotada arquitetura Event-Driven baseada em File-System com Atomic Rename para resiliência superior a Network Daemons.

### Sessão 126 — 2026-05-15

### Sessão 127 — 2026-05-15

### Sessão 128 — 2026-05-15
  - 1. Utilização de coordenadas absolutas (Sniper Mode) para clicar em botões de Canvas do Power BI. 2. Implementação de waittime de 25-35s devido à telemetria pesada do Power BI. 3. Configuração de Junction para a pasta docs/ visando memória global.

### Sessão 129 — 2026-05-14
  - Adoção do template V2 como padrão executivo; Restauração da integração com scanners reais no generator.py após validação de qualidade.

### Sessão 130 — 2026-05-14
  - Uso de Generative Blueprinting; Isolamento de contexto via subagentes em agents/; ADR-0007 para vínculo com Skill Folder Pattern; Divisão da governança em 4 pilares.

### Sessão 131 — 2026-05-14
  - Unificação do ecossistema de skills em 4 papéis chave; Adoção do Protocolo de Imunidade com travas físicas; Padronização de Specs com rastreabilidade SOW/AC/FR/Test; Otimização semântica para Gemini CLI.

### Sessão 132 — 2026-05-14
  - M2 (cache_vendas_rfm.parquet) e unica fonte de verdade para totais — vw_VENDAS apenas para NOME_VENDEDOR|audit_nf.py salva 6 parquets + manifest.json por execucao em data/audit_nf/<run_id>/|ritmo_atual usa media simples (acumulado/dias_uteis_corridos) — suficiente para decisao gerencial|projecao_mes = ritmo_atual x (dias_corridos + dias_restantes)|ritmo_necessario = (meta - acumulado) / dias_restantes

### Sessão 133 — 2026-05-14
  - Instalar apenas git-guardrails-claude-code e setup-pre-commit do misc, mas o npx instala o bundle completo

### Sessão 134 — 2026-05-14
  - using-matt é independente do Superpowers, não complementar. Cobre: diagnose, tdd, to-prd, to-issues, grill-me, grill-with-docs (Matt) + requesting-code-review, receiving-code-review, executing-plans, subagent-driven-development (Superpowers). TDD usa skill do Matt para testar. Skill criada via processo correto com testes de baseline

### Sessão 135 — 2026-05-14
  - Manifest de divergência vai apenas no log/audit (JSONL) + aviso condicional no email quando divergência > 0.05%
  - Top filiais substituído por ranking completo de todas as filiais ordenadas por receita de ontem
  - Tarefa H1.5 criada: estender Motor M2 para incluir NOME_VENDEDOR no parquet (pré-requisito para eliminar dependência de vw_VENDAS)

### Sessão 136 — 2026-05-14

### Sessão 137 — 2026-05-14
  - Cancelamentos de ontem (não mês) com threshold R0k — mais acionável no email diário. Bloco omitido quando abaixo do threshold. H2.1 bloqueado até BUP-AUTO-1 ser concluído — dados BUP/CEVAP defasados sem automação da VS1010.

### Sessão 138 — 2026-05-14

### Sessão 139 — 2026-05-14

### Sessão 140 — 2026-05-14
  - Adotar soberania do arquivo POPS para blindagem da Camada C2 contra locadoras; Priorizar análise de subgrupos por rentabilidade em quedas de demanda; Substituir servidor Google Drive MCP padrão pelo fork da comunidade (@piotr-agier/google-drive-mcp).

### Sessão 141 — 2026-05-14
  - Adoção do Padrão Ouro de Migração (Copy Folder + Replace); Implementação do Selo [STOUT-IMMUTABLE]; Unificação do Protocolo Universal V2.0; Criação do stout-cdd-orchestrator local.

### Sessão 142 — 2026-05-14
  - Adotado enter_plan_mode nativo na skill stout-writing-plans. Aprovado e criado ADR-0009. Habilitado useWriteTodos (experimental) no settings.json global.

### Sessão 143 — 2026-05-17
  - Adoção das Karpathy Laws como LEI GLOBAL no orquestrador; Migração do launcher para arquitetura baseada em registry.json; Correção de encoding UTF-8 para Windows.

### Sessão 144 — 2026-05-17
  - Utilizada codificação Ascii em settings.json para evitar BOM. V4.9 marcada como concluída no Roadmap.

### Sessão 145 — 2026-05-17
  - Ignorar .GCC/branches/ no Git para evitar bloqueios de ferramenta; Adotar Copy+Replace como fluxo único de upgrade; Implementar SkillSandbox em src/core/sandbox.py.

### Sessão 146 — 2026-05-17
  - Remover filtro VS1_TPATEN de extract_orcamentos.py (confirmado errado — exclui 53.6% dos registros válidos do BI)

### Sessão 147 — 2026-05-17
  - Migração de carteiras baseada em interseção de clientes (cod_cliente) em vez de mapeamento nominal.

### Sessão 148 — 2026-05-18
  - Adotar a extração e inserção de bytes de imagem pura via package.get_or_add_image_part() em consolidate_slides.py em vez de referenciar o part de origem diretamente, para evitar arquivos duplicados no ZIP.

### Sessão 149 — 2026-05-19
  - Desacoplar a validação usando um script de auditoria centralizado em c:\Projetos\Inova\shared que gera um arquivo Markdown (recency_status.md) lido na inicialização do motor BUP.

### Sessão 150 — 2026-05-19

### Sessão 151 — 2026-05-19
  - Usar conexao JDBC direta livre de driver ODBC, aplicar validacoes Fail-Fast em bases locais, orquestrar localmente via PowerShell

### Sessão 152 — 2026-05-19
  - Usar M0 para unificação de clientes; Ingestão estrita de strings para CNPJs; Filtro de Autoconsumo mandatório.

### Sessão 153 — 2026-05-19
  - Adotado padrão M0 de ingestão para o M1. Implementado orquestrador de pipeline com Gate de Qualidade.

### Sessão 154 — 2026-05-19
  - 1. Governança operando no modelo CDD (rules.yaml). 2. Modo Informativo adotado para evitar bloqueios de execução. 3. O Post-flight roda o generate_recency_report.py central via subprocess.run() para atualizar a saúde do M2.
