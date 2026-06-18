# Known Issues

| Bug ID | Categoria | Descrição | Ocorrências | Workaround | Resolução | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `bug_workaround` | Slicer de data usa locale PT-BR (DD/MM/AAAA); enviar MM/DD gera data inválida e export sem filtro | 1 | Usar `f"{dt.day}/{dt.month}/{dt.year}"` em `_formato_data_pbi` | Corrigido em `extract.py` commit 862bbf2 | `Resolvido` |
| **BUG-002** | `bug_workaround` | Botão confirmar export não encontrado ao buscar em `page` | 1 | Buscar em `pbi_iframe` — diálogo de confirmação está dentro do iframe | Corrigido em `extract.py` commit 3940c31 | `Resolvido` |
| **BUG-003** | `bug_workaround` | Export Power BI limitado a 150.000 linhas — trunca dados quando filtro não aplicado | 1 | Garantir filtro de data correto antes de exportar | Fix BUG-001 resolve a raiz | `Resolvido` |
| **BUG-004** | `bug_workaround` | de Lock e Permissão (Acesso Negado 0x5):** | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-005** | `bug_workaround` | * Como a tela do Power BI exibe múltiplas tabelas, os botões de cabeçalho *"Mais opções"* possuem classes e labels idênticos. O Playwright gerou downl | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-006** | `bug_workaround` | ] Threshold de Vendas violado. Abortando.') | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-007** | `bug_workaround` | ] Threshold de Devoluções violado. Abortando.') | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-008** | `bug_workaround` | executing cascade step: CORTEX_STEP_TYPE_RUN_COMMAND: opening NUL for ACL write: Access is denied. | 0.9 | `low` | `bug_workaround, Detalhamento-Pecas | 1 | executing cascade step: CORTEX_STEP_TYPE_RUN_COMMAND: opening NUL for ACL write: Access is denied. | 0.9 | `low` | `bug_workaround, Detalhamento-Pecas | Pendente de análise | `Pendente` |
| **BUG-009** | `bug_workaround` | " → debugging first, then domain-specific skills. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-010** | `bug_workaround` | DE AUTENTICAÇÃO] A SESSÃO DO POWER BI EXPIROU OU O PORTAL ESTÁ INACESSÍVEL.\n\n" | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-011** | `bug_workaround` | complexo. O objetivo aqui é o entendimento total do problema e a definição clara da solução antes de qualquer linha de código ser escrita. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-012** | `bug_workaround` | 64: 1. Erro `RuntimeError: Sessão expirada` em `02_extrair` → voltar para este estágio | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-013** | `bug_workaround` | 80: 1. Screenshot automático salvo em `debug_error_page.png` na raiz do projeto | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-014** | `bug_workaround` | de autenticação: voltar para `01_autenticar` | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-015** | `bug_workaround` | = ABORTA:** se colunas obrigatórias faltam, não prosseguir. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-016** | `bug_workaround` | 3. DataFrame resultante tem >0 linhas | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-017** | `bug_workaround` | 60: 1. `ValueError('Schema invalido')` → verificar se o Power BI mudou as colunas do relatório | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-018** | `bug_workaround` | 85: 1. Registrar `passed: false` em `output/audit.json` com `delta` calculado | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-019** | `bug_workaround` | ] Threshold violado: delta={delta:.1%}` | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-020** | `bug_workaround` | no recency report não bloqueia a persistência. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-021** | `bug_workaround` | 67: 1. Verificar permissões de escrita em `shared/data/` | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-022** | `bug_workaround` | found? Write failing test reproducing it. Follow TDD cycle. Test proves fix and prevents regression. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
| **BUG-023** | `bug_workaround` | (RED) para certificar a ausência do código de produção. | 1 | Verificar arquivos relacionados: py, js, md, yaml | Pendente de análise | `Pendente` |
