# 🐛 Lista de Bugs Conhecidos & Workarounds (Stout CDD)

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `permission` | `PermissionError` ao salvar slides V4.3 (`MASTER.pptx` travado aberto pelo PowerPoint) | 6 | Fechar o PowerPoint antes de rodar os scripts de compilação. | Implementar try/except com salvamento em arquivo incremental temporário. | `Pendente` |
| **BUG-002** | `packaging` | Imagens duplicadas no merge do ZIP na lib `python-pptx` | 1 | N/A | Reescrevemos a função `_copy_images` para isolar bytes puros. | `Resolvido` |
| **BUG-003** | `bug_workaround` | de concorrência inesperado no sqlite3 database com tabelas bloqueadas. | 1 | Verificar arquivos relacionados: js | Pendente de análise | `Pendente` |
| **BUG-004** | `bug_workaround` | de concorrência inesperado no sqlite3 database com tabelas bloqueadas."} | 1 | Verificar arquivos relacionados: js | Pendente de análise | `Pendente` |

---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
