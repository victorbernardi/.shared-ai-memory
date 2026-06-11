# Spec: Branch Policy Guard

**Data:** 2026-05-26
**Status:** Aprovado — pronto para implementação
**Origem:** Handoff `02_Faturamento/.handoff-branch-protection.md`

---

## 1. Objetivo

Impedir que commits de um subprojeto sejam feitos em branches pertencentes a outro projeto, cobrindo os 3 motores LLM (Claude, Antigravity, Gemini) e commits manuais no terminal.

**Root cause:** 3 commits do `02_Faturamento` foram feitos na branch `fix/stout-promote-antigravity-brain-path` porque o `stout-commit` só bloqueia `main`/`master`.

---

## 2. Requisitos

### Funcionais

- **RF1:** Git pre-commit hook bloqueia commit quando arquivos staged pertencem a um subprojeto mas a branch ativa não segue o padrão desse subprojeto
- **RF2:** Ao bloquear, exibe mensagem de erro clara com sugestão de branch correta derivada da branch atual (ex: `fix/stout-promote-*` → `feat/02-faturamento-stout-promote-*`)
- **RF3:** Detecção automática do subprojeto pelo caminho dos arquivos staged (ex: `pipelines/potencial-clientes/02_Faturamento/` → `02-faturamento`)
- **RF4:** `branch-policy.yaml` opcional por subprojeto para sobrescrever a convenção automática
- **RF5:** Inova — validação por arquivos staged vs. prefixo de branch
- **RF6:** Stout — validação apenas por nome de branch (cross-project por natureza); branch deve conter identificador do projeto Stout ativo
- **RF7:** Cobertura total: todos os subprojetos de Inova e Stout desde o início
- **RF8:** `stout-commit` atualizado para validar branch policy antecipadamente (feedback antes do hook)

### Não-funcionais

- **RNF1:** Script Python puro — sem dependências externas além da stdlib
- **RNF2:** Encoding UTF-8 explícito em todo I/O (padrão Windows do ecossistema)
- **RNF3:** Falha silenciosa se `.git/` não existir — nunca quebra o fluxo de desenvolvimento
- **RNF4:** Execução < 200ms — não impacta percepção do commit

---

## 3. Arquitetura

### Componentes

```text
stout-init/addons/cdd/
├── ADDON.md                           ← +seção Branch Policy (stitching)
└── templates/
    ├── branch_policy_validator.py     ← NOVO: lógica central
    ├── hooks/
    │   └── pre-commit                 ← NOVO: invoca o validator
    └── branch-policy.yaml.tpl         ← NOVO: template de policy

CDD Incubadora
└── templates/cdd/src/
    └── branch_policy_validator.py     ← espelho (fonte antes de promover)

Migração (execução única)
└── stout-migrate-branch-policy.py    ← instala hook + gera yamls nos 2 repos existentes
```text

### Fluxo de validação (Inova)

```text
git commit
  └── pre-commit hook
        └── branch_policy_validator.py
              ├── Lista arquivos staged (git diff --cached --name-only)
              ├── Detecta subprojeto pelo caminho
              ├── Lê branch-policy.yaml (se existir) ou usa convenção automática
              ├── Verifica se branch ativa contém o prefixo esperado
              ├── SE OK → exit 0 (commit prossegue)
              └── SE VIOLAÇÃO → exit 1 + mensagem + sugestão de branch
```text

### Convenção automática de nomes

| Diretório | Prefixo esperado na branch |
|-----------|---------------------------|
| `pipelines/potencial-clientes/02_Faturamento/` | `02-faturamento` |
| `pipelines/potencial-clientes/00_Motor_Identidade/` | `00-motor-identidade` |
| `projects/pricewatch-jd/` | `pricewatch-jd` |
| `projects/motor-cevap/` | `motor-cevap` |

Regra: nome do diretório em kebab-case lowercase.

### Propagação

- **Novos projetos:** `stout-init` Phase 3 → CDD addon → instala hook automaticamente
- **Projetos existentes:** `stout-migrate-branch-policy.py` (execução única manual)
- **Cobertura futura:** garantida pelo `stout-init` sem mudança adicional

---

## 4. Validação (Plano de Testes)

| Cenário | Esperado |
|---------|----------|
| Arquivos de `02_Faturamento` + branch `feat/02-faturamento-*` | Commit passa |
| Arquivos de `02_Faturamento` + branch `fix/stout-promote-*` | Bloqueado + sugestão `feat/02-faturamento-stout-promote-*` |
| Arquivos de `02_Faturamento` + branch `main` | Bloqueado (regra existente do stout-commit) |
| Arquivos mistos (shared/ + 02_Faturamento/) | Valida apenas o subprojeto detectado |
| Subprojeto sem `branch-policy.yaml` | Usa convenção automática |
| Subprojeto com `branch-policy.yaml` | Usa padrões do arquivo |
| Commit no Stout com branch sem identificador do projeto | Bloqueado + mensagem |

---

## 5. Decision Log

| Decisão | Alternativas | Motivo |
|---------|-------------|--------|
| Abordagem A: addon CDD | B (addon separado), C (git template global) | Todo projeto nasce via `stout-init` sem exceção — addon CDD é o ponto certo |
| Python puro no hook | Shell script | Padrão do ecossistema; resolve encoding no Windows |
| Convenção automática como padrão | Só YAML manual | Reduz atrito; YAML opcional para casos especiais |
| Stout: validação por nome de branch | Por arquivos staged | Stout é cross-project por natureza — arquivos não identificam o projeto |
| `stout-commit` atualizado como Camada 3 | Só hook | Feedback antecipado melhora UX sem duplicar lógica |

---

## 6. Suposições

- O nome do subprojeto é derivado automaticamente do diretório em kebab-case
- `branch-policy.yaml` sobrescreve a convenção automática quando presente
- O hook falha silenciosamente em repos sem `.git/`
- `caveman-commit` é coberto pelo hook (ele só gera mensagem, não executa o commit)
