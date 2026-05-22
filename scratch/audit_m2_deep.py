import sys
import os
import pandas as pd

# Adiciona o conector ao path
sys.path.append(r'C:\Users\victor.bernardi\Documents\Fabric_Database_Connector')
from fabric_db import ConexaoFabric

def run_audit():
    db = ConexaoFabric(
        '42bloq5ww5qurfq7c735qv7hha-qkcnnxqk3gtuth3wyfrgiqmgdy.datawarehouse.fabric.microsoft.com', 
        'LH_Consumo', 
        r'C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\jdk-11.0.30+7\bin\server\jvm.dll', 
        r'C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\mssql-jdbc-13.4.0.jre11.jar'
    )

    # 1. Top 15 Maiores Ofensores (Tickets Altos)
    query_top = """
    SELECT TOP 15 
        CAST(NUMERO_DA_NF AS VARCHAR(20)) as NF, 
        CAST(DESCRICAO_CC AS VARCHAR(100)) as CC, 
        CAST(CODIGO_DO_PRODUTO AS VARCHAR(30)) as SKU, 
        CAST(DESCRICAO_DO_PRODUTO AS VARCHAR(100)) as PRODUTO, 
        CAST(REPLACE(REPLACE(VALOR_DO_PRODUTO, '.', ''), ',', '.') AS FLOAT) as VALOR 
    FROM [dbo].[f_vendas_hist31102025] 
    WHERE TRY_CONVERT(DATE, DATA_EMISSAO_NF, 103) >= '2025-01-01' 
    ORDER BY VALOR DESC
    """
    df_top = db.consultar(query_top)
    
    # 2. Distribuição por Centro de Custo
    query_cc = """
    SELECT 
        CAST(DESCRICAO_CC AS VARCHAR(100)) as DESCRICAO_CC, 
        COUNT(*) as QTD_NOTAS, 
        SUM(CAST(REPLACE(REPLACE(VALOR_DO_PRODUTO, '.', ''), ',', '.') AS FLOAT)) as VALOR_TOTAL 
    FROM [dbo].[f_vendas_hist31102025] 
    WHERE TRY_CONVERT(DATE, DATA_EMISSAO_NF, 103) >= '2025-01-01' 
    GROUP BY CAST(DESCRICAO_CC AS VARCHAR(100))
    ORDER BY VALOR_TOTAL DESC
    """
    df_cc = db.consultar(query_cc)

    # 3. Análise de "Mecanica/Eletrica" e "Servicos" (Pedidos pelo user)
    query_serv = """
    SELECT 
        CAST(DESCRICAO_CC AS VARCHAR(100)) as CC, 
        SUM(CAST(REPLACE(REPLACE(VALOR_DO_PRODUTO, '.', ''), ',', '.') AS FLOAT)) as VALOR_TOTAL 
    FROM [dbo].[f_vendas_hist31102025] 
    WHERE (DESCRICAO_CC LIKE '%MECANICA%' OR DESCRICAO_CC LIKE '%ELETRICA%' OR DESCRICAO_CC LIKE '%SERVICOS%')
      AND TRY_CONVERT(DATE, DATA_EMISSAO_NF, 103) >= '2025-01-01'
    GROUP BY CAST(DESCRICAO_CC AS VARCHAR(100))
    ORDER BY VALOR_TOTAL DESC
    """
    df_serv = db.consultar(query_serv)

    print("\n" + "="*80)
    print("📋 AUDITORIA DE FATURAMENTO M2 - 2025")
    print("="*80)
    
    print("\n--- TOP 15 MAIORES TRANSAÇÕES (DETECÇÃO DE MÁQUINAS) ---")
    print(df_top.to_string(index=False))
    
    print("\n--- DISTRIBUIÇÃO POR CENTRO DE CUSTO (TOP 20) ---")
    print(df_cc.head(20).to_string(index=False))
    
    print("\n--- CCs DE SERVIÇOS/MECÂNICA/ELÉTRICA (SOLICITADOS) ---")
    print(df_serv.to_string(index=False))
    
    print("\n" + "="*80)
    
    # Salvando para análise em CSV
    df_cc.to_csv('audit_ccs_2025.csv', index=False)

if __name__ == "__main__":
    run_audit()
