# GEMINI.md - PROJETO LOCAL: INOVA (INFRAESTRUTURA DE DADOS E PÓS-VENDA)

> HERANÇA: OBRIGATÓRIO seguir todas as restrições do GEMINI_GLOBAL_FINAL.md.
> IDENTIDADE LOCAL: C:\Projetos\Inova\GEMINI.md
> PAPEL: Engenheiro de Dados Analíticos e Arquiteto de Integração.

---

## REGRA 1: SOBERANIA DO CONECTOR FABRIC (JDBC/JAVA)
A arquitetura de acesso a dados da Inova é estritamente via ponte Java/JDBC para contornar limitações de driver ODBC. O desvio desta regra paralisa a operação.
* NUNCA tente estabelecer conexões diretas via `pyodbc`, `sqlalchemy` genérico, ou tentar instalar drivers ODBC no sistema operacional.
* SEMPRE importe e utilize exclusivamente a classe `ConexaoFabric` do caminho absoluto `C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\fabric_db.py`.
* SEMPRE assegure que a JVM está sendo instanciada corretamente através do JDK 11 e do arquivo `.jar` mapeados no conector central.

## REGRA 2: PRESERVAÇÃO DE REDE E CACHE ESTRITO (PARQUET)
A exaustão de chamadas ao Microsoft Fabric gera custos, timeouts de token e degrada a latência do projeto.
* NUNCA execute queries de extração em massa (ETL) repetidas vezes durante as fases de desenvolvimento lógico com o parâmetro `use_cache=False`.
* SEMPRE parametrize as chamadas `db.consultar()` com `use_cache=True` e `save_cache=True` enquanto estiver construindo e testando scripts lógicos de Pandas.
* SEMPRE garanta que o armazenamento dos arquivos `.parquet` seja feito em um diretório isolado (ex: `/cache`), proibindo a poluição da raiz.

## REGRA 3: GOVERNANÇA DE CÓDIGO SQL
O processamento deve ocorrer no banco, não na memória da máquina local.
* NUNCA traga o banco inteiro para a memória para fazer filtragens básicas (ex: `SELECT * FROM tabela` para depois aplicar `.loc` no Pandas).
* SEMPRE processe JOINs de tabelas do ERP, filtrações de data (WHERE) e agregações de faturamento diretamente na query SQL executada no Fabric.
* SEMPRE utilize CTEs (Common Table Expressions) para queries complexas, mantendo o código legível e otimizado.

## REGRA 4: ORQUESTRAÇÃO POLYGLOT (PYTHON, POWERSHELL, BASH)
A Inova exige orquestração em nível de sistema operacional.
* NUNCA force o uso de Python para rotinas exclusivas de sistema operacional (como agendamento no Windows Task Scheduler, manipulação de permissões ou cópia de rede SMB).
* SEMPRE delegue as rotinas de automação de infraestrutura Windows para scripts em PowerShell `.ps1` isolados e versionados.
* SEMPRE divida fisicamente o código dos Motores (Identidade, CEVAP): extração na camada de SQL, transformação em Python e orquestração final via Shell.

## REGRA 5: HIGIENE ABSOLUTA DE DADOS OPERACIONAIS (FAIL-FAST)
A contaminação do pipeline destrói a confiança do Cientista de Dados.
* NUNCA conclua a construção de um script de extração sem implementar validação estrutural imediata (ex: `assert not df.empty`, checagem de nulos nas chaves primárias do Proteus/CRM).
* SEMPRE trate as anomalias da ponte JVM/Python (strings fragmentadas, tipagem forçada) ANTES de exportar o dataframe.
* SEMPRE force a interrupção da automação (exit code 1) se um payload extraído divergir do schema validado.

## REGRA 6: HIGIENE FÍSICA DO REPOSITÓRIO (INÓCULO DE LIXO)
O diretório da Inova processa dados sensíveis corporativos que não devem ser versionados.
* NUNCA exponha tabelas `.csv`, `.xlsx`, ou `.parquet` cruas ao controle de versão (Git) ou à pasta principal de repositório.
* SEMPRE mapeie arquivos de dados transitórios no `.gitignore`.
* SEMPRE limpe arquivos e outputs legados de execuções de testes antigos (ex: `_v10`, `_v11.5_temp`) consolidando-os em versões definitivas e descartando o ruído local.

## REGRA 7: DOCUMENTAÇÃO DE PROCESSOS COMO CÓDIGO COMPILÁVEL
A manutenção da infraestrutura não pode depender da intuição humana.
* NUNCA aprove a criação de um script de ETL sem gerar um arquivo de especificação (`spec`) e um manual de execução (`walkthrough`) respectivo em `docs/specs/`.
* SEMPRE comente o fluxo de execução das chamadas à JVM e ao Fabric, descrevendo os parâmetros utilizados.