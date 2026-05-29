# Arquivo Consolidado — 2026

### Sessão 155 — 2026-05-19
  - 1. Adotado o Padrão Elite (CDD) para governança de recência. 2. Os utilitários locais (Markdown Fixer e Pipeline Orchestrator) foram mapeados para promoção global no roadmap Stout. 3. Estabelecido o protocolo de 'Mocks Agressivos' para testes de orquestradores acoplados (até refatoração futura).

### Sessão 156 — 2026-05-19
  - Usar MAX(50% M3, 120% Histórico) para potencial; Aplicar amortecimento por SOW para equilibrar metas; Priorizar consultor ativo 2026.

### Sessão 157 — 2026-05-19
  - Usar MAX(50% M3, 120% Histórico) para potencial; Aplicar amortecimento por SOW para equilibrar metas; Priorizar consultor ativo 2026.

### Sessão 158 — 2026-05-20
  - Usar arredondamento de 2 casas e formato decimal 0-1 para percentuais no Excel; Adotar design 'Double-Bezel' da Inova para apresentações; Manter Autoconsumo (Inova Máquinas) no volume total da campanha.

### Sessão 159 — 2026-05-20
  - Mantido o faturamento de autoconsumo na base de metas conforme orientacao; Inclusao do Status da Carteira na aba PERF_POR_CONSULTOR por Folga Teto; Salvamento do padrao dourado de e-mail do Victor na skill local internal-comms.

### Sessão 160 — 2026-05-20
  - Consultor deriva do Status_Oportunidade (PENDENTE:INATIVO sempre CEVAP) | Dias_Inativo baseado em venda por consultor ativo, não qualquer venda | Filial sempre LIKE 02% ou 03%, nunca IN hardcoded | np.nan não é consultor válido — usar _consultor_valido() | test_bup_output_invariants.py é o QA oficial do BUP

### Sessão 161 — 2026-05-20
  - Centralizar governance_sensor.py em /shared. M3 salva datasets finais de forma redundante local e shared para viabilizar auditorias locais sem conexões de rede.

### Sessão 162 — 2026-05-20
  - Manter arquivos Excel locais do pipeline ativos e protegidos por regras estritas no .gitignore. Arquivar código canary antigo. Mapear migração estrutural para pasta docs/plans.

### Sessão 163 — 2026-05-20
  - Manter arquivos Excel de dados do pipeline no ambiente local, isolados por novos arquivos .gitignore em data/. Mapear a biblioteca Pandera como validador de schema estrutural declarativo unificado para o item 3 do Roadmap CDD.

### Sessão 164 — 2026-05-20
  - Centralização do sensor de governança exclusivamente em /shared/governance_sensor.py (padrão consolidado M3). Fail-Fast Tolerante (fail_fast=False) para execução local do M5. Post-flight com subprocess check=False envelopado em try/except. Chave M5 (Estratégico) renomeada para M4 (Estratégia) em generate_recency_report.py. Saída de ouro M5 (Segmentação Executiva) adicionada ao monitoramento de recência.

### Sessão 165 — 2026-05-20
  - Descartar 4 skills sem conteúdo real: cdd_technical_skill, self_healing_skill, stout_knowledge_fallback, welcome_skill. Corrigir audit script para usar regex uppercase-only para TODO/TBD (evitar falso positivo com português 'todos'). 20 skills stout-* promovidas ao Golden Copy substituindo legadas. stout-init separado do fix do stout_promote (será plano futuro).

### Sessão 166 — 2026-05-20
  - A transicao de carteira da Eliane Gils foi implementada usando apenas associacao de nomes (Vinicius Lenzi e Danilo Bernoulli) para soma e comparacao combinada.

### Sessão 167 — 2026-05-20
  - Utilizar servidor headless nativo (opencode serve) via localhost:4096 para bypass do bloqueio de API cloud

### Sessão 168 — 2026-05-20
  - Alinhamento das ferramentas stout_promote.py e post_approve.py nas instâncias local e global dos templates do cdd addon na skill stout-init; Atualização do manifesto ADDON.md local e global para a versão 1.3.0.

### Sessão 169 — 2026-05-20
  - O plano Go do Command Code nao permite o uso do DeepSeek v4 Pro em clientes externos via API, apenas na sua propria CLI oficial.

### Sessão 170 — 2026-05-20
  - Drift detection: threshold 5%%, WARNING sem bloqueio de pipeline. Baseline gravado em data/m1_baseline.json. Protocolo de deprecação: prefixo _legacy_ + cabeçalho no arquivo.

### Sessão 171 — 2026-05-20
  - Pre-flight usa governance_sensor.run_preflight com fail_fast=False - Post-flight dispara generate_recency_report.py via subprocess com check=False em try/except - Segue mesmo padrão do Motor M5 para consistência - Skills CDD acessadas via mklink /J (junction, não symlink) pois não requer admin no Windows

### Sessão 172 — 2026-05-20
  - 1. Pre-flight usa governance_sensor.run_preflight(str(_shared_dir), fail_fast=False) em try/except logo após check_recency_report() — 2. Post-flight dispara generate_recency_report.py via subprocess.run com check=False envelopado em try/except após to_excel() — 3. Segue o mesmo padrão do Motor M5 (plano 2026-05-20-m5-recency-governance-plan.md) para consistência entre motores — 4. Skills CDD acessadas via mklink /J (junction, não symlink) pois não requer admin no Windows — 5. TDD: 2 testes novos em test_bup_recency_alert.py (TestGovernanceIntegration) validam presença de governance_sensor e generate_recency_report.py no código fonte

### Sessão 174 — 2026-05-20
  - Usar funcao PowerShell no profile em vez de mecanismo nativo /add-dir. O profile ja foi atualizado com sucesso.

### Sessão 175 — 2026-05-20

### Sessão 176 — 2026-05-20
  - Log usa substring matching para evitar problemas de encoding Unicode (acentos). Apenas fontes consumidas pelo BUP aparecem no log (9 fontes). Seedz e InovaPay permanecem manuais.

### Sessão 177 — 2026-05-20

### Sessão 178 — 2026-05-20
  - Usar Python read_bytes/write_bytes como fallback quando edit_file falhar com CRLF|Nunca usar PowerShell -replace para editar código Python|Stout-init templates precisam de stout_promote.py e post_approve.py (corrigido)|4 skills casca vazia removidas e registradas no roadmap V6.12 como backlog

### Sessão 179 — 2026-05-20
  - Fonte de dados CC = M2 (cache_vendas_rfm.parquet), nao vw_VENDAS. Linha Sem Centro de Custo obrigatoria para reconciliacao 100%. Sem emojis no e-mail.

### Sessão 180 — 2026-05-20

### Sessão 181 — 2026-05-20
  - Threshold de cancelamentos mantido em R$ 50K|Formatação: M para milhões, K para milhares, vírgula como separador decimal, % sem casas decimais|Template sem emojis em nenhuma camada (generator, snapshot, auditor)|Quebras de linha com backslash no bloco RECAP e no bloco de acumulado/meta/ritmo

### Sessão 182 — 2026-05-20

### Sessão 183 — 2026-05-20
  - win32com em vez de SMTP/Graph API — Outlook já autenticado, zero config|Seg-Sex 08:20 para e-mail (não Ter-Sab) — Segunda pega relatório da Sexta automaticamente|StartWhenAvailable=true via XML — roda ao ligar se passou do horário|Título padronizado em português: 'Diário Inova' em assunto e corpo|Footer: 'Gerado automaticamente pelo agente Diário Inova' sem horário

### Sessão 184 — 2026-05-20
  - win32com (Outlook desktop) em vez de SMTP ou Graph API — zero config, usa sessao Outlook existente|Graph API descartada: client_id do Azure CLI (fabric_db.py) nao tem permissao para Mail.Send|StartWhenAvailable=true via XML — roda ao ligar se passou do horario|Tasks criadas via schtasks sem admin (modo usuario interativo)|Seg-Sex 08:20 para e-mail — Segunda captura relatorio da Sexta automaticamente|Titulo padronizado: 'Diario Inova' em PT em assunto e corpo|Footer sem horario: 'Gerado automaticamente pelo agente Diario Inova'|Backslashes MD removidos no _md_to_html antes da conversao
