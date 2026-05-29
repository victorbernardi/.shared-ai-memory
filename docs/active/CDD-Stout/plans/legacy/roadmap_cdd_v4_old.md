# Roadmap CDD - Stout Inova [LEGACY]

## Visão Geral

O projeto **Configuration-Driven Development (CDD)** visa padronizar a criação de soluções no ecossistema Stout Lab, separando regras de negócio de scripts de execução.

## Roadmap V1.0: Fundações (Concluído)

- [x] Estruturação do repositório base.
- [x] Implementação do `Shared Core` (engine.py).
- [x] Definição de Schemas JSON para validação.

## Roadmap V2.0: Inteligência & Escala (Concluído)

- [x] Implementação do `SkillRouter` com *Progressive Disclosure*.
- [x] Sistema de Hot-Reload para regras em `rules.yaml`.
- [x] Integração com Padrão de Pasta de Skills.

## Roadmap V3.0: Hardening & QA (Em Andamento)

- [x] Correção de anomalias e erros silenciosos.
- [x] Implementação de Fallback Inteligente.
- [x] Integração do repositório no `Context Agent` global.
- [ ] Implementar **Skill Sandboxing** para isolamento de comandos (Em Standby).

---

## Roadmap V4.0: Cognição, Simulação e Rastreabilidade Global (Proposta)

### Fase 4.1: O Rule Simulator (Simulador BDD)

Criar uma ferramenta nativa (`rule_simulator.py`) que permita testar o comportamento do motor de regras sem precisar engajar o LLM. 

- **Por quê?** Atualmente testamos regras via LLM. Ter um simulador Behavior-Driven Development (BDD) permite rodar testes de regressão automáticos em milissegundos.
- **O que envolve?** Injeção de contextos (JSON) via CLI para verificar qual *intent* e *skill* o `engine.py` resolve.

### Fase 4.2: Sincronização Ativa com Context Agent Global

O sistema atual notifica o Context Agent, mas de forma passiva. 

- **Por quê?** Para não perdermos histórico entre múltiplas sessões, o CDD deve poder não apenas enviar, mas consultar o banco SQLite FTS5 do Context Agent antes de tomar decisões complexas.
- **O que envolve?** Expandir o `gcc_controller.py` para consultar `context_manager.py search` ativamente, usando erros do passado para evitar cometer os mesmos erros no presente.

### Fase 4.3: Analytics Dashboard (HTML/Terminal)

Evoluir o `gcc_analytics.py` de um log de texto para um painel gerencial.

- **Por quê?** Para facilitar a vida dos engenheiros da Stout Inova. Precisamos visualizar "Intenções Órfãs" e taxas de falha graficamente para vender o valor do CDD.
- **O que envolve?** Um gerador de relatório HTML simples em `src/tools/` que consolide os dados do GCC.

### Fase 4.4: Arquitetura de Eventos (Hooks CDD)

Implementar "pré" e "pós" ações nas regras do `rules.yaml`.

- **Por quê?** Às vezes precisamos rodar um script *antes* da skill ser ativada (ex: buscar um token) ou *depois* (ex: disparar um webhook).
- **O que envolve?** Adicionar campos `pre_action` e `post_action` no schema de regras and no `engine.py`.
