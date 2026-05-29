# Critérios de Decisão — Auditoria de Skills

## Os três veredictos possíveis

### ✅ APROVAÇÃO — Quando emitir

- Score semântico < 40% em relação a TODAS as skills existentes
- Papel proposto não tem equivalente no registry
- Triggers propostos não colidem com triggers de outra skill ativa
- A skill resolve um problema real que nenhuma outra resolve hoje

### ⚠️ QUESTIONAR — Quando emitir

- Score semântico entre 40% e 80% com alguma skill existente
- Parte do comportamento proposto já é coberto por outra skill
- Os triggers colidem parcialmente com outra skill ativa
- A skill proposta poderia ser um novo Tipo/Modo de uma skill existente

**Ação ao questionar:**
Apresentar as opções de forma clara:

1. Redefinir fronteira da nova skill (excluir o overlap)
2. Melhorar a skill existente para cobrir o novo caso
3. Extrair parte comum para skill compartilhada

Aguardar decisão explícita de Victor antes de prosseguir.

### ❌ REJEIÇÃO — Quando emitir

- Score semântico > 80% com alguma skill existente
- Papel proposto é idêntico ou quase idêntico ao de skill existente
- Os triggers são os mesmos de outra skill ativa
- A nova skill seria um clone da existente com nome diferente

## Como calcular sobreposição semântica manualmente

Se `semantic_overlap.py` falhar, usar heurística:

**Pergunta 1:** O papel proposto e o papel existente começam com o mesmo verbo?
(ex: ambos "Cria...", ambos "Valida...") → +30 pontos

**Pergunta 2:** Mais de 50% dos triggers propostos existem na skill atual?
→ +30 pontos

**Pergunta 3:** Os exemplos de uso descritos são intercambiáveis?
→ +40 pontos

Score total determina o veredicto (< 40 = aprovar, 40-80 = questionar, > 80 = rejeitar).

## Documentando o veredicto

Todo veredicto DEVE ser salvo em `audit_result.json` com:

- Veredicto (APPROVED / QUESTIONED / REJECTED)
- Score de sobreposição por skill
- Motivo detalhado
- Data e versão do auditor