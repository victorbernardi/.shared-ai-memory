# Wiki Ingest — Raw Mode Promotion

Ingest and distill 10 draft documents currently staged in the `_raw/` directory of the `wiki-compiler-vault`. These files represent recent project specifications, business requirements, and task logs that need to be integrated into the permanent knowledge base.

## User Review Required

> [!IMPORTANT]
> The target folders and filenames have been mapped based on the existing `index.md` links to ensure consistency. Some files will be promoted to the `journal/` category as they represent point-in-time plans or logs, while others will go to `references/` or `projects/` as core documentation.

## Proposed Mapping

| Source File (`_raw/`) | Target Path | Category |
| :--- | :--- | :--- |
| `BRD-20260506-motor-cevap.md` | `references/brd-motor-cevap.md` | Referência |
| `fix-markdown-normalization.md` | `journal/2026-05-07-markdown-normalization.md` | Journal |
| `john-deere-api-docs-implementation.md` | `projects/john-deere-apis-implementation.md` | Projetos |
| `john-deere-api-docs.md` | `projects/john-deere-apis-docs.md` | Projetos |
| `v3_ajuste_colunas.md` | `journal/2026-05-07-plan-cevap-v3-columns.md` | Journal |
| `v4_ajuste_colunas_final.md` | `journal/2026-05-07-plan-cevap-v4-columns-refactor.md` | Journal |
| `v4_conformidade_final.md` | `journal/2026-05-07-plan-cevap-v4-compliance-final.md` | Journal |
| `v4_integracao_final.md` | `journal/2026-05-07-plan-cevap-v4-integration-final.md` | Journal |
| `v5_unificacao_pipeline.md` | `references/spec-inova-dashboard-v5-pipeline-unification.md` | Referência |
| `v6_consultant_filter.md` | `references/spec-inova-dashboard-v6-consultant-filter.md` | Referência |

## Proposed Changes

### Core Wiki Files

#### [MODIFY] [.manifest.json](file:///c:/Users/victor.bernardi/Documents/wiki-compiler-vault/.manifest.json)
- Add entries for the 10 new sources with content hashes and timestamps.
- Update `total_pages` and `total_sources_ingested` stats.

#### [MODIFY] [index.md](file:///c:/Users/victor.bernardi/Documents/wiki-compiler-vault/index.md)
- Ensure all links point to the correct files.
- Update the total page count.

#### [MODIFY] [log.md](file:///c:/Users/victor.bernardi/Documents/wiki-compiler-vault/log.md)
- Append an entry for the raw mode ingest operation.

#### [MODIFY] [hot.md](file:///c:/Users/victor.bernardi/Documents/wiki-compiler-vault/hot.md)
- Update "Recent Activity" to reflect the ingestion of CEVAP BRDs, M6 specs, and JD API docs.

### New Pages

- **[NEW]** `projects/motor-cevap.md`
- **[NEW]** `references/brd-motor-cevap.md`
- **[NEW]** `journal/2026-05-07-markdown-normalization.md`
- **[NEW]** `projects/john-deere-apis-implementation.md`
- **[NEW]** `projects/john-deere-apis-docs.md`
- **[NEW]** `journal/2026-05-07-plan-cevap-v3-columns.md`
- **[NEW]** `journal/2026-05-07-plan-cevap-v4-columns-refactor.md`
- **[NEW]** `journal/2026-05-07-plan-cevap-v4-compliance-final.md`
- **[NEW]** `journal/2026-05-07-plan-cevap-v4-integration-final.md`
- **[NEW]** `references/spec-inova-dashboard-v5-pipeline-unification.md`
- **[NEW]** `references/spec-inova-dashboard-v6-consultant-filter.md`

### Cleanup

- **[DELETE]** All 10 files from `_raw/` after successful promotion.

## Verification Plan

### Automated Verification
- Run `ls` on target directories to confirm file creation.
- Check `_raw/` is empty.
- Validate `.manifest.json` syntax.

### Manual Verification
- Review `index.md` to ensure links are resolved and page count is accurate.
