import os
import argparse
from pathlib import Path

def is_stout_project(path):
    """
    Detecta se uma pasta é um projeto Stout válido.
    Critérios: Ter GEMINI.md, ANTIGRAVITY.md ou pasta .git.
    """
    target = Path(path)
    indicators = ['GEMINI.md', 'ANTIGRAVITY.md', '.git']
    return any((target / ind).exists() for ind in indicators)

def retrofit(project_path, silent=False):
    target = Path(project_path)
    if not target.exists():
        if not silent: print(f"[-] Erro: Caminho {project_path} nao existe.")
        return

    # Verificação de Projeto
    if not is_stout_project(target):
        if not silent: print(f"[*] Ignorando: {target.name} nao parece ser um projeto Stout.")
        return

    # Verificação de Instalação Prévia (Idempotência)
    gcc_dir = target / '.GCC' / 'branches'
    if gcc_dir.exists() and (target / 'data' / 'config' / 'rules.yaml').exists():
        if not silent: print(f"[*] Ignorando: CDD ja instalado em {target.name}.")
        return

    if not silent: print(f"[*] [CDD VIRUS] Propagando motor para: {target.name}")

    # 1. Cria a pegada GCC
    gcc_dir.mkdir(parents=True, exist_ok=True)
    if not silent: print("  [+] Estrutura .GCC/branches criada.")

    # 2. Cria pegada Config
    config_dir = target / 'data' / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    rules_file = config_dir / 'rules.yaml'
    if not rules_file.exists():
        with open(rules_file, 'w', encoding='utf-8') as f:
            f.write("version: '1.0.0'\nrules: []\n")
        if not silent: print("  [+] Arquivo data/config/rules.yaml local criado.")

    # 3. Atualiza GEMINI.md
    gemini_file = target / 'GEMINI.md'
    directive = "\n\n## CDD GOVERNANCE\n- Este projeto utiliza o motor global `cdd_core`.\n- Regras locais em: `data/config/rules.yaml`\n- Rastreabilidade: `.GCC/` (Marcos lógicos)\n"
    
    # Evita duplicar a diretiva se já existir
    if gemini_file.exists():
        with open(gemini_file, 'r', encoding='utf-8') as f:
            if "CDD GOVERNANCE" in f.read():
                if not silent: print("  [!] Diretiva CDD ja presente no GEMINI.md.")
            else:
                with open(gemini_file, 'a', encoding='utf-8') as f:
                    f.write(directive)
                if not silent: print("  [+] GEMINI.md atualizado com diretivas CDD.")
    else:
        with open(gemini_file, 'w', encoding='utf-8') as f:
            f.write("# GEMINI.md\n" + directive)
        if not silent: print("  [+] GEMINI.md criado com diretivas CDD.")

    if not silent: print(f"[SUCCESS] CDD Virus: {target.name} agora esta sob governanca.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CDD Retrofit Utility (Virus Mode)')
    parser.add_argument('--path', type=str, required=True, help='Caminho do projeto')
    parser.add_argument('--silent', action='store_true', help='Modo silencioso')
    args = parser.parse_args()
    retrofit(args.path, args.silent)
