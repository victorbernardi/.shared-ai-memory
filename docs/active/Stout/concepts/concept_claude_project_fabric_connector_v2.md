---
name: Fabric Database Connector
description: Conector Python para Microsoft Fabric via JDBC/Java, sem permissão de admin para atualizar drivers ODBC
type: project
originSessionId: da11cf19-107f-4e33-a575-031a7ff28f07
---
Conector centralizado em `C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\fabric_db.py`.

**Por que existe:** ODBC driver desatualizado no computador corporativo, sem permissão de admin para atualizar. Solução usa Java (JDBC) como ponte via `jpype` + `jaydebeapi`.

**Banco:** `LH_Consumo` no Microsoft Fabric (`fabric.microsoft.com`)

**Auth:** `InteractiveBrowserCredential` (azure-identity) com cache persistente em disco:
- `TokenCachePersistenceOptions()` → salva tokens em `~/.azure/msal_token_cache.bin`
- `AuthenticationRecord` → salvo em `~/.azure/fabric_auth_record.json` na primeira auth
- Browser só abre na primeira execução ou se o refresh token expirar (~90 dias)
- Para forçar re-autenticação: deletar `~/.azure/fabric_auth_record.json`

**Cache de dados:** Parquet em subpasta `cache/`, controlado por `use_cache` e `save_cache` no método `consultar()`.

**Java:** JDK 11 em `C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\jdk-11.0.30+7`

**Why:** Restrição de admin impede atualização de drivers — esta é a única rota viável para conectar ao Fabric via Python nesta máquina.

**How to apply:** Ao trabalhar em notebooks que consultam o Fabric, usar `import_script.py` como template de importação do conector.
