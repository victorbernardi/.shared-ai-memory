# 🐛 Lista de Bugs Conhecidos & Workarounds (Stout CDD)

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `permission` | `PermissionError` ao salvar slides V4.3 (`MASTER.pptx` travado aberto pelo PowerPoint) | 10 | Fechar o PowerPoint antes de rodar os scripts de compilação. | Implementar try/except com salvamento em arquivo incremental temporário. | `Pendente` |
| **BUG-002** | `packaging` | Imagens duplicadas no merge do ZIP na lib `python-pptx` | 1 | N/A | Reescrevemos a função `_copy_images` para isolar bytes puros. | `Resolvido` |
| **BUG-003** | `bug_workaround` | de concorrência inesperado no sqlite3 database com tabelas bloqueadas."} | 3 | Verificar arquivos relacionados: js | Pendente de análise | `Pendente` |
| **BUG-004** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-005** | `bug_workaround` | " → debugging first, then domain-specific skills. | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-006** | `bug_workaround` | Erro fatal: No module named 'filtros' | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-007** | `bug_workaround` | fatal: No module named 'filtros' | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-008** | `bug_workaround` | na conexao DB. Tentando cache...") | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-009** | `bug_workaround` | ("Stage %s: FAIL", key) | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-010** | `bug_workaround` | ao executar o Pre-flight check: %s", exc) | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-011** | `bug_workaround` | não-bloqueante ao gerar relatório de recência global: %s", exc) | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-012** | `bug_workaround` | ("Validação falhou: %s", exc) | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-013** | `bug_workaround` | inesperado: %s", exc) | 2 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-014** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-015** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-016** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-017** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-018** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-019** | `bug_workaround` | \" → debugging first, then domain-specific skills.\r\n135: \r\n136: ## Skill Types\r\n137: \r\n138: **Rigid** (TDD, debugging, canary-deployment): Fol | 1 | Verificar arquivos relacionados: js, py, sql, md, yaml, bat | Pendente de análise | `Pendente` |
| **BUG-020** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz  | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-021** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz  | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-022** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-023** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-024** | `bug_workaround` | de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz  | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-025** | `bug_workaround` | , you must focus on fixing the failed tool call with sequential tool calls and try again. Do not do parallel tool calls and if you are fixing multiple | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
| **BUG-026** | `bug_workaround` | \" → debugging first, then domain-specific skills.\r\n135: \r\n136: ## Skill Types\r\n137: \r\n138: **Rigid** (TDD, debugging, canary-deployment): Fol | 1 | Verificar arquivos relacionados: js, bat, md, sql, py, yaml | Pendente de análise | `Pendente` |
---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
