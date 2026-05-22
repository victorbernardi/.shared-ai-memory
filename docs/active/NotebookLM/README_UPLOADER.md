# 🚀 Guia de Automação - NotebookLM Uploader

Este documento descreve como utilizar o motor de ingestão automatizada para popular notebooks no NotebookLM.

## 🛠️ Como Funciona
O script `src/notebooklm_uploader.py` realiza o download de URLs (via Trafilatura), converte o conteúdo em PDFs otimizados (via FPDF) e realiza o upload para o NotebookLM utilizando o **MCP (Model Context Protocol)** local.

## 📁 Modelo de Entrada (Template)
O arquivo de manifesto deve seguir o formato JSON abaixo:
👉 **Localização do Template:** `data/template_sources.json`

```json
[
  { "titulo": "Nome", "url": "link", "formato": "url" },
  { "titulo": "Vídeo", "url": "youtube_link", "formato": "youtube" },
  { "titulo": "Interno", "formato": "local", "caminho_local": "C:/path/file.pdf" }
]
```

## 🚀 Execução
Para processar um novo notebook, utilize o comando:

```powershell
.\venv\Scripts\python.exe src/notebooklm_uploader.py --notebook_id "SEU_NOTEBOOK_ID" --manifest "data/seu_arquivo.json"
```

## 📊 Observabilidade
- **Logs:** `data/uploader_run.log`
- **Relatório de Erros:** `data/error_report.json`
