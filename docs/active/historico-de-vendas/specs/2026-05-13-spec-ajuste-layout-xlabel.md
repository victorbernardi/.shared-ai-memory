# Especificação Técnica: Ajuste de Espaçamento de Eixo (X-Label)

**Data:** 2026-05-13  
**Status:** Validado  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Corrigir a sobreposição visual do rótulo do eixo X ("Impacto Financeiro Estimado") sobre os elementos do gráfico, garantindo uma leitura clara e um respiro visual adequado no rodapé da Página 1.

## 2. Requisitos de Negócio
- **Legibilidade:** O rótulo do eixo X deve estar claramente separado das barras e das notas de rodapé.
- **Design JD:** Manter o alinhamento centralizado e a tipografia em negrito.

## 3. Mudanças Propostas

### 3.1. Ajuste de Pad (Espaçamento)
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Linha:** ~147
- **Ação:** Alterar `labelpad=-2` para `labelpad=15`.

### 3.2. Ajuste de Margem (Opcional)
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Linha:** ~66
- **Ação:** Se necessário, aumentar ligeiramente o `bottom` no `plt.subplots_adjust` para acomodar o rótulo mais baixo.

## 4. Plano de Validação
- [ ] Gerar PDF e verificar se o rótulo do eixo X se afastou das barras.
- [ ] Confirmar que o rótulo não está saindo da página ou sobrepondo a nota de rodapé (posicionada em `0.01`).

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
