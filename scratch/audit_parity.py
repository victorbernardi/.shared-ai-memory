import json

def validate_parity(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    perf = data.get('performance', [])
    
    # Test for 2026, Jan
    year = 2026
    month = "Jan"
    
    filiais_sum_real = 0
    filiais_sum_meta = 0
    grupo_sum_real = 0
    grupo_sum_meta = 0
    
    for d in perf:
        if d['ANO'] == year and d['MES_NOME'] == month:
            if d['NOME_FILIAL'] == "GRUPO":
                grupo_sum_real += d['VALOR_REALIZADO']
                grupo_sum_meta += d['VALOR_META']
            else:
                filiais_sum_real += d['VALOR_REALIZADO']
                filiais_sum_meta += d['VALOR_META']
                
    print(f"Validation for {month}/{year}:")
    print(f"Sum of Branches Real: {filiais_sum_real:,.2f}")
    print(f"Sum of Group Real:    {grupo_sum_real:,.2f}")
    print(f"Diff Real:           {grupo_sum_real - filiais_sum_real:,.2f}")
    print("-" * 30)
    print(f"Sum of Branches Meta: {filiais_sum_meta:,.2f}")
    print(f"Sum of Group Meta:    {grupo_sum_meta:,.2f}")
    print(f"Diff Meta:           {grupo_sum_meta - filiais_sum_meta:,.2f}")

if __name__ == "__main__":
    validate_parity(r"c:\Projetos\Inova\Metas Peças\05_Resultados\snapshot_kpis.json")
