# Run Log — Detalhamento-Peças 2026
**Data:** 2026-06-17
**Executor:** Claude Code (rotina agendada remota)
**Resultado:** BLOQUEADO — ambiente incompatível

---

## O que foi tentado

Execução da carga diária do pipeline Detalhamento-Peças 2026 via rotina agendada no ambiente remoto (container Linux), com o comando:

```powershell
$env:PYTHONIOENCODING="utf-8"
chcp 65001
C:\Projetos\Inova\.venv\Scripts\python.exe run.py --ano 2026
```

## Diagnóstico

A pipeline não pôde ser executada. Três bloqueios críticos identificados:

| # | Bloqueio | Detalhe técnico |
|---|----------|-----------------|
| 1 | **Playwright não instalado** | `ModuleNotFoundError: No module named 'playwright'` no container Linux |
| 2 | **Sem display server** | `DISPLAY` vazio, sem Xvfb — browser headed impossível |
| 3 | **Paths hardcoded Windows** | `src/config.py` aponta para `C:/Projetos/Inova/...` — perfil Azure AD e `shared/data/` inexistentes no container |

### Causa raiz

O estágio `02_extrair` utiliza **Playwright com browser headed** para autenticação SSO via Azure AD no Power BI Embedded (`grupoinova.powerembedded.com.br`). O perfil de sessão autenticada está em:

```
C:\Projetos\Inova\projects\dashboard-inova-data-export\browser_state\user_profile\
```

Este caminho só existe na máquina Windows local do operador. Um container Linux remoto não tem acesso a esse perfil, não tem display para abrir um browser headed, e não tem Playwright instalado.

## Ação necessária

Executar localmente na máquina Windows:

```powershell
$env:PYTHONIOENCODING="utf-8"; chcp 65001
C:\Projetos\Inova\.venv\Scripts\python.exe run.py --ano 2026
```

## Caminhos para viabilizar execução remota futura

1. **Substituir scraping por API** — usar a API REST do Power BI Embedded em vez de Playwright (elimina dependência de browser)
2. **Externalizar sessão de autenticação** — armazenar tokens OAuth no Azure Key Vault ou similar, em vez de perfil local de browser
3. **Parametrizar paths** — substituir caminhos Windows hardcoded em `src/config.py` por variáveis de ambiente (`INOVA_ROOT`, `SHARED_DATA_DIR`)
