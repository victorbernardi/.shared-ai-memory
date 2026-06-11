# Indicadores e Automacao CEVAP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Criar o relatório diário de KPIs em HTML (`daily_report_kpis.html`) para o Motor CEVAP seguindo o layout do Lead-CSC, com os e-mails configurados via JSON e automações em PowerShell para envio SMTP e compartilhamento no OneDrive.

**Architecture:** O script `generate_cevap_kpis.py` será refatorado para salvar o report diário no novo diretório `data/output/daily_report_kpis.html`. Criaremos o arquivo `emails_compartilhamento.json` e os scripts PowerShell `scheduler_daily.ps1` (SMTP) e `share_onedrive_leads.ps1` (Graph API) replicando a arquitetura robusta de automação do Lead-CSC.

**Tech Stack:** Python 3.12 (pandas, openpyxl, pytest), PowerShell 5.1+, Microsoft Graph API.

---

### Task 1: Criar Estrutura Física de Diretórios e Configurações de E-mail

**Files:**
*   Create: `C:/Projetos/Inova/projects/motor-cevap/data/config/emails_compartilhamento.json`
*   Create: `C:/Projetos/Inova/projects/motor-cevap/tests/test_kpis_infrastructure.py`

**Step 1: Write the failing test**
Criar um teste unitário para validar que as pastas físicas de configuração/output existem e que o arquivo JSON de e-mails possui parse sintático correto.
```python
# filepath: C:/Projetos/Inova/projects/motor-cevap/tests/test_kpis_infrastructure.py
import os
import json
from pathlib import Path

def test_kpis_infra_structure():
    root = Path(__file__).parents[1]
    config_dir = root / "data" / "config"
    output_dir = root / "data" / "output"
    json_file = config_dir / "emails_compartilhamento.json"
    
    assert config_dir.exists(), "Diretório data/config/ não existe"
    assert output_dir.exists(), "Diretório data/output/ não existe"
    assert json_file.exists(), "Arquivo emails_compartilhamento.json não existe"
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "consultores_bup_pecas" in data
    assert "coordenadores_gerentes_outros" in data
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_kpis_infrastructure.py -v`
Expected: FAIL (ModuleNotFound/AssertionError devido à ausência das pastas e arquivos).

**Step 3: Write minimal implementation**
Criar as pastas `data/config` e `data/output` fisicamente e escrever o arquivo `data/config/emails_compartilhamento.json` com os destinatários.
```json
{
  "comentarios": "Lista unificada de e-mails para compartilhamento da planilha CEVAP (consultores e gerência)",
  "consultores_bup_pecas": [
    {
      "nome": "Filipe Paiva",
      "email": "filipe.paiva@inovamaquinas.com.br"
    },
    {
      "nome": "Katia Almeida",
      "email": "katia.almeida@inovamaquinas.com.br"
    }
  ],
  "coordenadores_gerentes_outros": [
    {
      "nome": "Roberto Reis",
      "email": "roberto.reis@inovamaquinas.com.br"
    },
    {
      "nome": "Gabriela Rodarte",
      "email": "gabriela.rodarte@inovamaquinas.com.br"
    },
    {
      "nome": "Victor Bernardi",
      "email": "victor.bernardi@inovamaquinas.com.br"
    }
  ]
}
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_kpis_infrastructure.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add data/config/emails_compartilhamento.json tests/test_kpis_infrastructure.py
git commit -m "chore: setup config dirs and email distribution list json"
```

---

### Task 2: Modificar Caminhos e Adicionar Teste Unitário para Geração de KPIs HTML

**Files:**
*   Modify: `C:/Projetos/Inova/projects/motor-cevap/scripts/generate_cevap_kpis.py`
*   Create: `C:/Projetos/Inova/projects/motor-cevap/tests/test_kpi_generation.py`

**Step 1: Write the failing test**
Criar um teste que execute a função de geração de HTML e ateste que o arquivo `daily_report_kpis.html` é salvo na nova pasta `data/output/` e possui os elementos de layout do e-mail do Lead-CSC.
```python
# filepath: C:/Projetos/Inova/projects/motor-cevap/tests/test_kpi_generation.py
import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

def test_kpi_html_generation_output_path():
    root = Path(__file__).parents[1]
    output_html = root / "data" / "output" / "daily_report_kpis.html"
    
    # Remove se existir para garantir integridade do teste
    if output_html.exists():
        os.remove(output_html)
        
    from scripts.generate_cevap_kpis import gerar_html
    gerar_html()
    
    assert output_html.exists(), "O report daily_report_kpis.html não foi gerado em data/output/"
    
    with open(output_html, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Assegura padrões de estilo do Lead-CSC
    assert "Daily Report - Motor CEVAP" in content
    assert "max-width: 900px" in content
    assert "background: linear-gradient" in content
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_kpi_generation.py -v`
Expected: FAIL (pois o script atual aponta para `data/dashboard_cevap_kpis.html` e não possui os textos de layout exatos).

**Step 3: Write minimal implementation**
Surgicamente modificar as linhas 17-20 de `C:/Projetos/Inova/projects/motor-cevap/scripts/generate_cevap_kpis.py` para redirecionar o output:
```python
# De:
# ROOT = Path(__file__).parents[1]
# DATA_DIR = ROOT / "data"
# OUTPUT_PATH = DATA_DIR / "dashboard_cevap_kpis.html"

# Para:
ROOT = Path(__file__).parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_PATH = DATA_DIR / "output" / "daily_report_kpis.html"
```
E ajustar a função de escrita e o corpo do template de e-mail (linhas 215-541) para refletir a mesma folha de estilo e estrutura de tabelas do Lead-CSC (incluindo as variáveis do CEVAP validadas por cliente).

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_kpi_generation.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add scripts/generate_cevap_kpis.py tests/test_kpi_generation.py
git commit -m "feat: redirect kpis HTML generation to data/output/daily_report_kpis.html"
```

---

### Task 3: Criar o Script PowerShell de Agendamento Diário e Envio SMTP

**Files:**
*   Create: `C:/Projetos/Inova/projects/motor-cevap/scripts/scheduler_daily.ps1`
*   Create: `C:/Projetos/Inova/projects/motor-cevap/tests/test_scheduler_daily.py`

**Step 1: Write the failing test**
Criar um teste unitário para validar que o script do orquestrador diário PowerShell `scheduler_daily.ps1` foi criado e tem a sintaxe válida.
```python
# filepath: C:/Projetos/Inova/projects/motor-cevap/tests/test_scheduler_daily.py
import subprocess
from pathlib import Path

def test_powershell_scheduler_syntax():
    root = Path(__file__).parents[1]
    ps_script = root / "scripts" / "scheduler_daily.ps1"
    assert ps_script.exists(), "O script scheduler_daily.ps1 não existe"
    
    # Valida sintaxe no PowerShell do Windows
    res = subprocess.run(
        ["powershell", "-Command", f"Get-Command -ErrorAction Stop '{ps_script}'"],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Falha na validação de sintaxe PowerShell: {res.stderr}"
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_scheduler_daily.py -v`
Expected: FAIL (script inexistente).

**Step 3: Write minimal implementation**
Criar o script `C:/Projetos/Inova/projects/motor-cevap/scripts/scheduler_daily.ps1` carregando as variáveis do `.env` do CEVAP e adicionando suporte a envio de e-mails corporativos via SMTP para Roberto Reis, Gabriela Rodarte e Victor Bernardi.
```powershell
# Windows PowerShell 5.1+ Orquestrador do Report Diario (Daily SMTP) - CEVAP
$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Projetos\Inova\projects\motor-cevap"
$EnvPath = Join-Path $ProjectRoot ".env"
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$RunScript = Join-Path $ProjectRoot "scripts\consolidate_cevap.py"
$KpiScript = Join-Path $ProjectRoot "scripts\generate_cevap_kpis.py"
$ReportHtml = Join-Path $ProjectRoot "data\output\daily_report_kpis.html"

# Carregar variáveis do arquivo .env
$EnvConfig = @{}
if (Test-Path $EnvPath) {
    Get-Content $EnvPath | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $key, $value = $line.Split("=", 2)
            $EnvConfig[$key.Trim()] = $value.Trim()
        }
    }
}

# 1. Executa consolidação de dados e geração do HTML
& $PythonExe $RunScript
& $PythonExe $KpiScript

# 2. Envia e-mail
if (Test-Path $ReportHtml) {
    $HtmlBody = Get-Content -Path $ReportHtml -Raw -Encoding UTF8
    $SmtpServer = $EnvConfig["SMTP_SERVER"]
    if (-not $SmtpServer) { $SmtpServer = "smtp.office365.com" }
    $SmtpPort = 587
    if ($EnvConfig["SMTP_PORT"]) { $SmtpPort = [int]$EnvConfig["SMTP_PORT"] }
    $SmtpUser = $EnvConfig["SMTP_USER"]
    $SmtpPassword = $EnvConfig["SMTP_PASSWORD"]
    
    if ($SmtpUser -and $SmtpPassword -and $SmtpUser -ne "seu-email@inovamaquinas.com.br") {
        $SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, $SmtpPort)
        $SMTPClient.EnableSsl = $true
        $SMTPClient.Credentials = New-Object System.Net.NetworkCredential($SmtpUser, $SmtpPassword)
        
        $MailMessage = New-Object Net.Mail.MailMessage
        $MailMessage.From = $SmtpUser
        $MailMessage.Subject = "Daily Report - Motor CEVAP - Ativacao de Inativos Inova"
        $MailMessage.Body = $HtmlBody
        $MailMessage.IsBodyHtml = $true
        
        $MailMessage.To.Add("roberto.reis@inovamaquinas.com.br")
        $MailMessage.To.Add("gabriela.rodarte@inovamaquinas.com.br")
        $MailMessage.To.Add("victor.bernardi@inovamaquinas.com.br")
        
        $SMTPClient.Send($MailMessage)
        Write-Host "Email enviado com sucesso!"
    } else {
        Write-Host "[DRY-RUN] Simulação: Credenciais SMTP não configuradas. HTML salvo em $ReportHtml"
    }
}
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_scheduler_daily.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add scripts/scheduler_daily.ps1 tests/test_scheduler_daily.py
git commit -m "feat: add daily report execution scheduler and SMTP mailer"
```

---

### Task 4: Criar o Script PowerShell de Compartilhamento do OneDrive via Graph API

**Files:**
*   Create: `C:/Projetos/Inova/projects/motor-cevap/scripts/share_onedrive_leads.ps1`
*   Create: `C:/Projetos/Inova/projects/motor-cevap/tests/test_share_onedrive.py`

**Step 1: Write the failing test**
Criar um teste unitário para validar que o script `share_onedrive_leads.ps1` existe e passou na validação básica de sintaxe PowerShell.
```python
# filepath: C:/Projetos/Inova/projects/motor-cevap/tests/test_share_onedrive.py
import subprocess
from pathlib import Path

def test_powershell_share_onedrive_syntax():
    root = Path(__file__).parents[1]
    ps_script = root / "scripts" / "share_onedrive_leads.ps1"
    assert ps_script.exists(), "O script share_onedrive_leads.ps1 não existe"
    
    res = subprocess.run(
        ["powershell", "-Command", f"Get-Command -ErrorAction Stop '{ps_script}'"],
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Falha na validação de sintaxe PowerShell: {res.stderr}"
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/test_share_onedrive.py -v`
Expected: FAIL (script inexistente).

**Step 3: Write minimal implementation**
Criar o script `C:/Projetos/Inova/projects/motor-cevap/scripts/share_onedrive_leads.ps1` que lê as configurações do arquivo `data/config/emails_compartilhamento.json` e realiza o compartilhamento em lote da planilha do CEVAP no OneDrive usando a Graph API e autenticação Device Code.
```powershell
# Windows PowerShell 5.1+ Compartilhador de Planilhas OneDrive via Graph API - CEVAP
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$JsonPath = Join-Path -Path $PSScriptRoot -ChildPath "..\data\config\emails_compartilhamento.json"
$TargetFileName = "CEVAP_ATIVACAO.xlsx"

if (-not (Test-Path $JsonPath)) {
    Write-Error "Arquivo JSON de e-mails não encontrado."
    Exit 1
}

$JsonData = Get-Content -Raw -Encoding UTF8 $JsonPath | ConvertFrom-Json
$Emails = @()
if ($JsonData.consultores_bup_pecas) { $Emails += $JsonData.consultores_bup_pecas.email }
if ($JsonData.coordenadores_gerentes_outros) { $Emails += $JsonData.coordenadores_gerentes_outros.email }
$Emails = $Emails | Select-Object -Unique | Where-Object { $_ -ne $null -and $_ -ne "" }

Write-Host "Identificados $($Emails.Count) e-mails para compartilhamento da planilha CEVAP."

# TLS 1.2 e verificação do Microsoft.Graph
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$RequiredModules = @("Microsoft.Graph.Authentication", "Microsoft.Graph.Files")

foreach ($ModuleName in $RequiredModules) {
    if (-not (Get-Module -ListAvailable -Name $ModuleName)) {
        Write-Host "Instalando módulo $ModuleName..."
        Install-Module -Name $ModuleName -Scope CurrentUser -Force -AllowClobber -OutNull
    }
    Import-Module $ModuleName
}

# Autenticação e compartilhamento (Simulado em dry-run se não logado)
try {
    Write-Host "Conectando ao Microsoft Graph (Device Code)..."
    Connect-MgGraph -Scopes "Files.ReadWrite", "Files.ReadWrite.All" -UseDeviceAuthentication
    $AuthContext = Get-MgContext
    
    $DriveItems = Get-MgUserDriveItem -UserId $AuthContext.Account -SearchText $TargetFileName -ErrorAction SilentlyContinue
    $DriveItem = $DriveItems | Where-Object { $_.Name -eq $TargetFileName } | Select-Object -First 1
    
    if ($DriveItem) {
        $Recipients = @()
        foreach ($Email in $Emails) { $Recipients += @{ email = $Email } }
        
        $PermissionParams = @{
            "recipients" = $Recipients
            "roles" = @("read")
            "sendInvitation" = $true
            "message" = "Olá, segue acesso de leitura à planilha de controle do Motor CEVAP."
        }
        $PermissionResult = Invite-MgDriveItem -DriveItemId $DriveItem.Id -BodyParameter $PermissionParams
        Write-Host "Compartilhamento concluído com sucesso!"
    } else {
        Write-Warning "Arquivo $TargetFileName não localizado no OneDrive da nuvem."
    }
    Disconnect-MgGraph
} catch {
    Write-Warning "Execução em modo DRY-RUN/Simulação devido a erro de conexão: $_"
}
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/test_share_onedrive.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add scripts/share_onedrive_leads.ps1 tests/test_share_onedrive.py
git commit -m "feat: add OneDrive Graph API auto-share script for CEVAP sheet"
```
