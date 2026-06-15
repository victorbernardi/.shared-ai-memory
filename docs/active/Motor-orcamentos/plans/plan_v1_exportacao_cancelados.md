# Plano de Execução: Extração de Orçamentos Cancelados via Fabric

## Meta
Implementar e validar a extração direta de orçamentos cancelados a partir do banco de dados Microsoft Fabric (via JDBC) utilizando as configurações compartilhadas de `shared/`.

---

## Estágios de Desenvolvimento

### Estágio 1: Modificação do Módulo de Extração (`src/extract.py`)
1. Importar as credenciais e parâmetros do Fabric (`FABRIC_SERVER`, `FABRIC_BANCO`, `FABRIC_JVM`, `FABRIC_JAR`) de `shared/config.py`.
2. Importar `ConexaoFabric` de `shared/fabric_db.py`.
3. Implementar a função `extrair_orcamentos_cancelados_fabric(data_inicio=None, data_fim=None)`.
4. Montar a query SQL dinâmica parametrizando as datas no formato string `AAAAMMDD` do Protheus.
5. Efetuar a consulta, decodificar os motivos de cancelamento com o mapeamento e retornar o DataFrame formatado com as colunas: `['Codigo da Peça', 'Número Orc', 'Cliente', 'Filial', 'Data Orc', 'Canceladas', 'Motivo Cancelado']`.

### Estágio 2: Script de Execução (`run.py`)
1. Importar `extrair_orcamentos_cancelados_fabric` no script de execução principal.
2. Adicionar o ponto de chamada para extrair os orçamentos cancelados da base de dados e salvá-los em formato Excel (`data/output/tabela_orçamentos_cancelados.xlsx`).

### Estágio 3: Validação & Testes
1. Rodar um teste local para garantir a integridade da conexão JDBC do Fabric e o formato do arquivo salvo em `data/output/`.
2. Comparar a volumetria e estrutura do arquivo final.

---

## Trava de Segurança
Este plano está em **STANDBY**. Nenhuma modificação nos arquivos do código-fonte em `src/` ou `run.py` será efetuada antes da aprovação do usuário.
