# Especificação Técnica: Melhoria Visual e Correção de Dados - PDF v2 (Revisada)

**Data:** 2026-05-12  
**Status:** Pesquisa (Brainstorming)  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Corrigir a exibição de rankings Top 5 e otimizar a distribuição espacial da Página 1, garantindo a distinção de SKUs com nomes idênticos sem poluir o visual com códigos numéricos.

## 2. Requisitos Funcionais (Problemas Identificados)
- **RF01 - Unicidade Visual:** Exibir barras distintas para SKUs diferentes, mesmo que possuam a mesma descrição.
- **RF02 - Otimização de Texto:** Não exibir códigos de ITEM nos labels para preservar o clean design.
- **RF03 - Visibilidade de Escala:** Utilizar escala logarítmica no gráfico de grupos para evidenciar itens de baixa magnitude.
- **RF04 - Layout Horizontal:** Migrar gráficos de barras para o formato horizontal para melhor aproveitamento de nomes longos.

## 3. Proposta de Solução (Arquitetura Visual)

### 3.1. Tratamento de Dados
- **Mapeamento de Eixo:** Plotar usando índices numéricos e aplicar `set_yticklabels` com as descrições. Isso força a separação de barras com nomes iguais.
- **Escala:** Aplicar escala logarítmica no eixo X (agora horizontal) do gráfico de Mortalidade por Grupo.

### 3.2. Novo Layout (GridSpec)
- **Organização:** 
  - Top 15%: Header Financeiro (Texto).
  - Meio 40%: Gráfico 1 (Maiores Quedas - Horizontal).
  - Base 40%: Gráfico 2 (Mortalidade por Grupo - Horizontal).
  - Rodapé 5%: Notas e Legendas.

## 4. Plano de Validação
- [ ] O gráfico de "Top Peças" deve exibir 5 barras horizontais independentes.
- [ ] Descrições idênticas devem aparecer repetidas no eixo Y, sem agrupamento.
- [ ] Gráfico de grupos deve exibir todos os 5 grupos via escala logarítmica.

---
**Próximo Passo:** Atualizar o Plano de Implementação (Strategy).
