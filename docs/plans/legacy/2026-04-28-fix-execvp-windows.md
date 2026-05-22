# Fix os.execvp Windows Compatibility — google-dev-knowledge-mcp.py

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir o script `google-dev-knowledge-mcp.py` para funcionar no Windows, substituindo `os.execvp` por `subprocess.run`, permitindo que o MCP `google-developer-knowledge` conecte com sucesso no Claude Code.

**Architecture:** O script gera um Bearer token via Service Account JWT e repassa para `mcp-remote` via `npx`. No Linux/Mac, `os.execvp` substitui o processo Python pelo `npx` — comportamento correto para MCP (processo único, stdio limpo). No Windows, `os.execvp` cria um subprocesso e retorna imediatamente, fazendo o Claude Code interpretar o encerramento do Python como falha. A correção usa `subprocess.run` com `sys.exit` propagando o código de saída, mantendo stdio herdado.

**Tech Stack:** Python 3, `subprocess`, `cryptography` (já instalada), `npx mcp-remote`

---

## Arquivos

| Ação | Caminho |
|------|---------|
| Modificar | `C:\Users\victor.bernardi\.gemini\antigravity\scripts\google-dev-knowledge-mcp.py` |
| Criar (teste) | `C:\Users\victor.bernardi\.gemini\antigravity\scripts\test_mcp_script.py` |

---

### Task 1: Escrever teste de regressão para geração do token

**Objetivo:** Garantir que `get_access_token()` retorna uma string não-vazia antes de alterar qualquer lógica.

**Files:**
- Create: `C:\Users\victor.bernardi\.gemini\antigravity\scripts\test_mcp_script.py`

- [ ] **Step 1: Criar o arquivo de teste**

```python
# test_mcp_script.py
import importlib.util
import sys
import os

# Carrega o módulo sem executar o bloco de nível superior (token + execvp)
# Fazemos isso isolando get_access_token antes da chamada de nível superior.
# Como o script executa token = get_access_token() no nível de módulo,
# precisamos testar a função diretamente via exec parcial.

def load_get_access_token():
    """Extrai e compila apenas a função get_access_token do script."""
    script_path = os.path.join(os.path.dirname(__file__), "google-dev-knowledge-mcp.py")
    with open(script_path) as f:
        source = f.read()
    # Pega somente até a definição da função (antes de token = get_access_token())
    func_source = source.split("token = get_access_token()")[0]
    namespace = {}
    exec(compile(func_source, script_path, "exec"), namespace)
    return namespace["get_access_token"]


def test_get_access_token_returns_string():
    get_access_token = load_get_access_token()
    token = get_access_token()
    assert isinstance(token, str), f"Esperado str, recebeu {type(token)}"
    assert len(token) > 20, "Token parece inválido (muito curto)"
    print(f"[OK] Token gerado: {token[:20]}...")


if __name__ == "__main__":
    test_get_access_token_returns_string()
    print("Todos os testes passaram.")
```

- [ ] **Step 2: Rodar o teste (deve passar — valida que o estado atual funciona)**

```
python C:\Users\victor.bernardi\.gemini\antigravity\scripts\test_mcp_script.py
```

Esperado:
```
[OK] Token gerado: ya29.c.c0ASRK0...
Todos os testes passaram.
```

- [ ] **Step 3: Commit do teste de regressão**

```bash
cd /c/Users/victor.bernardi/.gemini/antigravity
git add scripts/test_mcp_script.py
git commit -m "test: regressão para get_access_token do google-dev-knowledge-mcp"
```

---

### Task 2: Corrigir os.execvp → subprocess.run com compatibilidade Windows

**Files:**
- Modify: `C:\Users\victor.bernardi\.gemini\antigravity\scripts\google-dev-knowledge-mcp.py`

- [ ] **Step 1: Substituir o conteúdo do script**

Substituir o arquivo inteiro por:

```python
#!/usr/bin/env python
"""Wrapper: gera Bearer token do Service Account e inicia mcp-remote com --header."""
import json
import os
import sys
import time
import base64
import subprocess
import urllib.request
import urllib.parse

SA_FILE = os.path.expanduser("~/.credentials/google-service-account.json")


def get_access_token():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    with open(SA_FILE) as f:
        sa = json.load(f)

    now = int(time.time())
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({
            "iss": sa["client_email"],
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }).encode()
    ).rstrip(b"=").decode()

    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = base64.urlsafe_b64encode(
        key.sign(f"{header}.{payload}".encode(), padding.PKCS1v15(), hashes.SHA256())
    ).rstrip(b"=").decode()

    jwt = f"{header}.{payload}.{sig}"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    ).read())
    return resp["access_token"]


token = get_access_token()

cmd = [
    "npx", "-y", "mcp-remote",
    "https://developerknowledge.googleapis.com/mcp",
    "--header", f"Authorization: Bearer {token}",
]

# os.execvp não funciona corretamente no Windows (não substitui o processo).
# subprocess.run herda stdin/stdout/stderr e propaga o exit code corretamente.
result = subprocess.run(cmd)
sys.exit(result.returncode)
```

- [ ] **Step 2: Rodar o teste de regressão para confirmar que get_access_token ainda funciona**

```
python C:\Users\victor.bernardi\.gemini\antigravity\scripts\test_mcp_script.py
```

Esperado:
```
[OK] Token gerado: ya29.c.c0ASRK0...
Todos os testes passaram.
```

- [ ] **Step 3: Smoke test do script corrigido (timeout de 8s — deve conectar e ficar aguardando)**

Abrir um segundo terminal e rodar:
```
python C:\Users\victor.bernardi\.gemini\antigravity\scripts\google-dev-knowledge-mcp.py
```

Esperado (primeiras linhas, depois pode fechar com Ctrl+C):
```
[NNNN] Connecting to remote server: https://developerknowledge.googleapis.com/mcp
[NNNN] Connected to remote server using StreamableHTTPClientTransport
[NNNN] Local STDIO server running
```

Se aparecer essas linhas: script funciona. Ctrl+C para encerrar.

- [ ] **Step 4: Commit da correção**

```bash
cd /c/Users/victor.bernardi/.gemini/antigravity
git add scripts/google-dev-knowledge-mcp.py
git commit -m "fix: substituir os.execvp por subprocess.run para compatibilidade com Windows"
```

---

### Task 3: Verificar que o MCP conecta no Claude Code

- [ ] **Step 1: Recarregar os MCPs no Claude Code**

No terminal do Claude Code, rodar:
```
! claude mcp list
```

Esperado: `google-developer-knowledge` aparece como `✓ Connected`.

- [ ] **Step 2: Confirmar via ToolSearch que as ferramentas do MCP estão disponíveis**

Pedir ao Claude Code:
> "Use ToolSearch para buscar ferramentas do google-developer-knowledge"

Esperado: ferramentas como `search_documentation` ou similares aparecem no resultado.

---

## Notas

- O `subprocess.run` herda `stdin`, `stdout` e `stderr` do processo pai por padrão — comportamento correto para MCP via STDIO.
- `sys.exit(result.returncode)` propaga exit codes corretamente para o Claude Code monitorar a saúde do processo.
- Essa mudança é compatível com Linux/Mac também (não quebra outros ambientes).
