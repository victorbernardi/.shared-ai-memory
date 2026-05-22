# Contexto Ativo — Atualizado em 2026-05-12 11:37

## Projetos Ativos
| Projeto | Status | Última Sessão | Próxima Ação |
|---------|--------|---------------|--------------|
| **Antigravity Stout** | 🛠️ Em Estabilização | — | Validar detecção do NotebookLM pós-restart. |
| **Inova John Deere** | 📅 Em Espera | — | Prosseguir com M1-M4 após estabilização do motor. |
| **Context Agent** | ✅ Ativo | — | Manter sincronização de sessões Antigravity. |
| Context Agent | active | — | — |

## Tarefas Pendentes
### Média Prioridade
- [ ] **[GOVERNANCE] Auditoria de Junctions:** Validar e corrigir mapeamentos de projetos Inova/Stout existentes para o novo padrão `active/`. (Prioridade: Usuário precisa resolver)
- [ ] Resolver autenticação NotebookLM via injeção de cookies (contornar erro de 'browser não confiável'). (desde 2026-05-11)
- [ ] **[SKILL] Atualizar `stout-init`:** Garantir que Junctions locais apontem obrigatoriamente para `.shared-ai-memory\docs\active\[projeto]`.
- [ ] **[SCHEDULER] Higiene de Docs:** Validar se o script `docs_archiver.py` está agendado e operando corretamente o fluxo active -> legacy.
- [ ] Implementar agendamento diário do Wave9_Deployment_OnePage.py no Windows Task Scheduler. (desde session-034)
- [ ] Monitorar estabilidade da conexão MCP nas próximas sessões; Validar se outros editores (Cursor/Windsurf) precisam de configuração similar via 'nlm setup add'. (desde session-053)
- [ ] Restaurar fidelidade visual 1:1 com o Dashboard_Executivo_M6.html original (Bento/GSAP/Glow) mantendo o motor modular. (desde session-040)
- [ ] Monitorar performance do ScrollTrigger; Avaliar necessidade de cores adicionais para alertas críticos. (desde session-041)
- [ ] Atualizar paleta de cores e background conforme item 1 do Design DNA. (desde session-041)
- [ ] Forçar o grid de filiais para `repeat(3, 1fr)` (2 linhas de 3). (desde session-041)
- [ ] Padronizar o título "PERFORMANCE POR UNIDADE" com o mesmo CSS das labels (`0.65rem`, `0.25em letter-spacing`). (desde session-041)
- [ ] Aplicar `backdrop-filter: blur(10px)` e fundo semi-transparente nos inputs `select`. (desde session-041)
- [ ] Reposicionar o overlay para o topo centralizado do card Hero. (desde session-041)
- [ ] Estilizar Tag com borda verde (`var(--jd-green)`) e fundo glass. (desde session-041)
- [ ] Refinar design das pílulas; Integrar outros KPIs na mesma bandeja no futuro. (desde session-042)
- [ ] Implementar filtro de Consultor; Aplicar regras de 4 casos no gráfico de linhas. (desde session-044)
- [ ] Iniciar nova sessão em C:\Projetos\Inova e configurar estratégia de rastreamento similar. (desde session-043)
- [ ] Validar APIs do Simonete, configurar follow-up automático no CRM e mapear horímetros do projeto Vitorânea. (desde session-049)
- [ ] Processar novas planilhas Excel assim que recebidas; Validar classificação (Balcao/Servicos/Wirtgen). (desde session-046)
- [ ] Transcrição dos áudios restantes na próxima sessão. (desde session-048)
- [ ] Refatorar FastMCP (upstream) para remover emojis nativos (opcional, patch atual é suficiente).
- [ ] Implementar filtro de Consultor; Agendamento do Wave 9; Ajustes de Grid UI. (desde session-070)
- [ ] Auditoria do Laboratório de Elos (Top 5); Bloqueio agressivo de telefone Dealer (Inova); Aguardar conclusão do QSA Crawler; Desenvolver Interface CLI Interativa SEO GE. (desde session-074)
- [ ] Realizar auditoria de rotina no laboratório; Integrar Dataset v11.7 ao Motor CEVAP. (desde session-075)
- [ ] Nenhuma pendencia critica de infraestrutura. Auditoria do Motor Identidade mapeada. (desde session-077)
- [ ] Executar busca massiva por dominios corporativos (Soberania Digital) em toda a base. Rodar wiki-ingest para sincronizar sessao com vault Obsidian. (desde session-079)
- [ ] Concluir auditoria dos demais grupos do snapshot; Monitorar crawler QSA (23%); Desenvolver interface CLI amigável ao ambiente. (desde session-080)
- [ ] Monitorar conclusão do Crawler QSA (23%); Implementar o consolidado da v11.7 no Microsoft Fabric. (desde session-081)
- [ ] Monitorar conclusão do crawler QSA (~23%); Executar unificação final societária (C9). (desde session-082)
- [ ] Aguardar massa crítica do QSA para unificação societária final. (desde session-083)
- [ ] Nenhuma pendência imediata para o CLI. (desde session-084)
- [ ] Atualizar ~43 scripts auxiliares que ainda referenciam path antigo C:\Projetos\Inova\Potencial Clientes. Usar grep -r 'Potencial Clientes' --include=*.py para localizar. Padrao de correcao: importar shared/config.py via parents[N]. Arquivos afetados: metas-pecas/scripts/rascunhos/ (7), pipelines/00_Motor_Identidade/ (~14), pipelines/05_Segmentacao/ (~8), pipelines/02_Faturamento/ (2), pipelines/99_Documentacao/ (~6), ligar_motores.py (1). (desde session-085)
- [ ] Proximo passo: brainstorming/plano de refatoracao modular para os 6 motores do pipeline (00_Motor_Identidade, 01_DNA, 02_Faturamento, 03_Potencial, 04_Estrategia, 05_Segmentacao). Padrao: extract.py + transform.py + load.py + run.py por motor. (desde session-086)
- [ ] PENDENCIA 1 (PRIORIDADE ALTA): Refatoracao modular dos 6 motores do pipeline (00 a 05) — dividir cada motor em extract.py + transform.py + load.py + run.py. Fazer brainstorming antes de implementar. Pesquisa deep research ja solicitada. | PENDENCIA 2 (BAIXA PRIORIDADE): ~43 scripts auxiliares e rascunhos ainda referenciam path antigo C:\Projetos\Inova\Potencial Clientes. Usar grep -r 'Potencial Clientes' --include=*.py para localizar. Corrigir importando shared/config.py via parents[N]. Nao bloqueia o pipeline principal. (desde session-087)
- [ ] Validar consumo do novo parquet pelo Motor de Estratégia, Migrar motor_identidade_m0.py para legado. (desde session-088)
- [ ] [PENDENTE] Validar execução de todos os motores em 'pipelines/potencial-clientes' para garantir que não há erros causados pelo novo dataset_ouro_identidade.parquet. (desde session-089)
- [ ] Validar ingestao de orfaos no M0 (proxima sessao); Rodar Motor M4 (Estrategia) com novos datasets ouro. (desde session-090)
- [ ] Monitorar conclusao do QSA Scan. Executar batch v11.7 final apos 100% de coleta. (desde session-091)
- [ ] Corrigir ~43 scripts com path hardcoded antigo (desde session-092)
- [ ] Nenhuma acao imediata. Aguardar conclusao automatica. (desde session-093)
- [ ] Migrar 04_Estrategia; Migrar 05_Segmentacao; Deletar _pre_migration após 2026-05-26; Configurar Task Scheduler; Corrigir ~43 scripts com path antigo (desde session-094)
- [ ] Restart Gemini CLI session; Resume wiki-ingest process; Read vault metadata (.manifest.json, index.md, log.md) (desde session-095)
- [ ] Corrigir ~43 scripts com path hardcoded Potencial Clientes (desde session-096)

## Decisões Recentes
- [session-085] Estrutura: pipelines/, projects/, shared/. Shared data = parquets consumidos por 2+ projetos. Stage data = caches internos com hash MD5. scripts/ + data/ + docs/ para todos os projects. parents[N] para resolucao de paths relativa ao script.
- [session-086] Cada motor sera dividido em 4 arquivos: extract.py (queries SQL + cache Fabric), transform.py (logica Pandas e regras de negocio), load.py (exportacao parquet/xlsx), run.py (orquestrador). Isso separa responsabilidades e facilita testes unitarios por camada.
- [session-088] Usar Double Export (Local/Shared), Implementar Schema Ouro de 11 colunas, Resolução híbrida de caminhos para cache e POPS.
- [session-089] Removida hierarquia de prioridade do POPS; caminho fixado em shared/data/Product_details_full.xlsx.
- [session-090] Usar CNPJ_GRUPO como chave unica de agregacao no M3 para evitar fragmentacao; Priorizar nomes do M0 no output final; Criar arquivo de feedback para expansao da base M0.
- [session-091] Uso de watchdog.py para gerenciar resiliencia do crawler. Remocao de emojis/acentos em logs de console Windows.
- [session-092] fabric_db.py em Documents/Fabric_Database_Connector mantido em sincronia com shared/fabric_db.py
- [session-094] 01_DNA lê dataset_ouro_dna_maquinas_v1.parquet (novo nome); 03_Potencial aponta para o mesmo arquivo novo; parque removido do 03_Potencial (dead code); dedup de PINs por maior Potencial Total antes do assert
- [session-095] Vault at C:\Users\victor.bernardi\Documents\wiki-compiler-vault is now trusted for wiki-ingest operations.
- [session-096] 05_Segmentacao: pot_total no auditoria inclui orfaos D1/D2 para paridade com M4

## Bloqueadores Ativos
- Nenhum

## Últimas Sessões
- session-092: Refatoração Pipeline Potencial Clientes — Piloto 02_Faturamento
- session-093: Registro Global do Monitoramento QSA
- session-094: Migração ETL — 01_DNA e 03_Potencial concluídos
- session-095: Persisting Vault Access & Preparing Wiki Ingest
- session-096: Deploy ETL Pipeline: Migração 04_Estrategia e 05_Segmentacao
