# Especificação Técnica: Unificação da Arquitetura de Memória Stout

| Campo | Valor |
|---|---|
| **Data** | 2026-05-12 |
| **Status** | ✅ Aprovado |
| **Autor** | Gemini CLI Builder |
| **Versão** | 1.0 |

---

## 1. Objetivo
Estabelecer um padrão único e imutável para a documentação e memória dos projetos no ecossistema Antigravity (Gemini, Claude, OpenCode), eliminando fragmentações de diretórios e nomenclatura legada.

## 2. Requisitos Funcionais

### 2.1. Memória Global (Junctions)
- Todo projeto DEVE possuir a pasta `docs/` como um **Junction** (Windows) ou **Symlink** (Unix) apontando para `~/.shared-ai-memory/docs/<nome-projeto>`.
- Caso a pasta física local já exista, o conteúdo deve ser migrado para a memória global antes de estabelecer o link (Protocolo Zero Ponto Cego).

### 2.2. Taxonomia Claude
- A nomenclatura `superpowers` está oficialmente **DEPRECIADA**.
- O Claude deve salvar planos em `docs/plans/` e especificações em `docs/specs/`.
- Skills de planejamento (`writing-plans`, `executing-plans`) não devem utilizar o prefixo `superpowers:`.

### 2.3. Promoção de Artefatos Gemini
- Planos gerados na pasta `tmp` do Gemini CLI devem ser promovidos automaticamente para `docs/plans/` do projeto ativo via `stout_promote.py`.

### 2.4. Unificação de Código (SRC)
- A pasta raiz `scripts/` está **DEPRECIADA**.
- Ferramentas de automação e Stout residirão em `src/tools/`.
- O scaffold do `stout-init` refletirá essa estrutura.

## 3. Arquitetura Proposta

### Nova Hierarquia de Pastas
```text
[Projeto]/
├── GEMINI.md              # Regras de negócio
├── ANTIGRAVITY.md         # Regras técnicas
├── docs/ → junction       # Memória Global
│   ├── specs/             # Especificações Técnicas (Imutáveis)
│   ├── plans/             # Planos de Implementação (Versionados)
│   ├── walkthroughs/      # Manuais de execução
│   └── business/          # Documentos de negócio
├── src/
│   ├── tools/             # Automações e scripts Stout
│   └── core/              # Lógica da aplicação
└── tests/                 # Validações TDD
```

## 4. Plano de Validação
1. **Teste de Migração:** Verificar se `Historico-de-Vendas/docs` é agora um junction funcional.
2. **Teste de Promoção:** Executar `python src/tools/stout_promote.py` e confirmar captura de planos da pasta `tmp`.
3. **Audit de Skills:** Garantir que nenhuma skill ativa referencia `superpowers:`.

---
*Assinado: Arquiteto de Design Agêntico*
