# Spec: Main Guard — Bloqueio de Commits Diretos em main/master

**Data:** 2026-06-02
**Status:** Aprovada (pronta para implementação)
**Autor:** Brainstorming colaborativo Victor + Claude

---

## 1. Objetivo

Impedir que LLMs e usuários façam commits diretos nas branches `main` ou `master` de qualquer repositório do ecossistema Stout/Inova, com válvula de escape via footer da mensagem de commit.

**Problema raiz:** O `branch_policy_validator.py` isenta explicitamente `main`/`master` (`return 0`) para não bloquear merges legítimos. Essa isenção cria o gap: trabalho iniciado diretamente em `main` passa pelo hook sem bloqueio.

---

## 2. Requisitos

### Funcionais

- **RF-01:** Qualquer commit em `main` ou `master` deve ser bloqueado por padrão.
- **RF-02:** O bloqueio deve ser bypassável via footer `Allow-Main: true` na mensagem de commit.
- **RF-03:** A mensagem de erro deve orientar o usuário sobre como liberar o commit.
- **RF-04:** Commits em qualquer outra branch não devem ser afetados.
- **RF-05:** O `branch_policy_validator.py` não deve ser modificado.
- **RF-06:** O `pre-commit` hook não deve ser modificado.

### Não-funcionais

- **RNF-01:** Compatibilidade total com Windows (Python nativo, sem Bash).
- **RNF-02:** Encoding UTF-8 explícito em todas as leituras de arquivo.
- **RNF-03:** A mudança deve ser aplicada em 5 arquivos: 1 template + 4 hooks ativos.
- **RNF-04:** O novo arquivo de teste deve entrar no mesmo commit que o template.

---

## 3. Arquitetura

### Hook afetado: `commit-msg`

O `commit-msg` é o único hook com acesso garantido ao arquivo de mensagem em todos os cenários (`git commit -m "..."` e `git commit` interativo).

### Bloco a adicionar (topo do hook, antes da delegação ao validator)

```python
# ── MAIN GUARD ──────────────────────────────────────────────────
_msg = Path(sys.argv[1]).read_text(encoding="utf-8")
_branch = subprocess.run(
    ["git", "branch", "--show-current"],
    capture_output=True, text=True, encoding="utf-8",
).stdout.strip()

if _branch in ("main", "master") and "Allow-Main: true" not in _msg:
    print(
        "\n[main-guard] BLOQUEADO: commits diretos em 'main' não são permitidos.\n"
        "  Para liberar, adicione ao footer do commit:\n\n"
        "    Allow-Main: true\n",
        file=sys.stderr,
    )
    sys.exit(1)
# ── FIM MAIN GUARD ───────────────────────────────────────────────
```

### Arquivos modificados (ordem de deploy)

| # | Arquivo | Rastreado pelo git |
|---|---|---|
| 1 | `templates/cdd/hooks/commit-msg` | Sim — entra no commit |
| 2 | `.git/hooks/commit-msg` (CDD) | Não — deploy local |
| 3 | `C:\Projetos\Stout\.git\hooks\commit-msg` | Não — deploy local |
| 4 | `C:\Projetos\Inova\.git\hooks\commit-msg` | Não — deploy local |
| 5 | `C:\Projetos\Stout\Projetos\NotebookLM\.git\hooks\commit-msg` | Não — deploy local |

### Exemplo de uso legítimo do escape hatch

```
chore: bump version para 1.2.0

Release manual direto na main por ausência de CI neste repo.

Allow-Main: true
```

---

## 4. Validação (Plano de Testes)

### Teste 1 — Unitário: `tests/test_commit_msg_guard.py` (novo arquivo)

| Cenário | Branch | Footer | Saída esperada |
|---|---|---|---|
| Commit em main sem escape | `main` | ausente | `exit 1` |
| Commit em main com escape | `main` | `Allow-Main: true` | `exit 0` |
| Commit em feature branch | `feat/x-y` | ausente | `exit 0` |
| Commit em master sem escape | `master` | ausente | `exit 1` |

### Teste 2 — Integração (hook ativo no CDD)

1. Stagear qualquer arquivo no CDD (em `main`)
2. Tentar `git commit -m "test: tentativa"` → deve bloquear com mensagem `[main-guard]`
3. Tentar `git commit -m "test: tentativa\n\nAllow-Main: true"` → deve passar

### Teste 3 — Regressão

```powershell
python -m pytest tests/ -q
```

**Critério de aceite:** 80 testes existentes + N novos do guard, todos verdes.

---

## 5. Assumptions

- `git branch --show-current` retorna string vazia em estado de detached HEAD — o guard não bloqueia nesse caso (branch não é `main`/`master`).
- O escape hatch `Allow-Main: true` é case-sensitive.
- Repos sem `commit-msg` instalado continuam sem proteção — o deploy manual nos 4 repos ativos resolve os casos produtivos.

---

## 6. Decision Log

| Decisão | Alternativas consideradas | Motivo da escolha |
|---|---|---|
| Escape via footer da mensagem | Variável de ambiente; flag no subject | Footer segue Conventional Commits; não polui `git log --oneline`; sinaliza intencionalidade |
| Implementar no `commit-msg` (não `pre-commit`) | `pre-commit` com leitura de `COMMIT_EDITMSG` | `pre-commit` não tem acesso à mensagem em commits interativos; `commit-msg` tem acesso garantido sempre |
| Não modificar `branch_policy_validator.py` | Adicionar modo `--commit-msg-file` ao validator | Mantém separação de responsabilidades; validator faz subprojeto, guard faz main |
| Opção A: inline no hook | Opção B: nova função no validator; Opção C: `commit_guard.py` intermediário | Menor mudança possível, sem novas dependências, template centraliza a fonte canônica |
| Scope: todos os 4 repos + template | Apenas repos isolados (CDD, NotebookLM) | Proteção uniforme em todo o ecossistema |
