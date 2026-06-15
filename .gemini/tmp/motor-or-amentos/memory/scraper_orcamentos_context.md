# Contexto Arquitetural: Scraper Motor-Orçamentos

## Metadados
- **Projeto**: `pipelines/potencial-clientes/Motor-orçamentos`
- **Tipo de Contexto**: Arquitetura e Decisões Técnicas (Scraping)
- **Data de Captura**: 11/06/2026

## Decisões Arquiteturais
1. **Reuso de Autenticação**: O scraper reaproveita a pasta `browser_state/user_profile` gerada pelo projeto `dashboard-inova-data-export` (`authenticate.py`). Isso evita prompts de SSO e desafios interativos na execução automática.
2. **Framework**: Playwright (Sync API) e Pandas.
3. **Padrão de Espera e Interação**: Ao interagir com o Power BI Embedded, os tempos de espera são explicitamente controlados por meio de variáveis em `config.py` (`PAGE_LOAD_TIMEOUT`, `RENDER_WAIT`, etc.) em vez de tempos chumbados no código.

## Quirks (Comportamentos Específicos) do Power BI Embedded
- **Visibilidade Falsa (DOM Virtualization)**: Os componentes do Power BI, especialmente o `visual-container` das tabelas, frequentemente reportam `hidden` no Playwright mesmo quando visíveis na tela, o que faz com que `.wait_for(state="visible")` resulte em timeout.
  - **Solução**: Usar as classes nativas `.tableEx, .pivotTable`, aguardar o estado `attached` em vez de `visible`, e forçar o evento via `.hover(force=True)`.
- **Filtros de Data (Date Slicers)**: A estrutura de inputs de data suporta seletor genérico (`input.date-slicer-datepicker`). O formato aceito pela caixa de texto precisa estar limpo, ex: `dd/mm/yyyy`.
- **Botão de Exportação**: O botão "Mais opções" (`.vc-menu-trigger`) exige um hover explícito na tabela para ser ativado. O menu "Exportar dados" renderiza fora do iframe, então procuramos nos dois escopos (iframe e page) e interceptamos o download com `page.expect_download`.

## Integração
- O processo é acionado no orquestrador pelo `run.py`.
- Em iterações futuras, os dados serão cruzados com a fonte do `Microsoft Fabric` (`shared/fabric_db.py`).