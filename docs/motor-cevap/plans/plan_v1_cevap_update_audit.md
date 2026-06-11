# Plano de Execução: Atualização CEVAP e Auditoria BUP

**ID:** plan_v1_cevap_update_audit
**Data:** 2026-05-13
**Objetivo:** Sincronizar Motor CEVAP com dados atualizados e auditar paridade com BUP.

## 1. Ajustes no Script (scripts/consolidate_cevap.py)
- Alterar as variáveis de caminho de cotação para usar o `SHARED_DATA`.
- Unificar a fonte de verdade entre BUP e CEVAP.

## 2. Execução do Motor
- Rodar `python scripts/consolidate_cevap.py`.
- Verificar o output `data/CEVAP_ATIVACAO_YYYYMMDD_HHMM.xlsx`.

## 3. Auditoria de Paridade
- Criar `scripts/audit_cevap_bup_parity.py`.
- Carregar os últimos outputs de ambos os projetos.
- Verificar se `CNPJ_Grupo` do CEVAP possui `Consultor == 'CEVAP'` no BUP.

## 4. Verificação Final
- Gerar relatório de discrepâncias (se houver).
- Validar se os feedbacks do Filipe foram preservados.
