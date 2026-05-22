#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador completo do ecossistema STOUT-INIT.

Copia:
- GEMINI.md → ~/.gemini/GEMINI.md (regras globais)
- SKILL.md + templates → ~/.gemini/antigravity/skills/stout-init/ (skill)
- SKILL.md + templates → ~/.gemini/skills/stout-init/ (skill alternativa)

Uso:
    python install_stout_init.py
"""

import os
import sys
import shutil
from pathlib import Path

SKILL_NAME = "stout-init"

# Arquivos que vão para o diretório de skills
SKILL_FILES = {
    "SKILL.md": "SKILL.md",
    "references/gemini-local-template.md": "GEMINI_LOCAL_TEMPLATE.md",
    "references/antigravity-template.md": "ANTIGRAVITY.md",
}

def detect_environments():
    """Detecta todos os ambientes disponíveis."""
    home = Path.home()
    envs = []

    # Verificar Antigravity
    antigravity_path = home / ".gemini" / "antigravity" / "skills"
    if antigravity_path.exists():
        envs.append(("antigravity", antigravity_path))

    # Verificar Gemini CLI
    gemini_path = home / ".gemini" / "skills"
    if gemini_path.exists():
        envs.append(("gemini", gemini_path))

    # Se nenhum encontrado, criar estrutura padrão
    if not envs:
        gemini_path.mkdir(parents=True, exist_ok=True)
        envs.append(("gemini", gemini_path))
        print("Nenhum ambiente detectado. Criando Gemini CLI como padrao.")

    return envs

def install_global_gemini_md():
    """Instala o GEMINI.md global no home directory."""
    home = Path.home()
    gemini_home = home / ".gemini"
    gemini_home.mkdir(parents=True, exist_ok=True)

    global_gemini = Path(__file__).parent / "GEMINI.md"
    dest = gemini_home / "GEMINI.md"

    if global_gemini.exists():
        # Fazer backup se já existir
        if dest.exists():
            backup = gemini_home / "GEMINI.md.backup"
            shutil.copy2(dest, backup)
            print(f"Backup criado: {backup}")

        shutil.copy2(global_gemini, dest)
        print(f"OK GEMINI.md global -> {dest}")
        return True
    else:
        print(f"ERRO GEMINI.md nao encontrado no diretorio atual")
        return False

def install_skill():
    """Instala a skill nos ambientes detectados."""
    envs = detect_environments()
    current_dir = Path(__file__).parent

    print(f"Ambientes detectados: {len(envs)}")

    for env_type, skills_dir in envs:
        skill_dir = skills_dir / SKILL_NAME

        print(f"
Instalando skill em: {env_type}")
        print(f"  Diretorio: {skill_dir}")

        # Criar estrutura
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)

        # Copiar arquivos da skill
        for dest_rel, src_name in SKILL_FILES.items():
            src = current_dir / src_name
            dest = skill_dir / dest_rel

            if src.exists():
                shutil.copy2(src, dest)
                print(f"  OK {src_name} -> {dest_rel}")
            else:
                print(f"  ERRO {src_name} nao encontrado")

    return True

def main():
    print("=" * 60)
    print("INSTALADOR STOUT-INIT")
    print("=" * 60)

    # Passo 1: Instalar GEMINI.md global
    print("
[1/2] Instalando GEMINI.md global...")
    global_ok = install_global_gemini_md()

    # Passo 2: Instalar skill
    print("
[2/2] Instalando skill stout-init...")
    skill_ok = install_skill()

    # Resumo
    print("
" + "=" * 60)
    print("RESUMO DA INSTALACAO")
    print("=" * 60)

    if global_ok:
        print("✓ GEMINI.md global instalado")
        print(f"  Local: {Path.home() / '.gemini' / 'GEMINI.md'}")
    else:
        print("✗ GEMINI.md global FALHOU")

    if skill_ok:
        print("✓ Skill stout-init instalada")
    else:
        print("✗ Skill stout-init FALHOU")

    print("
Proximos passos:")
    print("1. Configure as API keys dos MCPs no .env")
    print("2. Teste: 'Iniciar novo projeto chamado meu-teste'")
    print("=" * 60)

if __name__ == "__main__":
    main()
