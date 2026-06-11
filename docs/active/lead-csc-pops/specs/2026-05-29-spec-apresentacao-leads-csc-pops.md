# Spec — Apresentação PowerPoint: Campanha de Leads Preventivos de Pós-Vendas

**Data:** 2026-05-29 | **Status:** READY FOR DEV

---

## Understanding Summary

Gerar apresentação PPTX de 10 slides para a Campanha de Leads Preventivos (FPS e Material Rodante) destinada a gerentes e coordenadores regionais da Inova Máquinas. A apresentação utiliza o layout dark brutalist premium já validado em `apresentacao-roberto-2505`, replicando a estrutura visual e alterando apenas os textos.

## Assumptions

- Layout 100% reaproveitado de `apresentacao-roberto-2505/src/generate_slides.py`
- Logos vindos de `C:\Projetos\Inova\projects\lead-csc-pops\Template\`
- Sem gráficos (sem dados ainda); conteúdo é textual/tabular
- Slides 6 e 7 usam visual do `daily_report_kpis.html` como imagem de fundo/referência com anotações de seta

## Decision Log

| Decisão | Motivo |
|---------|--------|
| Replicar layout existente sem alterações de tema | Economiza tempo, mantém identidade visual aprovada |
| Capa: título + logos + subtítulo, sem data | Instrução explícita do usuário |
| 2 slides de KPI separados (Bloco 1 e Bloco 2) | Conteúdo da campanha tem duas camadas: resultado e metodologia |
| Screenshot do HTML para slides KPI | Não temos dados reais ainda; HTML já tem visual pronto |
| Usar imagens pequenas ilustrativas quando possível | Instrução explícita do usuário |

## Estrutura dos 10 Slides

| # | Slide | Eyebrow | Título | Conteúdo Principal |
|---|-------|---------|--------|-------------------|
| 1 | Capa | — | CAMPANHA DE LEADS PREVENTIVOS DE PEÇAS | Logo Inova + Logo JD + subtítulo |
| 2 | O Problema | diagnóstico comercial // peças | O CUSTO DO PROCESSO REATIVO | Cards: FPS, Rodante, perdas para concorrência |
| 3 | A Solução | motor de leads // visão geral | MOTOR AUTOMATIZADO DE GERAÇÃO DE LEADS | 5 passos do fluxo operacional |
| 4 | Como os Alertas São Gerados | régua de alertas // horímetros | QUANDO O SISTEMA DISPARA O ALERTA | Tabela de réguas + diagrama do ciclo |
| 5 | Carga Inicial vs Ciclo Contínuo | régua de alertas // carga inicial | PRIMEIRA CARGA: PARTINDO DO ZERO SEM RUÍDO | Exemplo prático 200G 4.200h |
| 6 | KPI Bloco 1 | indicadores // desempenho | INDICADORES DE DESEMPENHO (KPIs) | Visual KPI + setas explicativas |
| 7 | KPI Bloco 2 | indicadores // metodologia | METODOLOGIA E AGING COMERCIAL | Visual Aging table + setas explicativas |
| 8 | Ponte da Verdade | governança // auditoria | A PONTE DA VERDADE: PLANILHA × PROTHEUS | Fluxo auditoria + Aderência de Propostas |
| 9 | Responsabilidades | papéis e responsabilidades | QUEM FAZ O QUê NA CAMPANHA | Tabela RACI simplificada |
| 10 | Próximos Passos | roadmap // implantação | PRIMEIROS MARCOS DA CAMPANHA | Timeline Semana 1 → Mês 2 |

## Arquivos de Output

- `C:\Projetos\Inova\projects\lead-csc-pops\docs\business\Campanha-Leads-Preventivos-Inova.pptx`
- Script: `C:\Projetos\Inova\projects\lead-csc-pops\docs\business\generate_slides_leads.py`
