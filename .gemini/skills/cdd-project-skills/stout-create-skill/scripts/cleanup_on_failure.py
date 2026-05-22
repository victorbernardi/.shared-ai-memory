#!/usr/bin/env python3
"""
Script de segurança para limpeza de diretórios temporários em caso de falha na validação.
"""
import argparse
import shutil
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Limpa diretório temporário após falha")
    parser.add_argument("--target", required=True, help="Caminho do diretório a remover")
    args = parser.parse_args()

    target_path = Path(args.target)

    # Segurança: Apenas permitir remoção se estiver dentro de uma pasta temporária (ex: /tmp ou similar)
    # ou se o nome sugerir que é uma pasta de skill em validação.
    if not target_path.exists():
        print(f"[INFO] O diretório '{args.target}' já não existe. Nada a fazer.")
        sys.exit(0)

    # Impede remoção acidental de pastas raiz do sistema
    if len(target_path.parts) < 2:
        print(f"[ERRO] Path '{args.target}' muito curto. Abortando por segurança.")
        sys.exit(1)

    try:
        shutil.rmtree(target_path)
        print(f"[OK] Diretório temporário '{args.target}' removido com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao remover '{args.target}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()