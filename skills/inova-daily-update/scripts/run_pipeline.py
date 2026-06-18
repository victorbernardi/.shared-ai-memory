#!/usr/bin/env python3
"""
scripts/run_pipeline.py — Wrapper para execução robusta do pipeline Inova Daily.
"""
import sys
import argparse
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DAILY_PROJECT_ROOT = Path("C:/Projetos/Inova/projects/Inova-Daily")
RUN_DAILY_SCRIPT = DAILY_PROJECT_ROOT / "run_daily.py"

def run_pipeline(mes: int = None, skip_m2: bool = False, force: bool = False) -> int:
    if not RUN_DAILY_SCRIPT.exists():
        print(f"[ERRO] Script run_daily.py não encontrado no caminho: {RUN_DAILY_SCRIPT}")
        return 1

    cmd = [sys.executable, str(RUN_DAILY_SCRIPT)]
    if mes is not None:
        cmd.extend(["--mes", str(mes)])
    if skip_m2:
        cmd.append("--skip-m2-check")
    if force:
        cmd.append("--force")

    print(f"[INFO] Executando comando: {' '.join(cmd)}")
    print("[INFO] Iniciando pipeline do Inova Daily...\n")

    try:
        # Executa em tempo real exibindo a saída no terminal
        process = subprocess.Popen(
            cmd,
            cwd=str(DAILY_PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        rc = process.poll()
        if rc != 0:
            print(f"\n[ERRO] O pipeline do Inova Daily terminou com código de falha: {rc}")
            return rc
            
        print("\n[OK] Pipeline executado com sucesso.")
        return 0

    except Exception as e:
        print(f"[ERRO] Ocorreu uma exceção ao iniciar o subprocesso: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Wrapper de execução do Inova Daily")
    parser.add_argument("--mes", type=int, default=None, help="Mês do recap mensal")
    parser.add_argument("--skip-m2-check", action="store_true", help="Ignora atualização do M2")
    parser.add_argument("--force", action="store_true", help="Força geração mesmo com alertas")
    args = parser.parse_args()

    sys.exit(run_pipeline(mes=args.mes, skip_m2=args.skip_m2_check, force=args.force))

if __name__ == "__main__":
    main()
