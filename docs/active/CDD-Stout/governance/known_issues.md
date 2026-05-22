# 🐛 Lista de Bugs Conhecidos & Workarounds (Stout CDD)

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `permission` | `PermissionError` ao salvar slides V4.3 (`MASTER.pptx` travado aberto pelo PowerPoint) | 7 | Fechar o PowerPoint antes de rodar os scripts de compilação. | Implementar try/except com salvamento em arquivo incremental temporário. | `Pendente` |
| **BUG-002** | `packaging` | Imagens duplicadas no merge do ZIP na lib `python-pptx` | 1 | N/A | Reescrevemos a função `_copy_images` para isolar bytes puros. | `Resolvido` |
| **BUG-003** | `bug_workaround` | de concorrência inesperado no sqlite3 database com tabelas bloqueadas. | 2 | Verificar arquivos relacionados: js | Pendente de análise | `Pendente` |
| **BUG-004** | `bug_workaround` | de concorrência inesperado no sqlite3 database com tabelas bloqueadas."} | 1 | Verificar arquivos relacionados: js | Pendente de análise | `Pendente` |
| **BUG-005** | `bug_workaround` | ] Falha ao rodar audit_skills.py:") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-006** | `bug_workaround` | ] Nenhum relatório de auditoria encontrado.") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-007** | `bug_workaround` | ] '{choice}' não está na lista de skills prontas.") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-008** | `bug_workaround` | Skills root not found: {SKILLS_ROOT}") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-009** | `bug_workaround` | No audit report found. Run audit_skills.py first.") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-010** | `bug_workaround` | ] audit_skills.py não encontrado em: {AUDIT_SCRIPT}") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-011** | `bug_workaround` | ] promote_skills.py não encontrado em: {PROMOTE_SCRIPT}") | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-012** | `bug_workaround` | in step execution: Permission prompt for action 'command' on target 'python -m pytest tests/ -v' timed out waiting for user response. The user was not | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-013** | `bug_workaround` | in step execution: Permission prompt for action 'command' on target 'python scripts/audit_skills.py' timed out waiting for user response. The user was | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-014** | `bug_workaround` | in step execution: Permission prompt for action 'unsandboxed' on target 'python scripts/audit_skills.py' timed out waiting for user response. The user | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-015** | `bug_workaround` | ao não sugerir as outras skills pendentes de promoção global: | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-016** | `bug_workaround` | in step execution: exec: "grep": executable file not found in %PATH% | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-017** | `bug_workaround` | in step execution: Permission prompt for action 'command' on target 'C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe scripts/audit_skills. | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-018** | `bug_workaround` | in step execution: Permission prompt for action 'unsandboxed' on target 'C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe scripts/audit_ski | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-019** | `bug_workaround` | física deve resultar na criação do .audit_gate. | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-020** | `bug_workaround` | de comando não encontrado no log apenas reflete que o interpretador Python global no caminho absoluto do Anaconda não estava disponível para o console | 1 | Verificar arquivos relacionados: bat, py, sh, js, yaml, ps1, md | Pendente de análise | `Pendente` |
| **BUG-021** | `bug_workaround` | in step execution: Permission denied for read_file(C:\Users\victor.bernardi\.gemini\antigravity-cli). Matches hardcoded system protection boundary rul | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-022** | `bug_workaround` | mais de duas vezes seguidas, você deve forçar uma parada de Standby para auditoria humana.`n* SEMPRE gere um registro documentado da falha antes de al | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-023** | `bug_workaround` | de teste e isolamento de contexto. | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-024** | `bug_workaround` | in step execution: Permission prompt for action 'write_file' on target 'C:\Users\victor.bernardi\.gemini\config\skills\wiki-ingest\SKILL.md' timed out | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-025** | `bug_workaround` | ", "falha", "fix", "workaround"]): | 1 | ", "falha", "fix", "workaround"]): | Pendente de análise | `Pendente` |
| **BUG-026** | `bug_workaround` | \d+\*\* \|.*?)(?=\n)", content) | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-027** | `bug_workaround` | ["occurrences"] += 1 | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-028** | `bug_workaround` | existente detectado ({bug['id']}). Incrementando contagem para {bug['occurrences']}.") | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-029** | `bug_workaround` | detectado! Registrando | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-030** | `security` | Ceiling (~200k tokens práticos).`n* NUNCA permita a proliferação de subagentes na infraestrutura para resolver tarefas lineares; exija a orquestração  | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |
| **BUG-031** | `security` | ** Também criamos uma cópia preventiva local da skill corrigida na pasta do projeto em [C:\Projetos\Stout\skills\wiki-ingest\SKILL.md](file:///C:/Proj | 1 | Verificar arquivos relacionados: bat, md, py, yaml, js | Pendente de análise | `Pendente` |

---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
