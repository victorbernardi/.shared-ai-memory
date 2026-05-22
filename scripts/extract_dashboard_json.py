import pandas as pd
import json
import os
from datetime import datetime

# Configurações de Caminhos
EXCEL_PATH = r'C:\Projetos\Inova\Metas Peças\05_Resultados\Motor_Gestao_M6_v4_3.xlsx'
OUTPUT_JSON = r'C:\Projetos\Inova\Metas Peças\05_Resultados\data.json'

def extrair_dados():
    print(f"Lendo dados de: {EXCEL_PATH}")
    
    # 1. Carregar Abas
    df_perf = pd.read_excel(EXCEL_PATH, sheet_name='GESTAO_PERFORMANCE')
    df_funil = pd.read_excel(EXCEL_PATH, sheet_name='GESTAO_STATUS_FUNIL')
    
    # 2. Tratamento Básico
    df_perf = df_perf.fillna(0)
    df_funil = df_funil.fillna(0)
    
    # 2. Extrair Listas Únicas para Filtros
    filiais = sorted([f for f in df_perf['NOME_FILIAL'].unique().tolist() if f != 'GRUPO'])
    segmentos = sorted(df_perf['SEGMENTO'].unique().tolist())
    anos = sorted(df_perf['ANO'].unique().tolist(), reverse=True)
    piramides = sorted(df_funil['PIRAMIDE_SEGMENTACAO'].unique().tolist())
    
    # Ordenação cronológica de meses
    meses_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    meses = sorted(df_perf['MES_NOME'].unique().tolist(), key=lambda x: meses_map.get(x, 0))

    # 3. Processar Performance (KPIs e Evolução)
    performance_data = df_perf.to_dict(orient='records')

    # 4. Processar Funil (Pipeline)
    pipeline_data = df_funil.to_dict(orient='records')

    # 5. Objeto Final
    dashboard_data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "filiais": filiais,
            "segmentos": segmentos,
            "meses": meses,
            "anos": anos,
            "piramides": piramides
        },
        "performance": performance_data,
        "pipeline": pipeline_data
    }

    # 6. Injetar no HTML
    html_path = r'C:\Projetos\Inova\Metas Peças\05_Resultados\index.html'
    output_html = r'C:\Projetos\Inova\Metas Peças\05_Resultados\Dashboard_Executivo_M6.html'
    
    print(f"Lendo template HTML: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Serializar JSON e injetar na linha correta
    json_str = json.dumps(dashboard_data, ensure_ascii=False)
    target_string = "let dashboardData = null; /* INJECT_DATA_HERE */"
    new_string = f"let dashboardData = {json_str}; /* INJECTED */"
    
    if target_string in html_content:
        html_content = html_content.replace(target_string, new_string)
        print(f"Dados injetados com sucesso! Gerando arquivo final: {output_html}")
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
    else:
        print("ERRO: Marcador de injecao nao encontrado no HTML.")
    
    print("Extracao concluida com sucesso!")

if __name__ == "__main__":
    extrair_dados()
