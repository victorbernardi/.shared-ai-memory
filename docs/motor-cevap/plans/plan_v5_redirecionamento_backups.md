# Redirecionamento e Migração de Backups Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Redirecionar a gravação de novos backups do motor CEVAP para a pasta local `data/backups/` do projeto e migrar de forma segura 65 arquivos de backups e cópias históricas atualmente na pasta de Documentos do OneDrive do usuário.

**Architecture:** A movimentação será feita por um script Python seguro (`scripts/migrate_cevap_backups.py`) que usa `shutil.copy2` para preservar metadados, valida o tamanho dos arquivos gerados no destino contra a origem e deleta os originais do OneDrive apenas após a validação de tamanho. O motor `scripts/consolidate_cevap.py` será alterado para usar `data/backups/` para futuros backups. Testes do Pytest em `tests/test_backup_migration.py` validarão cenários simulados (mocks) e pós-condições reais.

**Tech Stack:** Python (pathlib, shutil, os), Pytest.

---

### Task 1: Scaffolding de Teste Unitário (TDD)

**Files:**
- Create: `tests/test_backup_migration.py`
- Create: `scripts/migrate_cevap_backups.py`

**Step 1: Write the failing test**
Escrever a estrutura básica de testes unitários que simula a cópia de backups em diretórios temporários controlados pelo Pytest (usando `tmp_path`). O teste tentará importar a função de migração de `scripts.migrate_cevap_backups`.

*No arquivo `tests/test_backup_migration.py`:*
```python
import os
import shutil
import pytest
from pathlib import Path

# Tentativa de importação da função de migração
try:
    from scripts.migrate_cevap_backups import migrate_backups, FILES_TO_MOVE
except ImportError:
    migrate_backups = None
    FILES_TO_MOVE = []

def test_migrate_backups_simulated(tmp_path):
    assert migrate_backups is not None, "Função de migração não importada corretamente."
    
    # Criar estruturas de origem e destino simuladas
    source_dir = tmp_path / "onedrive"
    source_dir.mkdir()
    dest_dir = tmp_path / "project_backups"
    dest_dir.mkdir()
    
    # Criar arquivos fictícios de teste
    test_files = ["CEVAP_ATIVACAO_backup_20260522_1018.xlsx", "CEVAP_ATIVACAO - Copia.xlsx"]
    for f_name in test_files:
        p = source_dir / f_name
        p.write_text("dummy content", encoding="utf-8")
        
    # Executar migração
    migrate_backups(source_path=source_dir, dest_path=dest_dir, file_list=test_files)
    
    # Asserções
    for f_name in test_files:
        assert (dest_dir / f_name).exists(), f"Arquivo {f_name} não foi criado no destino."
        assert not (source_dir / f_name).exists(), f"Arquivo {f_name} não foi excluído da origem."
```

**Step 2: Run test to verify it fails**
Executar o teste via pytest. Ele deve falhar porque o módulo `scripts.migrate_cevap_backups` ainda não existe ou não possui a função `migrate_backups`.

Run: `python -m pytest tests/test_backup_migration.py -k test_migrate_backups_simulated -v`
Expected: FAIL (ImportError / AssertionError "Função de migração não importada corretamente.")

**Step 3: Write minimal implementation**
Criar o arquivo `scripts/migrate_cevap_backups.py` apenas declarando a função e a lista de arquivos de forma vazia para passar a importação.

*No arquivo `scripts/migrate_cevap_backups.py`:*
```python
import sys
from pathlib import Path

FILES_TO_MOVE = []

def migrate_backups(source_path: Path, dest_path: Path, file_list: list) -> None:
    pass
```

**Step 4: Run test to verify it passes/fails in assert**
Executar novamente para confirmar que agora a importação passa, mas a lógica falha no assert de existência dos arquivos de destino.

Run: `python -m pytest tests/test_backup_migration.py -k test_migrate_backups_simulated -v`
Expected: FAIL (AssertionError "Arquivo CEVAP_ATIVACAO_backup_20260522_1018.xlsx não foi criado no destino.")

**Step 5: Commit**
```bash
git add tests/test_backup_migration.py scripts/migrate_cevap_backups.py
git commit -m "test: add scaffolding and failing TDD test for backup migration"
```

---

### Task 2: Implementar a Lógica de Migração Segura

**Files:**
- Modify: `scripts/migrate_cevap_backups.py`
- Test: `tests/test_backup_migration.py`

**Step 1: Write the final implementation for the migration script**
Desenvolver a lógica robusta de migração em `scripts/migrate_cevap_backups.py` contendo a lista completa dos 65 arquivos e tratando erros de arquivos em uso e validação de tamanho pós-cópia.

*No arquivo `scripts/migrate_cevap_backups.py`:*
```python
import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backup_migrator")

FILES_TO_MOVE = [
    # 62 Backups padrão
    "CEVAP_ATIVACAO_backup_20260522_1018.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1051.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1055.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1059.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1106.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1255.xlsx",
    "CEVAP_ATIVACAO_backup_20260522_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260526_0807.xlsx",
    "CEVAP_ATIVACAO_backup_20260526_0824.xlsx",
    "CEVAP_ATIVACAO_backup_20260526_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260527_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260528_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260529_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1114.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1128.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1129.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1130.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1132.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1133.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1134.xlsx",
    "CEVAP_ATIVACAO_backup_20260601_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1443.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1445.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1446.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1939.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1940.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1941.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1942.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1943.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_1948.xlsx",
    "CEVAP_ATIVACAO_backup_20260602_2002.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0212.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0223.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0257.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0300.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0308.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0319.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0334.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_0340.xlsm",
    "CEVAP_ATIVACAO_backup_20260603_0359.xlsm",
    "CEVAP_ATIVACAO_backup_20260603_0404.xlsm",
    "CEVAP_ATIVACAO_backup_20260603_0409.xlsm",
    "CEVAP_ATIVACAO_backup_20260603_0415.xlsm",
    "CEVAP_ATIVACAO_backup_20260603_1207.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_1215.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_1222.xlsx",
    "CEVAP_ATIVACAO_backup_20260603_1740.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0838.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0947.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0953.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0954.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0957.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0958.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_0959.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1001.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1003.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1005.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1007.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1018.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1019.xlsx",
    "CEVAP_ATIVACAO_backup_20260608_1020.xlsx",
    # 3 Cópias adicionais
    "CEVAP_ATIVACAO - 090526.xlsx",
    "CEVAP_ATIVACAO - Copia.xlsx",
    "CEVAP_ATIVACAO - Copia (2).xlsx",
]

def migrate_backups(source_path: Path, dest_path: Path, file_list: list) -> None:
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for file_name in file_list:
        src_file = source_path / file_name
        dst_file = dest_path / file_name
        
        if not src_file.exists():
            if dst_file.exists():
                logger.info(f"Arquivo já migrado: {file_name}")
                continue
            else:
                logger.warning(f"Arquivo não localizado na origem nem no destino: {file_name}")
                continue
        
        try:
            logger.info(f"Copiando {file_name}...")
            shutil.copy2(src_file, dst_file)
            
            # Validação pós-cópia
            if dst_file.exists() and dst_file.stat().st_size == src_file.stat().st_size:
                logger.info(f"Validação OK! Removendo original: {file_name}")
                os.remove(src_file)
            else:
                logger.error(f"Erro de integridade na cópia de {file_name}. Arquivo original mantido.")
        except Exception as e:
            logger.error(f"Falha ao migrar arquivo {file_name}: {e}. Arquivo original mantido.")

if __name__ == "__main__":
    # Caminhos padrão do ambiente do usuário
    onedrive_dir = Path(r"C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos")
    project_backups_dir = Path(__file__).parents[1] / "data" / "backups"
    
    logger.info("Iniciando processo de migração real...")
    migrate_backups(onedrive_dir, project_backups_dir, FILES_TO_MOVE)
    logger.info("Migração concluída.")
```

**Step 2: Run test to verify it passes**
Rodar o teste para comprovar que a lógica unitária em diretório temporário passa com sucesso.

Run: `python -m pytest tests/test_backup_migration.py -k test_migrate_backups_simulated -v`
Expected: PASS

**Step 3: Commit**
```bash
git add scripts/migrate_cevap_backups.py
git commit -m "feat: implement robust and safe backup migration logic"
```

---

### Task 3: Criar os Testes de Validação Real Pós-Migração

**Files:**
- Modify: `tests/test_backup_migration.py`

**Step 1: Write validation test for the real environment**
Escrever a rotina de testes que verifica a pós-condição no ambiente real do usuário após executarmos a migração. Ela deve checar se a pasta local possui exatamente os 65 arquivos e que o OneDrive não os possui mais.

*No final de `tests/test_backup_migration.py`:*
```python
def test_real_migration_post_check():
    onedrive_dir = Path(r"C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos")
    project_backups_dir = Path(__file__).parents[1] / "data" / "backups"
    
    # 1. Garantir que a planilha principal existe no OneDrive
    main_planilha = onedrive_dir / "CEVAP_ATIVACAO.xlsx"
    assert main_planilha.exists(), "ERRO: Planilha principal CEVAP_ATIVACAO.xlsx foi removida do OneDrive!"
    
    # 2. Garantir que a pasta local data/backups contém todos os 65 arquivos migrados
    from scripts.migrate_cevap_backups import FILES_TO_MOVE
    assert len(FILES_TO_MOVE) == 65, f"Lista de migração esperava 65 arquivos, encontrou {len(FILES_TO_MOVE)}."
    
    arquivos_faltando_local = []
    for f_name in FILES_TO_MOVE:
        if not (project_backups_dir / f_name).exists():
            arquivos_faltando_local.append(f_name)
            
    assert not arquivos_faltando_local, f"Arquivos que não estão na pasta local de backup: {arquivos_faltando_local}"
    
    # 3. Garantir que nenhum arquivo de backup histórico permaneceu no OneDrive
    arquivos_restantes_onedrive = []
    for f_name in FILES_TO_MOVE:
        if (onedrive_dir / f_name).exists():
            arquivos_restantes_onedrive.append(f_name)
            
    assert not arquivos_restantes_onedrive, f"Arquivos de backup que ainda permanecem poluindo o OneDrive: {arquivos_restantes_onedrive}"
```

**Step 2: Run test to verify it fails**
O teste deve falhar no ambiente real antes da migração física ser executada, pois os arquivos ainda estão no OneDrive.

Run: `python -m pytest tests/test_backup_migration.py -k test_real_migration_post_check -v`
Expected: FAIL (arquivos ausentes no local / presentes na origem)

**Step 3: Commit**
```bash
git add tests/test_backup_migration.py
git commit -m "test: add real post-migration verification test"
```

---

### Task 4: Executar a Migração no Ambiente Real

**Files:**
- Modify: nenhuma alteração de código. Apenas execução.

**Step 1: Execute the migration script**
Executar o script Python de migração que fará o processamento dos arquivos reais no disco.

Run: `python scripts/migrate_cevap_backups.py`
Expected: Logs detalhados de cópia e remoção segura dos 65 arquivos de backups.

**Step 2: Verify it passes**
Rodar os testes novamente. Agora o teste unitário simulado e a verificação no ambiente real devem passar!

Run: `python -m pytest tests/test_backup_migration.py -v`
Expected: PASS em todos os cenários (tanto o simulado quanto o real).

---

### Task 5: Redirecionar Novos Backups no Motor CEVAP

**Files:**
- Modify: `scripts/consolidate_cevap.py`

**Step 1: Modify backup path in consolidate_cevap.py**
Ajustar o script principal do motor para que ele aponte a pasta de backup para a pasta local e crie-a caso ela não exista.

*Modificar em `scripts/consolidate_cevap.py`:*
Substituir o bloco que gera backups:
```python
<<<<
            else:
                backup_path = ONEDRIVE_PATH.parent / f"CEVAP_ATIVACAO_backup_{timestamp}.xlsx"
                shutil.copy2(ONEDRIVE_PATH, backup_path)
                print(f"[OK]    Backup OneDrive: {backup_path.name}")
====
            else:
                backup_dir = DATA_DIR / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / f"CEVAP_ATIVACAO_backup_{timestamp}.xlsx"
                shutil.copy2(ONEDRIVE_PATH, backup_path)
                print(f"[OK]    Backup Local do Projeto: {backup_path.name}")
>>>>
```

**Step 2: Run test to verify the change**
Rodar a suíte de testes padrão do projeto para garantir que o comportamento de salvamento e proteção do motor não foi afetado.

Run: `python -m pytest tests/ -v`
Expected: PASS em todas as validações (incluindo as de integridade de colunas e regras de recência).

**Step 3: Commit**
```bash
git add scripts/consolidate_cevap.py
git commit -m "feat: redirect future backups to local data/backups/ directory"
```
