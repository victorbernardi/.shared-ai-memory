# 📄 BRD — Business Requirements Document: Motor CEVAP

> **Versão:** 1.0 (06/05/2026)
> **Status:** Validado
> **Propósito:** Reativação Inteligente de Clientes Inativos

---

## 1. Executive Summary
O Motor CEVAP é uma engine de inteligência comercial projetada para identificar e priorizar clientes da base Inova que estão sem realizar compras há mais de 90 dias. Ao consolidar dados de faturamento (M3), segmentação estratégica (M5) e fidelidade (Seedz/Inovapay), o motor entrega uma lista de ativação cirúrgica, focada em maximizar o retorno sobre o esforço comercial.

## 2. Business Goals
Os principais objetivos de negócio são:
- **Redução do Churn:** Identificar precocemente clientes em risco de abandono.
- **Eficiência Comercial:** Priorizar leads de alto potencial (A1/A2) e com saldo de pontos (Seedz), facilitando o fechamento da venda.
- **Saneamento de Base:** Garantir que o time de vendas não perca tempo com CNPJs inválidos ou clientes que já possuem orçamentos abertos.

## 3. Stakeholders (Matriz RACI Simplificada)
| Papel | Nome / Área | Responsabilidade |
| :--- | :--- | :--- |
| **Accountable** | Filipe (Comercial) | Dono do processo e aprovação final da lista. |
| **Responsible** | Victor Bernardi (Dados) | Construção e manutenção da engine de cálculo. |
| **Consulted** | Roberto (Estratégia) | Definição das regras de segmentação (A1, B1, etc). |
| **Informed** | Time de Vendas | Usuários finais da lista de ativação. |

## 4. Requirements
1.  **Visão por Grupo:** A inatividade deve ser calculada a nível de Grupo Econômico (CNPJ Raiz).
2.  **Seleção de Filial:** Para cada grupo inativo, deve-se eleger a unidade com maior faturamento histórico para o contato.
3.  **Higiene de Dados:** Excluir leads sem identificação clara (CNPJ zero) e oportunidades já em negociação (orçamentos abertos).
4.  **Enriquecimento:** Incluir informações de frota (Equipamentos) e recursos financeiros (Seedz/Inovapay).

## 5. Success Metrics (KPIs)
| KPI | Meta / Descrição |
| :--- | :--- |
| **Taxa de Reativação** | % de clientes da lista que voltaram a faturar em < 30 dias. |
| **Volume Recuperado** | R$ total faturado a partir dos leads da lista. |
| **Acurácia Identidade** | 0% de CNPJs zerados ou duplicados na entrega. |
| **Eficiência Filtro** | Redução de contatos improdutivos por orçamentos já abertos. |

---
*Este documento é a base para a Especificação Técnica Gold v5.1.*
