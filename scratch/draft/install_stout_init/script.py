
import zipfile
import os

# Criar ZIP com todos os arquivos da pasta output
zip_path = 'output/stout-init-v1.0.zip'

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    files_to_zip = [
        'GEMINI.md',
        'ANTIGRAVITY.md', 
        'GEMINI_LOCAL_TEMPLATE.md',
        'SKILL.md',
        'install_stout_init.py',
        'ENTREGA_FINAL.md',
        'ESTRUTURA_DE_ARQUIVOS.md',
        'README_STOUT_INIT.md'
    ]
    
    for filename in files_to_zip:
        filepath = f'output/{filename}'
        if os.path.exists(filepath):
            zipf.write(filepath, filename)
            print(f"✓ Adicionado: {filename}")
        else:
            print(f"✗ Não encontrado: {filename}")

zip_size = os.path.getsize(zip_path)
print(f"\n📦 ZIP criado: {zip_path}")
print(f"   Tamanho: {zip_size} bytes ({zip_size/1024:.1f} KB)")
print(f"   Arquivos: {len(files_to_zip)}")
