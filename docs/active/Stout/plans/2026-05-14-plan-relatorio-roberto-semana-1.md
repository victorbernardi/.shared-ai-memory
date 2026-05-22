# Plano de Implementacao: Relatorio Executivo (Roberto) - Semana 1

> **Para Claude:** Este plano foca na criacao das ferramentas de apoio para que o Victor gere o relatorio manualmente.

**Objetivo:** Criar scripts de extracao e analise para compor o "Storytelling" da Semana 1 (Historia Atual + Recapitulacao 2026).

---

### Tarefa 1: Setup do Ambiente Analitico

**Arquivos:**
- Criar: `Projetos/Relatorio-Roberto/src/config.py`
- Criar: `Projetos/Relatorio-Roberto/src/db_utils.py`
- Criar: `Projetos/Relatorio-Roberto/.env` (Copiar do Historico-de-Vendas)

**Passo 1: Criar estrutura de pastas**
`mkdir -p Projetos/Relatorio-Roberto/src Projetos/Relatorio-Roberto/data/outputs`

**Passo 2: Configurar conexao e filtros base**
Consolidar filtros de TES (Oficina vs Consultores) e caminhos para os Motores M0-M5.

### Tarefa 2: Motor de Recapitulacao (2026 ate hoje)

**Arquivos:**
- Criar: `Projetos/Relatorio-Roberto/src/recap_2026.py`

**Passo 1: Extrair marcos historicos**
Script para identificar meses de pico, evolucao de familias (Lubrificantes, etc) e performance acumulada por filial.

**Passo 2: Gerar insights de GAP**
Cruzar com M5 para quantificar "O que foi perdido" em 2026.

### Tarefa 3: Motor de Historia Atual (Ontem/Semana)

**Arquivos:**
- Criar: `Projetos/Relatorio-Roberto/src/current_history.py`

**Passo 1: Extracao Ontem vs Anteontem**
Faturamento por Filial e Consultor.

**Passo 2: Calculo de Intensidade de Mix**
Media de SKUs por NF ontem.

### Tarefa 4: Motor de Oportunidades (BUP + CEVAP)

**Arquivos:**
- Criar: `Projetos/Relatorio-Roberto/src/opportunities.py`

**Passo 1: Consolidar listas de acao**
Clientes Top GAP (M5) sem compra (CEVAP).

### Tarefa 5: Gerador de Texto (Template)

**Arquivos:**
- Criar: `Projetos/Relatorio-Roberto/src/generator.py`

**Passo 1: Unificar outputs em Markdown**
Criar a estrutura do e-mail em texto puro com os placeholders preenchidos pelos scripts acima.
