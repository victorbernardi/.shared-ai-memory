# Plano de Validação de Dados (Data QA) - Motor M6

## 1. Objetivo
Validar a existência, qualidade e integridade das colunas do banco de dados Microsoft Fabric, garantindo que o faturamento do Motor M6 seja idêntico ao Motor M2 e que a tabela de orçamentos (VS1010) contenha os dados esperados.

## 2. Etapas de Validação

### Passo 1: Alinhamento de Filtros (M2 vs M6)
- **Ação:** Abrir o código do `motor_de_faturamento_v1.py` (M2) e extrair a cláusula `WHERE` exata.
- **Verificação:** Garantir que filtros de Devolução, Vendas Internas (Uso e Consumo) e Tipos de Nota específicos sejam replicados no M6.
- **Critério de Sucesso:** A query de faturamento do M6 deve ser uma cópia da lógica do M2.

### Passo 2: Diagnóstico da Tabela VS1010 (Orçamentos)
- **Ação:** Executar query de amostragem na `VS1010`.
- **Verificações:**
    - `VS1_STATUS`: Quais códigos aparecem? Existem nulos?
    - `VS1_CENCUS`: Os códigos batem com os Centros de Custo da Meta?
    - `VS1_CODVEN`: Os códigos de vendedor existem na `SA3010`?
- **Critério de Sucesso:** Identificar 100% dos domínios de valores para os campos de status e tipos.

### Passo 3: Verificação de Schema da vw_VENDAS
- **Ação:** Executar `DESCRIBE` ou `SELECT TOP 1` na view de vendas.
- **Verificação:** Confirmar se os nomes das colunas (ex: `VALOR_DO_PRODUTO` vs `VALOR_LIQUIDO`) são os mesmos usados no plano.
- **Critério de Sucesso:** Mapeamento de colunas no plano batendo com o Banco.

### Passo 4: Cobertura de Centros de Custo (CC)
- **Ação:** Cruzar a lista de CCs das "Metas 2026" com os CCs que aparecem na `vw_VENDAS` e na `VS1010`.
- **Verificação:** Identificar se algum CC das metas nunca aparece no faturamento (possível erro de digitação na planilha ou no ERP).

### Passo 5: Reconciliação Financeira (Teste de Soma)
- **Ação:** Somar o faturamento de uma Filial específica no M2 e comparar com a soma do novo motor M6 para o mesmo período.
- **Critério de Sucesso:** Diferença = R$ 0,00.

## 3. Ferramentas Utilizadas
- `03_Scripts_Rascunhos/explorador_schema_proteus.py` (Atualizado para QA).
- Conexão nativa Microsoft Fabric (JayDeBeApi).

## 📈 Progresso da Validação

### [X] 1. Estrutura das Metas (Excel)
- **Localização:** `04_Dados\Metas de peças John Deere 2026 - Revisão março.xlsx`
- **Hierarquia:** Coluna `Unnamed: 0` (Filial), `Segmento` (Tipo de Peça).
- **Meses:** Colunas formatadas como datetime (2026-01-01, etc).

### [/] 2. Diagnóstico de Tabelas (Fabric)
- **vw_VENDAS:** Colunas mapeadas e compatíveis com Motor M2.
- **VS1010 (Status):** Identificados domínios `0` (Aberto), `F` (Faturado), `C` (Cancelado), `X` (Provável Expirado/Perdido), `I` (Provável Ordem de Serviço).
- **VS1_CENCUS:** Códigos numéricos (ex: 131) que precisam de de-para para nomes legíveis.

### [ ] 3. Reconciliação M6 vs M2
- **Ação Pendente:** Executar query de faturamento total 2025 no M6 e comparar com o dashboard M2 atual.
