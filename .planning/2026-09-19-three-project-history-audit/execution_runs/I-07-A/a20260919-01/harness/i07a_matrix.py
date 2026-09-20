"""I-07-A: derive the frozen state matrix and the per-case state records from the
already-produced evidence (before/snapshot.json, after/rehash.json,
after/observe_readonly.json, iso/cases/*/case.json).

Pure derivation: no production access, no writes outside the attempt directory.
Every cell is bound / planned / blocked with a concrete reason; `not_applicable`
is only ever emitted with a justification string.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]


def rd(rel: str):
    return json.loads((ATT / rel).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    snap = rd("before/snapshot.json")
    rehash = rd("after/rehash.json")
    obs = rd("after/observe_readonly.json")
    iso_state = rd("iso/isolated_state.json")
    cfg = rd("iso/config_rebind.json")
    # r2 (post-review corrections F-I07A-01/F-I07A-02): the roots table as SQL output, and the
    # multi-root census reported untruncated.  The first pass carried LIMIT 20 and both review.md
    # and state_matrix.md wrote "20", which read as a total; the true total is 3440.
    facts = rd("after/r2_review_facts.json")
    roots_sql = facts["observations"]["roots_table"]
    root_loc = {r["root_id"]: r for r in
                facts["observations"]["root_location_counts"]["rows"]}
    census_total = facts["observations"]["multi_root_same_bytes_total"]["rows"][0]["COUNT(*)"]
    census_top = facts["observations"]["multi_root_same_bytes_top5"]["rows"]
    docs_census_total = \
        facts["observations"]["multi_root_same_document_total"]["rows"][0]["COUNT(*)"]
    census_truncated = len(obs["multi_root_same_bytes"]) >= 20
    cn_locations_sql = facts["observations"]["cn_sample_locations"]["rows"]
    cn_primary = [r for r in cn_locations_sql if r["role"] == "original_primary"]
    cn_primary_roots = sorted(r["root_id"] for r in cn_primary)
    cn_primary_sizes = sorted({r["observed_size"] for r in cn_primary})

    by_id = {s["id"]: s for s in rehash["samples"]}
    obs_by_id = {s["id"]: s for s in obs["samples"]}
    isolated = {c["id"]: c for c in iso_state["copied"]}

    derived = {}
    for sid in ("CN-ZIJIN-2025", "HK-XIAOMI-2025", "US-MSFT-2026"):
        o = obs_by_id[sid]
        loc_roots = sorted({l["root_id"] for l in o["locations"] if "__sql_error__" not in l})
        derived[sid] = {
            "documents_rows": len([r for r in o["documents"] if "__sql_error__" not in r]),
            "sources_rows": len([r for r in o["sources"] if "__sql_error__" not in r]),
            "locations_rows": len([r for r in o["locations"] if "__sql_error__" not in r]),
            "artifacts_rows": len([r for r in o["artifacts"] if "__sql_error__" not in r]),
            "location_roots": loc_roots,
            "document_status": [r.get("source_status") for r in o["documents"]
                                if "__sql_error__" not in r],
            "artifact_status": [r.get("status") for r in o["artifacts"]
                                if "__sql_error__" not in r],
            "multi_root_same_bytes": len(loc_roots) > 1,
        }

    def cell(state, reason, evidence, origin=None):
        out = {"status": state, "reason": reason, "evidence": evidence}
        if origin:
            out["state_origin"] = origin
        return out

    # ---------------- per-case state records ----------------
    cn = "CN-ZIJIN-2025"
    hk = "HK-XIAOMI-2025"
    us = "US-MSFT-2026"

    case01 = {
        "case": "case-01-indexed-quality",
        "state": "indexed_quality_candidate",
        "state_origin": "live_production_observation",
        "sample_ids": [cn],
        "sample_identity": {
            "document_id": by_id[cn]["document_id_urn"],
            "raw_sha256_actual": by_id[cn]["raw_sha256_actual"],
            "raw_sha256_matches_manifest": by_id[cn]["checks"]["raw_sha256_match"],
            "provider": by_id[cn]["provider"],
            "request_identity": by_id[cn]["request_identity"],
        },
        "catalog_observation": derived[cn],
        "derived_state": {},
        "isolated_case_dir": "iso/cases/case-01-indexed-quality",
        "isolated_copy_sha256": isolated[cn]["isolated_sha256"],
        "production_original_still_present": isolated[cn]["source_still_present_after_copy"],
        "accepted_qualification": "indexed document observed read-only; artifact readiness is "
                                  "NOT uniform (one completed, one partial) — see derived_state",
    }
    case01["derived_state"] = {
        "already_downloaded_and_indexed": True,
        "artifact_valid": {
            "roles": derived[cn]["artifact_status"],
            "summary": "artifact_role=summary status=completed",
        },
        "artifact_stale": {
            "roles": derived[cn]["artifact_status"],
            "summary": "artifact_role=normalized status=partial with "
                       "quality_flags [empty_output] in its front matter; the file is "
                       "complete on disk and hashes as recorded, so 'partial' is a "
                       "producer-declared quality state, not a missing or tampered artifact",
        },
        "artifact_tampered": {
            "checked": ["normalized.md", "summary.md"],
            "recorded_sha256_vs_actual": "all match",
            "summary": "artifact content_sha256 equals the bytes on disk for both roles",
        },
        "artifact_missing": {"missing_roles": [], "summary": "no required role is absent"},
        "artifact_not_applicable": {"count": 0, "summary": "no NA artifact cell for this sample"},
        "source_only_qualification": {
            "location_roots": derived[cn]["location_roots"],
            "companies_only": False,
            "reason": "the same bytes are also registered under the dropbox_stock root, so the "
                      "sample is a REAL multi-root same-bytes case and may never be reported as "
                      "companies-only",
            "uniqueness_disproved_by_SQL": {
                "query": facts["observations"]["cn_sample_locations"]["sql"],
                "params": facts["observations"]["cn_sample_locations"]["params"],
                "original_primary_rows": cn_primary,
                "original_primary_roots": cn_primary_roots,
                "distinct_observed_sizes": cn_primary_sizes,
                "verdict": "CN uniqueness is empirically DISPROVED: the same content hash is an "
                           "original_primary location under company_raw and under dropbox_stock, "
                           "both observed_size 79925886 bytes. Any product document or code path "
                           "that presents CN as a companies-only unique source is contradicted by "
                           "this card's evidence (F-I07A-05).",
            },
        },
    }

    case02 = {
        "case": "case-02-present-unregistered",
        "state": "present_unregistered",
        "state_origin": "live_production_observation",
        "record_type": "OBSERVATION RECORD, NOT an isolated build",
        "record_type_note": "This case carries no isolated catalog rows: the isolated catalog has "
                            "0 rows for HK/US (they are deliberately NOT registered there). The "
                            "state it records is the production-observed precondition, cited from "
                            "after/observe_readonly.json. Labelling it 'isolated build' would be "
                            "false, so the attempt does not create fabricated rows for it "
                            "(F-I07A-04).",
        "isolated_catalog_rows_for_this_case": 0,
        "sample_ids": [hk, us],
        "samples": {},
        "isolated_case_dir": "iso/cases/case-02-present-unregistered",
        "accepted_qualification": "raw bytes and sidecar exist and hash-match the plan manifest "
                                  "while the production catalog holds no documents row; this is "
                                  "the I-07-B input state and requires no re-download",
    }
    for sid in (hk, us):
        case02["samples"][sid] = {
            "document_id": by_id[sid]["document_id_urn"],
            "raw_path": by_id[sid]["raw_path"],
            "raw_sha256_actual": by_id[sid]["raw_sha256_actual"],
            "raw_sha256_matches_manifest": by_id[sid]["checks"]["raw_sha256_match"],
            "sidecar_sha256_actual": by_id[sid]["sidecar_sha256_actual"],
            "sidecar_sha256_matches_manifest": by_id[sid]["checks"]["sidecar_sha256_match"],
            "provider": by_id[sid]["provider"],
            "provider_document_id": by_id[sid]["provider_document_id"],
            "request_identity": by_id[sid]["request_identity"],
            "catalog_observation": derived[sid],
            "isolated_copy_sha256": isolated[sid]["isolated_sha256"],
            "production_original_still_present": isolated[sid]["source_still_present_after_copy"],
            "state_evidence": "documents/sources/locations/artifacts are all empty for this "
                              "document_id and content hash in the production catalog",
        }

    case03 = {
        "case": "case-03-simulated-missing",
        "state": "simulated_missing",
        "state_origin": "simulated_in_isolation",
        "sample_ids": [],
        "query_identity": {
            "market": "CN", "document_kind": "annual_report", "fiscal_year": 2019,
            "as_of_date": "2026-09-18", "company_query": "000000",
        },
        "isolated_case_dir": "iso/cases/case-03-simulated-missing",
        "live_label": "NOT a live missing sample",
        "reason": "every sample in the plan manifest exists on disk and hashes correctly, so a "
                  "genuinely-missing live cell cannot be bound by this attempt; the three "
                  "CN/HK/US-NEW-MISSING identities remain unbound in sample_manifest.json",
        "not_manufactured": "no production copy was deleted or moved to create this state",
        "as_of_discipline": {
            "as_of_date": "2026-09-18",
            "historical_reconstruction_supported": True,
            "note": "the three frozen requests already carry as_of_date 2026-09-18 and were "
                    "re-hashed unchanged; no capture time was rewritten and none was needed",
        },
    }

    for name, payload in (("case-01-indexed-quality", case01),
                          ("case-02-present-unregistered", case02),
                          ("case-03-simulated-missing", case03)):
        path = ATT / "iso" / "cases" / name / "state.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    # ---------------- the frozen matrix ----------------
    def d(key, cells):
        return {"dimension": key, "cells": cells}

    matrix = {
        "card": "I-07-A",
        "attempt_id": "a20260919-01",
        "as_of_frozen": "2026-09-18",
        "counts": {},
        "not_applicable_justified": [],
        "dimensions": [
            d("market", {
                "A_share_CN": cell("bound",
                                   "real raw rehash + identity match on CN-ZIJIN-2025",
                                   "after/rehash.json"),
                "HK": cell("bound",
                           "real raw rehash + identity match on HK-XIAOMI-2025",
                           "after/rehash.json"),
                "US": cell("bound",
                           "real raw rehash + identity match on US-MSFT-2026",
                           "after/rehash.json"),
            }),
            d("file_state", {
                "downloaded_and_indexed": cell(
                    "bound",
                    "CN-ZIJIN-2025 has a documents row (source_status active), 1 source, "
                    "3 locations and 2 artifacts",
                    "after/observe_readonly.json", "live_production_observation"),
                "downloaded_not_indexed": cell(
                    "bound",
                    "HK-XIAOMI-2025 and US-MSFT-2026 have 0 rows in documents/sources/"
                    "locations/artifacts while their bytes exist and hash-match",
                    "after/observe_readonly.json", "live_production_observation"),
                "genuinely_missing": cell(
                    "blocked",
                    "no live missing identity is bound (sample_manifest.json lists "
                    "CN/HK/US-NEW-MISSING as unbound) and every plan sample exists on disk; "
                    "only the isolated simulation case-03 exists and it is labelled "
                    "simulated_in_isolation",
                    "iso/cases/case-03-simulated-missing/state.json"),
            }),
            d("source", {
                "companies_only": cell(
                    "blocked",
                    "CN-ZIJIN-2025 is registered under BOTH company_raw and dropbox_stock, so it "
                    "is a real multi-root same-bytes case; CN uniqueness is empirically DISPROVED "
                    "(two original_primary location rows, observed_size 79925886 each, SQL in "
                    "after/r2_review_facts.json); no plan sample is single-root companies-only, "
                    "and exclusivity must not be manufactured by deleting the other copy",
                    "after/r2_review_facts.json:cn_sample_locations"),
                "dayu_only": cell(
                    "blocked",
                    "no sample in the plan manifest is bound to the dayu_portfolio root "
                    "(root exists at C:/Users/.../dayu-agent/workspace/portfolio and is "
                    "registered with 3660 location rows, but no identity is frozen for it)",
                    "after/r2_review_facts.json:root_location_counts"),
                "external_dir_only": cell(
                    "blocked",
                    "sample_manifest.json unbound_live_samples[EXTERNAL-ONLY] is unbound; "
                    "card clause 5 forbids deleting other copies to create exclusivity",
                    "sample_manifest.json:unbound_live_samples"),
                "multi_root_same_bytes": cell(
                    "bound",
                    "CN-ZIJIN-2025 has location rows under company_raw (two: original_primary + "
                    "metadata) and dropbox_stock (one). The production census, reported "
                    "UNTRUNCATED, has "
                    f"{census_total} content hashes with >=2 distinct roots (the first pass carried "
                    "LIMIT 20 and reported '20', which was an undercount by ~172x — corrected per "
                    "F-I07A-02); top row spans company_raw + dayu_portfolio + dropbox_stock",
                    "after/r2_review_facts.json:multi_root_same_bytes_total"),
            }),
            d("artifact", {
                "valid": cell("bound",
                              "artifact_role=summary status=completed, content_sha256 matches "
                              "the bytes on disk",
                              "after/observe_readonly.json + after/cmd-V2/stdout.json"),
                "missing": cell("planned",
                                "no required artifact role is absent for the indexed sample; "
                                "the cell is frozen and will bind when a sample with a missing "
                                "role is observed",
                                "after/observe_readonly.json"),
                "stale": cell("bound",
                              "artifact_role=normalized status=partial with quality_flags "
                              "[empty_output] declared in its own front matter (parser "
                              "pdf_page_aware_core 1.26.7)",
                              "after/cmd-V2/stdout.json + after/observe_readonly.json"),
                "tampered": cell("planned",
                                 "no tampered artifact was observed; the detection is a hash "
                                 "comparison and was performed on both roles of the indexed "
                                 "sample (all matched)",
                                 "after/cmd-V2/stdout.json"),
                "not_applicable": cell("planned",
                                       "no artifact role is NA for the indexed sample; the cell "
                                       "remains frozen, and if it ever binds it must carry a "
                                       "justification string",
                                       "after/observe_readonly.json"),
            }),
            d("request", {
                "exact": cell("planned",
                              "the request artifact is frozen and hash-verified; executing the "
                              "exact resolve is I-07-B",
                              "after/rehash.json"),
                "latest": cell("planned",
                               "same frozen request carries as_of_date 2026-09-18 for the "
                               "latest_as_of path; execution is I-07-B",
                               "after/rehash.json"),
                "new_revision": cell("planned", "no revision pair is frozen in this card",
                                     "PLAN/execution_v2/card_I-07-B.md"),
                "mixed_period": cell("planned", "period-ambiguity handling is a resolve-time "
                                                "behaviour, executed in I-07-B",
                                     "PLAN/execution_v2/card_I-07-B.md"),
                "duplicate": cell("planned", "idempotence of a repeated request is I-07-B",
                                  "PLAN/execution_v2/card_I-07-B.md"),
                "concurrent": cell("planned", "concurrency is I-07-B/I-07-D",
                                   "PLAN/execution_v2/card_I-07-B.md"),
            }),
            d("config", {
                "installed_entry": cell("planned",
                                        "the installed entry is bound and exercised by I-16-A",
                                        "PLAN/execution_v2/card_I-16-A.md"),
                "production_config_copy": cell(
                    "bound",
                    "an isolated copy of CW/config/source_catalog.yaml with exactly one line "
                    "changed (catalog_dir rebound to the isolated catalog); the production "
                    "config hash is unchanged before and after",
                    "iso/config_rebind.json, iso/config/source_catalog.yaml",
                    "simulated_in_isolation"),
                "legal_fifth_root": cell(
                    "planned",
                    "root_id future_lake IS declared by config only (kind directory, "
                    "adapter_id sidecar_filing_v1, read_only true, reusable_for_filing true) at "
                    "${PROJECT_ROOT}/future_lake and the directory exists, and the production "
                    "roots table has exactly 4 rows including future_lake (SQL in "
                    "after/r2_review_facts.json). It is NOT bound because ingestion is unproven: "
                    "the only future_lake location is future_lake/README.md (545 bytes, "
                    "document_kind broker_research, title 'README', active) — a placeholder, not "
                    "a filing. Ingest feasibility stays with I-07-C (F-I07A-01)",
                    "after/r2_review_facts.json:roots_table + root_location_counts + "
                    "iso/config/source_catalog.yaml"),
            }),
            d("fault", {
                "provider_failure": cell("planned",
                                         "needs a live provider; fault injection is I-07-D",
                                         "PLAN/execution_v2/card_I-07-D.md"),
                "scan_failure": cell("planned", "fault injection is I-07-D",
                                     "PLAN/execution_v2/card_I-07-D.md"),
                "db_lock": cell("planned", "fault injection is I-07-D",
                                "PLAN/execution_v2/card_I-07-D.md"),
                "process_interruption": cell("planned", "fault injection is I-07-D",
                                             "PLAN/execution_v2/card_I-07-D.md"),
            }),
            d("generality", {
                "company_not_in_fixture_names": cell(
                    "blocked",
                    "implementation_plan.md:141 requires a company/file outside the fixture "
                    "names; no such sample is frozen and this card may not download, so the cell "
                    "stays blocked and is handed to I-07-C",
                    "PLAN/implementation_plan.md:141 + PLAN/execution_v2/card_I-07-C.md"),
            }),
        ],
    }

    counts = {"bound": 0, "planned": 0, "blocked": 0, "not_applicable": 0}
    na_justified = 0
    for dim in matrix["dimensions"]:
        for name, c in dim["cells"].items():
            counts[c["status"]] = counts.get(c["status"], 0) + 1
            if c["status"] == "not_applicable" and c.get("justification"):
                na_justified += 1
    matrix["counts"] = counts
    matrix["not_applicable_count"] = counts.get("not_applicable", 0)
    matrix["not_applicable_justified_count"] = na_justified
    matrix["blocked_cells"] = [
        f"{dim['dimension']}.{name}"
        for dim in matrix["dimensions"] for name, c in dim["cells"].items()
        if c["status"] == "blocked"
    ]
    matrix["r2_corrections"] = {
        "F-I07A-01": {
            "what": "config.legal_fifth_root was bound on a program structure rather than SQL "
                    "output, and its reason claimed 'the production roots table registers all "
                    "four root ids'",
            "disposition": "cell downgraded to planned; the roots table is now shown as SQL with "
                           f"{roots_sql['row_count']} rows and the per-root location counts are "
                           "recorded",
            "sql": roots_sql["sql"],
            "root_location_counts": list(root_loc.values()),
            "reviewer_claim_check": {
                "reviewer_said": "future_lake has 0 location rows",
                "measured": "future_lake has exactly 1 location row: future_lake/README.md "
                            "(545 bytes, document_kind broker_research, title 'README', "
                            "location_status active, document_id NOT NULL)",
                "consequence": "the reviewer's stated mechanism does not match the catalog, but "
                               "the recommended disposition is still correct and is adopted: a "
                               "placeholder README is not ingest capability, so the cell is "
                               "planned either way",
            },
        },
        "F-I07A-02": {
            "what": "the census query carried LIMIT 20 and the write-up presented 20 as a total",
            "disposition": "reported untruncated; the first pass is relabelled top-20-of-many",
            "first_pass_query_had_limit": 20,
            "first_pass_truncated": census_truncated,
            "true_total_content_hashes_with_multiple_roots": census_total,
            "true_total_documents_with_multiple_roots": docs_census_total,
            "undercount_factor": round(census_total / max(len(obs["multi_root_same_bytes"]), 1), 1),
            "top5": census_top,
        },
        "F-I07A-03": {
            "what": "the isolated catalog is NOT production-isomorphic",
            "disposition": "accepted as scoped-usable with an explicit prohibition recorded below",
        },
        "F-I07A-04": {
            "what": "case-02 has no isolated build of its own",
            "disposition": "relabelled an OBSERVATION RECORD; no fabricated rows were added",
        },
        "F-I07A-05": {
            "what": "CN uniqueness disproved",
            "disposition": "recorded with SQL: two original_primary rows, observed_size 79925886 "
                           "each",
        },
        "F-I07A-06": {
            "what": "the write-up treated the plan's dimension list as six where its own oracle.md "
                    "section 3 had already said 'six' while the plan table at "
                    "implementation_plan.md:131-139 actually has SEVEN rows",
            "disposition": "kept as a separate family; the alignment note below records the "
                           "authoritative row count (7), the extra family (generality, from "
                           "implementation_plan.md:141) and the corrected phrasing",
        },
    }
    matrix["isolated_catalog_prohibition"] = {
        "statement": "iso/catalog/catalog.sqlite3 is an attempt-owned MINIMAL schema (5 tables: "
                     "roots, sources, documents, locations, artifacts) created only to carry the "
                     "three state labels. It is NOT production-isomorphic (production has 18 "
                     "tables; 5/5 CREATE statements differ). It therefore CANNOT carry a resolve "
                     "or a registration, and MUST NOT be reused by I-07-B or any later card.",
        "required_for_i07b": "a production-isomorphic catalog, or a table-filtered copy of the "
                             "production catalog built with the SQLite backup API as I-00-B's "
                             "isolated_binding_plan describes",
        "iso_tables": ["roots", "sources", "documents", "locations", "artifacts"],
        "production_table_count": 18,
    }
    matrix["dimension_alignment"] = {
        "plan_source": "PLAN/implementation_plan.md:131-139",
        "plan_table_rows": {
            "count": 7,
            "names": ["市场", "文件状态", "来源", "工件", "请求", "配置", "故障"],
            "note": "the review's phrasing 'six dimensions' was loose: the plan's table at "
                    "lines 131-139 has SEVEN rows (市场/文件状态/来源/工件/请求/配置/故障). The "
                    "implementer's own oracle.md section 3 also said '六个维度' in prose once; "
                    "that phrasing is corrected here and the rows are the authority.",
        },
        "implemented_dimensions": [d["dimension"] for d in matrix["dimensions"]],
        "implemented_dimension_count": len(matrix["dimensions"]),
        "extra": "generality",
        "why": "the plan names seven rows in its table but its prose (line 141) adds an obligation "
               "that belongs to none of them: '另选未在 fixture 名称中出现的公司和文件做独立泛化'. "
               "Folding it into another dimension would hide it, so it is an eighth cell family. "
               "The cell count is what matters, not the row count.",
    }
    matrix["v_checks"] = {
        "V1_rehash": {"pass": rehash["all_match"],
                      "detail": {k: v["all_checks_match"] for k, v in by_id.items()}},
        "V2_state_observation": {
            "pass": obs["catalog_identity_unchanged"],
            "derived": derived,
        },
        "V3_isolated_states": {
            "pass": iso_state["table_counts"] == {"roots": 1, "sources": 1, "documents": 1,
                                                  "locations": 1, "artifacts": 1},
            "table_counts": iso_state["table_counts"],
            "copies_hash_match": all(c["source_sha256"] == c["isolated_sha256"]
                                     for c in iso_state["copied"]),
            "sources_still_present": all(c["source_still_present_after_copy"]
                                         for c in iso_state["copied"]),
        },
        "V4_config_rebind": {
            "pass": cfg["changed_line_count"] == 1
            and cfg["production_config_sha256_before"] == cfg["production_config_sha256_after"],
            "changed_lines": cfg["changed_lines"],
        },
        "V5_no_production_mutation": {"pass": None, "detail": "filled by the after/ snapshot diff"},
        "V6_generality_cell": {"pass": False, "status": "blocked",
                               "reason": "no unbound-in-fixture sample and no download authority"},
        "V7_no_silent_NA": {"pass": counts.get("not_applicable", 0) == 0,
                            "not_applicable_count": counts.get("not_applicable", 0)},
    }
    (ATT / "after" / "state_matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # markdown rendering for the reader
    lines = ["# I-07-A frozen sample matrix (attempt a20260919-01)", "",
             f"as-of frozen: {matrix['as_of_frozen']}  ",
             "cell states: bound / planned / blocked — `not_applicable` requires a written "
             "justification and is currently **0**", "",
             "| dimension | cell | state | reason | evidence |", "|---|---|---|---|---|"]
    for dim in matrix["dimensions"]:
        for name, c in dim["cells"].items():
            reason = c["reason"].replace("|", "/")
            lines.append(f"| {dim['dimension']} | {name} | **{c['status']}** | {reason} | "
                         f"`{c['evidence']}` |")
    lines += ["", f"counts: {json.dumps(counts, ensure_ascii=False)}", "",
              f"blocked cells: {', '.join(matrix['blocked_cells'])}", "",
              "## r2 corrections after the independent review", "",
              f"- **F-I07A-01** `config.legal_fifth_root` downgraded to **planned**. Roots table as "
              f"SQL: {roots_sql['row_count']} rows "
              f"({', '.join(r['root_id'] for r in roots_sql['rows'])}); per-root location counts "
              f"{json.dumps({k: v['locations'] for k, v in root_loc.items()}, ensure_ascii=False)}. "
              "The reviewer's stated mechanism (zero future_lake locations) does not match the "
              "catalog — there is exactly one, `future_lake/README.md`, a placeholder — but the "
              "disposition is the same because a README is not ingest capability.",
              f"- **F-I07A-02** census reported untruncated: **{census_total}** content hashes with "
              f">=2 distinct roots ({docs_census_total} documents). The first pass carried LIMIT 20 "
              f"and its '20' was an undercount by {matrix['r2_corrections']['F-I07A-02']['undercount_factor']}x.",
              "- **F-I07A-03** isolated catalog is NOT production-isomorphic and MUST NOT be reused "
              "for resolve/registration by I-07-B.",
              "- **F-I07A-04** case-02 is an OBSERVATION RECORD, not an isolated build.",
              "- **F-I07A-05** CN uniqueness empirically disproved (two original_primary rows, "
              "observed_size 79925886 each).",
              f"- **F-I07A-06** {matrix['dimension_alignment']['implemented_dimension_count']} "
              "dimensions implemented: the plan's table (implementation_plan.md:131-139) has "
              f"{matrix['dimension_alignment']['plan_table_rows']['count']} rows, plus `generality` "
              "from implementation_plan.md:141, which belongs to none of them.",
              ""]
    (ATT / "after" / "state_matrix.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"counts": counts,
                      "not_applicable_count": counts.get("not_applicable", 0),
                      "blocked_cells": matrix["blocked_cells"],
                      "census_total": census_total,
                      "census_first_pass_len": len(obs["multi_root_same_bytes"]),
                      "v_checks": {k: v.get("pass") for k, v in matrix["v_checks"].items()}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
