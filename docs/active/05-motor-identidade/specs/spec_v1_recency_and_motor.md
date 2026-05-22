# ESPECIFICAÇÃO TÉCNICA - v1.0
## Atualização do Motor Identidade & Relatório de Recência Inova/BUP

### 1. Contexto de Negócio
- **Objetivo:** Garantir a atualização semanal confiável da "Tabela Verdade" (M0) de clientes no Protheus, mantendo a governança dos dados analíticos através do relatório de recência.
- **KPI Principal:** Percentual de recência das fontes de dados analíticos atualizados hoje.
- **Impacto:** Evita que os motores de DNA, Estratégico (M5) e de Vendas tomem decisões com dados desatualizados (stale data).

### 2. Escopo Técnico
1. **Auditoria de Conexão:** Testar a integridade das conexões com o Microsoft Fabric para as tabelas críticas (`SA1010`, `VV1010`, `VO1010`).
2. **Atualização Lógica (Ingestão/Download):**
   - Baixar os dados atualizados das 3 tabelas no Microsoft Fabric sem cache (`use_cache=False`).
   - Salvar os dados diretamente nos caminhos de cache definidos:
     - `m0_cache_sa1010_983280b9.parquet` (em `C:\Projetos\Inova\shared\data` e `data/`)
     - `m0_cache_vo1010_4871db6c.parquet` (em `data/`)
     - `m0_cache_vv1010_b6488ada.parquet` (em `data/`)
3. **Consolidação Batch (v11.7):**
   - Rodar o motor de elos transacionais e QSA (`scripts/seo_ge_batch_v11_7.py`) para gerar a nova Golden Copy `dataset_ouro_identidade.parquet` no diretório compartilhado.
4. **Relatório de Recência (Orquestração):**
   - Disparar o script `C:\Projetos\Inova\shared\generate_recency_report.py` para inspecionar os tempos de modificação físicos e registrar o status em `C:\Projetos\Inova\shared\recency_status.md`.
5. **Automação Pós-Carga:**
   - Propor/Implementar um script ou pipeline de orquestração local em PowerShell (`scripts/seo_ge_update_pipeline.ps1` ou similar) para encadear a atualização lógica, a unificação e a geração do relatório em um único comando orquestrado (atendendo à Regra 4 de Orquestração Polyglot).
