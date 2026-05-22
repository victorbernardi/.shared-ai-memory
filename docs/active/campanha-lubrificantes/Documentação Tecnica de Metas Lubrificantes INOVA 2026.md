### Relatório de Auditoria Técnica e de Negócios: Projeto Campanha de Lubrificantes 2026

#### 1\. Visão Geral e Arquitetura do Projeto

O projeto de unificação das bases transacionais da INOVA Máquinas é uma iniciativa estratégica de governança voltada para a consolidação dos históricos de vendas e devoluções. O objetivo central é mitigar distorções financeiras e extrair o Faturamento Líquido real, correlacionando-o ao Potencial de Mercado (Frotas). A integração entre a camada transacional (o que o cliente efetivamente comprou) e a camada de potencial (o que a frota do cliente exige) constitui o pilar fundamental para o sucesso da Campanha 2026, garantindo que as metas sejam baseadas em dados concretos de  *Share of Wallet*  e não em estimativas superficiais.**Arquitetura de Dados:**  A solução baseia-se no processamento e unificação de arquivos .parquet — otimizados para performance e preservação de tipagem — extraídos do Dashboard Diário de Bordo. Esta estrutura permite a aplicação de álgebra relacional entre vendas e estornos para a obtenção do faturamento real por CNPJ, servindo de base para o cruzamento com dados externos de frotas.Antes de avançar para o processamento de modelos, é imperativo assegurar a integridade estrutural dos ativos, transicionando para a análise rigorosa de  *Data Understanding* .

#### 2\. Fase 2: Data Understanding & Data Quality

A qualidade dos dados é a fundação de qualquer análise preditiva ou definição de metas comerciais. Na INOVA, o entendimento profundo das variáveis brutas preveniu distorções financeiras massivas que poderiam comprometer o ROI da campanha.

##### Padronização e Tipagem

Implementamos o padrão snake\_case para todas as colunas (ex: data\_emissao, valor\_liquido) para garantir a escalabilidade do pipeline. Um ponto crítico da auditoria foi a conversão de identificadores como cnpj, nota\_fiscal, centro\_custo e cod\_cliente de float64 para string. Esta ação técnica elimina o risco de perda de zeros à esquerda e evita a conversão automática para notação científica (ex: 8.96e+13), garantindo a integridade das chaves primárias essenciais para o  *Join*  com a base de Potencial de Mercado.

##### Diagnóstico de Nulos

A auditoria revelou lacunas significativas de preenchimento, sendo o ponto mais crítico a coluna subgrupo com 62,50% de valores nulos, driver essencial para a identificação do mix de lubrificantes.

Auditoria de Anomalias  
Detectamos um erro estrutural grave nas extrações: a presença de 4 linhas de "Total" provenientes do rodapé do PowerBI. Embora em baixa volumetria, essas linhas inflam artificialmente o faturamento em mais de  **R$ 653 milhões** . A detecção precoce e o expurgo desses registros garantiram a sanidade aritmética do projeto.

##### Status da Auditoria

* x  **Volumetria:**  Base inicial de 432.951 linhas de vendas auditada e estabilizada em 346.622 registros pós-limpeza.  
* x  **Temporalidade:**  Janela de 1.282 dias (setembro/2022 a março/2026) validada, com 2024 estabelecido como  *baseline*  de alta performance.  
* x  **Duplicidade:**  0% de duplicidade exata encontrada para a combinação nota\_fiscal \+ cod\_produto.Com os diagnósticos concluídos, o projeto avançou para a higienização ativa na fase de ETL.

#### 3\. Fase 3: Data Preparation e Transformações (ETL)

A transformação de dados brutos em ativos de inteligência exige regras de negócio que reflitam a realidade comercial da INOVA. O ETL aqui atua como um filtro de pureza para garantir que apenas transações de mercado sejam consideradas.

##### Higiene de Dados e Autoconsumo

O pipeline executou o expurgo das linhas de totalização e a exclusão estratégica de "Autoconsumo" (vendas para CNPJs da própria INOVA, como INOVA Máquinas e INOVA Equipamentos). Justificamos a remoção de **R $36,7 milhões** (valor de mercado) em vendas internas para garantir que o ROI e as metas reflitam exclusivamente a performance perante clientes externos. Tecnicamente, isso resultou no expurgo bruto de R$  40,1 milhões conforme os logs de sistema, preservando a pureza da base final.

##### Recuperação via Text Mining

Para sanear os 62,50% de nulos na coluna subgrupo, aplicamos mineração de texto nos campos descrição e grupo.

* **Recuperação Estratégica:**  Itens como "FUEL PROTECT" foram recuperados via padrão textual, mesmo com subgrupo nulo.  
* **Regra de Exceção:**  O produto "BREAK IN PLUS" foi isolado e reclassificado como ÓLEO DE AMACIAMENTO (EXCEÇÃO). Esta ação, em vez da simples exclusão, preserva a trilha de auditoria e permite que o item seja analisado separadamente do mix estratégico da campanha.

##### Cálculo do Faturamento Líquido

Utilizamos álgebra relacional para unificar vendas e devoluções, garantindo que o sinal negativo dos estornos produza o saldo líquido real por CNPJ.  
\# Lógica de Saneamento e Atribuição  
1\. Filtrar registros onde cod\_produto \!= 'Total'  
2\. Excluir clientes contendo 'INOVA' (exceto 'INOVAR ENGENHARIA')  
3\. Normalizar CNPJ via zfill(14) após casting para String  
4\. Faturamento\_Liquido \= soma(valor\_venda) \- soma(valor\_devolucao)

#### 4\. Integração de Dados e Engenharia de Atributos

A engenharia de atributos agrega valor ao criar indicadores que não existem nos sistemas de origem, permitindo o cruzamento do histórico real com o potencial teórico.

##### Estratégia de Join em Duas Camadas

Para reduzir pontos cegos, cruzamos a  **Camada Fiscal**  (cnpj normalizado) com a  **Camada Cadastral**  (Nome do cliente saneado). A auditoria revelou uma inconsistência de ERP: existem 3.971 nomes de clientes exclusivos para 3.988 CNPJs. Este delta de 17 registros indica duplicidades de cadastro que foram mitigadas pela nossa estratégia de unificação, recuperando faturamentos que estariam "órfãos".

##### Métricas Dinâmicas

Implementamos o índice de  **Inflação Ponderada por SKU** . Esta métrica ajusta o faturamento de 2025 para uma base comparável em 2026, neutralizando distorções de reajustes de preços e focando no crescimento real de volume.**Definições Técnicas:**

* **CNPJ Normalizado:**  Chave primária tratada com 14 dígitos, livre de notação científica.  
* **Faturamento Líquido (SSS Clean):**  Valor real pós-expurgo de devoluções, totais e autoconsumo.  
* **Deltas Cadastrais:**  Identificação de divergências entre Razão Social e Identificador Fiscal.

#### 5\. Inteligência de Negócio e Definição de Metas

A transição do dado técnico para a estratégia comercial remove a subjetividade na definição de metas para os consultores através de segmentação algorítmica.

##### Taxonomia Estratégica (Regra 50/20)

A segmentação utiliza a capacidade da frota mapeada em relação ao histórico de consumo.

* **Recuperação**: Faturamento abaixo de 50% da capacidade estimada da frota.  
* **Crescimento**: Clientes ativos com meta de 20% de incremento sobre o faturado em 2025\.  
* **Prospecção**: Clientes com frota mapeada, mas faturamento zerado no mix de lubrificantes.

##### Sazonalidade e Janela Comercial

O GAP anual foi proporcionado para a janela de 12 meses. O pipeline pondera esta meta pela curva sazonal de compras de cada cliente em 2025, respeitando os ciclos de manutenção e promovendo metas lineares de acordo com a realidade do campo.

##### Auditoria de Força de Vendas

O sistema identifica automaticamente "Clientes Órfãos" (sem consultor) e distingue tecnicamente entre o  **Churn Global**  (parou de comprar na INOVA) e o  **Churn Lubrificantes**  (continua comprando peças, mas migrou o óleo para a concorrência).

#### 6\. Saídas do Pipeline (Outputs) e Governança Final

A estrutura entregue garante erro zero e alta fidelidade matemática para a tomada de decisão executiva.

##### Matrizes Gerenciais

1. **Matriz Gerencial:**  Visão consolidada para a diretoria, focada em Market Share e cobertura de metas por filial.  
2. **Base Exportada Mensalizada:**  Estrutura  *Tidy Data*  (formato longo) para analistas, permitindo  *drill-down*  por SKU e CNPJ.

##### Trava de Qualidade

Implementamos o protocolo de  **Erro Zero**  para ingestão no Excel. O pipeline trava automaticamente se detectar duplicidades matemáticas ou se o faturamento líquido resultante for inconsistente com os parâmetros de auditoria financeira.

**Entregáveis do Projeto:**

* **Base Transacional Saneada (Parquet)**  
* **Matriz de Metas por Consultor e Cliente**  
* **Relatório de Recuperação de Nulos via Text Mining**  
* **Excel de Acompanhamento de GAP de Potencial**  
* **Parecer Técnico Final:**  A base de dados atual apresenta integridade total após o expurgo de  **R$ 693 milhões**  em anomalias (somatórios de totais e autoconsumo). Os dados estão tecnicamente aptos, validados e saneados para suportar a execução estratégica e o monitoramento da  **Campanha de Lubrificantes 2026** .

