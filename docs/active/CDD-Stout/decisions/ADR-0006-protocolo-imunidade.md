# ADR-0006: Protocolo de Imunidade a Erros e Arquitetura de Delegação

## Status

Proposto (2026-05-14)

## Contexto

O ecossistema Antigravity/Stout opera em múltiplos projetos via Gemini CLI. Observou-se que falhas recorrentes não eram documentadas adequadamente e que o agente orquestrador frequentemente tentava correções rápidas (ad-hoc) sem analisar a causa raiz, levando a erros em cascata e perda de rastreabilidade. Além disso, o orquestrador estava acumulando excesso de responsabilidades, violando o princípio do Context Wall.

## Decisão

Implementaremos o **Protocolo de Imunidade a Erros** integrado à skill `using-superantigravity`.

1.  **Separação de Poderes:** O orquestrador (`using-superantigravity`) será responsável apenas pela consciência de estado e controle de fluxo. A resolução de erros será obrigatoriamente delegada à skill `systematic-debugging`.
2.  **Trava Física (Audit Gate):** Criaremos um mecanismo de bloqueio via arquivo `.audit_gate` que impede operações de escrita (`replace`, `write_file`) em caso de falha não auditada.
3.  **Validação Externa:** A MCP `context7` será a fonte obrigatória de verdade para diagnósticos técnicos.
4.  **Imutabilidade Proativa:** Aplicaremos tecnicamente o `protocolo_ferramentas_cli.md`, proibindo `write_file` em arquivos existentes para garantir edições cirúrgicas via `replace`.
5.  **Metadados de Qualidade:** Utilizaremos o arquivo `.stout_seal.json` para rastrear a governança de cada arquivo, evitando poluição visual no código-fonte.

## Consequências

- **Positivas:** Maior resiliência do sistema, documentação automática de falhas (failure-log), e redução de erros por "tentativa e erro".
- **Negativas:** Leve aumento na fricção durante o desenvolvimento (necessidade de limpar o gate), risco de deadlock (mitigado pela flag bypass).
- **Neutras:** Mudança na forma como o agente interage com o sistema de arquivos (preferência absoluta por `replace`).

## Referências

- `docs/plans/2026-05-14-refactor-skill-superantigravity.md`
- `docs/governance/protocolo_ferramentas_cli.md`
- `src/distributed/orchestrator_sync.py` (Inspiração de resiliência v5)
