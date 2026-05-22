# Contexto Ativo — Atualizado em 2026-05-13 03:25

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
- [ ] PENDENCIA (BAIXA PRIORIDADE): ~43 scripts auxiliares e rascunhos ainda referenciam path antigo C:\Projetos\Inova\Potencial Clientes. Usar grep -r 'Potencial Clientes' --include=*.py para localizar. Corrigir importando shared/config.py via parents[N]. Nao bloqueia o pipeline principal. (desde session-087)
- [ ] Validar consumo do novo parquet pelo Motor de Estratégia, Migrar motor_identidade_m0.py para legado. (desde session-088)
- [ ] [PENDENTE] Validar execução de todos os motores em 'pipelines/potencial-clientes' para garantir que não há erros causados pelo novo dataset_ouro_identidade.parquet. (desde session-089)
- [ ] Validar ingestao de orfaos no M0 (proxima sessao); Rodar Motor M4 (Estrategia) com novos datasets ouro. (desde session-090)
- [ ] Monitorar conclusao do QSA Scan. Executar batch v11.7 final apos 100% de coleta. (desde session-091)
- [ ] Corrigir ~43 scripts com path hardcoded antigo (desde session-092)
- [ ] Nenhuma acao imediata. Aguardar conclusao automatica. (desde session-093)
- [ ] Migrar 04_Estrategia; Migrar 05_Segmentacao; Deletar _pre_migration após 2026-05-26; Configurar Task Scheduler; Corrigir ~43 scripts com path antigo (desde session-094)
- [ ] Restart Gemini CLI session; Resume wiki-ingest process; Read vault metadata (.manifest.json, index.md, log.md) (desde session-095)
- [ ] Corrigir ~43 scripts com path hardcoded Potencial Clientes (desde session-096)
- [ ] Automatizar copia de segmentation_logic.py e inova_audit_core.py de 00_Cerebro_Inova para shared/ via stout_promote.py ou hook (desde session-097)
- [ ] Automatizar copia de segmentation_logic.py e inova_audit_core.py de 00_Cerebro_Inova para shared/ via stout_promote.py ou hook (desde session-099)
- [ ] Executar testes em producao para liberar _pre_migration dos stages 01/03/04/05 da quarentena (prazo minimo: 2 semanas apos 2026-05-12) (desde session-099)
- [ ] [PESQUISA CRÍTICA] Refinar e modernizar o Agentic Design Framework (Stout Edition) com base em estudos de 2025/2026 sobre MAS e Cognitive Architectures. (desde session-101)
- [ ] [SKILL] Criar skill de autocorreção de linting automática (sem acionamento manual) no núcleo Stout. (desde session-102)
- [ ] Executar seo_ge_batch_v11_7.py; configurar agendamento semanal. (desde session-103)
- [ ] [STOUT] Criar skill de autocorreção de linting (pendência registrada no storage global). (desde session-104)
- [ ] Monitorar conversão inversa no log JSON; Sincronizar logs de auditoria com o dashboard central. (desde session-105)

## Decisões Recentes
- [session-099] segmentation_logic.py e inova_audit_core.py: source of truth em 00_Cerebro_Inova/, copia obrigatoria em shared/ para o pipeline importar via parents[N]
- [session-099] Baseline de validate_pipeline.py deve ser atualizado no mesmo commit de refatoracao que mude schema de parquet — divergencia cascata em stages downstream e esperada e documentada
- [session-099] Arquivos _pre_migration em quarentena: 02_Faturamento liberado a partir de 2026-05-26, demais stages a definir apos testes em producao
- [session-099] context-agent --decisions e --tasks agora suportam multiplos flags (action=append) — cada flag acumula na lista em vez de sobrescrever
- [session-103] Scan QSA marcado como concluído; prioridade alterada para BATCH FINAL.
- [session-104] Priorizar CNPJ da Filial como chave primária de herança de feedback (fallback para ID/Nome de Grupo); Adotar validação de volumetria de observações como check obrigatório pré-exportação.
- [session-105] Implementação de filtragem física total de convertidos (<90 dias); Migração do relatório de alertas Excel para Log JSON acumulativo (conversao_audit.json); Saneamento sistêmico de encoding UTF-8 em todo o projeto.
- [session-105] 1.  **Brainstorming:** Escolhemos a abordagem executiva **"Onde as vendas perderam fôlego?"** para substituir a afirmação imprecisa de que as vendas haviam parado.
- [session-106] Substituir similaridade de string por mapeamento de CNPJ Grupo via M0 para listas de exceção; Integrar listas estratégicas permanentemente no código fonte do motor.
- [session-106] 1.  **Brainstorming:** Escolhemos a abordagem executiva **"Onde as vendas perderam fôlego?"** para substituir a afirmação imprecisa de que as vendas haviam parado.

## Bloqueadores Ativos
- Nenhum

## Últimas Sessões
- session-102: <USER_REQUEST>
- session-103: Monitoramento QSA Scan e Atualização GEMINI.md
- session-104: Consolidação Motor CEVAP v1.5 - Blindagem de Feedbacks e Integração M0
- session-105: Consolidação Motor CEVAP Gold v2
- session-106: Conclusão Final: Motor CEVAP Gold v2


---
## ✅ GCC MERGE — Branch 'scanner-v2-stock-integration' Consolidado (2026-05-13 04:08)

# Learnings: scanner-v2-stock-integration
- Branch encerrado para dar lugar a nova hierarquia do Relatorio Executivo.
- Conhecimento sobre filtros TES e integracao de estoque consolidado no motor M2.
---
