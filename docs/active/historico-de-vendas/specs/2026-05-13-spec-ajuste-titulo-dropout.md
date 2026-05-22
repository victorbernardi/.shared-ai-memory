# Especificação Técnica: Ajuste Narrativo do Gráfico de Dropout

**Data:** 2026-05-13  
**Status:** Validado (Brainstorming Concluído)  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Refinar a narrativa do gráfico de análise de queda de vendas (Dropout) para garantir precisão técnica e alinhamento com o tom executivo, substituindo a afirmação de interrupção total ("paramos de vender") por uma indagação sobre desaceleração de performance.

## 2. Requisitos de Negócio
- **Executivo:** O título deve instigar a análise de performance sem alarmismo.
- **Precisão:** Deve refletir que as vendas diminuíram em relação ao passado, mas não necessariamente cessaram.
- **Impacto:** Manter a conexão com a perda de capital financeiro.

## 3. Mudanças Propostas

### 3.1. Título do Gráfico (Página 1)
- **De:** `"O que paramos de vender? (Top 6 Subgrupos por Perda de Capital)"`
- **Para:** `"Onde as vendas perderam fôlego? (Top 6 Subgrupos por Perda de Capital)"`

### 3.2. Localização no Código
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Linha:** ~139 (Método `ax1.set_title`)

## 4. Plano de Validação
- [ ] Gerar PDF v5 e verificar se o título na Página 1 foi atualizado corretamente.
- [ ] Garantir que o sufixo explicativo entre parênteses foi mantido.
- [ ] Validar a harmonia visual com o restante do cabeçalho John Deere.

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
