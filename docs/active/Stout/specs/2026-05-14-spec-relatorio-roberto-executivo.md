# Spec: Relatorio Executivo de Vendas (Roberto)

**Status:** Aprovado para Implementacao
**Data:** 2026-05-14
**Responsavel:** Victor Bernardi / IA (Apoio Analitico)
**Modelo de Operacao:** Desenvolvimento Iterativo e Manual

## 1. Objetivo do Negocio
Munir o gestor Roberto com informacoes densas, escritas e de alto valor agregado sobre a saude das vendas de pecas e oficina, utilizando o sumario como uma ferramenta de validacao de dados para futuras analises preditivas.

## 2. Escopo Narrativo (Storytelling)

### 2.1 Semana 1: "A Grande Recapitulacao"
- **Conteudo:** Historia atual (ontem/semana) + Resumo profundo do ano de 2026 ate hoje.
- **Destaques:** Identificar marcos historicos (ex: meses de pico, crescimentos anomalos em familias de produtos como lubrificantes, recordes de consultores).
- **Intuito:** Mostrar profundidade analitica e estabelecer a "linha de base" de confianca.

### 2.2 Semana 2 em diante: "O Ritmo da Operacao"
- **Conteudo:** Acompanhamento fluido da historia atual (ontem, semana, mes, ano atual).
- **Foco:** Desvios, metas, performance de consultores e gaps de oportunidade imediatos.

## 3. Requisitos de Informacao (Ampla e Profunda)
O relatorio nao deve ser massivo, mas deve cobrir multiplas dimensoes:
- **Performance Temporal:** Ontem vs. Anteontem, Semana vs. Semana Passada, Mes vs. Mes Passado, Ano vs. Ano Passado.
- **Dimensoes:** Consultores, Produtos (SKUs), Grupos/Subgrupos, Centros de Custos (Filiais/Oficina).
- **KPIs de Qualidade:** Intensidade de Mix (Itens por NF), Ticket Medio, Concentracao de Vendas.
- **Oportunidades:** Cruzamento de Clientes com Alto Potencial (M5/BUP) e Inatividade (CEVAP).

## 4. Arquitetura de Dados
- **Acesso Total:** Liberdade para cruzar qualquer tabela do Fabric (SQL) conforme a analise evoluir.
- **Motores (M0 a M5):** Consumo dos dados ja tratados de Identidade, Potencial (M4), SOW/Fidelidade (M5) e RFM.
- **CRM/Planilhas:** Integracao com CEVAP e BUP para a camada de "Acao Recomendada".

## 5. Entrega Final (Formato)
- Texto em Markdown formatado para e-mail.
- **NAO incluir graficos** (Foco em narrativa de gestão).
- Linguagem executiva, clara e provocativa (orientada a acao).

## 6. Validacao de Sucesso
- Roberto validar que os numeros de "Ontem" batem com o faturamento real.
- Identificacao de erros de filtros ou TES atraves do feedback do gestor.
- Evolucao progressiva da densidade do conteudo.
