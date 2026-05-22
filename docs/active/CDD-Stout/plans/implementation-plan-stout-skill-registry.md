# Implementation Plan: stout-skill-registry

> **Status:** Brainstorming Concluído / Em Planejamento
> **Data:** 2026-05-15
> **Versão:** 1.0.0

## 1. Visão Geral
Implementação da primeira peça do Ecossistema de Elite Stout: o `stout-skill-registry`. Esta skill atuará como um ledger (livro-razão) de metadados, garantindo que o ecossistema tenha uma fonte única de verdade sobre as habilidades instaladas e suas interdependências.

## 2. Requisitos Validados
- **Banco de Metadados Simples:** `registry.json` na raiz da skill.
- **Automação com HITL:** A `stout-create-skill` chama o registro ao final da manufatura, exigindo aprovação explícita do usuário.
- **Consulta de Impacto:** Suporte para verificar dependências antes de qualquer ação (query_registry.py com suporte a impacto).
- **Consistência:** Operado pela IA (ou pelo usuário em modo CLI).

## 3. Estrutura de Arquivos
```
skills/stout-skill-registry/
├── SKILL.md                  # Orquestração e governança
├── registry.json             # DB de metadados (Ledger)
├── schemas/
│   └── skill_entry.schema.json
├── scripts/
│   ├── register_skill.py     # Registro e bump de versão
│   ├── query_registry.py     # Busca e consulta de impacto
│   └── deregister_skill.py   # Depreciação com histórico
└── references/
    └── versioning_guide.md
```

## 4. Fluxo de Implementação (Passo a Passo)

### Fase A: Estruturação
1. Criar diretórios da `stout-skill-registry`.
2. Escrever o `registry.json` com a entrada inicial da própria skill.
3. Criar o schema `skill_entry.schema.json` para garantir integridade.

### Fase B: Lógica de Registro (register_skill.py)
1. Implementar `register_skill.py`:
   - Validar prefixo `stout-`.
   - Garantir unicidade do `role`.
   - Implementar versionamento SemVer (patch/minor/major).
   - Validar contra schema.

### Fase C: Lógica de Consulta e Impacto (query_registry.py)
1. Implementar `query_registry.py`:
   - Suporte a filtros (nome, categoria, trigger).
   - **Novo:** Função de impacto: ao consultar uma skill, listar quais outras skills a apontam como `dependency`.

### Fase D: Depreciação (deregister_skill.py)
1. Implementar `deregister_skill.py`:
   - Bloquear exclusão física.
   - Mover para lista `deprecated` com motivo.

### Fase E: Finalização
1. Registrar a própria `stout-skill-registry` usando o script recém-criado.
2. Validar integridade com o quality gate definido.

## 5. Testes e Validação
- **Teste 1:** Registrar uma skill fictícia (`stout-teste-1`) e verificar o arquivo `registry.json`.
- **Teste 2:** Tentar registrar `stout-teste-2` com o mesmo `role` de `stout-teste-1` e validar a rejeição.
- **Teste 3:** Consultar o impacto da `stout-skill-registry` e confirmar se ela aparece como dependência.
- **Teste 4:** Deprecar `stout-teste-1` e validar a mudança de estado e preservação do histórico.

---
*Assinado: Arquiteto Stout Inova*
