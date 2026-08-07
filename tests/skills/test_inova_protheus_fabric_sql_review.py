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
