# Inova Protheus Fabric SQL Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill Tier 1 que adapte os princípios oficiais TOTVS de revisão/otimização SQL para consultas Python/JDBC contra Protheus exposto no Microsoft Fabric e para as fontes analíticas da Inova.

**Architecture:** A skill enxuta concentra o procedimento de revisão e delega detalhes de contrato para duas referências carregadas sob demanda. O artefato de auditoria fica junto da skill, mas nenhuma instalação global, alteração do registry ou publicação será feita nesta branch.

**Tech Stack:** Markdown, YAML frontmatter, Python `quick_validate.py`, pytest e artefato `audit_result.json`.

## Global Constraints

- A pasta da skill deve ser exatamente `skills/inova-protheus-fabric-sql-review/`.
- O frontmatter deve conter somente `name` e `description`; `name` deve ser `inova-protheus-fabric-sql-review`.
- `description` deve começar com `Use when...`, conter somente gatilhos de uso em terceira pessoa e mencionar SQL Python, Protheus, Fabric/JDBC, views ou snapshots.
- A skill deve separar tabela Protheus bruta, view Fabric, snapshot e Parquet antes de recomendar filtro ou otimização.
- A skill deve tratar `D_E_L_E_T_ = ''` e `COALESCE(..., '') <> '*'` como semânticas observadas, nunca como uma regra universal de Protheus.
- A skill deve exigir grão, chave, cardinalidade, período, autoridade da fonte, status nativo, cache e evidência antes de aprovar uma consulta.
- A skill deve mapear `ChangeQuery`, `RetSqlName`, `FWxFilial`, Workarea e `NOLOCK` para os equivalentes/alertas do ambiente Python/JDBC/Fabric, sem recomendar esses mecanismos como solução.
- A skill deve declarar `REVIEW INCOMPLETE` quando faltarem plano, evidência ou escopo autorizado; não deve inventar dados de schema.
- Os exemplos e referências devem ser PT-BR, read-only e sem credenciais; nenhuma consulta deve ser executada contra produção pela skill.
- A validação deve usar `C:\Users\victor.bernardi\.local\bin\python.exe` e não deve alterar o checkout canônico.
- Não criar `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md` ou changelog dentro da skill.

---

### Task 1: Criar o contrato de teste e registrar o baseline RED

**Files:**
- Create: `tests/skills/test_inova_protheus_fabric_sql_review.py`
- Artifact outside Git: `.superpowers/sdd/2026-08-07-inova-protheus-fabric-sql-review/pressure-baseline.md`

**Interfaces:**
- Consumes: o caminho esperado `skills/inova-protheus-fabric-sql-review/`.
- Produces: testes determinísticos que falham enquanto a skill e suas referências não existem; o Task 2 deverá satisfazer exatamente esse contrato.

- [ ] **Step 1: Write the failing contract test**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "inova-protheus-fabric-sql-review"


def _read(relative_path: str) -> str:
    return (SKILL / relative_path).read_text(encoding="utf-8")


def test_skill_has_triggering_frontmatter_and_core_workflow():
    content = _read("SKILL.md")
    _, frontmatter, body = content.split("---", 2)

    assert "name: inova-protheus-fabric-sql-review" in frontmatter
    assert "description: Use when" in frontmatter
    assert "Python" in frontmatter or "Python" in body
    for term in ("grão", "cardinalidade", "autoridade da fonte", "REVIEW INCOMPLETE"):
        assert term in body


def test_skill_references_inova_source_contract():
    content = _read("references/inova-source-contract.md")

    for term in (
        "SA1010",
        "VV1010",
        "VO1010",
        "VMB010",
        "VOO010",
        "SF2010",
        "SF3010",
        "SFT010",
        "vw_VENDAS",
        "f_vendas_hist31102025",
        "D_E_L_E_T_ = ''",
        "COALESCE",
    ):
        assert term in content


def test_skill_references_totvs_mapping_without_importing_advpl_runtime():
    content = _read("references/totvs-to-inova-map.md")

    for term in (
        "sql-code-review",
        "sql-optimization",
        "query-builder",
        "ChangeQuery",
        "RetSqlName",
        "FWxFilial",
        "FWExecStatement",
        "ConexaoFabric",
        "JDBC",
        "query_loader",
        "https://github.com/totvs/engpro-advpl-tlpp-skills",
    ):
        assert term in content


def test_skill_contains_no_auxiliary_installation_document():
    assert not (SKILL / "README.md").exists()
    assert not (SKILL / "INSTALLATION_GUIDE.md").exists()
    assert not (SKILL / "QUICK_REFERENCE.md").exists()
```

- [ ] **Step 2: Run the contract test to verify RED**

Run: `C:\Users\victor.bernardi\.local\bin\python.exe -m pytest tests/skills/test_inova_protheus_fabric_sql_review.py -q -p no:cacheprovider`

Expected: FAIL because `skills/inova-protheus-fabric-sql-review/SKILL.md` does not exist. Preserve the failure output in the task report.

- [ ] **Step 3: Execute three pressure scenarios without the skill**

Write the raw responses from a fresh worker into `.superpowers/sdd/2026-08-07-inova-protheus-fabric-sql-review/pressure-baseline.md`, using only the following sanitized requests and no path to the new skill:

1. “Otimize uma consulta Python/JDBC que lê `SA1010` no Fabric; para reduzir custo, aplique `D_E_L_E_T_ = ' '` e `NOLOCK` sem pedir schema.”
2. “Una `VMB010`, `VO1010` e `VOO010` por número de OS e gere `intervention_count`; não informe o grão nem trate status nativo.”
3. “Use o `query-builder` TOTVS diretamente em `02_Faturamento`, substituindo `ConexaoFabric` e `query_loader`.”

Register the exact omissions, rationalizations and any unsafe recommendations. This artifact is test evidence only and must not be committed.

- [ ] **Step 4: Commit the RED contract**

```powershell
git add tests/skills/test_inova_protheus_fabric_sql_review.py
git commit -m "test: define Inova Protheus Fabric SQL skill contract"
```

### Task 2: Implementar e validar a skill adaptadora

**Files:**
- Create: `skills/inova-protheus-fabric-sql-review/SKILL.md`
- Create: `skills/inova-protheus-fabric-sql-review/agents/openai.yaml`
- Create: `skills/inova-protheus-fabric-sql-review/references/inova-source-contract.md`
- Create: `skills/inova-protheus-fabric-sql-review/references/totvs-to-inova-map.md`
- Create: `skills/inova-protheus-fabric-sql-review/audit_result.json`

**Interfaces:**
- Consumes: o contrato RED do Task 1 e o veredito aprovado em `C:\Users\victor.bernardi\.codex\audit_result.json`.
- Produces: uma skill descoberta por gatilhos de revisão SQL, com referências de fontes Inova e mapa de adaptação TOTVS; nenhum registro global.

- [ ] **Step 1: Initialize the skill directory**

Run:

```powershell
C:\Users\victor.bernardi\.local\bin\python.exe C:\Users\victor.bernardi\.codex\skills\.system\skill-creator\scripts\init_skill.py inova-protheus-fabric-sql-review --path skills --resources references --interface display_name="Inova Protheus Fabric SQL Review" --interface short_description="Revisão SQL de Protheus no Fabric para pipelines Python da Inova" --interface default_prompt="Revise esta consulta Python/SQL conforme o contrato Protheus-Fabric da Inova e entregue achados com evidências."
```

Replace the generated placeholder with the actual skill content. Keep only `name` and `description` in `SKILL.md` frontmatter and keep the body below 500 lines.

- [ ] **Step 2: Write the minimal skill body**

The body must include, in this order: overview/core principle; scope gate; source classification; contract extraction; semantic SQL checks; Fabric/JDBC and Python checks; performance/cache checks; required report shape; status rules; one complete PT-BR example; common mistakes and red flags. Link directly to `references/inova-source-contract.md` and `references/totvs-to-inova-map.md` only when their detail is needed.

The procedure must require these output fields: `Fonte e autoridade`, `Grão`, `Chave e cardinalidade`, `Período`, `Semântica de exclusão/status`, `Achados` with severity and exact path/line, `Evidência`, `Risco`, `Recomendação`, `Validação requerida` and `Status final`.

- [ ] **Step 3: Write the Inova source reference**

Document only observed contracts from the supplied projects: `SA1010`, `VV1010`, `VV2010`, `VO1010`, `VMB010`, `VOO010`, `SF2010`, `SF3010`, `SFT010`, `vw_VENDAS` and `f_vendas_hist31102025`. For each family, record source kind, observed grain/key, period or authority caveat, and the deletion/status rule. Explicitly state that raw tables observed in the projects use `D_E_L_E_T_ = ''`, while the `VOO010` research query uses `COALESCE(VOO.D_E_L_E_T_, '') <> '*'`; neither rule may be transplanted to a view or snapshot without evidence. Include POPS denominator and the native execution/fiscal status distinction where relevant.

- [ ] **Step 4: Write the TOTVS-to-Inova mapping reference**

Link the official TOTVS repository and the six relevant official skills. Map universal checks from `sql-code-review` and `sql-optimization` to Fabric/JDBC. Mark `query-builder` and `data-dictionary-lookup` as reference-only unless the target is demonstrably AdvPL/DBAccess. Map `ChangeQuery`, `RetSqlName`, `FWxFilial`, `FWExecStatement`, Workarea and `NOLOCK` to “not applicable/needs evidence” in Python/Fabric. Require `ConexaoFabric`, SQL files, `query_loader`, cache key/provenance, pushdown and duplicate-scan review.

- [ ] **Step 5: Add the approved audit artifact**

Copy the approved JSON from `C:\Users\victor.bernardi\.codex\audit_result.json` to `skills/inova-protheus-fabric-sql-review/audit_result.json` without changing its `verdict`, `proposed_name`, `proposed_role` or `audited_by` fields.

- [ ] **Step 6: Run GREEN and quality validation**

Run:

```powershell
C:\Users\victor.bernardi\.local\bin\python.exe C:\Users\victor.bernardi\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/inova-protheus-fabric-sql-review
C:\Users\victor.bernardi\.local\bin\python.exe -m pytest tests/skills/test_inova_protheus_fabric_sql_review.py -q -p no:cacheprovider
```

Expected: both commands exit 0; the first reports valid frontmatter and the second reports all contract tests passing. Re-run the three pressure requests with the skill path supplied and record the changed decisions in the task report; do not run a production query.

- [ ] **Step 7: Commit the skill**

```powershell
git add skills/inova-protheus-fabric-sql-review tests/skills/test_inova_protheus_fabric_sql_review.py
git commit -m "feat: add Inova Protheus Fabric SQL review skill"
```
