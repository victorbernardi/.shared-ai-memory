#!/usr/bin/env python3
"""
Stout Markdown Sanitizer (PDP - Protocolo de Documentação Premium)
Garante que arquivos .md sigam os padrões de qualidade para IA/RAG.
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path

# Configuração da Golden Copy
GOLDEN_COPY_PATH = Path(r"C:\Motores-LLM\gemini-cli\antigravity\templates\markdown-quality")
LINT_CONFIG_NAME = ".markdownlint.json"

def get_indent(line):
    """Retorna o recuo (espaços/tabs) de uma linha."""
    match = re.match(r'^(\s*)', line)
    return match.group(1) if match else ""

def sanitize_content(content):
    """
    Aplica as regras de normalização validadas no projeto John Deere.
    """
    # 1. MD040: Fenced Code Blocks sem linguagem -> text
    # Captura ``` seguidos de nada ou apenas espaços/quebra de linha
    content = re.sub(r'```(?!\w)(.*?\n)', r'```text\1', content)
    
    # 2. MD034: Bare URLs -> Proteção com <>
    # Protege URLs que não estão em links markdown ou tags HTML
    def protect_url(match):
        url = match.group(0)
        # Se já estiver entre <>, não faz nada
        if url.startswith('<') and url.endswith('>'):
            return url
        return f"<{url}>"
    
    url_pattern = r'(?<!\()(?<!\[)(?<!src=")(?<!href=")(https?://[^\s\)\>\]]+)'
    content = re.sub(url_pattern, protect_url, content)
    
    # 3. MD022/MD031/MD032: Espaçamento de cabeçalhos, listas e blocos de código
    lines = content.split('\n')
    new_lines = []
    
    in_code_block = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Controle de estado de bloco de código
        if stripped.startswith('```'):
            # MD031: Linha em branco antes do bloco (se não estiver dentro de um)
            if not in_code_block and new_lines and new_lines[-1].strip():
                new_lines.append("")
            
            in_code_block = not in_code_block
            new_lines.append(line)
            
            # MD031: Linha em branco após o fechamento do bloco
            if not in_code_block and i + 1 < len(lines) and lines[i+1].strip():
                new_lines.append("")
            continue

        # Se estivermos dentro de um bloco de código, não mexemos no conteúdo
        if in_code_block:
            new_lines.append(line)
            continue
            
        # MD022: Cabeçalhos
        if stripped.startswith('#') and re.match(r'^#+\s', stripped):
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append(line)
            if i + 1 < len(lines) and lines[i+1].strip():
                new_lines.append("")
            continue
            
        # MD032: Itens de lista
        if re.match(r'^(\s*)([\*\-\+]|\d+\.)\s+', line):
            # Adiciona linha em branco antes se a anterior não for lista nem vazia
            if new_lines and new_lines[-1].strip() and not re.match(r'^(\s*)([\*\-\+]|\d+\.)\s+', new_lines[-1]):
                new_lines.append("")
            new_lines.append(line)
            # Adiciona linha em branco depois se o próximo não for lista nem vazio
            if i + 1 < len(lines) and lines[i+1].strip() and not re.match(r'^(\s*)([\*\-\+]|\d+\.)\s+', lines[i+1]):
                new_lines.append("")
            continue
        
        new_lines.append(line)
    
    # 4. MD012: Multiple blank lines (Limpeza final)
    content = '\n'.join(new_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def fix_file(file_path, dry_run=False):
    """Corrige um único arquivo."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
        
        fixed = sanitize_content(original)
        
        if original != fixed:
            if dry_run:
                print(f"[CHECK] {file_path}: Necessita correções.")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                print(f"[FIXED] {file_path}: Sanitizado com sucesso.")
            return True
        else:
            if dry_run:
                print(f"[OK] {file_path}: Em conformidade.")
            return False
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return False

def init_project():
    """Copia a configuração da Golden Copy para o projeto atual."""
    source = GOLDEN_COPY_PATH / LINT_CONFIG_NAME
    dest = Path(".") / LINT_CONFIG_NAME
    
    if not source.exists():
        print(f"[ERROR] Fonte da Golden Copy não encontrada: {source}")
        return False
        
    try:
        shutil.copy2(source, dest)
        print(f"[INIT] {LINT_CONFIG_NAME} copiado para a raiz.")
        return True
    except Exception as e:
        print(f"[ERROR] Falha ao copiar configuração: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Stout Markdown Sanitizer")
    parser.add_argument("--init", action="store_true", help="Inicializa o padrão de qualidade no projeto atual")
    parser.add_argument("--fix", type=str, help="Sanitiza um arquivo específico")
    parser.add_argument("--fix-all", action="store_true", help="Sanitiza todos os arquivos .md recursivamente")
    parser.add_argument("--check", type=str, help="Verifica um arquivo sem alterá-lo (dry-run)")
    
    args = parser.parse_args()
    
    if args.init:
        init_project()
    
    if args.fix:
        fix_file(args.fix)
        
    if args.check:
        fix_file(args.check, dry_run=True)
        
    if args.fix_all:
        md_files = list(Path(".").rglob("*.md"))
        # Pula arquivos em pastas de sistema ou virtuais se necessário
        count = 0
        for md_file in md_files:
            if ".venv" in str(md_file) or "node_modules" in str(md_file):
                continue
            if fix_file(md_file):
                count += 1
        print(f"\nTotal de arquivos processados: {len(md_files)}")
        print(f"Total de arquivos corrigidos: {count}")

if __name__ == "__main__":
    main()
