# Spec: Mission_Stout — Bússola Estratégica do Ecossistema Inova AI

**Data:** 2026-04-19
**Autor:** Victor Bernardi
**Status:** Aprovado

---

## Propósito

O Mission_Stout é uma bússola de trabalho — não um documento corporativo. Serve para que Victor e o LLM verifiquem, a qualquer momento, se o que estamos construindo está alinhado com os objetivos de longo prazo da transformação da Inova em uma empresa gerida por IA e agentes.

---

## Seção 1: Norte Verdadeiro + Visão de Longo Prazo

### Norte Verdadeiro
> *"Transformar a Inova em uma empresa onde agentes de IA operam os processos e humanos dirigem a estratégia."*

### Missão Atual
> *"Entregar agentes que ampliam a capacidade de decisão de cada pessoa da Inova — em vendas, técnica, operações e conhecimento."*

### Visão de Longo Prazo (10+ anos)
A Inova opera com uma fração do headcount atual. Cada área tem agentes autônomos integrados ao ERP (Proteus), CRM, Power BI e telemetria de máquinas (JDLink/MTG). O consultor humano é diretor de estratégia — não executor de processo. A Inova é referência nacional em AI para concessionárias de equipamentos pesados.

---

## Seção 2: Valores Operacionais

Princípios que guiam cada decisão de construção. Quando em dúvida, voltar aqui.

**1. Dados antes de opinião**
Nenhum agente, processo ou decisão é validado por feeling. Toda hipótese tem uma métrica.

**2. Agente como colega**
O AI não é ferramenta — é membro da equipe. Cada agente tem papel, responsabilidade e contexto definidos.

**3. Entregar antes de perfeiçoar**
Um agente funcionando em produção aprende mais do que um agente perfeito no papel. Ship cedo, itere rápido.

**4. Simplicidade radical**
Nenhum processo humano existe se um agente pode fazer melhor. A complexidade é o inimigo.

**5. Decisão com contexto completo**
Todo consultor, técnico e gestor decide com a melhor informação disponível — fornecida pelos agentes, no momento certo.

---

## Seção 3: Mapa de Agentes por Área

### Vendas
| Agente | Status | Função |
|--------|--------|--------|
| Insight Sales | Em construção | Gera script de visita, análise de frota e oportunidades antes do consultor sair para o cliente |
| Previsão de Faturamento | Futuro | Previsão por consultor/região, integrado a vendas e pós-vendas |

### Pós-vendas / Técnica
| Agente | Status | Função |
|--------|--------|--------|
| Diagnóstico de Máquina | Futuro | Histórico + telemetria JDLink/MTG, sugestão de peças, abertura inteligente de OS |

### Conhecimento Interno
| Agente | Status | Função |
|--------|--------|--------|
| Cérebro Inova | Planejado | Responde perguntas sobre processos, manuais, decisões históricas, políticas internas |

### Operações / Logística
| Agente | Status | Função |
|--------|--------|--------|
| Disponibilidade Física | Futuro | Estoque preditivo, disponibilidade de peças e máquinas |

### Estratégia & Mercado
| Agente | Status | Função |
|--------|--------|--------|
| Novos Negócios | Futuro | Pesquisa de mercado externo, tendências do setor, benchmark de concorrentes |

### Evolução do Ecossistema
| Agente | Status | Função |
|--------|--------|--------|
| Córtex | Futuro | Consulta NotebookLMs, gera notas que viram fontes, retroalimenta todos os agentes e o ecossistema (Antigravity, Claude Code, LLMs, Victor) com orientações de evolução |

---

## Seção 4: Critério de Priorização de Agentes

Antes de construir qualquer agente, três perguntas a responder juntos:

1. **Qual decisão ele melhora?** — se não há decisão clara, não construir
2. **Qual dado ele consome?** — se o dado não existe ou não é confiável, resolver isso primeiro
3. **Quem evolui com ele?** — pessoa, processo ou outro agente

---

## Fora de Escopo

- Financeiro (exceto previsão de faturamento relacionada a vendas/pós-vendas)
- RH e gestão de pessoas
- Documento formal para apresentação à liderança da Inova

---

## Relação com o Ecossistema Técnico

O Mission_Stout orienta o que construir. O ecossistema técnico é como construímos:

| Camada | Ferramentas |
|--------|-------------|
| Desenvolvimento | Claude Code, OpenCode |
| Memória & Conhecimento | Wiki (Obsidian), NotebookLM, Antigravity (context-agent) |
| Orquestração | Antigravity skills, MCP/A2A protocols |
| Evolução | Córtex (agente futuro) |
