# Plano de Evolução: GCC Automático + TDD (Isolamento de Falhas)

## Problema
Quando um teste falha (Fase RED), a tendência do agente é tentar corrigi-lo imediatamente no branch principal. Se a tentativa de correção falha, o histórico de mensagens e o estado do código ficam "envenenados" com erros, dificultando o rollback mental.

## Proposta
Vincular o status de saída dos testes à abertura de um branch GCC temporário.

## Estratégia de Implementação
1. **Trigger de Falha:** Se `pytest` retornar saída != 0, o agente deve invocar `gcc branch fix-<test-name>`.
2. **Ciclo de Tentativa:**
   - O agente tenta o fix no branch isolado.
   - Se funcionar e passar no teste -> `gcc merge`.
   - Se falhar ou causar regressão -> `gcc discard`.
3. **Proteção de Memória:** O branch principal permanece "puro" e sempre funcional (Working State).

## Benefício
Evita que o agente entre em loops de "tentativa e erro" que consomem contexto e degradam a qualidade da solução.
