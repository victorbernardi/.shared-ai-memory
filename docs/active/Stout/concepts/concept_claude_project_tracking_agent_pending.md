---
name: Agente de Rastreamento — próximo do ecossistema
description: Agente urgente pendente para fechar o loop sugestão→decisão→plano→implementação no ecossistema Inova AI
type: project
originSessionId: 77fa934c-e7c1-4128-962b-dd61f988c294
---
O ecossistema tem um gap crítico: o Córtex gera sugestões em SUGESTOES-HOJE.md mas não há rastreamento do que acontece depois.

**Por que:** Sem este agente, sugestões do Córtex se perdem. O usuário não tem como saber o que foi implementado, rejeitado ou esquecido. A wiki pode acumular ideias não executadas como se fossem fatos.

**How to apply:** Quando o usuário iniciar próxima sessão de planejamento de ecossistema, lembrar que este agente é a prioridade. Já foi registrado em SUGESTOES-HOJE.md em 2026-04-20.

**Fluxo esperado do agente:**

- Lê SUGESTOES-HOJE.md
- Para cada sugestão: pergunta ao usuário (implementar / rejeitar / adiar)
- Aprovadas → cria tarefa no Notion + inicia plano no Stout
- Implementadas → gera handoff `tipo: referencia` real para a wiki
- Rejeitadas → arquiva com motivo
