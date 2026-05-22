# Plano de Estratégia: Erradicação de Erros de Encoding (Vacina Erro Zero)

Este plano define a estratégia para corrigir sistemicamente a corrupção de caracteres especiais (Mojibake) e garantir a integridade UTF-8 em toda a infraestrutura Stout/Antigravity.

## 1. Diagnóstico da Causa Raiz
- **Falha 1:** Scripts Python (`stout_promote.py`, `brain-watcher.py`) utilizam `open()` sem o parâmetro `encoding='utf-8'`, assumindo o padrão do sistema (CP1252 no Windows).
- **Falha 2:** Comandos Powershell via `Set-Content` ou `Out-File` salvam em UTF-16 ou ANSI por padrão, causando double-encoding ao serem lidos como UTF-8.
- **Falha 3:** A ingestão do `wiki-compiler` propaga caracteres corrompidos para o vault Obsidian sem validação de integridade.

## 2. Abordagem de Implementação (A Vacina)

### Fase 1: Blindagem de Infraestrutura (Scripts)
- **Patch Python:** Adicionar `encoding='utf-8'` em todos os `open()`, `read_text()` e `write_text()` nos diretórios:
  - `C:\Users\victor.bernardi\.shared-ai-memory\scripts\`
  - `C:\projetos\stout\wiki-compiler\`
- **Patch Powershell:** Substituir comandos de escrita nativos por chamadas diretas ao .NET `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)` para evitar o BOM do UTF-16.

### Fase 2: Sanitarização em Massa (O Vault)
- **Script de Limpeza:** Executar script robusto em `C:\Users\victor.bernardi\Documents\wiki-compiler-vault` que:
  1. Detecta padrões de Mojibake (ex: `Ã§`, `Ãµ`).
  2. Converte o arquivo para o formato canônico UTF-8.
  3. Valida a ausência de BOM (Byte Order Mark).

### Fase 3: Vacina de Erro Zero (Governance)
- Atualizar o `GEMINI.md` e a skill `using-superantigravity` com a restrição impeditiva: **"PROIBIDO salvar arquivos .md sem declarar UTF-8 explicitamente."**
- Criar um pre-commit hook ou watcher que valide o encoding antes de permitir a promoção de artefatos.

## 3. Validação (QA)
- Rodar o `wiki_health_check.py` atualizado para buscar caracteres não-UTF-8.
- Verificar visualmente arquivos críticos: `GEMINI.md`, `industrial-telemetry-motion.md` e `index.md`.

---
**Status:** Aguardando Aprovação (Standby Mode)
**Autor:** Gemini CLI Builder
