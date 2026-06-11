# Contexto Ativo — Atualizado em 2026-06-11 11:28
**Total de sessões registradas:** 242

## Projetos Ativos
| Projeto | Status | Última Sessão | Próxima Ação |
|---------|--------|---------------|--------------|
| **Antigravity Stout** | 🛠️ Em Estabilização | — | Validar detecção do NotebookLM pós-restart. |
| **Inova John Deere** | 📅 Em Espera | — | Prosseguir com M1-M4 após estabilização do motor. |
| **Configuration-Driven Development** | ✅ Ativo | — | Finalizar Auditoria e Sincronização de Skills. |
| **Context Agent** | ✅ Ativo | — | Manter sincronização de sessões Antigravity. |
| Context Agent | active | — | — |

## Tarefas Pendentes
### Média Prioridade
- [ ] **[STOUT-ENV] Addon de Setup do Ambiente (`env-setup`):** Desenvolver um addon ou script utilitário para mapear automaticamente o PATH do Git/Python do host e ativar o ambiente virtual (`.venv` ou conda) na sessão da IA antes da execução dos comandos locais. (desde session-167)
- [ ] **[STOUT-RETROFIT] Skill de Auto-Retrofit (`stout-retrofit`):** Criar uma skill dedicada a varrer pastas de pipelines antigos que estão em andamento e automatizar a injeção estrutural de UTF-8, o scaffolding físico e o preenchimento do `stout-manifest.json` com base em código existente. (desde session-167)
- [ ] **[STOUT-VALIDATION] Validador Contínuo de Schemas (Data Quality Addon):** Integrar ao CDD Addon validações contínuas de consistência física e assertivas (ex: usando Pydantic ou Great Expectations) para proteger as Colunas Soberanas de Peças em todos os stages do pipeline de dados. (desde session-167)
- [ ] **[STOUT-SECURITY] Proteção de Staging Ativa:** Configurar ganchos (hooks) de pré-commit para impedir que dados sensíveis em arquivos Parquet ou planilhas locais burlem o `.gitignore` e sejam indexados por engano. (desde session-167)
- [ ] 1. Instalar command-code globalmente (npm install -g command-code) 2. Configurar o opencode.json para usar o cmd via MCP 3. Conectar cliente OpenCode ao localhost:4096 (desde session-167)
- [ ] Validar o motor em novas inicializações de projetos; Refatorar regras declarativas e intenções órfãs detectadas pelo Sentinel no rules.yaml. (desde session-168)
- [ ] Nenhuma pendente. Sessao concluida com feedback de baixa produtividade por falta de alinhamento de objetivos. (desde session-169)
- [ ] BACKLOG STOUT — PRIORIDADE ALTA: (1) Criar motor_template/ com scaffold padrão (Fail-Fast + Drift + Baseline + Log KPI) para todo motor novo. (2) Adicionar git init como Passo 0 obrigatório na skill stout-init. PRIORIDADE MÉDIA: (3) Checklist de Impactos Downstream na skill stout-executing-plans — antes de fechar tarefa listar consumidores do artefato. (4) Protocolo formal de deprecação — skill stout-deprecate ou incorporar à stout-commit. (5) Adicionar .editorconfig com charset=utf-8 no stout-init. PRIORIDADE BAIXA: (6) Regra de encoding UTF-8 sem BOM no GEMINI.md local do projeto Inova. PROJETO INOVA: (7) Inicializar Git no projeto 01_DNA (instalar Git for Windows + git init). (desde session-170)
- [ ] Copiar BUP timestamp -> BUP_POS_VENDA.xlsx fixo no Post-flight - Copiar para OneDrive Documentos BUP_POS_VENDA.xlsx - Criar setup_junctions.ps1 para automatizar junctions - Instalar ripgrep no ambiente - Configurar PYTHONIOENCODING=utf-8 para evitar erros de emoji no terminal - Clonar skills CDD sob demanda quando necessário (desde session-171)
- [ ] 1. [CRÍTICO] Copiar BUP_POS_VENDA_<timestamp>.xlsx -> BUP_POS_VENDA.xlsx (nome fixo) no Post-flight para que o recency_status.md sempre encontre o arquivo — 2. [CRÍTICO] Copiar BUP_POS_VENDA.xlsx -> OneDrive\Documentos\BUP_POS_VENDA.xlsx para eliminar trabalho manual diário de upload — 3. [MELHORIA] Criar setup_junctions.ps1 que automatiza todos os mklink /J necessários (skills, shared, pipelines, OneDrive) — 4. [MELHORIA] Instalar ripgrep no ambiente para habilitar busca por grep nas sessões — 5. [MELHORIA] Configurar PYTHONIOENCODING=utf-8 ou chcp 65001 antes de rodar testes para eliminar warnings de emoji no terminal — 6. [MELHORIA] Clonar skills CDD sob demanda via junction quando o orchestrator precisar ativar uma skill que não está no projeto (desde session-172)
- [ ] Adicionar pytest.mark.skipif nos testes restantes; Corrigir launcher.py com path frágil; Sincronizar skills_catalog.yaml com skills/; Adicionar import guard nas ferramentas de governança; Sincronizar stout_promote.py/post_approve.py com templates stout-init; Implementar network_daemon.py para V5.0 (desde session-173)
- [ ] Testar na proxima sessao se process-context-agent aparece no available_skills. (desde session-174)
- [ ] BUP-AUTO-1: extrair orcamentos direto do Fabric (VS1010) para eliminar PowerBI. Atualizar bases Seedz/InovaPay quando receber. (desde session-176)
- [ ] BUP-AUTO-1: Implementar extract_orcamentos.py consultando VS1010 no Fabric para gerar os xlsx de orçamentos abertos e cancelados, eliminando dependência do PowerBI. (desde session-177)
- [ ] Corrigir skills.schema.json para validar catálogo no formato {version, skills: []}|Atualizar paths no registry.json de cdd-project-skills/ para skills/|Implementar poda de tarefas stale no Context Agent|Criar Central UTF-8 Utility em /shared/utils/logging.py|Criar stout-retrofit skill para injeção de UTF-8 em projetos legados|Melhorar GitGuard UX com detecção de shell (PowerShell vs CMD) (desde session-178)
- [ ] Ajustar bloco RECAP para refletir dados de 20 e 21/05 (nao 19/05) — ver arquivo DAILY_ROBERTO_20260521_1831.md. Gerar e-mail de sexta-feira 23/05 (e-mails de terca, quarta e quinta nao foram enviados por falta de tempo). Revisar se data_ontem no generator precisa ser parametrizado para sexta. (desde session-179)
- [ ] Próxima sessão: criar automação de envio do e-mail diário (desde session-181)
- [ ] Monitorar primeira execução automática (Seg 25/05 às 08:20) — confirmar entrega para Roberto e Gabriela (desde session-183)
- [ ] Monitorar primeira execucao automatica: Seg 25/05 17:20 (geracao) e Ter 27/05 08:20 (email) — confirmar entrega para Roberto e Gabriela (desde session-184)
- [ ] Validar formatacao de datas dd/mm/aaaa apos proxima execucao automatica (BUP 17:30, CEVAP 17:40) (desde session-187)
- [ ] Investigar/corrigir LEICA GEOSYSTEMS zero CNPJ (bug pre-existente nos testes BUP) (desde session-187)
- [ ] Promover stout-promote-skill ao golden copy quando auditoria passar (desde session-188)
- [ ] Nenhuma tarefa pendente (desde session-190)
- [ ] Corrigir extract.py para incluir filiais 03XX. Verificar se há outras diferenças (TES, Centro Custo, VALOR_DO_PRODUTO vs Valor Líquido). Rodar M2 contra Fabric e comparar total com R75.2M. Investigar se VALOR_DO_PRODUTO no banco = Valor Bruto ou Valor Líquido. (desde session-191)
- [ ] Concluído saneamento. (desde session-192)
- [ ] Promover sandbox para produção: substituir extract.py com nova query via query_loader|Validar 2025 (-1.58%) e 2026 (+1.22%) — investigar resíduo se necessário|Atualizar run.py para usar VALOR_LIQUIDO ao invés de VALOR_DO_PRODUTO (desde session-193)
- [ ] Promover sandbox para produção: reescrever extract.py com query_loader; Ajustar run.py para logar VALOR_LIQUIDO; Investigar resíduo +-1.5% por ano (fronteira out/nov 2025); Replicar .gitignore padrão nos outros stages do pipeline (desde session-194)
- [ ] Consolidar as 10 copias do stout-memory-capture.py em uma unica source of truth com symlinks (desde session-197)
- [ ] Verificar definição de vw_VENDAS (sp_helptext) para rastrear origem de COD_GRUPO; Solicitar snapshot corrigido com CBIT ao responsável do Fabric; Promover motor para produção após decisão sobre resíduo (desde session-198)
- [ ] Executar sp_helptext vw_VENDAS para rastrear origem de COD_GRUPO; Solicitar reprocessamento do snapshot com CBIT ao responsável Fabric; Promover motor para produção (desde session-199)
- [ ] Investigar NULL DESCRICAO_CC: R5.8M no motor sem CC correspondente no BI — query Fabric para identificar filiais/origem. Investigar anomalia LEIC: R.4M no motor vs R/usr/bin/bash.016M no BI — verificar se é classificação correta ou ruído. Executar sp_helptext vw_VENDAS para rastrear origem de COD_GRUPO e verificar se existe fonte histórica para CBIT. Solicitar ao responsável do Fabric reprocessamento do snapshot com dados CBIT de Jan-Oct 2025. (desde session-200)
- [ ] Nenhuma pendencia tecnica restou no pipeline de Faturamento. (desde session-201)
- [ ] Aguardar ~24h ativação app ML no DevCenter e testar OAuth com: python scripts/02-pesquisa/adaptadores/ml_auth.py. Após ML funcionar: rodar scraper.py com lista_pecas.csv completa. Limpar qa_test_ml_api.py da raiz após validação. (desde session-202)
- [ ] Estudar CronCreate vs Windows Task Scheduler para polling horário do ML API. Quando /sites/MLB retornar 200, executar ml_auth.py e rodar scraper completo. Comando de teste manual: python qa_test_ml_api.py (esperar status 200 no endpoint sites/MLB). (desde session-203)
- [ ] Próxima sessão: construir monitoramento de outros concorrentes (tblagro, mfrural, agrofy)|Quando ML liberar (notificação Toast), executar ml_auth.py manualmente para completar OAuth (desde session-204)
- [ ] Investigar JDPC -R$3.77M (imposto filial 203). Investigar EPRC +R$0.68M. Investigar BI grupos NaN R$1.74M. Investigar Balcao delta +/-1.9%. Deploy query para producao apos resolucao das pendencias. (desde session-205)
- [ ] Avançar no planejamento da fase V5.0 Distributed CDD com foco na priorização de estabilidade do ecossistema ao invés de sincronização prematura assíncrona. (desde session-206)
- [ ] Buscar tabela original do Protheus (nao vw_VENDAS) para obter dados completos dos CNPJs 0212 (desde session-207)
- [ ] Investigar imposto filial 203 e TES/devolucoes (desde session-207)
- [ ] Resolver filial 0302 (R$0.74M no BI, R$0 no motor) (desde session-207)
- [ ] Investigar classificacao da filial 0211 (padrao de split 0201 vs 0211) (desde session-207)
- [ ] Sessão 02_Faturamento: renomear branch fix/stout-promote-antigravity-brain-path (commits faturamento já em feat/02-faturamento-filtros-whitelist); revisar branch-policy.yaml gerados se needed; wiki-ingest para sincronizar vault (desde session-208)
- [ ] Sessão 02_Faturamento: decidir o que fazer com fix/stout-promote-antigravity-brain-path (branch que contém 3 commits de faturamento na história — responsabilidade da sessão de faturamento, não desta) (desde session-209)
- [ ] Implementar extract_protheus.py com query SD2010 + JOIN SA1010/SA2010 filtrando 3 CNPJs + CCs CSN + D2_TP='ME' + periodo 2022+|Integrar no run.py entre extract e filtros|Remover f_vendas_hist31102025 da query SQL (substituir pelo SD2010)|Atualizar testes|Solicitar a TI replicacao das tabelas faltantes do Protheus para o Fabric (desde session-210)
- [ ] Solicitar a TI replicacao completa das tabelas Protheus (SD2010/SF2010) para o Fabric | Apos replicacao: criar extract_protheus.py com query SD2010+SA1010 | Apos replicacao: substituir f_vendas_hist por SD2010 em vendas_pecas_construcao.sql | Apos replicacao: integrar no run.py e atualizar testes (desde session-211)
- [ ] Reativar INOVA_DAILY_EMAIL após validar correção do M2: Enable-ScheduledTask -TaskName INOVA_DAILY_EMAIL (desde session-212)
- [ ] Investigar branch fix/stout-promote-antigravity-brain-path com 3 commits do 02_Faturamento (responsabilidade da sessão 02_Faturamento) (desde session-213)
- [ ] **[M3-AUDITORIA] Inclusão do Audit M3/M0:** Incluir o script de auditoria `audit_m3_m0_granularity.py` na validação contínua e no runner principal do motor M3 para auditoria automática da tabela e prevenção de desvios de granularidade. (desde session-214)
- [ ] **[GOVERNANÇA-DADOS] Central Data Schema Guardrail (`data_validator.py`):** Desenvolver um validador de contratos de dados centralizado em `shared/data_validator.py` consumido por todos os motores (M0 a M5) durante o `extract`. Ele deve validar schemas de entrada, barrar e limpar automaticamente colunas duplicadas ou colidentes inesperadas e monitorar taxas de nulos em chaves de merge para fail-fast na origem. (desde session-214)
- [ ] Concluído o download e transcrição diarizada; Concluído o enriquecimento cognitivo Stout-Aware da ata executiva; Concluída a movimentação física dos arquivos para C:\Projetos\Inova\projects\lead-csc-pops\Transcricao (desde session-214)
- [ ] Autenticar Mercado Livre: python scripts/02-pesquisa/adaptadores/mercadolivre.py --headed; Rodar ML + GHT Shop na lista completa do BD Inova (filtros RE/AT/DZ/AM); Gerar data/lista_pecas_producao.csv com filtros da lista real; Construir tabela cross-reference JD→fabricante em data/crossref_jd_fabricante.csv (desde session-215)
- [ ] Merge do branch feat/pricewatch-concorrentes-scraping-v2 ao master do Inova (contém upgrade do pricewatch-jd). Implementar group_related_facts (backlog v2) em sessão futura. (desde session-216)
- [ ] Nenhuma pendencia desta sessao (desde session-218)
- [ ] Investigar NFs LEIC e EPRC que sobraram no motor — verificar se o BI as classifica sob outro grupo/CC. Validar filial 0302 (R$625K no BI vs R$0 no motor). Validar filial 201 (-18.1%). Validar imposto filial 203. Investigar grupo NAN (-R$768K no BI). (desde session-219)
- [ ] Migrar Inova-Daily para ICM quando db_utils.py for restaurado. Criar REFERENCES.md e .GCC/ no dominio Inova. Testar pipeline do Skill-Folder-Pattern com uma sessao real. Criar thin wrappers em .gemini/skills/ e .agents/skills/. Migrar proximo projeto Stout usando stout-icm-migrate. (desde session-222)
- [ ] Investigar NAN SERVICOS IRRIGACAO. Investigar filial 302. Investigar gap de imposto global (filial 203, TES). (desde session-223)
- [ ] Testar stout-skill-manager end-to-end com skillfish real. Promover stout-skill-manager para golden copy via stout-promote-skill. Atualizar SKILL.md do stout-create-skill para referenciar novo fluxo com stout-skill-manager antes de fabricar. (desde session-226)
- [ ] Filtrar promote_skills.py por skill escolhida (hoje promove tudo do PROMOTION_MAP); Remover/inativar stout-governance-orchestration-engine do registry (inactive); Migrar stout-brainstorming e stout-cdd-orchestrator para .shared-ai-memory/skills permanentemente (desde session-227)
- [ ] stash{0} faturamento-auditoria-bi: verificar se consolidate_cevap.py +93 linhas e trabalho valido ou duplicado (desde session-229)
- [ ] stash{1} potencial-forecasted: verificar se transform.py ja esta em master antes de descartar (branch mergeada) (desde session-229)
- [ ] Merge feat/cooldown-aging-backfill -> master na sessao do cooldown-aging (desde session-229)
- [ ] Proxima tarefa: 2026-06-09-plano-implementacao-preenchimentos.md em lead-csc-pops (branch feat/cevap-operational-steps) (desde session-230)
- [ ] Avaliar 6 fontes com alerta de recencia: Cadastro Clientes, Seedz, InovaPay, Orcamentos Abertos/Cancelados, BUP Pos-Venda (desde session-231)
- [ ] Taxa cobertura oficina M3 = 0% - investigar imputacao de horimetro (desde session-231)
- [ ] Fazer merge ou PR da branch feat/pipeline-potencial-refresh (desde session-231)
- [ ] Merge feat/bup-cevap-entrada-dates para master no BUP standalone|Items 2-5 do handoff: threshold Dias_Inativo<90, path cidade_mesoregiao, resgate_dados_v4.py, orquestrador (desde session-232)
- [ ] Merge fix/cevap-kpis-n-orcamento-html-report em main quando aprovado (desde session-233)
- [ ] Sincronizar CEVAP_ATIVACAO no OneDrive apos usuario fechar Excel e rodar patch_n_orcamento.py (desde session-233)
- [ ] Aging por consultor mostra N/A ate BUP rodar com Fabric e gerar cevap_entrada_dates.json (desde session-233)
- [ ] Corrigir CLAUDE_SESSION_DIR no config do context-agent para apontar para ~/.claude/projects|Commitar mudancas pendentes no lead-csc-pops (rename Data_Primeiro_Alerta->Data_Alerta) na branch correta|Atualizar fontes ausentes no BUP: Cadastro Clientes, Orcamentos Abertos/Cancelados, Detalhamento Pecas 2025/2026 (desde session-234)
- [ ] Rodar motor M2 antes de gerar daily para ter dados atualizados. Substituir Excel BI por detalhamento_vendas_2026.parquet no audit_bi.py quando motor Detalhamento-Pecas for corrigido. (desde session-235)
- [ ] Nenhuma pendencia nesta sessao; continuar o desenvolvimento de consultores na branch feat/de-volta-consultor-cnpj. (desde session-237)
- [ ] Deletar branch feat/lead-csc-pops-kpi-mensal-consultor|Monitorar novos ciclos encerrados no historico (desde session-238)
- [ ] Rodar run.py --ano 2026 na proxima sessao; Validar soma Valor Liquido 2026 contra referencia manual (desde session-239)
- [ ] Testar generate_leads.py end-to-end apos mudancas de schema Serial_Number com underscore (desde session-241)
- [ ] Replicar design system CEVAP para outros relatorios HTML da suite (ex: De-volta-para-inova) (desde session-242)

## Decisões Recentes
- [session-240] *.parquet, *.xlsx e *.xls nunca devem ser commitados - outputs de pipeline sao regeneraveis via ligar_motores.py; .gitignore atualizado em commit 5d9651b (2026-06-11)
- [session-240] Commits de refresh de pipeline devem conter apenas arquivos de codigo, config e docs — nunca dados brutos ou artefatos de saida
- [session-240] - [session-236] 67	    "decidimos", "vamos usar", "optamos por", "escolhemos",
- [session-240] - [session-236] 68	    "a decisão foi", "ficou decidido", "definimos que",
- [session-240] - [session-236] 69	    "a abordagem será", "seguiremos com",
- [session-240] - [session-236] 70	    "we decided", "let's use", "we'll go with", "the decision is",
- [session-240] - [session-236] 71	    "we chose", "going with", "the approach will be", "decided to",
- [session-240] - [session-239] 235	            r"\b(decidimos?|optamos?|escolhemos?|vamos usar|foi definido)\b\s+(?:por|que|o|a)?\s*(.{20,200})",
- [session-241] Usar carregar_mapa_consultores_por_chassi nunca mapeamento inline para coluna Consultor|Chave de persistencia Nota_Fiscal e Serial_Number 1-1 por chassi|Estado de Nota_Fiscal em parquet consistente com padrao do projeto|Regra Proxima_Revisao=2000 tem prioridade sobre verde A-Ataque Imediato|OUTPUT_XLSX aponta para leads_campanha_de-volta-para-inova.xlsx
- [session-242] Design system CEVAP (#1F2937+#FFC20E) adotado como padrao para relatorios HTML da suite Inova; logos em Template/ local para evitar dependencia cross-project; semaforo adesao >=80% verde/>=50% amarelo/<50% vermelho; Potencial Financeiro sempre neutro

## Bloqueadores Ativos
- Nenhum

## Últimas Sessões
- session-238: lead-csc-pops: KPI HTML mensal+consultor + fix historico ciclos legados
- session-239: Deploy Detalhamento-Pecas + stout-init
- session-240: Pipeline potencial-clientes: refresh diário + gitignore dados
- session-241: De-volta-para-inova: Consultor, formatação e persistência de Nota_Fiscal
- session-242: Padronizacao Design HTML lead-csc-pops (CEVAP dark+yellow)
