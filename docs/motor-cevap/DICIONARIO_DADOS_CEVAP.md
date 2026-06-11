# 📖 DICIONÁRIO DE DADOS — Motor CEVAP

> **Objetivo:** Definição oficial das colunas da Planilha de Ativação (Filipe).
> **Versão:** 1.0 (06/05/2026)

---

## 🏗️ COLUNAS DA PLANILHA (ESCOPO COMERCIAL)

| Coluna | Descrição | Origem |
| :--- | :--- | :--- |
| **CNPJ_Cliente** | CNPJ individual (14 dígitos) do cliente que não realiza compras. | Base M5 / M3 |
| **Nome_Cliente** | Razão Social ou Nome do cliente individual. | Cadastro (SA1010) |
| **Telefones** | Telefones de contato (consolidado). | Cadastro / Seedz |
| **E-mail** | E-mail de contato cadastrado. | Cadastro (SA1010) |
| **DT_Ultima_Compra** | Data da última Nota Fiscal emitida. | Base M3 (Faturamento) |
| **Valor_12m** | Soma do faturamento bruto nos últimos 12 meses. | Base M3 (Faturamento) |
| **Dias_Inativo** | Dias decorridos desde a última compra (Base: 05/05/2026). | Calculado |
| **Grupo_Economico** | Nome do Grupo Econômico ao qual o cliente pertence. | Base M5 (Segmentação) |
| **CNPJ_Grupo** | CNPJ Raiz (8 dígitos) do grupo econômico. | Base M5 (Segmentação) |
| **Classificacao** | Classificação estratégica do cliente (**A1, A2, B1, B2, C1**). | Piramide de Segmentação |
| **SOW** | Share of Wallet (SOW Total Auditado). | Base M5 |
| **Pontos_Seedz** | Saldo de pontos Seedz acumulado. | Base Seedz |
| **InovaPay_Limite_Dis** | Limite de crédito disponível para compras faturadas. | Base Inovapay |
| **Equipamentos** | Lista de modelos de máquinas vinculados. | Base Máquinas (M1) |
| **QTD_Orcamento_12m** | Número de orçamentos gerados nos últimos 12 meses. | Base Orçamentos |
| **Data_Tentativa_1** | Data do primeiro contato comercial. | Controle Filipe |
| **Status_Contato_1** | Status do 1º contato (Pendente/Sem Sucesso/Em Negociacao/Sem Intencao/Venda). | Controle Filipe |
| **Data_Tentativa_2** | Data do segundo contato comercial. | Controle Filipe |
| **Status_Contato_2** | Status do 2º contato (Pendente/Sem Sucesso/Em Negociacao/Sem Intencao/Venda). | Controle Filipe |
| **Observacao** | Campo livre para observações gerais. | Controle Filipe |

---

## ⚙️ REGRAS DE NEGÓCIO APLICADAS (v4 - Modelo Híbrido)

1. **Filtro Primário (Inatividade):** Inatividade >= 90 dias consolidada por **Grupo Econômico (Raiz 8)**. Se qualquer filial do grupo realizar uma compra, o grupo inteiro é considerado ativo.
2. **Seleção do CNPJ de Ativação:** Dentro de um grupo inativo, o motor seleciona apenas o **CNPJ de 14 dígitos com o maior faturamento nos últimos 12 meses** para figurar na planilha.
3. **Filtro Secundário (Orçamentos):** Clientes (Filiais selecionadas) que possuem orçamentos **abertos** no sistema são excluídos da lista para evitar dupla abordagem.
4. **Grão de Dados Inteligente:**
    - **Nível Grupo:** Segmentação, Saldo Seedz, Limite InovaPay e Fallback de Equipamentos.
    - **Nível Filial:** Contatos, Contagem de Orçamentos e Cidade.
5. **Priorização de Telefone:** Prioriza o número celular da base Seedz. Na ausência deste, utiliza o telefone do cadastro fiscal (ERP) da filial selecionada.
6. **Hierarquia de Máquinas:** A coluna `Equipamentos` busca primeiro máquinas vinculadas ao CNPJ de 14 dígitos. Caso não existam, traz as máquinas vinculadas ao CNPJ Raiz do grupo.

---
*Este documento é a referência única para a estrutura da planilha final.*
