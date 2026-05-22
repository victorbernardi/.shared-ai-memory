# Plano de Implementação: Correção da Lógica de Safras (Discretas)

**Data:** 2026-05-13  
**Status:** Em Estratégia (Strategy Phase)  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Corrigir a premissa de cálculo temporal do relatório. Os dados de entrada são safras anuais discretas, mas o motor estava tratando-os como acumulados. Isso causava a "desaparição" da safra 24/25 e distorções no ranking.

## 2. Mudanças Propostas

### 2.1. Ajuste no Motor de Vendas (Excel)
- **ANO_1:** Direto de `VENDAS ÚLT. 12`
- **ANO_2:** Direto de `VENDAS ÚLT. 24`
- **ANO_3:** Direto de `VENDAS ÚLT. 36`

### 2.2. Ajuste na Matriz de Recuperação (Parquet)
- **DISC_Y1:** Direto de `VENDAS ÚLT. 12 `
- **DISC_Y3:** Direto de `VENDAS ÚLT. 36 `

## 3. Plano de Validação
- [ ] Verificar item `AT338612`: Pág 2 deve mostrar barras crescentes (1, 12, 61).
- [ ] Verificar item `4635305`: Pág 2 deve mostrar pico na safra central (0, 11, 8).
- [ ] Gerar versão `v6.4`.

---
**Próximo Passo:** Aguardar aprovação para Execução (Build).
