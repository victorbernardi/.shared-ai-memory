import pandas as pd

file_path = r'C:\Projetos\Inova\Metas Peças\Metas de peças John Deere 2026 - Revisão março.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    print(f"Abas encontradas: {xl.sheet_names}")
    for sheet in xl.sheet_names[:3]: # Primeiras 3 abas para não poluir
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
        print(f"\n--- Top 5 linhas da aba: {sheet} ---")
        print(df.to_string())
except Exception as e:
    print(f"Erro: {e}")
