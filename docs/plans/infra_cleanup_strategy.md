# Estratégia de Saneamento: .gitignore e Dívida de Commits (v1.0)

## 1. Objetivo
Proteger arquivos sensíveis (segredos), ignorar artefatos pesados/temporários e limpar a fila de milhares de commits/mudanças pendentes de forma organizada e segura.

## 2. Diagnóstico (Research)
- **Segredos Expostos:** `.env` na raiz e `.gemini/` contém tokens ativos (Tavily, GitHub, Notion).
- **Arquivos Pesados/Untracked:** Pastas como `extensions/`, `browser_recordings/`, `chrome_profile_notebooklm/` e caches de Python (`__pycache__`).
- **Dívida Técnica:** Mudanças em `docs/`, `skills/` e `context-agent/` misturadas sem commits lógicos.

## 3. Plano de Ação

### Fase 1: Proteção de Infraestrutura (.gitignore)
1. **Atualizar `.gitignore` raiz:** Incluir explicitamente:
   - `.env` e `**/.env`
   - `.gemini/*.json` (exceto `projects.json` e `settings.json` se necessário, mas idealmente ignorar segredos).
   - `extensions/`
   - `chrome_profile_*/`
   - `**/*.pyc`, `**/__pycache__/`
   - `context-agent/logs/`, `context-agent/sessions/`
   - `browser_recordings/`
2. **Remover do index (se rastreados):** Garantir que arquivos que entrarão no gitignore sejam removidos do cache do git (`git rm --cached`).

### Fase 2: Organização de Commits (The Big Cleanup)
Dividir as mudanças em blocos lógicos seguindo o padrão `chore`, `feat`, `docs`:
1. **Bloco Infra:** `.gitignore` e proteções.
2. **Bloco Docs:** Mudanças em `docs/active/` e `docs/business/`.
3. **Bloco Skills:** Atualizações em `skills/` e `context-agent/`.
4. **Bloco Governança:** `GEMINI.md`, `STYLE_GUIDE.md`, etc.

### Fase 3: Validação
- Verificar `git status` para confirmar se apenas o necessário está sendo rastreado.
- Rodar `git diff --staged` para revisão final antes de cada commit.

## 4. Segurança (Protocolo Canary)
Como vamos mexer no `.gitignore` e potencialmente remover arquivos do index, o protocolo `canary-deployment` será mantido como guia de segurança para arquivos de infraestrutura.

---
**Status:** Aguardando Aprovação Humana (Standby Mode).
