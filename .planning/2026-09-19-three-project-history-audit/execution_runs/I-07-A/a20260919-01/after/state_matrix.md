# I-07-A frozen sample matrix (attempt a20260919-01)

as-of frozen: 2026-09-18  
cell states: bound / planned / blocked — `not_applicable` requires a written justification and is currently **0**

| dimension | cell | state | reason | evidence |
|---|---|---|---|---|
| market | A_share_CN | **bound** | real raw rehash + identity match on CN-ZIJIN-2025 | `after/rehash.json` |
| market | HK | **bound** | real raw rehash + identity match on HK-XIAOMI-2025 | `after/rehash.json` |
| market | US | **bound** | real raw rehash + identity match on US-MSFT-2026 | `after/rehash.json` |
| file_state | downloaded_and_indexed | **bound** | CN-ZIJIN-2025 has a documents row (source_status active), 1 source, 3 locations and 2 artifacts | `after/observe_readonly.json` |
| file_state | downloaded_not_indexed | **bound** | HK-XIAOMI-2025 and US-MSFT-2026 have 0 rows in documents/sources/locations/artifacts while their bytes exist and hash-match | `after/observe_readonly.json` |
| file_state | genuinely_missing | **blocked** | no live missing identity is bound (sample_manifest.json lists CN/HK/US-NEW-MISSING as unbound) and every plan sample exists on disk; only the isolated simulation case-03 exists and it is labelled simulated_in_isolation | `iso/cases/case-03-simulated-missing/state.json` |
| source | companies_only | **blocked** | CN-ZIJIN-2025 is registered under BOTH company_raw and dropbox_stock, so it is a real multi-root same-bytes case; CN uniqueness is empirically DISPROVED (two original_primary location rows, observed_size 79925886 each, SQL in after/r2_review_facts.json); no plan sample is single-root companies-only, and exclusivity must not be manufactured by deleting the other copy | `after/r2_review_facts.json:cn_sample_locations` |
| source | dayu_only | **blocked** | no sample in the plan manifest is bound to the dayu_portfolio root (root exists at C:/Users/.../dayu-agent/workspace/portfolio and is registered with 3660 location rows, but no identity is frozen for it) | `after/r2_review_facts.json:root_location_counts` |
| source | external_dir_only | **blocked** | sample_manifest.json unbound_live_samples[EXTERNAL-ONLY] is unbound; card clause 5 forbids deleting other copies to create exclusivity | `sample_manifest.json:unbound_live_samples` |
| source | multi_root_same_bytes | **bound** | CN-ZIJIN-2025 has location rows under company_raw (two: original_primary + metadata) and dropbox_stock (one). The production census, reported UNTRUNCATED, has 3440 content hashes with >=2 distinct roots (the first pass carried LIMIT 20 and reported '20', which was an undercount by ~172x — corrected per F-I07A-02); top row spans company_raw + dayu_portfolio + dropbox_stock | `after/r2_review_facts.json:multi_root_same_bytes_total` |
| artifact | valid | **bound** | artifact_role=summary status=completed, content_sha256 matches the bytes on disk | `after/observe_readonly.json + after/cmd-V2/stdout.json` |
| artifact | missing | **planned** | no required artifact role is absent for the indexed sample; the cell is frozen and will bind when a sample with a missing role is observed | `after/observe_readonly.json` |
| artifact | stale | **bound** | artifact_role=normalized status=partial with quality_flags [empty_output] declared in its own front matter (parser pdf_page_aware_core 1.26.7) | `after/cmd-V2/stdout.json + after/observe_readonly.json` |
| artifact | tampered | **planned** | no tampered artifact was observed; the detection is a hash comparison and was performed on both roles of the indexed sample (all matched) | `after/cmd-V2/stdout.json` |
| artifact | not_applicable | **planned** | no artifact role is NA for the indexed sample; the cell remains frozen, and if it ever binds it must carry a justification string | `after/observe_readonly.json` |
| request | exact | **planned** | the request artifact is frozen and hash-verified; executing the exact resolve is I-07-B | `after/rehash.json` |
| request | latest | **planned** | same frozen request carries as_of_date 2026-09-18 for the latest_as_of path; execution is I-07-B | `after/rehash.json` |
| request | new_revision | **planned** | no revision pair is frozen in this card | `PLAN/execution_v2/card_I-07-B.md` |
| request | mixed_period | **planned** | period-ambiguity handling is a resolve-time behaviour, executed in I-07-B | `PLAN/execution_v2/card_I-07-B.md` |
| request | duplicate | **planned** | idempotence of a repeated request is I-07-B | `PLAN/execution_v2/card_I-07-B.md` |
| request | concurrent | **planned** | concurrency is I-07-B/I-07-D | `PLAN/execution_v2/card_I-07-B.md` |
| config | installed_entry | **planned** | the installed entry is bound and exercised by I-16-A | `PLAN/execution_v2/card_I-16-A.md` |
| config | production_config_copy | **bound** | an isolated copy of CW/config/source_catalog.yaml with exactly one line changed (catalog_dir rebound to the isolated catalog); the production config hash is unchanged before and after | `iso/config_rebind.json, iso/config/source_catalog.yaml` |
| config | legal_fifth_root | **planned** | root_id future_lake IS declared by config only (kind directory, adapter_id sidecar_filing_v1, read_only true, reusable_for_filing true) at ${PROJECT_ROOT}/future_lake and the directory exists, and the production roots table has exactly 4 rows including future_lake (SQL in after/r2_review_facts.json). It is NOT bound because ingestion is unproven: the only future_lake location is future_lake/README.md (545 bytes, document_kind broker_research, title 'README', active) — a placeholder, not a filing. Ingest feasibility stays with I-07-C (F-I07A-01) | `after/r2_review_facts.json:roots_table + root_location_counts + iso/config/source_catalog.yaml` |
| fault | provider_failure | **planned** | needs a live provider; fault injection is I-07-D | `PLAN/execution_v2/card_I-07-D.md` |
| fault | scan_failure | **planned** | fault injection is I-07-D | `PLAN/execution_v2/card_I-07-D.md` |
| fault | db_lock | **planned** | fault injection is I-07-D | `PLAN/execution_v2/card_I-07-D.md` |
| fault | process_interruption | **planned** | fault injection is I-07-D | `PLAN/execution_v2/card_I-07-D.md` |
| generality | company_not_in_fixture_names | **blocked** | implementation_plan.md:141 requires a company/file outside the fixture names; no such sample is frozen and this card may not download, so the cell stays blocked and is handed to I-07-C | `PLAN/implementation_plan.md:141 + PLAN/execution_v2/card_I-07-C.md` |

counts: {"bound": 9, "planned": 15, "blocked": 5, "not_applicable": 0}

blocked cells: file_state.genuinely_missing, source.companies_only, source.dayu_only, source.external_dir_only, generality.company_not_in_fixture_names

## r2 corrections after the independent review

- **F-I07A-01** `config.legal_fifth_root` downgraded to **planned**. Roots table as SQL: 4 rows (company_raw, dayu_portfolio, dropbox_stock, future_lake); per-root location counts {"company_raw": 33092, "dayu_portfolio": 3660, "dropbox_stock": 9853, "future_lake": 1}. The reviewer's stated mechanism (zero future_lake locations) does not match the catalog — there is exactly one, `future_lake/README.md`, a placeholder — but the disposition is the same because a README is not ingest capability.
- **F-I07A-02** census reported untruncated: **3440** content hashes with >=2 distinct roots (3436 documents). The first pass carried LIMIT 20 and its '20' was an undercount by 172.0x.
- **F-I07A-03** isolated catalog is NOT production-isomorphic and MUST NOT be reused for resolve/registration by I-07-B.
- **F-I07A-04** case-02 is an OBSERVATION RECORD, not an isolated build.
- **F-I07A-05** CN uniqueness empirically disproved (two original_primary rows, observed_size 79925886 each).
- **F-I07A-06** 8 dimensions implemented: the plan's table (implementation_plan.md:131-139) has 7 rows, plus `generality` from implementation_plan.md:141, which belongs to none of them.
