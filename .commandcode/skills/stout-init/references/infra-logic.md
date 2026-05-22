# Configuração e Lógica de Infraestrutura

## 🛠️ Configuração de MCPs (settings.json)

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp@latest"]
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-drive@latest"]
    },
    "notebooklm": {
      "command": "npx",
      "args": ["-y", "notebooklm-mcp@latest"]
    }
  }
}
```

## 🛠️ Lógica de Junctions (Windows)

Sempre utilize o comando de link físico (Junction) para conectar a pasta de documentação local à memória global.

O destino **obrigatório** é `.shared-ai-memory\docs\active\[NomeProjeto]`. Nunca aponte para `docs\` diretamente.

```powershell
# Padrão correto — substitua [NomeProjeto] pelo nome real do projeto
$projeto = "[NomeProjeto]"
$destino = "$HOME\.shared-ai-memory\docs\active\$projeto"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
mklink /J "C:\Projetos\[Caminho]\docs" $destino
```

**Verificação pós-criação:**

```powershell
(Get-Item "C:\Projetos\[Caminho]\docs").LinkType  # deve retornar "Junction"
(Get-Item "C:\Projetos\[Caminho]\docs").Target     # deve apontar para active\[NomeProjeto]
```

## 🛠️ Detecção de Ferramentas por Ambiente

| Operação | Gemini CLI | Antigravity |
| :--- | :--- | :--- |
| Ler | `read_file` | `view_file` |
| Escrever | `write_file` | `write_to_file` |
| Editar | `replace` | `replace_file_content` |
| Shell | `run_shell_command` | `run_command` |
