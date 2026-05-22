# Plano de Implementação: Refinamento Final do Relatório PDF (v6.3)

**Data:** 2026-05-13  
**Status:** Em Estratégia (Strategy Phase)  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Consolidar os ajustes de layout, nomenclatura e narrativa para entregar a versão `v6.3` do Relatório Executivo de Performance de Vendas, garantindo 100% de consistência com as especificações validadas hoje.

## 2. Mudanças Propostas

### 2.1. Nomenclatura e Versão
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Alteração:** Mudar string de versão de `v6_2` para `v6_3`.
- **Lógica:** Manter o timestamp `YYYYMMDD_HHMMSS`.

### 2.2. Ajustes de Layout (Página 1 e 2)
- **Pág 1:** Aumentar `bottom` margin de `0.08` para `0.12` no `plt.subplots_adjust`.
- **Pág 1:** Refinar `labelpad` do Eixo X para `12`.
- **Pág 2:** Refinar `labelpad` do Eixo X para `12` (consistência).
- **Pág 2:** Ajustar o `left` margin se os nomes dos SKUs estiverem cortando.

### 2.3. Sincronização Narrativa
- **Pág 2 Title:** Atualizar para `"Onde as vendas de peças perderam fôlego? (Top 5 SKUs por Perda de Capital)"`.

## 3. Plano de Validação
- [ ] Executar script e validar geração do arquivo com timestamp.
- [ ] Conferir PNGs de preview para garantir que o rótulo do Eixo X não bate na nota de rodapé.
- [ ] Verificar se os títulos estão idênticos em estrutura entre P1 e P2.

---
**Próximo Passo:** Aguardar aprovação para Execução (Build).
