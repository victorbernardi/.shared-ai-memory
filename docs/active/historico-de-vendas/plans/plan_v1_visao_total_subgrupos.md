# Plano de Implementação - Visão Total de Subgrupos (Página 1)

**Data:** 2026-05-13
**Autor:** Antigravity (Engineering Mode)
**Status:** Aguardando Aprovação

## 1. Objetivo
Expandir a visão macro do relatório de vendas para exibir todos os 20 subgrupos ativos no portfólio, removendo a limitação do "Top 5". Isso permitirá à gerência identificar não apenas os grandes ofensores, mas também subgrupos menores que podem estar em estágio inicial de abandono.

## 2. Abordagem Técnica

### 2.1. Alterações em `src/analyses/macro_overview.py`
1.  **Remoção de Filtros de Volume:** Excluir a linha `df_trend = df_trend[df_trend['ANO_3_V'] >= 10].copy()`.
2.  **Expansão da Lista:** Remover `.head(5)` da seleção de `top_dropout`.
3.  **Refatoração do Gráfico:**
    *   Ajustar `y_pos = np.arange(len(df_trend))`.
    *   Reduzir a espessura das barras (`width`) para `0.20` ou `0.15`.
    *   Ajustar o `fontsize` dos nomes dos subgrupos para `8` ou `7` pontos.
    *   Garantir que o `GridSpec` utilize o máximo de espaço vertical disponível.
4.  **Atualização Semântica:** Mudar o título para "Onde as vendas perderam fôlego? (Visão Geral de Todos os Subgrupos)".

## 3. Plano de Verificação

### 3.1. Testes Automatizados
- Execução do orquestrador: `python src/report_orchestrator.py`.
- Verificação de logs: Garantir que 20 subgrupos foram processados.

### 3.2. Validação Visual
- Gerar o PDF e verificar se os 20 subgrupos estão legíveis e se as barras não se sobrepõem.

---
**Aguardando aprovação para prosseguir com a execução.**
