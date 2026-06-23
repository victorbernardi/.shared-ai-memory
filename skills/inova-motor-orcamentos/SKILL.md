---
name: inova-motor-orcamentos
description: "Use quando precisar atualizar, rodar ou orquestrar o motor de orçamentos da Inova. Esta skill executa o pipeline completo (estágio 01_abertos via scraper Power BI + Fabric e estágio 02_cancelados via Fabric JDBC) e consolida os parquets de handoff em shared/data. Triggers: atualizar motor orcamentos, rodar motor orcamentos, atualizar orcamentos, motor-orcamentos, inova-motor-orcamentos."
---

# inova-motor-orcamentos

## Objetivo

Atualizar de forma íntegra o motor de orçamentos da Inova, executando sequencialmente os estágios `01_abertos` e `02_cancelados` e consolidando os parquets de handoff para o pipeline de Inteligência Comercial (estágio 08 do Potencial Clientes).

## Inputs esperados

- **Perfil Chrome persistente** (estágio 01): `C:\Projetos\Inova\projects\dashboard-inova-data-export\browser_state\user_profile` — obrigatório para o scraper Power BI evitar MFA/SSO.
- **Acesso JDBC ao Microsoft Fabric** (estágios 01 e 02): credenciais em `shared/config.py`.
- **Período de referência**: Janeiro de 2025 até `datetime.now()` (configurável no `run.py`).

<!-- @if platform=claude -->
## Fluxo Detalhado

O workspace fica em `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos`. Leia o `CONTEXT.md` da raiz antes de executar.

1. **Pre-flight**:
   - Configure o encoding do terminal Windows: `chcp 65001` e `PYTHONIOENCODING=utf-8`.
   - Confirme o runtime: use **sempre** `C:\Projetos\Inova\.venv\Scripts\python.exe` (nunca `python` nu).
   - Verifique a recência dos dados em `shared/recency_status.md`. O `run.py` já dispara `governance_sensor.run_preflight()` no início.
   - Garanta que o perfil Chrome persistente existe (estágio 01 aborta com `FileNotFoundError` se ausente).

2. **Execução do pipeline completo** (a partir da raiz do workspace):
   - `C:\Projetos\Inova\.venv\Scripts\python.exe run.py`
   - O `run.py` orquestra na ordem ICM: preflight de governança → estágio 01 (scraper PBI + limpeza + enriquecimento Fabric) → estágio 02 (extração Fabric JDBC + limpeza) → post-flight de recência.
   - O scraper do estágio 01 roda **headed** com perfil persistente (Azure AD SSO bloqueia headless).

3. **Validação (Critérios de Conclusão)**:
   - Confirme que os 3 parquets de handoff existem em `C:\Projetos\Inova\shared\data\` e têm > 0 linhas:
     - `orcamentos_abertos_enriquecidos.parquet` (deve conter `cod_vendedor`, `nome_vendedor`, `cnpj_cliente`)
     - `orcamentos_cancelados_2025.parquet`
     - `orcamentos_cancelados_2026.parquet` (coluna `motivo_cancelamento` legível, não códigos `000001`)
   - Reporte ao operador o total de linhas de cada artefato.

## Referências

- [CONTEXT.md (pipeline)](file:///C:/Projetos/Inova/pipelines/potencial-clientes/Motor-or%C3%A7amentos/CONTEXT.md)
- [01_abertos/CONTEXT.md](file:///C:/Projetos/Inova/pipelines/potencial-clientes/Motor-or%C3%A7amentos/01_abertos/CONTEXT.md)
- [02_cancelados/CONTEXT.md](file:///C:/Projetos/Inova/pipelines/potencial-clientes/Motor-or%C3%A7amentos/02_cancelados/CONTEXT.md)
<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->
## Fluxo

1. Configure o encoding (`chcp 65001`, `PYTHONIOENCODING=utf-8`) e use o venv canônico `C:\Projetos\Inova\.venv\Scripts\python.exe`.
2. A partir de `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos`, rode `python run.py` — ele executa preflight de governança, estágio 01 (PBI scraper + Fabric), estágio 02 (Fabric JDBC) e post-flight de recência.
3. Valide os 3 parquets em `C:\Projetos\Inova\shared\data\` (abertos enriquecidos + cancelados 2025/2026) e reporte as contagens de linhas.
<!-- @endif -->

## Constraints

- NUNCA pule estágios — a ordem numérica (01 → 02) é absoluta.
- NUNCA use `python` nu — sempre o path absoluto do venv canônico `C:\Projetos\Inova\.venv\Scripts\python.exe` ou `uv run --no-project python`.
- SEMPRE configure `PYTHONIOENCODING=utf-8` e `chcp 65001` antes de rodar no terminal Windows.
- NUNCA rode o estágio 01 sem o perfil Chrome persistente — aborta com `FileNotFoundError`.
- O estágio 02 exige acesso JDBC ao Fabric — sem fallback via scraper.
- NUNCA propague artefatos incompletos para downstream; se um estágio falhar, sinalize ao operador e pare.
- SEMPRE consuma o output do estágio anterior como input do próximo.

## Scripts

- `run.py` — entry point que orquestra o pipeline completo (governança + estágio 01 + estágio 02 + recência).
- `src/extract.py` — `extrair_orcamentos_abertos()`, `extrair_orcamentos_cancelados_fabric()`.
- `src/transform.py` — `limpar_orcamentos_abertos()`, `enriquecer_orcamentos_abertos()`, `limpar_orcamentos_cancelados()`.
- `src/config.py` — URLs do Power BI, paths e timeouts.

## Critérios de Conclusão

A skill é concluída quando o `run.py` roda os dois estágios sem falhas e os 3 parquets de handoff existem em `shared/data/` com > 0 linhas e as colunas obrigatórias presentes.
