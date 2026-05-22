import os
import shutil
import subprocess
import sys
from pathlib import Path

def force_docs_junction(project_path_str):
    project_path = Path(project_path_str).resolve()
    local_docs = project_path / "docs"
    
    # Destino global na memória
    shared_memory_docs = Path.home() / ".shared-ai-memory" / "docs" / project_path.name.lower()
    
    print(f"--- Protocolo de Migração Stout: {project_path.name} ---")
    
    # 1. Preparar destino global
    if not shared_memory_docs.exists():
        shared_memory_docs.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Criado diretório global: {shared_memory_docs}")
    
    # 2. Migrar arquivos se docs/ local for uma pasta real
    if local_docs.exists() and not os.path.islink(local_docs):
        # Se for um diretório real e não estiver vazio
        if local_docs.is_dir():
            print(f"[!] Detectada pasta docs/ local com arquivos. Migrando...")
            
            for item in local_docs.iterdir():
                dest_item = shared_memory_docs / item.name
                if dest_item.exists():
                    if dest_item.is_dir():
                        # Merge simples: move conteúdo recursivamente
                        # Para fins de segurança, vamos apenas renomear o local se houver conflito
                        print(f"  [AVISO] Conflito em {item.name}. Renomeando local.")
                        item.rename(local_docs / f"{item.name}_backup_{int(os.path.getmtime(item))}")
                    else:
                        print(f"  [AVISO] Arquivo {item.name} já existe no global. Sobrescrevendo.")
                        os.remove(dest_item)
                        shutil.move(str(item), str(shared_memory_docs))
                else:
                    shutil.move(str(item), str(shared_memory_docs))
            
            # Remover a pasta local agora vazia
            try:
                local_docs.rmdir()
                print(f"[OK] Pasta docs/ local removida após migração.")
            except OSError as e:
                print(f"[ERRO] Não foi possível remover docs/ local: {e}")
                return False

    # 3. Criar Junction
    if not local_docs.exists():
        print(f"[...] Criando Junction: {local_docs} -> {shared_memory_docs}")
        try:
            # Comando mklink /J exige cmd.exe e aspas para caminhos com espaços
            cmd = f'mklink /J "{local_docs}" "{shared_memory_docs}"'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"[SUCESSO] Junction estabelecido.")
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Falha ao criar junction: {e.stderr.decode(errors='ignore')}")
            return False
    else:
        if os.path.islink(local_docs) or (local_docs.is_dir() and os.path.exists(local_docs / ".junction")):
             print(f"[SKIP] Junction já existe.")
        else:
             print(f"[ERRO] Pasta docs/ ainda existe e não é um link. Abortando.")
             return False

    # 4. Criar subpastas padrão se não existirem
    subfolders = ["specs", "plans", "decisions", "business", "walkthroughs"]
    for sf in subfolders:
        (shared_memory_docs / sf).mkdir(exist_ok=True)
    
    print(f"--- Migração Concluída para {project_path.name} ---")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python force_docs_junction.py <caminho_do_projeto>")
        sys.exit(1)
    
    force_docs_junction(sys.argv[1])
