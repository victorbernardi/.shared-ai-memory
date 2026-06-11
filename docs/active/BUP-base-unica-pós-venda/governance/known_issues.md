# Known Issues — BUP Pós-Venda

Bugs e workarounds identificados em sessões de desenvolvimento.
Atualizar sempre que um novo incidente for reproduzido ou resolvido.

---

## [BUG-001] Coluna inexistente `VS1_NRORCO` no VS1010

- **Status:** Identificado (não corrigido em scripts permanentes)
- **Sessão:** 2026-06-01
- **Sintoma:** Query ao Fabric retorna `Invalid column name 'VS1_NRORCO'`
- **Causa:** O nome correto da coluna de número de orçamento no VS1010 é `VS1_NUMORC`, não `VS1_NRORCO`
- **Workaround:** Usar `VS1_NUMORC` em todas as queries ao VS1010
- **Arquivos afetados:** Qualquer script ad-hoc que consulte VS1010 — o `consolidate_bup.py` usa apenas `VS1_DATORC` e `VS1_CODVEN`, portanto não é afetado

---

## [BUG-002] `recency_status.md` salvo com encoding quebrado

- **Status:** ✅ Resolvido em 2026-06-01
- **Sessão:** 2026-06-01
- **Sintoma:** Arquivo exibia `RelatÃ³rio`, `RecÃªncia`, `ðŸŸ¢` em vez dos caracteres UTF-8 corretos
- **Causa raiz:** `shared/generate_recency_report.py` foi editado/salvo com encoding CP1252 em algum momento — as strings literais no código fonte já continham mojibake, fazendo o `write_text(encoding='utf-8')` gravar bytes corrompidos
- **Correção:** Reescrita completa do arquivo fonte com strings UTF-8 corretas. Label "Feedbacks BUP" também corrigido para "BUP Pós-Venda (relatório + feedbacks consultores)"

---

## [BUG-003] Falha de cópia OneDrive com `WinError 32` (arquivo em uso)

- **Status:** Comportamento esperado do OS (não é bug do motor)
- **Sessão:** 2026-06-01
- **Sintoma:** `AVISO: Falha ao copiar para OneDrive: [WinError 32] O arquivo já está sendo usado por outro processo`
- **Causa:** Excel mantém lock exclusivo no arquivo `BUP_POS_VENDA.xlsx` enquanto está aberto
- **Workaround:** Fechar o Excel antes de rodar o motor, ou recopiar manualmente após o Excel ser fechado
- **Melhoria sugerida:** Tentar cópia com retry + backoff (3 tentativas, 2s de intervalo) antes de emitir o aviso
