# Spec: Projeto Roberto Summary Email

**Status:** Rascunho
**Data:** 2026-05-14
**Responsável:** Context-Manager / Arquiteto Agêntico
**Prazo:** 2026-05-15 (Sexta-feira)

## 1. Objetivo do Negócio
Entregar uma "foto" executiva da situação atual de vendas de peças para o gestor Roberto, consolidando dados de faturamento e oportunidades comerciais (CEVAP) em um formato de e-mail conciso e visualmente profissional.

## 2. Requisitos Funcionais
O resumo deve apresentar os seguintes indicadores, agrupados por **Centro de Custo (Filial)** e **Consultor (Vendedor)**:

### 2.1 Indicadores de Venda (Mês Corrente)
- **Notas Fiscais Emitidas:** Quantidade de NFs de peças no mês.
- **Valor Total (Receita):** Faturamento líquido (vendas - devoluções) filtrado por TES específicas.
- **Quantidade de Peças:** Soma total de itens vendidos.
- **SKUs (Partnumbers):** Contagem de códigos de produtos únicos comercializados.

### 2.2 Indicadores de Oportunidade (CRM/CEVAP)
- **Oportunidades Pendentes:** Quantidade de clientes na campanha CEVAP com status "Em aberto" ou aguardando contato.

## 3. Fontes de Dados
- **SQL (Fabric - LH_Consumo):** Tabela/View `vw_VENDAS` para dados de faturamento.
- **Excel (CEVAP):** Arquivo `C:\Projetos\Inova\projects\motor-cevap\data\CEVAP_ATIVACAO.xlsx` para status de oportunidades.
- **Configurações:** Lista de TES válidas e regras de negócio provenientes do projeto `Historico-de-Vendas`.

## 4. Formato de Saída
- Um documento Markdown estruturado pronto para ser colado em um corpo de e-mail, utilizando tabelas e formatação limpa (Executive Summary).

## 5. Próximos Passos (IA Integration)
- No futuro, este relatório poderá ser gerado automaticamente por um agente que envia o e-mail via API do Outlook/Gmail assim que os dados do Fabric forem atualizados.
