# WALKTHROUGH: Operando o Protocolo de Imunidade a Erros (V2)

Este guia descreve como agir sob a nova governança do Orquestrador V2 e do Sentinel Agent v5.

## 1. O Fluxo de Travamento (Auto-Audit)
Sempre que um comando técnico (ex: script Python, teste, deploy) falhar com **Exit Code != 0**, o sistema agirá da seguinte forma:

1.  **Interceptação:** O Sentinel Agent detecta o erro.
2.  **Gatekeeper:** Um arquivo `.audit_gate` é criado na raiz do projeto.
3.  **Bloqueio:** O `src/core/preflight.py` passará a retornar `valid: False`.
4.  **Imobilidade:** Qualquer tentativa de usar `replace` ou `write_file` será negada pelo agente orquestrador.

## 2. Como Resolver (O Caminho do Sucesso)
Não tente burlar a trava. Siga o protocolo Stout:

1.  **Invocação:** Ative a skill specialized: `/systematic-debugging`.
2.  **Análise:** O agente consultará a MCP `context7` para entender a falha técnica.
3.  **Registro:** Escreva a causa raiz e a solução no `notes/failure-log.md`.
4.  **Governança:** Valide o `ADR` e o `Plano de Implementação` diretamente no chat.
5.  **Liberação:** Após a confirmação da documentação, o sistema removerá o `Audit Gate` automaticamente.

## 3. Comandos de Emergência (Bypass)
Se você estiver em um impasse técnico (Deadlock) onde precisa consertar o próprio motor:

- **Flag de Bypass:** `--bypass-gate`
- **Restrição:** Permitido apenas para arquivos dentro de `src/core/`.
- **Exemplo:** `python src/core/preflight.py --fix --bypass-gate`

## 4. Regras de Ouro da CLI
- **NUNCA** use `write_file` em arquivos que já existem. O sistema monitora a imutabilidade.
- **SEMPRE** prefira o `replace` cirúrgico para manter a integridade do código.

---
**Status:** IMPLEMENTADO E VALIDADO (2026-05-14)
**ADR de Referência:** [[ADR-0006-protocolo-imunidade]]
