# Especificação Técnica: Limpeza e Enriquecimento de Orçamentos

## 1. Escopo e Objetivos
Definir as regras de transformação (limpeza e tipagem) e o mecanismo de enriquecimento (cruzamento com Microsoft Fabric) para os orçamentos extraídos. O foco principal é enriquecer os **Orçamentos Abertos** (raspados do Power BI) com metadados adicionais, elevando sua utilidade para análises de Inteligência Comercial.

---

## 2. Regras de Limpeza de Dados (`transform.py`)

A limpeza tem o objetivo de padronizar a estrutura de dados oriunda das duas fontes distintas (Scraper e Fabric).

### 2.1 Orçamentos Abertos (Origem: Scraper Power BI)
* **Colunas Esperadas (Baseadas na inspeção prévia):** `Num Orc`, `Filial`, `Cliente`, `Data Abertura`, `Data Validade`, `Reservado`, `Orc. em Aberto`, `Tempo Orc em Aberto`.
* **Transformações Aplicadas:**
    * Limpeza de strings (Strip e Upper) nas colunas chave como `Num Orc` e `Filial`.
    * Conversão das colunas de Data (`Data Abertura`, `Data Validade`) para objetos `datetime` do Pandas, inferindo formatos brasileiros (dia/mês/ano) conforme necessidade.
    * Tipagem rigorosa dos campos financeiros (`Orc. em Aberto`) e numéricos (`Tempo Orc em Aberto`) convertendo as strings raspadas para tipos `float` nativos, efetuando limpeza de separadores monetários, se necessário.
    * Normalização dos nomes de coluna para o padrão _snake_case_ a fim de facilitar processamento posterior (ex: `num_orc`, `data_abertura`).

### 2.2 Orçamentos Cancelados (Origem: Fabric)
* Como os dados já vêm diretamente do banco de dados relacional (`extract.py`), a etapa de transformação atuará como um validador de conformidade e padronizador visual, apenas garantindo tipos `datetime` e `float` e normalização das colunas.

---

## 3. Estratégia de Enriquecimento (`transform.py` -> Fabric)

O enriquecimento cruzará a base local raspada (Orçamentos Abertos) com as tabelas ERP espelhadas no Fabric.

### 3.1 Fonte e Credenciais
A conexão reutilizará o módulo `shared.fabric_db.ConexaoFabric` com as variáveis importadas do `shared.config.py` (`FABRIC_SERVER`, `FABRIC_BANCO`, etc.), idêntico ao processo de extração de cancelados.

### 3.2 Query SQL Parametrizada
A consulta não deverá buscar todos os orçamentos da base do Fabric, mas **somente os orçamentos presentes no DataFrame base (Orçamentos Abertos)**.
Isto requer a geração de uma cláusula `IN` dinâmica ou junção parametrizada na montagem da query baseada nas tuplas de `(Filial, Número do Orçamento)`.

**Tabelas de Interesse no Fabric (Protheus):**
* `VS1010` (Cabeçalho de Orçamento): Para recuperar campos como `VS1_VEND1` (Código do Vendedor).
* `SA1010` (Cadastro de Clientes): Para trazer o `A1_NOME` completo e `A1_CGC` (CNPJ), útil caso o PBI exponha apenas uma versão abreviada do nome do cliente.
* `SA3010` (Cadastro de Vendedores - Hipotético padrão Protheus): Para recuperar o Nome do Vendedor.

**Lógica de Querying:**
```sql
SELECT 
    LTRIM(RTRIM(v.VS1_NUMORC)) AS [num_orc],
    LTRIM(RTRIM(v.VS1_FILIAL)) AS [filial_erp],
    LTRIM(RTRIM(v.VS1_VEND1))  AS [cod_vendedor],
    LTRIM(RTRIM(c.A1_CGC))     AS [cnpj_cliente]
FROM VS1010 v
LEFT JOIN SA1010 c 
    ON c.A1_COD = v.VS1_CLIFAT 
   AND c.A1_LOJA = v.VS1_LOJA
WHERE v.D_E_L_E_T_ = '' 
  AND c.D_E_L_E_T_ = ''
  AND v.VS1_NUMORC IN (...) -- Injetado dinamicamente via pandas
```

### 3.3 Mecanismo de Merge (Pandas)
1. **Chave Primária Composta:** A junção (`pd.merge`) deve ocorrer de forma `how='left'` com base na tupla `['num_orc', 'filial_cod']`.
2. Como a filial extraída pelo scraper (`0210 - Pouso Alegre`) difere do ERP (`0210`), é mandatório extrair os primeiros 4 caracteres numéricos da coluna `Filial` do DataFrame raspado para servir como chave de cruzamento com `filial_erp`.

---

## 4. Orquestração e Tolerância a Falhas (`run.py`)
* O enriquecimento atua como um "melhor esforço" (_best effort_). Se a query ao Fabric demorar excessivamente (timeout) ou falhar, a exceção deve ser capturada, registrada (via logger), e o processo principal deve persistir salvando pelo menos os dados crus processados.
* Para otimização de ciclos (Regra 5 e Regra 8 do projeto Inova), a query será construída concatenando as chaves. Se o volume extraído do Power BI for muito alto (>10.000, embora os testes apontem ~500), considerar paginação ou carregar um dump consolidado da VS1 para cruzamento local.

---

## 5. Estrutura de Saída (`data/output/`)
Ao final do run.py teremos:
1. `orcamentos_abertos_enriquecidos.xlsx`: Resultado consolidado do scraper + Fabric (via `transform.py`).
2. `tabela_orçamentos_cancelados.xlsx`: Resultado extraído nativamente via Fabric.