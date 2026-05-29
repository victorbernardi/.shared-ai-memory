# Spec: Alinhamento Nativo - Task Planning (write_todos & Plan Mode)

**Data:** 2026-05-16
**Status:** Design
**Autor:** Arquiteto Stout

## 1. Objetivo

Alinhar o fluxo de trabalho "Elite Stout" com as ferramentas nativas de planejamento do Gemini CLI (`write_todos` e `plan mode`), garantindo visibilidade visual via `Ctrl+T` e persistência de foco agêntico conforme a documentação oficial.

## 2. Requisitos Funcionais

### FR-001: Integração com Motor de Todos

- A skill `stout-writing-plans` deve, além de gerar o arquivo Markdown, invocar a ferramenta `write_todos` (se disponível) para popular a lista visual do CLI.
- As tarefas devem ser mapeadas 1:1 entre o Markdown e o CLI Todo List.

### FR-002: Ciclo de Vida da Tarefa Nativa

- A skill `stout-executing-plans` e os subagentes devem atualizar o status de cada Todo no CLI:
  - Início da Task -> `IN_PROGRESS`.
  - Fim da Task -> `COMPLETED`.

### FR-003: Uso de Plan Mode

- Toda fase de **Research** e **Strategy** de um projeto novo deve ser iniciada via `enter_plan_mode`.
- O Maestro deve garantir que o design seja concluído e aprovado antes de chamar `exit_plan_mode` para iniciar a execução.

## 3. Matriz de Mapeamento de Ferramentas

| Ação Stout | Ferramenta Nativa Gemini CLI |
| :--- | :--- |
| Iniciar Pesquisa | `enter_plan_mode` |
| Registrar Plano | `write_todos` (ou `tracker_create_task`) |
| Visualizar Progresso | `Ctrl+T` (Interface do Usuário) |
| Executar Task | `invoke_agent` (@generalist) |

## 4. Plano de Validação

1. **Teste de Disponibilidade:** Tentar invocar `write_todos` com uma tarefa fake.
2. **Teste de Integração:** Criar um pequeno projeto de teste e verificar se as tarefas aparecem no `Ctrl+T`.
3. **Teste de Foco:** Verificar se o subagente reconhece a tarefa ativa no CLI.

## 5. Riscos e Mitigações

- **Risco:** A ferramenta `write_todos` pode não estar habilitada na sessão atual (não consta no system prompt).
- **Mitigação:** Se falhar, manteremos o fluxo via `TODO.md` mas formatado de forma que o sistema Gemini CLI possa indexar (seguindo padrões de nomes do tutorial).
