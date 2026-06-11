# Backup Multidestino, Cópia Histórica e Rotação de Leads

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implementar o salvamento duplo da planilha de leads (local e OneDrive), gravação de cópias temporais de backup local com timestamp, e purga automática de backups locais com mais de 7 dias de idade.

**Architecture:**
1. **Configuração Dinâmica (CDD):** Adicionar variáveis de ambiente `.env` e `.env.example` para os caminhos do OneDrive e da pasta local de backups, integrando-as no carregador central `src/config.py`.
2. **Camada de Carregamento (`src/load.py`):** Criar uma rotina interna chamada `gerenciar_backup_e_rotacao(caminho_local_salvo)` executada ao final do processo de geração do Excel:
   - Tenta copiar o arquivo gerado para o OneDrive (caminho configurado no `.env`). O tratamento é antifrágil: se o OneDrive estiver inacessível, registra um `[WARNING]` no log e não quebra a execução do pipeline de dados.
   - Cria o diretório de backups local (`data/backups/`) se não existir.
   - Copia a versão gerada para a pasta de backups com um timestamp no nome: `leads_preventivos_pos_vendas_YYYYMMDD_HHMMSS.xlsx`.
   - Limpa automaticamente a pasta de backups excluindo arquivos cujo tempo de última modificação seja superior a 7 dias (604.800 segundos).
3. **Mecanismo de Testes (TDD):** Implementar um arquivo de testes `tests/test_backup_rotation.py` simulando os caminhos e arquivos para validar o salvamento duplo, a cópia temporal e o algoritmo de rotação por idade.

**Tech Stack:** Python 3.11, openpyxl, pandas, pytest, os, shutil, datetime, pydantic-settings

---

### Task 1: Configuração Dinâmica dos Caminhos (CDD)

**Files:**
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\.env`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\.env.example`
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\src\config.py`

**Step 1: Adicionar variáveis de caminho nos arquivos de ambiente**

Em `C:\Projetos\Inova\projects\lead-csc-pops\.env.example`:
```ini
# Caminhos de Output e Backup
PLANILHA_ONEDRIVE_PATH=C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\leads_preventivos_pos_vendas.xlsx
PASTA_BACKUP_LOCAL=./data/backups/
```

Em `C:\Projetos\Inova\projects\lead-csc-pops\.env` (especificar explicitamente `encoding='utf-8'` em qualquer edição de arquivo):
```ini
# Segurança de Planilha no OneDrive
PLANILHA_PROTECTION_PASSWORD=InovaPosVendas2026

# Caminhos de Output e Backup
PLANILHA_ONEDRIVE_PATH=C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\leads_preventivos_pos_vendas.xlsx
PASTA_BACKUP_LOCAL=./data/backups/
```

**Step 2: Adicionar campos na classe `Config` em `src/config.py`**

Modificar `src/config.py` para carregar essas duas variáveis do `.env`:
```python
# Modificar na classe Config (linhas 25-34):
class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    rules_path: str = './data/config/rules.yaml'
    rules_schema_path: str = './data/config/rules.schema.json'
    skills_schema_path: str = './data/config/skills.schema.json'
    
    local_skills_path: str = './skills'
    global_skills_path: str = os.path.expanduser('~/.shared-ai-memory/.gemini/skills')
    
    # Adicionar novos campos para suporte ao OneDrive e Backups
    planilha_onedrive_path: str = r"C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\leads_preventivos_pos_vendas.xlsx"
    pasta_backup_local: str = "./data/backups/"
```

**Step 3: Validar carregamento das variáveis**

Executar verificação rápida no prompt (ou rodar suíte de teste).
Comando: `python -c "from config import config; print(config.planilha_onedrive_path)"`
Esperado: Exibir o caminho do OneDrive correto do Victor.

**Step 4: Commit**
```bash
git add .env .env.example src/config.py
git commit -m "chore: add OneDrive and backup paths to configuration"
```

---

### Task 2: Criar Testes Unitários para o Sistema de Backup e Rotação (TDD - Fase Vermelha)

**Files:**
- Create: `C:\Projetos\Inova\projects\lead-csc-pops\tests\test_backup_rotation.py`

**Step 1: Escrever teste unitário completo**

Criar `tests/test_backup_rotation.py` com o seguinte conteúdo para validar a lógica sem poluir os caminhos reais de produção (usando caminhos temporários):

```python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import time
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Mockamos a config para usar pastas temporárias controladas
from config import config

def test_backup_e_rotacao_leads():
    """Testa a geração de backups locais, cópia para o OneDrive simulado e rotação de 7 dias."""
    from load import gerenciar_backup_e_rotacao
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Preparar caminhos temporários de teste
        temp_dir_path = Path(temp_dir)
        caminho_local = temp_dir_path / "leads_local.xlsx"
        caminho_onedrive = temp_dir_path / "OneDrive" / "leads_onedrive.xlsx"
        pasta_backups = temp_dir_path / "backups"
        
        # Sobrescreve as configurações temporariamente para o teste
        original_onedrive = config.planilha_onedrive_path
        original_backup = config.pasta_backup_local
        
        config.planilha_onedrive_path = str(caminho_onedrive)
        config.pasta_backup_local = str(pasta_backups)
        
        try:
            # 2. Criar planilha local falsa de simulação
            pd.DataFrame({"Chassi": ["TEST001"]}).to_excel(caminho_local, index=False)
            
            # 3. Executar o gerenciamento de backups
            gerenciar_backup_e_rotacao(str(caminho_local))
            
            # --- Validação 1: Salvamento Duplo ---
            assert caminho_local.exists(), "Planilha local de controle original deve existir"
            assert caminho_onedrive.exists(), "Planilha deve ter sido copiada com sucesso para o OneDrive"
            
            # --- Validação 2: Cópia com Timestamp ---
            arquivos_backup = list(pasta_backups.glob("leads_preventivos_pos_vendas_*.xlsx"))
            assert len(arquivos_backup) == 1, "Deve existir exatamente uma cópia com timestamp na pasta de backups"
            
            # --- Validação 3: Rotação de Backups antigos (mais de 7 dias) ---
            # Vamos simular um arquivo antigo (modificado há 8 dias)
            arquivo_antigo = pasta_backups / "leads_preventivos_pos_vendas_20260520_120000.xlsx"
            # Cria um arquivo vazio
            arquivo_antigo.touch()
            
            # Altera o tempo de modificação do arquivo antigo para 8 dias atrás (8 * 86400 segundos)
            tempo_antigo = time.time() - (8 * 86400)
            os.utime(str(arquivo_antigo), (tempo_antigo, tempo_antigo))
            
            # Vamos simular um arquivo recente (modificado há 2 dias atrás)
            arquivo_recente = pasta_backups / "leads_preventivos_pos_vendas_20260527_120000.xlsx"
            arquivo_recente.touch()
            tempo_recente = time.time() - (2 * 86400)
            os.utime(str(arquivo_recente), (tempo_recente, tempo_recente))
            
            # Roda a função novamente para acionar a purga/limpeza
            gerenciar_backup_e_rotacao(str(caminho_local))
            
            # O arquivo antigo deve ter sido excluído e o recente deve permanecer
            assert not arquivo_antigo.exists(), "Backup com mais de 7 dias deve ser deletado automaticamente"
            assert arquivo_recente.exists(), "Backup recente com 2 dias deve ser preservado na rotação"
            
        finally:
            # Restaura caminhos originais
            config.planilha_onedrive_path = original_onedrive
            config.pasta_backup_local = original_backup
```

**Step 2: Rodar teste e verificar se falha (Fase Vermelha)**

Comando: `python -m pytest tests/test_backup_rotation.py -v`
Esperado: Falha com erro `ImportError: cannot import name 'gerenciar_backup_e_rotacao' from 'load'` (Fase Vermelha ativada com sucesso).

**Step 3: Commit**
```bash
git add tests/test_backup_rotation.py
git commit -m "test: add unit test for backup rotation and multi-destination save"
```

---

### Task 3: Implementar a Lógica de Salvamento Duplo e Purga no `src/load.py`

**Files:**
- Modify: `C:\Projetos\Inova\projects\lead-csc-pops\src\load.py`

**Step 2: Implementar a rotina `gerenciar_backup_e_rotacao` no `src/load.py`**

Adicionar a implementação robusta e antifrágil no final do arquivo:

```python
def gerenciar_backup_e_rotacao(caminho_local_salvo):
    """
    Executa a rotina de salvamento multidestino e governança de backups:
    1. Copia o arquivo local gerado para a pasta compartilhada do OneDrive.
       - Tratamento de exceção amigável e antifrágil para não parar o pipeline caso
         haja problemas de permissão ou rede temporários no OneDrive do usuário.
    2. Copia o arquivo local para o diretório de backups local com timestamp temporal.
    3. Executa a purga automática de arquivos antigos de backup com mais de 7 dias de idade.
    """
    import shutil
    import datetime
    import time
    from pathlib import Path
    from config import config
    
    # Obter caminhos das configurações centralizadas
    caminho_onedrive = config.planilha_onedrive_path
    pasta_backup_dir = Path(config.pasta_backup_local)
    
    # --- 1. Salvamento Duplo (OneDrive) ---
    if caminho_onedrive:
        try:
            caminho_od_path = Path(caminho_onedrive)
            # Cria a pasta de destino no OneDrive se não existir
            os.makedirs(caminho_od_path.parent, exist_ok=True)
            # Copia preservando metadados
            shutil.copy2(caminho_local_salvo, caminho_onedrive)
            print(f"[BACKUP] Copia de segurança sincronizada no OneDrive com sucesso em: {caminho_onedrive}")
        except Exception as e:
            # Princípio da Antifragilidade: Um erro de rede/sincronização do OneDrive
            # NUNCA deve interromper a execução do pipeline de dados semanal.
            print(f"[WARNING] Nao foi possivel sincronizar a planilha no OneDrive: {e}")
            print("[WARNING] A execucao do pipeline prosseguiu de forma segura usando o backup local principal.")

    # --- 2. Geração da Cópia Temporal com Timestamp ---
    try:
        os.makedirs(pasta_backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"leads_preventivos_pos_vendas_{timestamp}.xlsx"
        caminho_backup_completo = pasta_backup_dir / nome_backup
        
        shutil.copy2(caminho_local_salvo, caminho_backup_completo)
        print(f"[BACKUP] Backup temporal armazenado localmente em: {caminho_backup_completo}")
    except Exception as eb:
        print(f"[WARNING] Erro ao gerar copia temporal de backup: {eb}")

    # --- 3. Purga Automática (Retenção Estrita de 7 Dias) ---
    try:
        limite_tempo = 7 * 24 * 60 * 60  # 7 dias em segundos (604.800s)
        tempo_atual = time.time()
        excluidos_count = 0
        
        # Varre a pasta de backups buscando arquivos correspondentes ao nosso padrão
        for item in pasta_backup_dir.glob("leads_preventivos_pos_vendas_*.xlsx"):
            if item.is_file():
                idade_arquivo = tempo_atual - item.stat().st_mtime
                if idade_arquivo > limite_tempo:
                    try:
                        os.remove(item)
                        excluidos_count += 1
                    except Exception as ere:
                        print(f"[WARNING] Falha ao excluir arquivo expirado {item.name}: {ere}")
                        
        if excluidos_count > 0:
            print(f"[BACKUP] Purga Concluida: {excluidos_count} arquivos de backup antigos (mais de 7 dias) foram removidos.")
    except Exception as ep:
        print(f"[WARNING] Erro durante o processo de purga de backups: {ep}")
```

**Step 3: Chamar a rotina ao final da função `exportar_planilha_leads`**

No `src/load.py`, logo antes do `return caminho_saida` (por volta da linha 218):
```python
    # Salvar
    wb.save(caminho_saida)
    print(f"[LOAD] Planilha de leads gerada com sucesso e protegida com senha em: {caminho_saida}")
    
    # Inicia a orquestração de backups e rotação automática de 7 dias
    gerenciar_backup_e_rotacao(caminho_saida)
    
    return caminho_saida
```

**Step 4: Executar testes de validação unitária (Fase Verde)**

Comando: `python -m pytest tests/test_backup_rotation.py -v`
Esperado: PASS (Todos os 3 assertions de salvamento duplo, timestamp e rotação devem passar com sucesso).

**Step 5: Commit**
```bash
git add src/load.py
git commit -m "feat: implement multi-destination save, timestamp backup, and 7-day rotation policy"
```

---

### Task 4: Execução do Smoke Test & Testes Gerais

**Files:**
- Test: `tests/`

**Step 1: Rodar toda a suíte de testes do projeto via default Python**

Comando: `python -m pytest -v`
Esperado: Todos os testes (`test_history.py`, `test_transform.py`, `test_load_consultor.py` e `test_backup_rotation.py`) passando sem erros.

**Step 2: Commit final**
```bash
git commit --allow-empty -m "verify: final test validation passes successfully"
```
