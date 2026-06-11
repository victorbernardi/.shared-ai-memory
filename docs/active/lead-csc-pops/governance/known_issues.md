# 🐛 Lista de Bugs Conhecidos & Workarounds

Este documento registra de forma viva, imutável e estruturada todos os bugs de ambiente, bibliotecas ou travas físicas reincidentes descobertos nas sessões do ecossistema Stout, juntamente com suas soluções temporárias (workarounds) e status de correção definitiva.

---

| Bug ID | Categoria | Descrição | Ocorrências | Workaround Conhecido | Correção Definitiva | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BUG-001 | Excel Protection | A planilha de leads gerada com senha de proteção impedia a alteração das colunas O e P (Retorno/Obs). Além disso, a atualização do Power Query no Excel de destino resetava as propriedades de desbloqueio celular de volta para o padrão da folha (locked=True). | 1 | N/A | Remoção da proteção geral de senha (`ws.protection.sheet = False`) e aplicação de validação de dados restritiva pura (`DataValidation`) nas colunas editáveis: lista dropdown em O e limite de 250 caracteres em P. | Resolvido |


---

> [!NOTE]
> Este arquivo é atualizado de forma dinâmica e programática pela skill `stout-session-learning` ao final de cada sessão.
