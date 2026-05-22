# Spec: Separação de Memória (CLI vs Antigravity)

## Objetivo
Desacoplar o arquivo `GEMINI.md` (usado nativamente pelo wrapper Gemini CLI para persistência de fatos e telemetria) da documentação de contexto de projeto e regras de negócio do **Antigravity**.

## Problema Atual
O arquivo `GEMINI.md` está sendo usado como a "Bíblia do Projeto" (Contexto, Stack, Regras Críticas). No entanto, o Gemini CLI (wrapper) pode tentar utilizar esse mesmo arquivo para salvar memórias automáticas (`save_memory`), gerando conflito de responsabilidades e poluição de contexto.

## Arquitetura de Memória Proposta

| Camada | Arquivo | Responsabilidade | Gestão |
|--------|---------|------------------|--------|
| **CLI (Nativo)** | `GEMINI.md` | Fatos aprendidos pelo wrapper, telemetria e estado de baixo nível da ferramenta. | Gemini CLI (`save_memory`) |
| **Projeto (Human-Readable)** | `ANTIGRAVITY.md` | "Bíblia do Projeto": Visão geral, Stack, Regras Críticas, Estrutura de Pastas e Comportamento Esperado. | Humano / Agente (Manual) |
| **Sessão (Agente)** | `MEMORY.md` | Continuidade entre sessões: Tarefas pendentes, decisões recentes e histórico de conversas. | `context-agent` (Automático) |

## Mudanças Necessárias
1. Renomear o atual `c:\Projetos\Inova\GEMINI.md` para `c:\Projetos\Inova\ANTIGRAVITY.md`.
2. Criar um novo `GEMINI.md` limpo (ou deixar o CLI criá-lo) para uso exclusivo do wrapper.
3. Atualizar as referências de "Contexto de Projeto" nas skills para apontarem para `ANTIGRAVITY.md`.

## Critérios de Sucesso
- `GEMINI.md` livre para telemetria nativa do CLI.
- `ANTIGRAVITY.md` consolidado como a fonte de verdade para regras de negócio e arquitetura Stout.
- Nenhuma perda de informação durante a migração.
