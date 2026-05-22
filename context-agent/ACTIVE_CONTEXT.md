# Contexto Ativo — Atualizado em 2026-05-22 17:22

## Projetos Ativos
| Projeto | Status | Última Sessão | Próxima Ação |
|---------|--------|---------------|--------------|
| **Antigravity Stout** | 🛠️ Em Estabilização | — | Validar detecção do NotebookLM pós-restart. |
| **Inova John Deere** | 📅 Em Espera | — | Prosseguir com M1-M4 após estabilização do motor. |
| **Configuration-Driven Development** | ✅ Ativo | — | Finalizar Auditoria e Sincronização de Skills. |
| **Context Agent** | ✅ Ativo | — | Manter sincronização de sessões Antigravity. |

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

## Decisões Recentes
- [session-181] Threshold de cancelamentos mantido em R$ 50K|Formatação: M para milhões, K para milhares, vírgula como separador decimal, % sem casas decimais|Template sem emojis em nenhuma camada (generator, snapshot, auditor)|Quebras de linha com backslash no bloco RECAP e no bloco de acumulado/meta/ritmo
- [session-183] win32com em vez de SMTP/Graph API — Outlook já autenticado, zero config|Seg-Sex 08:20 para e-mail (não Ter-Sab) — Segunda pega relatório da Sexta automaticamente|StartWhenAvailable=true via XML — roda ao ligar se passou do horário|Título padronizado em português: 'Diário Inova' em assunto e corpo|Footer: 'Gerado automaticamente pelo agente Diário Inova' sem horário
- [session-187] CEVAP usa BUP como fonte unica — nao mais pipeline proprio
- [session-187] Dias_Inativo e Data_Ultima_Compra derivados do SF2010 ao vivo (qualquer consultor, sem filtro de data)
- [session-187] Valor_12m permanece do cache M3 — migracao para SF2010 rejeitada por complexidade do TES
- [session-187] Task CEVAP agendada 17:40 Seg-Sex com StartWhenAvailable para recuperar execucoes perdidas
- [session-187] BUP tem repositorio git proprio dentro do monorepo Inova — commits separados
- [session-188] preflight.py verifica dependencias de primeiro nivel antes de lancar qualquer skill via orchestrator / campo promoted_at adicionado a todos os registries (null=nunca promovida, ISO date=ultima promocao) / promote_runner.py exibe skills pendentes ao final e oferece continuar promovendo / docs_archiver ativo-para-legado abandonado pois move diretorios que sao alvos de junctions dos projetos / stout-promote-skill tem dependencies:[stout-skill-auditor] no registry
- [session-190] Remoção automática de zeros padding para busca de CPFs de 11 caracteres no banco Fabric
- [session-191] Valor alvo = Valor Líquido (não Valor Bruto). Targets: 2025=R99.8M, 2026=R5.4M, combinado=R75.2M (dentro de 0,045% do PowerBI R75.367M). Correção principal no extract.py: incluir OR FILIAL LIKE 03% no WHERE.

## Bloqueadores Ativos
- Nenhum

## Últimas Sessões
- session-187: Motor CEVAP: BUP como fonte unica + task scheduler
- session-188: Orchestrator Preflight + promoted_at + stout-promote-skill
- session-189: <USER_REQUEST>
- session-190: Consulta Cadastral e de Faturamento do BUP
- session-191: M2 Faturamento - Reverse Engineering da Query PowerBI
