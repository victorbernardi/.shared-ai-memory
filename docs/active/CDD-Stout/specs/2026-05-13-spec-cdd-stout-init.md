# Especificação Técnica: Padrão CDD & Integração stout-init (Stout Edition)

**Data:** 2026-05-13  
**Status:** Aprovado em Brainstorming  
**Versão:** 1.0  
**Autor:** Gemini CLI & Victor Bernardi

---

## 1. Objetivo
Padronizar a criação de projetos no ecossistema Stout Lab utilizando **Configuration-Driven Development (CDD)**. O objetivo é desacoplar regras de negócio de scripts de execução, garantindo que a governança seja declarativa (JSON/YAML) e a infraestrutura seja resiliente a múltiplos ambientes (`C:\Projetos\Stout` e `C:\Projetos\Inova`).

## 2. Requisitos

### 2.1 Funcionais
- **Geração Automática:** O comando `stout-init` deve oferecer a opção de injetar a arquitetura CDD.
- **Níveis de Maturidade (Modularidade):**
    - **Nível 1 (Básico):** Geração de `src/config.py` com `PATHS` e `ENVIRONMENT`.
    - **Nível 2 (Regras):** Inclusão de suporte ao Motor de Regras (`BRE`) e Validação `JSON Schema`.
    - **Nível 3 (Agentes):** Inclusão do `Prompt Router` para orquestração de múltiplos agentes.
- **Motor Centralizado (Shared Core):** O código pesado do motor (filtros recursivos, loaders) deve residir em `C:\Projetos\Stout\scripts\core` para evitar duplicação.
- **Auto-Descoberta:** O `src/config.py` deve ser capaz de localizar o motor central de forma inteligente (local, vizinho, absoluto ou fallback por env).

### 2.2 Não-Funcionais
- **Performance:** Uso de `Pydantic Settings` para carregamento rápido e tipagem forte.
- **Segurança:** Bloqueio total de funções `eval()` ou `exec()` no motor de regras.
- **Resiliência:** Implementação de "Fail-fast" (o sistema trava se a configuração estiver inválida) e "Fail-safe hot-reload" (mantém a config anterior se a nova estiver corrompida).

## 3. Arquitetura de Pastas (Projeto Gerado)
```text
meu-projeto/
├── GEMINI.md           # Manual do Engenheiro
├── src/
│   ├── config.py       # Orquestrador de Configuração (Loader)
│   └── main.py         # Script de Execução (Opaco)
├── data/
│   └── config/         # Onde reside a "Alma" do projeto
│       ├── segment_rules.json   # Regras de Negócio (exemplo)
│       └── rules_catalog.yaml   # Catálogo de Ações
└── docs/
    └── specs/          # Documentação técnica
```

## 4. Estratégia de Validação (Plano de Testes)
1. **Teste de Localização:** Mover um projeto gerado da pasta `Stout` para `Inova` e verificar se o `src/config.py` continua carregando o motor corretamente.
2. **Teste de Integridade:** Editar um arquivo JSON de regras com erro de sintaxe e verificar se o `RulesConfigLoader` bloqueia a execução com uma mensagem de erro clara.
3. **Teste de Prioridade:** Criar duas regras conflitantes e validar se o motor respeita o campo `priority` corretamente.

## 5. Log de Decisões (Brainstorming)
- **Decisão:** Uso de Referência Global (Shared Core) em vez de copiar o código para cada projeto.
- **Motivo:** Facilidade de manutenção e atualização da "Golden Copy".
- **Decisão:** Implementação modular via `stout-init`.
- **Motivo:** Evitar complexidade desnecessária em projetos simples (YAGNI).
- **Decisão:** Busca de caminhos por Hierarquia de Descoberta.
- **Motivo:** Garantir que projetos em `Inova` e `Stout` funcionem sem configuração manual de variáveis de ambiente.

---
*Este documento encerra a fase de brainstorming e autoriza o início da fase de implementação.*
