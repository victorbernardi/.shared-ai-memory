# Lista de Saneamento: Arquivos e Pastas a Ignorar

## 1. Pastas de Cache e Artefatos Temporários
- `**/__pycache__/`
- `**/.pytest_cache/`
- `**/.mypy_cache/`
- `**/.tox/`
- `**/build/`
- `**/dist/`
- `html_artifacts/`
- `templates/` (a revisar se deve ser versionado)
- `scratch/cache/`

## 2. Dados de Sessão e Perfis de Browser (Sensíveis)
- `antigravity-browser-profile/`
- `chrome_profile_notebooklm/`
- `scratch/chrome_profile_notebooklm/`
- `browser_recordings/`
- `context-agent/data/sessions/`
- `context-agent/data/logs/`
- `**/*.sqlite`
- `**/*.log`

## 3. Configurações Sensíveis (Proteção)
- `.env` (Raiz e subpastas)
- `.gemini/*.json` (exceto `projects.json`, `settings.json`)
- `oauth_creds.json`
- `google_accounts.json`

## 4. Extensões e Binários
- `extensions/`
- `**/*.pyc`
- `**/*.db`

---
## Plano de Execução (Tasks)
1. **Task 01:** Atualizar `.gitignore` com a lista acima.
2. **Task 02:** Executar `git rm -r --cached` para remover arquivos rastreados que deveriam estar ignorados.
3. **Task 03:** Limpar fila de commits pendentes com commits lógicos (Infra, Docs, Skills).
4. **Task 04:** Rodar auditoria final (`git status`).
