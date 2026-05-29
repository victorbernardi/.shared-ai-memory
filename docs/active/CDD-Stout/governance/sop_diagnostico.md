# SOP de Diagnóstico e Correção (Search-Before-Code)

> **STATUS:** IMUTÁVEL / MANDATÓRIO
> **LOCALIZAÇÃO:** `docs/governance/sop_diagnostico.md`

## 1. OBJETIVO

Eliminar desperdício operacional por "tentativa e erro" (trial and error) durante o desenvolvimento. Garantir que a resolução de falhas seja pautada em conhecimento técnico validado e melhores práticas da indústria.

## 2. PROCEDIMENTO (SEARCH-BEFORE-CODE)

Toda vez que o motor de análise detectar um erro (runtime, compilação, linting ou teste), o agente DEVE interromper qualquer tentativa de correção autônoma e seguir o fluxo:

1.  **INTERRUPÇÃO:** Bloqueio total de modificação de código ou tentativa de execução de correção ("adivinhação").
2.  **CONSULTA (Context-Fetch):** Envio obrigatório do sinal de erro para a MCP `context7`.
    *   *Input:* `context7: explicar erro [COLAR_ERRO] na lib [LIB_NAME] e prover solução oficial.`
3.  **VALIDAÇÃO ESTRATÉGICA:** O agente deve comparar o retorno da MCP com a arquitetura definida em `GEMINI.md`.
4.  **EXECUÇÃO CIRÚRGICA:** Aplicação da correção baseada estritamente no contexto obtido.
5.  **REGISTRO (Feedback Loop):** Inserção obrigatória do aprendizado em `notes/failure-log.md`.

## 3. MECANISMO DE PROTEÇÃO

Este documento é a **Fonte da Verdade**. Agentes de IA estão proibidos de modificar ou ignorar este procedimento em prol de velocidade ou conveniência. Qualquer desvio é classificado como "Falha de Governança" e deve ser reportado no `failure-log.md`.
