# sdd-cmdc-opencode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar, testar, registrar e instalar `sdd-cmdc-opencode`, uma skill SDD que mantém a implementação via Command Code e substitui todas as revisões Codex por Open Code Review em modo delegado.

**Architecture:** A nova skill será uma cópia independente dos componentes de implementação de `skills/sdd-cmdc`, sem copiar os prompts de reviewer Codex. Seu `SKILL.md` exigirá `open-code-review-delegate` para selecionar arquivos, resolver regras e conduzir as revisões no agente host. O OCR não receberá endpoint, API key ou chamada LLM; a fonte canônica será `skills/sdd-cmdc-opencode`, e as cópias físicas só serão sincronizadas após a validação.

**Tech Stack:** Markdown/YAML de Agent Skills, Python 3, `pytest`, Codex CLI, Open Code Review CLI `ocr`, PowerShell/Windows e Git.

## Global Constraints

- Não modificar `skills/sdd-cmdc`, `skills/subagent-driven-development` ou qualquer cópia existente dessas skills.
- O implementador continua sendo executado exclusivamente por `scripts/cmdc-implementer.py` via Command Code; não existe fallback de implementação para Codex.
- Toda revisão usa `open-code-review-delegate`, `ocr delegate preview` e `ocr delegate rule`; não usar `ocr review`, `ocr llm test`, `OCR_LLM_*` ou `OPENAI_API_KEY`.
- O host Codex executa a análise sem transformar a assinatura ChatGPT Pro em credencial de API.
- Falha do OCR, falha de `preview`/`rule`, escopo parcial, timeout ou evidência ausente é `BLOCKED` ou `REVIEW INCOMPLETE`, nunca aprovação.
- Cada revisão deve registrar escopo, arquivos excluídos, regras, comandos, exit codes, achados e estado final.
- A revisão deve usar o range exato informado pelo plano: `BASE`, `FIX_BASE`, merge-base, commit ou workspace explicitamente escolhido; nunca inferir o range com `HEAD~1`.
- A nova skill não publica comentários automaticamente no GitHub.
- A fonte canônica é `C:\Users\victor.bernardi\.shared-ai-memory\skills\sdd-cmdc-opencode`; os destinos físicos são `.agents\skills\sdd-cmdc-opencode` e `.codex\skills\sdd-cmdc-opencode`.
- Toda alteração rastreada será commitada na branch `feat/sdd-cmdc-opencode`; não executar merge, push ou reset destrutivo.
- As cópias físicas externas não serão adicionadas ao commit do repositório.

---

## File Map

| Caminho | Responsabilidade |
| --- | --- |
| `skills/sdd-cmdc-opencode/SKILL.md` | Workflow SDD com revisão delegada por tarefa, re-revisão e revisão final |
| `skills/sdd-cmdc-opencode/implementer-prompt.md` | Contrato do implementador Command Code, copiado sem mudança funcional |
| `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py` | Adaptador Command Code, copiado sem mudança funcional |
| `skills/sdd-cmdc-opencode/scripts/sdd-workspace` | Resolução do workspace por plano |
| `skills/sdd-cmdc-opencode/scripts/task-brief` | Extração do brief de cada tarefa |
| `skills/sdd-cmdc-opencode/scripts/review-package` | Geração de evidência do diff |
| `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py` | Regressão do adaptador copiado |
| `skills/sdd-cmdc-opencode/tests/test_skill_contract.py` | Contrato estrutural, proibições e paridade |
| `skills/sdd-cmdc-opencode/tests/pressure/` | Cenários de pressão para OCR, credencial, timeout e escopo |
| `skills/sdd-cmdc-opencode/audit_result.json` | Auditoria aprovada da nova skill |
| `skills/stout-skill-registry/registry.json` | Registro ativo de `sdd-cmdc-opencode` |
| `docs/superpowers/specs/2026-08-01-sdd-cmdc-opencode-design.md` | Design aprovado |
| `docs/superpowers/plans/2026-08-01-sdd-cmdc-opencode.md` | Este plano |

Não serão criados `task-reviewer-prompt.md` nem `re-review-prompt.md`: esses prompts representam a revisão Codex que esta skill substitui.

---

### Task 1: Criar contrato RED e cenários de pressão

**Files:**
- Create: `skills/sdd-cmdc-opencode/tests/__init__.py`
- Create: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`
- Create: `skills/sdd-cmdc-opencode/tests/pressure/api-key-fallback.md`
- Create: `skills/sdd-cmdc-opencode/tests/pressure/ocr-timeout.md`
- Create: `skills/sdd-cmdc-opencode/tests/pressure/partial-preview.md`
- Create: `skills/sdd-cmdc-opencode/tests/pressure/dirty-workspace.md`
- Create: `skills/sdd-cmdc-opencode/tests/pressure/finding-fix-round.md`

**Interfaces:**
- `test_skill_contract.py` deve calcular `REPO_ROOT = Path(__file__).resolve().parents[3]` e `SKILL = REPO_ROOT / "skills" / "sdd-cmdc-opencode"`.
- A Task 3 deverá fazer todos os testes passarem sem alterar os testes para acomodar a implementação.

- [ ] **Step 1: Escrever os testes estruturais que começam falhando**

  O teste deve verificar, usando `read_text(encoding="utf-8")`, que `SKILL.md` contém `name: sdd-cmdc-opencode`, descrição iniciada por `Use when`, `open-code-review-delegate`, `ocr delegate preview`, `ocr delegate rule`, `REVIEW INCOMPLETE`, `BLOCKED`, `FIX_BASE` e a exigência de não usar fallback de revisão Codex. Também deve exigir que os arquivos de implementação existam e que `task-reviewer-prompt.md` e `re-review-prompt.md` não existam no novo diretório.

- [ ] **Step 2: Adicionar testes para cópia e não mutação**

  Exigir que os digests SHA-256 de `cmdc-implementer.py`, `implementer-prompt.md`, `sdd-workspace`, `task-brief` e `review-package` sejam iguais aos correspondentes de `skills/sdd-cmdc`. Executar `git diff --name-only -- skills/sdd-cmdc skills/subagent-driven-development` e exigir saída vazia.

- [ ] **Step 3: Escrever os cinco cenários de pressão**

  Cada arquivo deve conter pressão, atalho proibido, evidência obrigatória e linha de ledger esperada. Cobrir: API key ausente com pedido para chamar `ocr review`; timeout de `ocr delegate preview`; preview parcial com arquivo excluído; workspace sujo com artefatos; e finding que exige uma rodada de correção e re-revisão.

- [ ] **Step 4: Executar RED antes de criar a skill**

  ```powershell
  python -m pytest skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
  ```

  Expected: falha porque `skills/sdd-cmdc-opencode/SKILL.md` e os arquivos de implementação ainda não existem. Não criar a skill operacional para tornar o RED verde nesta tarefa.

- [ ] **Step 5: Rodar o controle de pressão sem a nova skill**

  Para cada cenário, usar uma sessão Codex efêmera, sem instalar/carregar `sdd-cmdc-opencode`, em modo somente leitura:

  ```powershell
  codex exec --ephemeral --sandbox read-only --cd "C:\Users\victor.bernardi\.shared-ai-memory\.worktrees\feat-sdd-cmdc-opencode" "Leia um cenário em skills/sdd-cmdc-opencode/tests/pressure/SCENARIO_FILE e descreva como executaria a revisão. Não use a skill sdd-cmdc-opencode."
  ```

  Registrar as decisões observadas em `.superpowers/sdd/2026-08-01-sdd-cmdc-opencode-baseline-pressure.md`, que deve permanecer ignorado e fora do commit. O baseline serve para capturar tentativas de usar API, aceitar escopo parcial ou substituir OCR por revisão Codex.

- [ ] **Step 6: Commitar o contrato RED**

  ```powershell
  git add skills/sdd-cmdc-opencode/tests
  git commit -m "test: define sdd-cmdc-opencode contract"
  ```

### Task 2: Copiar os componentes de implementação sem alterar `sdd-cmdc`

**Files:**
- Create: `skills/sdd-cmdc-opencode/SKILL.md` (placeholder mínimo somente após o RED)
- Create: `skills/sdd-cmdc-opencode/implementer-prompt.md`
- Create: `skills/sdd-cmdc-opencode/scripts/__init__.py`
- Create: `skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py`
- Create: `skills/sdd-cmdc-opencode/scripts/sdd-workspace`
- Create: `skills/sdd-cmdc-opencode/scripts/task-brief`
- Create: `skills/sdd-cmdc-opencode/scripts/review-package`
- Create: `skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py`

**Interfaces:**
- Preservar os comandos `sdd-workspace PLAN_FILE`, `task-brief PLAN_FILE TASK_NUMBER [OUTFILE]` e `review-package PLAN_FILE BASE HEAD [OUTFILE]` exatamente.
- Preservar `build_command`, `resolve_cmdc`, `classify_failure`, `render_blocked` e `run_implementer` do adaptador existente.
- O novo workflow só adiciona comportamento em `SKILL.md`; nenhum script copiado deve ser reformatado ou alterado.

- [ ] **Step 1: Copiar os arquivos exatos**

  ```powershell
  $source = "C:\Users\victor.bernardi\.shared-ai-memory\.worktrees\feat-sdd-cmdc-opencode\skills\sdd-cmdc"
  $target = "C:\Users\victor.bernardi\.shared-ai-memory\.worktrees\feat-sdd-cmdc-opencode\skills\sdd-cmdc-opencode"
  New-Item -ItemType Directory -Force -Path "$target\scripts" | Out-Null
  Copy-Item "$source\implementer-prompt.md" "$target\implementer-prompt.md"
  Copy-Item "$source\scripts\__init__.py" "$target\scripts\__init__.py"
  Copy-Item "$source\scripts\cmdc-implementer.py" "$target\scripts\cmdc-implementer.py"
  Copy-Item "$source\scripts\sdd-workspace" "$target\scripts\sdd-workspace"
  Copy-Item "$source\scripts\task-brief" "$target\scripts\task-brief"
  Copy-Item "$source\scripts\review-package" "$target\scripts\review-package"
  Copy-Item "$source\tests\test_cmdc_implementer.py" "$target\tests\test_cmdc_implementer.py"
  ```

- [ ] **Step 2: Executar a regressão do adaptador**

  ```powershell
  python -m pytest skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py -q
  python -m py_compile skills/sdd-cmdc-opencode/scripts/cmdc-implementer.py
  ```

  Expected: todos os testes do adaptador passam e a compilação retorna `0`.

- [ ] **Step 3: Confirmar paridade e não mutação**

  ```powershell
  git diff --check
  git diff --name-only -- skills/sdd-cmdc skills/subagent-driven-development
  ```

  Expected: nenhum arquivo das skills existentes aparece no diff.

- [ ] **Step 4: Commitar o scaffold**

  ```powershell
  git add skills/sdd-cmdc-opencode/implementer-prompt.md skills/sdd-cmdc-opencode/scripts skills/sdd-cmdc-opencode/tests/test_cmdc_implementer.py
  git commit -m "feat: add sdd-cmdc-opencode implementation scaffold"
  ```

### Task 3: Implementar o workflow de revisão delegada

**Files:**
- Modify: `skills/sdd-cmdc-opencode/SKILL.md`
- Modify: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`

**Interfaces:**
- O frontmatter deve ser exatamente `name: sdd-cmdc-opencode` e a descrição deve iniciar com `Use when` e descrever somente os gatilhos.
- O workflow deve exigir `open-code-review-delegate` como subskill para cada revisão.
- Cada revisão deve usar `ocr delegate preview` e depois `ocr delegate rule PATHS`; os diffs devem ser obtidos conforme `mode`, `merge_base`, `commit` e `to` retornados pelo preview.
- O relatório deve conter `Files reviewed`, `Excluded files`, `Commands`, `Exit codes`, `Critical/High`, `Medium`, `Review status` e recomendações com `path`, `start_line` e `end_line`.

- [ ] **Step 1: Escrever a skill com o contrato de revisão**

  Preservar no `SKILL.md` a sequência de worktree, ledger, brief, implementação, relatório e fix loop de `sdd-cmdc`. Substituir as três etapas Codex por este fluxo textual obrigatório:

  ```text
  1. Generate the review package with the exact BASE or FIX_BASE.
  2. Run `ocr delegate preview` for that exact repository and range.
  3. Stop as BLOCKED if preview fails or the scope is incomplete.
  4. Run `ocr delegate rule` for every reviewable path, in batches if needed.
  5. Read each exact diff and its resolved rule group.
  6. Review and report findings in the delegated Open Code Review format.
  7. Treat Critical/High as blocking and run a fresh Command Code fix round.
  8. Re-run only the fix range through delegated preview/rule/diff review.
  ```

  Incluir explicitamente que `ocr review`, `ocr llm test`, `OCR_LLM_*` e `OPENAI_API_KEY` não podem ser executados, e que o agente não pode substituir OCR por uma revisão Codex comum quando OCR falhar.

- [ ] **Step 2: Documentar os estados de governança**

  Definir `BLOCKED`, `REVIEW INCOMPLETE` e `REVIEW CLEAN` com os mesmos significados da especificação. Timeout, preview parcial, arquivo excluído sem justificativa ou regra não resolvida nunca podem produzir aprovação.

- [ ] **Step 3: Documentar o loop de cinco rodadas**

  Manter o limite de cinco rodadas, o implementador Command Code novo em cada rodada, a exigência de testes no relatório, o re-review delegado escopado e o estacionamento com ruling somente no breaker. O controller nunca edita diretamente.

- [ ] **Step 4: Tornar os testes estruturais verdes**

  Adicionar asserções para: `open-code-review-delegate`; comandos `ocr delegate preview` e `ocr delegate rule`; ausência de prompts Codex; ausência de configuração LLM executável; states de falha; regras de escopo; e preservação das skills existentes.

  ```powershell
  python -m pytest skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
  ```

- [ ] **Step 5: Commitar o workflow**

  ```powershell
  git add skills/sdd-cmdc-opencode/SKILL.md skills/sdd-cmdc-opencode/tests/test_skill_contract.py
  git commit -m "feat: replace Codex reviews with delegated OCR"
  ```

### Task 4: Registrar, auditar e executar a verificação com a skill

**Files:**
- Create: `skills/sdd-cmdc-opencode/audit_result.json`
- Modify: `skills/stout-skill-registry/registry.json`
- Modify: `skills/sdd-cmdc-opencode/tests/test_skill_contract.py`
- Modify: `skills/sdd-cmdc-opencode/tests/pressure/*.md` only if the RED baseline exposes a missing case

**Interfaces:**
- Registro: `name: "sdd-cmdc-opencode"`, `path: "skills/sdd-cmdc-opencode"`, `tier: 4`, `category: "meta-factory"`, `status: "active"`.
- Triggers: `sdd-cmdc-opencode`, `open-code-review`, `revisão delegada`, `revisão por tarefa`, `executar plano`.
- Notes: `Implementador via cmdc; revisão por tarefa, re-review e revisão final via Open Code Review Delegation Mode; sem OPENAI_API_KEY.`
- Auditoria: `verdict: "APPROVED"`, `proposed_name: "sdd-cmdc-opencode"`, tier `4`, com papel correspondente ao workflow delegado.

- [ ] **Step 1: Criar o artefato de auditoria sem tocar nos artefatos antigos**

  Escrever JSON válido em `skills/sdd-cmdc-opencode/audit_result.json`; não sobrescrever `audit_result.json` da raiz nem o de `skills/sdd-cmdc`.

- [ ] **Step 2: Adicionar registro único e validar JSON**

  Inserir exatamente um objeto ativo para `sdd-cmdc-opencode`, preservar a entrada `sdd-cmdc` e validar com:

  ```powershell
  $null = Get-Content skills/stout-skill-registry/registry.json -Raw | ConvertFrom-Json
  python -m pytest skills/sdd-cmdc-opencode/tests/test_skill_contract.py -q
  ```

- [ ] **Step 3: Repetir os cenários com a skill carregada**

  Usar uma nova sessão Codex por cenário, instruindo explicitamente o uso de `$sdd-cmdc-opencode`. Verificar que API-key pressure produz `BLOCKED`, timeout produz `REVIEW INCOMPLETE`, preview parcial não é aprovação, workspace sujo é escopado e finding dispara fix round + delegated re-review.

- [ ] **Step 4: Executar validações locais**

  ```powershell
  python -m pytest skills/sdd-cmdc-opencode/tests -q
  git diff --check
  rg -n "OPENAI_API_KEY|OCR_LLM_|ocr review|ocr llm test" skills/sdd-cmdc-opencode/SKILL.md
  ```

  Expected: a busca encontra somente as proibições documentadas, nunca comandos executáveis de configuração/call LLM; a suíte e `git diff --check` passam.

- [ ] **Step 5: Commitar governança e auditoria**

  ```powershell
  git add skills/sdd-cmdc-opencode/audit_result.json skills/stout-skill-registry/registry.json skills/sdd-cmdc-opencode/tests
  git commit -m "chore: register and audit sdd-cmdc-opencode"
  ```

### Task 5: Sincronizar os destinos físicos e fechar a validação

**Files:**
- Create/update only: `C:\Users\victor.bernardi\.agents\skills\sdd-cmdc-opencode\`
- Create/update only: `C:\Users\victor.bernardi\.codex\skills\sdd-cmdc-opencode\`
- Do not modify: `skills/sdd-cmdc`, `skills/subagent-driven-development`, or unrelated runtime skills

**Interfaces:**
- Os destinos devem ter os mesmos caminhos relativos e SHA-256 da fonte canônica.
- Nenhum destino pode conter `.git` copiado.
- O conteúdo anterior de outras skills deve permanecer inalterado.

- [ ] **Step 1: Validar as ferramentas antes de copiar**

  ```powershell
  ocr version
  ocr delegate preview --help
  ocr delegate rule --help
  codex plugin list | Select-String 'open-code-review-codex'
  ```

  Expected: OCR v1.8.4 ou superior, subcomandos de delegação disponíveis e plugin Codex habilitado. A ausência do plugin ou do CLI é `BLOCKED`, não motivo para instalar uma cópia incompleta.

- [ ] **Step 2: Copiar somente a nova skill**

  Resolver os destinos com caminho absoluto, validar que são exatamente os diretórios sob o perfil do usuário, remover somente um destino anterior de `sdd-cmdc-opencode` se ele existir e copiar o diretório canônico inteiro. Não usar `Copy-Item` sobre a pasta pai de todas as skills.

- [ ] **Step 3: Verificar paridade e descoberta**

  Comparar caminhos relativos recursivos, SHA-256 de todos os arquivos e presença de `SKILL.md` nos dois destinos. Verificar que o frontmatter contém `sdd-cmdc-opencode`, que não há `.git` e que `codex plugin list` continua com `open-code-review-codex` habilitado.

- [ ] **Step 4: Executar verificação final da branch**

  ```powershell
  python -m pytest skills/sdd-cmdc-opencode/tests -q
  git diff --check
  git status --short
  git log --oneline --decorate -5
  ```

  Confirmar que o branch contém somente os commits desta feature, que as skills antigas não têm diff e que os destinos externos têm hash parity. Não commitar cópias externas.

---

## Final Verification

```powershell
python -m pytest skills/sdd-cmdc-opencode/tests -q
git diff --check
git diff --name-only -- skills/sdd-cmdc skills/subagent-driven-development
ocr version
ocr delegate preview --help
ocr delegate rule --help
```

Confirmar manualmente:

- `sdd-cmdc` não foi alterada;
- `sdd-cmdc-opencode` não contém prompts de reviewer Codex;
- o implementador continua usando apenas Command Code;
- todos os reviews passam por `preview` → `rule` → diff → relatório delegado;
- nenhuma configuração `OPENAI_API_KEY` é necessária;
- timeout, escopo parcial e falha de OCR não são aprovação;
- os destinos `.agents` e `.codex` são byte-equivalentes à fonte canônica.
