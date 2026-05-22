import json
import os
import sys

class OnePageScanner:
    """
    Motor de Auditoria Matemática - OnePage Inova M6
    Garante a integridade dos dados entre visões granulares e consolidadas.
    """
    
    def __init__(self, kpi_path):
        self.kpi_path = kpi_path
        self.errors = []
        self.warnings = []

    def scan(self):
        print("\n" + "="*50)
        print(" SCANNER ONEPAGE INOVA - MOTOR DE AUDITORIA ")
        print("="*50)
        
        if not os.path.exists(self.kpi_path):
            print(f"ERRO CRITICO: Snapshot nao encontrado em {self.kpi_path}")
            return False

        with open(self.kpi_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        perf = data.get('performance', [])
        
        # Agrupar por Periodo (Ano/Mes) para checagem de paridade
        audit_map = {}
        
        for d in perf:
            key = (d['ANO'], d['MES_NOME'])
            if key not in audit_map:
                audit_map[key] = {'branches_real': 0, 'branches_meta': 0, 'grupo_real': 0, 'grupo_meta': 0}
            
            if d['NOME_FILIAL'] == "GRUPO":
                audit_map[key]['grupo_real'] += d['VALOR_REALIZADO']
                audit_map[key]['grupo_meta'] += d['VALOR_META']
            else:
                audit_map[key]['branches_real'] += d['VALOR_REALIZADO']
                audit_map[key]['branches_meta'] += d['VALOR_META']

        # Validar Resultados
        print(f"{'PERIODO':<15} | {'DIFF REAL':<15} | {'DIFF META':<15} | {'STATUS'}")
        print("-" * 65)
        
        total_errors = 0
        for (ano, mes), vals in sorted(audit_map.items(), key=lambda x: (x[0][0], x[0][1])):
            diff_real = vals['grupo_real'] - vals['branches_real']
            diff_meta = vals['grupo_meta'] - vals['branches_meta']
            
            status = "OK"
            if abs(diff_meta) > 1.0:
                status = "ERRO"
                total_errors += 1
            elif vals['grupo_real'] > 0 and abs(diff_real) > 1.0:
                status = "AVISO"
            
            print(f"{mes}/{ano:<10} | {diff_real:>15,.2f} | {diff_meta:>15,.2f} | {status}")

        print("="*65)
        if total_errors == 0:
            print("SCAN CONCLUIDO: Todos os filtros possuem integridade matematica.")
            return True
        else:
            print(f"SCAN FALHOU: Encontrados {total_errors} erros de paridade.")
            return False

if __name__ == "__main__":
    scanner = OnePageScanner(r'c:\Projetos\Inova\Metas Peças\05_Resultados\snapshot_kpis.json')
    success = scanner.scan()
    if not success:
        sys.exit(1)
