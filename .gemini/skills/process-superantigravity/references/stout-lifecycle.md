# Stout Edition Architecture & Lifecycle

Este arquivo representa o **Nível 2 (Activation)** da skill `using-superantigravity`. Estas diretrizes são obrigatórias para qualquer projeto operando sob o framework Stout.

## Ciclo de Vida do Projeto

Você deve seguir **obrigatoriamente** este fluxo de trabalho:

### 1. Fase de Pesquisa (`/brainstorm`)
- **Objetivo:** Entender o problema e o contexto sem tocar no código.
- **Saída:** Documento de especificação versionado em `./docs/specs/`.
- **Trava de Segurança:** **Modo Read-Only**. Nenhuma alteração de código é permitida.
- **Memória:** Consulte o `ACTIVE_CONTEXT.md` na pasta `./memory/` para alinhar pendências.

### 2. Fase de Estratégia (`/plan`)
- **Objetivo:** Formular a abordagem técnica detalhada.
- **Saída:** Um plano de execução em `./docs/plans/`.
- **Trava de Segurança:** **STANDBY MODE**. Pare após gerar o plano e aguarde a aprovação humana.

### 3. Fase de Execução (`/build`)
- **Objetivo:** Implementar com segurança.
- **Ferramentas de Proteção:**
  - Aplique a skill `canary-deployment` para alterações sensíveis.
  - Siga rigorosamente `dev-tdd`.
- **Memória:** Atualize o `ACTIVE_CONTEXT.md` ao final de marcos lógicos.

## Idioma Mandatório
Toda a comunicação, especificação e documentação do projeto Stout deve ser conduzida em **Português (PT-BR)**.
