# As 4 Fases do Debugging Stout

### Fase 1: Investigação de Causa Raiz
- Leia mensagens de erro integralmente.
- Reproduza de forma consistente.
- Verifique alterações recentes (Git Diff).

### Fase 2: Análise de Padrão
- Encontre exemplos de código que funcionam.
- Identifique a diferença mínima entre o que funciona e o que falha.

### Fase 3: Hipótese e Teste
- Formule uma teoria: "Acho que X quebra por causa de Y".
- Faça a menor mudança possível para testar a teoria.

### Fase 4: Implementação e Verificação
- Crie o caso de teste falhando (**TDD**).
- Aplique a correção.
- Verifique se o bug sumiu e se não houve regressões.
