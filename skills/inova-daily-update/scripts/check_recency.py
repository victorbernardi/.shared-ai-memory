#!/usr/bin/env python3
"""
scripts/check_recency.py — Auditor de recência de dados analíticos do Inova Daily.
Verifica o arquivo recency_status.md por status de erro crítico (🔴) ou aviso (🟡).
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

RECENCY_STATUS_PATH = Path("C:/Projetos/Inova/shared/recency_status.md")

def check_recency() -> int:
    if not RECENCY_STATUS_PATH.exists():
        print("[ERRO] Arquivo de recência recency_status.md não encontrado!")
        print(f"Caminho esperado: {RECENCY_STATUS_PATH}")
        return 2

    critical_sources = []
    warning_sources = []

    try:
        content = RECENCY_STATUS_PATH.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        
        # Ignorar linhas iniciais e achar a tabela
        in_table = False
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            
            # Se for a linha de cabeçalho ou a linha divisória, pular
            if "Fonte de Dados" in line or ":---" in line:
                in_table = True
                continue
                
            if in_table:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 3:
                    source_name = cells[0]
                    status = cells[2]
                    
                    if "🔴" in status:
                        critical_sources.append(source_name)
                    elif "🟡" in status:
                        warning_sources.append(source_name)
                        
    except Exception as e:
        print(f"[ERRO] Falha ao processar o arquivo de recência: {e}")
        return 2

    # Emitir relatório
    if critical_sources:
        print("[CRÍTICO] As seguintes fontes analíticas estão críticas (🔴) ou ausentes:")
        for src in critical_sources:
            print(f"  - {src}")
        print("\nA execução do pipeline foi BLOQUEADA devido a fontes críticas.")
        return 2

    if warning_sources:
        print("[AVISO] As seguintes fontes estão desatualizadas (🟡):")
        for src in warning_sources:
            print(f"  - {src}")
        print("\nOs dados da Daily podem apresentar divergências ou alertas na auditoria complementar.")
        return 0

    print("[OK] Todas as fontes de dados analíticos estão atualizadas (🟢).")
    return 0

if __name__ == "__main__":
    sys.exit(check_recency())
