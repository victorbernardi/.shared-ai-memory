# SPEC: Motor de Ativação CEVAP (v1)

> **Documentação de Referência:** [Relatório de Descobertas](./RELATORIO_DESCOBERTAS_CEVAP.md)



## 1. Visão Geral
O Motor CEVAP tem como objetivo consolidar dados de faturamento, segmentação e fidelidade para identificar clientes John Deere inativos há mais de 90 dias, permitindo uma abordagem consultiva.

## 2. Requisitos de Dados
- **M5 (Segmentação):** Fornece Quadrante (A1, A2...) e Potencial Total.
- **M3 (Faturamento):** Fornece Recência (Última NF) e Valor 12m.
- **Seedz:** Saldo de pontos para troca em serviços.
- **InovaPay:** Limite de crédito disponível.
- **Orçamentos:** Filtragem de negociações ativas (Transbordo).

## 3. Regras de Negócio
- **Filtro Primário:** Dias de inatividade >= 90.
- **Priorização:** 1º Quadrante (A1 > A2), 2º Maior Saldo Seedz.
- **Normalização:** Join via CNPJ Raiz (8 dígitos).

---

# PLAN: Implementação e Validação (v1)

## Tarefas
1. [x] Criar estrutura de pastas.
2. [x] Gerar script de consolidação com rate_match.
3. [x] Validar joins (M5+M3, Seedz, InovaPay).
4. [ ] Realizar Auditoria de Valores (Faturamento Consolidado vs Original).

## TDD (Test Driven Development)
- **Teste 1:** Garantir que todos os clientes na planilha final possuem `Dias_Inativo >= 90`.
- **Teste 2:** Verificar se o `Potencial Total` está preenchido para todos os clientes da classe A.
- **Teste 3:** Validar que clientes com `Orcamento_Aberto == SIM` não foram excluídos, mas sim sinalizados para Transbordo.
