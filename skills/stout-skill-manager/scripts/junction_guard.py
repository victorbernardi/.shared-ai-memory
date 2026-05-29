#!/usr/bin/env python3
"""
Junction Guard — verifica e restaura junctions do ecossistema Stout.
Executar antes de qualquer operação de escrita de skills.
"""
import os
import stat
import sys
import subprocess
import yaml
from pathlib import Path

# Garante UTF-8 no stdout (Windows cp1252 quebra caracteres especiais)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR.parent / "config" / "junction_map.yaml"


def resolve_path(raw: str) -> Path:
    return Path(os.path.expandvars(raw))


def is_junction(path: Path) -> bool:
    """Verifica se path é uma junction usando Python nativo (sem subprocess)."""
    if not path.exists() and not path.is_symlink():
        return False
    # Python 3.12+ tem Path.is_junction()
    if hasattr(path, "is_junction"):
        return path.is_junction()
    # Fallback: FILE_ATTRIBUTE_REPARSE_POINT (0x400) via os.lstat
    try:
        st = os.lstat(path)
        FILE_ATTRIBUTE_REPARSE_POINT = 0x400
        return bool(getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)
    except OSError:
        return False


def create_junction(junction: Path, target: Path) -> bool:
    """Cria junction via cmd /c mklink /J (mais rápido que PowerShell)."""
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True, text=True
    )
    return result.returncode == 0


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"[ERRO] junction_map.yaml não encontrado em {CONFIG_PATH}")
        sys.exit(1)
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def main() -> int:
    config = load_config()
    junctions = config.get("junctions", [])
    issues = 0
    restored = 0

    for entry in junctions:
        junction_path = resolve_path(entry["junction"])
        target_path = resolve_path(entry["target"])
        platform = entry.get("platform", "?")

        if not target_path.exists():
            print(f"[AVISO] Target não existe, pulando: {target_path} ({platform})")
            continue

        if is_junction(junction_path):
            print(f"[OK] {platform}: {junction_path}")
        elif junction_path.is_dir():
            # É um diretório real — situação de risco
            print(f"[ALERTA] Junction destruída em {junction_path} ({platform})")
            print(f"         Era um diretório real. Fazendo backup e restaurando...")
            backup = junction_path.with_name(junction_path.name + ".guard-bak")
            junction_path.rename(backup)
            if create_junction(junction_path, target_path):
                print(f"[RESTAURADO] {junction_path} → {target_path}")
                restored += 1
            else:
                print(f"[ERRO] Falha ao recriar junction em {junction_path}")
                issues += 1
        else:
            # Não existe — cria
            print(f"[AUSENTE] {junction_path} ({platform}) — criando...")
            junction_path.parent.mkdir(parents=True, exist_ok=True)
            if create_junction(junction_path, target_path):
                print(f"[CRIADO] {junction_path} → {target_path}")
                restored += 1
            else:
                print(f"[ERRO] Falha ao criar junction em {junction_path}")
                issues += 1

    print(f"\nResumo: {len(junctions)} junctions verificadas | {restored} restauradas | {issues} erros")
    return 1 if issues > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
