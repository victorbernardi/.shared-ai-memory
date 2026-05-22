# Spec: Atualização Motor CEVAP e Auditoria de Paridade BUP

**Data:** 2026-05-13
**Autor:** Antigravity (Engineeiro)
**Contexto:** Sincronização entre o Motor de Ativação (CEVAP) e a Base Única de Pós-Venda (BUP).

## 1. Objetivo
1. Atualizar o **Motor CEVAP** com os inputs mais recentes de cotações (Victor) e feedbacks de ativação (Filipe).
2. Validar a integridade da atribuição: Todos os clientes do pool de ativação CEVAP devem estar marcados como `Consultor = CEVAP` no relatório BUP.

## 2. Requisitos de Dados
- **CEVAP Ativação:** `C:\Projetos\Inova\projects\motor-cevap\data\CEVAP_ATIVACAO.xlsx`
- **Cotações Abertas:** `C:\Projetos\Inova\shared\data\tabela_orçamentos_abertos.xlsx`
- **Cotações Canceladas:** `C:\Projetos\Inova\shared\data\tabela_orçamentos_cancelados.xlsx`
- **Output BUP Ref:** `C:\Projetos\Inova\projects\BUP-base-unica-pós-venda\data\BUP_POS_VENDA_20260513_1955.xlsx`

## 3. Mudanças Técnicas (scripts/consolidate_cevap.py)
- Ajustar `PATH_ORCAMENTOS` para apontar para `SHARED_DATA`.
- Adicionar `PATH_CANCELADOS` apontando para `SHARED_DATA`.
- Garantir que a lógica de "Conversão" (exclusão do pool de ativação) use ambos os arquivos.

## 4. Plano de Validação (Auditoria de Paridade)
- Criar script `scripts/audit_cevap_bup_parity.py`.
- **Passo 1:** Carregar último output CEVAP.
- **Passo 2:** Carregar último output BUP.
- **Passo 3:** Cruzar por `CNPJ_Grupo`.
- **Sucesso:** 100% dos registros CEVAP devem ter `Consultor == 'CEVAP'` no BUP.
- **Alerta:** Se houver divergência, listar CNPJs para investigação de causa raiz (ex: desvio de regra de atribuição).

## 5. Cronograma
1. Brainstorming (Concluído)
2. Spec (Este arquivo)
3. Plano de Execução
4. Build & Audit
