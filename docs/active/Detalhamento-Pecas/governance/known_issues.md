# Known Issues

| Bug ID | Categoria | Descrição | Ocorrências | Workaround | Resolução | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `bug_workaround` | Slicer de data usa locale PT-BR (DD/MM/AAAA); enviar MM/DD gera data inválida e export sem filtro | 1 | Usar `f"{dt.day}/{dt.month}/{dt.year}"` em `_formato_data_pbi` | Corrigido em `extract.py` commit 862bbf2 | `Resolvido` |
| **BUG-002** | `bug_workaround` | Botão confirmar export não encontrado ao buscar em `page` | 1 | Buscar em `pbi_iframe` — diálogo de confirmação está dentro do iframe | Corrigido em `extract.py` commit 3940c31 | `Resolvido` |
| **BUG-003** | `bug_workaround` | Export Power BI limitado a 150.000 linhas — trunca dados quando filtro não aplicado | 1 | Garantir filtro de data correto antes de exportar | Fix BUG-001 resolve a raiz | `Resolvido` |
