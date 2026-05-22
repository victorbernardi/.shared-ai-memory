# 🛡️ Plano de Evolução: Stout Shield (Maturidade Nível 3)

> **Status:** 🟡 Planejado
> **Data:** 2026-05-13
> **Objetivo:** Blindar o ecossistema Stout contra falhas silenciosas, corrupção de dados e rigidez de infraestrutura.

---

## 1. Iniciativa: Autocura (Self-Healing Background)

**Problema:** Watchers falham silenciosamente no background, e o erro só é descoberto via auditoria manual de logs.
**Solução:** Implementar um mecanismo de "Heartbeat" e Alertas Ativos.

- **Ação 1:** Watchers devem escrever um timestamp em `.stout/heartbeat.json` a cada 5 minutos.
- **Ação 2:** Criar uma função de pré-vôo (`pre-flight check`) no `GEMINI.md` global que verifica se os heartbeats estão atualizados. Caso não estejam, o Agente avisa o usuário no início da sessão.
- **Ação 3:** Captura de exceções críticas enviando um "Signal File" que força um alerta visual na próxima interação.

## 2. Iniciativa: Independência de Ambiente (Path Resilience)

**Problema:** Caminhos absolutos hardcoded (ex: `C:\Motores-LLM\...`) impedem a portabilidade e causam quebras em atualizações.
**Solução:** Abstração de caminhos via Variáveis de Ambiente e Roots Dinâmicos.

- **Ação 1:** Substituir todos os caminhos absolutos nos scripts (`watcher.py`, `stout_promote.py`) por referências baseadas em `os.path.dirname` ou variáveis de ambiente como `STOUT_RESOURCES`.
- **Ação 2:** Criar um script `env_setup.py` que valida e mapeia os caminhos necessários no primeiro uso.

## 3. Iniciativa: Integridade de Encoding (UTF-8 Guard)

**Problema:** Caracteres especiais (diagramas de árvore, acentos) são corrompidos ao transitar entre diferentes shells e scripts (UTF-8 vs ANSI).
**Solução:** Protocolo de Escrita e Leitura Blindada.

- **Ação 1:** Adicionar validação de `BOM` (Byte Order Mark) em scripts de edição automática.
- **Ação 2:** Implementar no `markdown-auto-fixer` um check de sanitização que substitui caracteres corrompidos comuns (`├`) por seus equivalentes corretos (`├──`) automaticamente.
- **Ação 3:** Configurar `.editorconfig` na raiz de todos os projetos gerados pelo `stout-init`.

---

## 📅 Cronograma de Implementação

1. **Sprint 1 (Encoding):** Correção de caracteres e proteção UTF-8.
2. **Sprint 2 (Paths):** Refatoração de caminhos absolutos para relativos.
3. **Sprint 3 (Autocura):** Sistema de Heartbeat e alertas no chat.
