# Plano de Execução do Ecossistema

Este documento consolida a conversa e os planos de instalação do `stout-init`.

## 1. Instalação
1. Copiar `GEMINI.md` para a pasta pai dos projetos.
2. Executar `python install_stout_init.py`.
3. Configurar API Keys no `.env`.

## 2. Configuração de MCPs
Configuração padrão em `.gemini/settings.json`:
- `context7`
- `google-drive`
- `notebooklm`

## 3. Estrutura do Projeto
- `GEMINI.md` (Negócio)
- `ANTIGRAVITY.md` (Kernel)
- `.gemini/settings.json` (MCPs)
- Pastas: `src/`, `data/`, `tests/`, `scripts/`, `docs/`
