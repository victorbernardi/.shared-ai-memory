# Plano: Branch Policy Guard

**Spec:** `docs/specs/2026-05-26-branch-policy-guard.md`
**Data:** 2026-05-26

---

## Tarefas

### TASK-01 — `branch_policy_validator.py` (lógica central)

Criar o script Python que valida branch vs. subprojeto.

- Detecta subprojeto pelos arquivos staged
- Lê `branch-policy.yaml` se existir, senão usa convenção automática
- Bloqueia com mensagem + sugestão de branch derivada da branch atual
- Destino: `templates/cdd/src/branch_policy_validator.py` (incubadora)

### TASK-02 — `pre-commit` hook

Criar o hook que invoca o validator.

- Script Python executável
- Destino: `templates/cdd/hooks/pre-commit`

### TASK-03 — `branch-policy.yaml.tpl`

Criar template de policy por subprojeto.

- Destino: `templates/cdd/hooks/branch-policy.yaml.tpl`

### TASK-04 — Promover para `stout-init` addon

Copiar os 3 arquivos para `stout-init/addons/cdd/templates/`.
Atualizar `ADDON.md` com instruções de instalação do hook.

### TASK-05 — `stout-migrate-branch-policy.py`

Script de migração para projetos existentes (Inova + Stout).

- Instala hook nos 2 repos
- Gera `branch-policy.yaml` para todos os subprojetos detectados
- Destino: `scripts/stout-migrate-branch-policy.py`

### TASK-06 — Atualizar `stout-commit`

Adicionar validação antecipada de branch policy na skill.

### TASK-07 — Executar migração

Rodar `stout-migrate-branch-policy.py` nos repos Inova e Stout.

### TASK-08 — Validação end-to-end

Testar os cenários da spec: commit correto passa, commit errado bloqueia com sugestão.
