"""WC-6 end-to-end reason chain: prove the sidecar-computed string reaches the
catalog READER surface, hop by hop, on the same isolated cell.

  python reason_chain.py <label>

Hops measured on live product objects (iso copy under test):
  H1 adapters/sidecar.py computed string   -> NormalizedCandidate.evidence["remediation"]
  H2 adapter_dispatch._to_scanner_candidate -> _Candidate.error          (the REM-95 seam)
  H3 locations table after product `cli scan` -> locations.error
  H4 service.query() document.locations[].error -> reader-visible field

Expected strings are the literals frozen in oracle.md S1.1 BEFORE any run;
they are pasted here as constants (never derived from the functions under test).
Exit 0 = every hop matches the frozen expectation; 3 = a hop does not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from wc6_common import ATT, CASES, EVID, load_fixture, read_json, sha256_file, write_json

#: oracle.md S1.1 — frozen before the first judged run
EXPECTED = {
    "clean_probe.txt": None,
    "no_sidecar_probe.txt": "missing_sidecar",
    "broken_sidecar_probe.txt": "sidecar_parse_failed",
    "mismatch_probe.txt":
        "missing_identity:canonical_entity_id;content_hash_mismatch;path_escape:canonical_path",
}


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "chain"
    from company_wiki.source_catalog.adapter_dispatch import _to_scanner_candidate
    from company_wiki.source_catalog.adapters.sidecar import SidecarFilingAdapter
    from company_wiki.source_catalog.config import load_catalog_config
    from company_wiki.source_catalog.models import RootSpec

    cwroot = CASES / "probes" / "cwroot"
    lake = cwroot / "lake"
    cfg_path = cwroot / "config" / "source_catalog.yaml"
    fx = load_fixture()

    # H1 — adapter output (reason computed by sidecar.py:60/74)
    adapter = SidecarFilingAdapter()
    candidates = adapter.enumerate(lake)
    h1 = {c.relative_path: (c.evidence or {}).get("remediation") for c in candidates}

    # H2 — the dispatch seam (REM-95's line)
    root = RootSpec(root_id=fx["root"]["root_id"], path=lake, kind="directory",
                    adapter_id="sidecar_filing_v1", read_only=True,
                    reusable_for_filing=True)
    h2 = {}
    for c in candidates:
        conv = _to_scanner_candidate(root, c, ())
        h2[c.relative_path] = conv.error

    # H3 — what the product's own scan persisted (needs a scanned cell)
    import sqlite3
    db = cwroot / ".source_catalog" / "catalog.sqlite3"
    h3: dict = {}
    if db.is_file():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        con.execute("PRAGMA query_only=ON")
        for rel, err in con.execute(
                "SELECT relative_path,error FROM locations ORDER BY relative_path"):
            h3[rel] = err
        con.close()

    # H4 — reader surface: service.query() -> document.locations[].error
    h4: dict = {}
    h4_view: dict = {}
    query_rows = None
    query_views = {}
    try:
        config = load_catalog_config(cfg_path)  # product API takes a Path
        from company_wiki.source_catalog.service import SourceCatalog
        service = SourceCatalog(config)
        # The product's default query view is ACTIVE-ONLY (service.py:710-718);
        # a non-active document is visible only through an explicit
        # source_status filter.  Both views are read so the chain covers every
        # probe, and the view that surfaced each row is recorded (not hidden).
        for view_name, kwargs in (("default_active_only", {}),
                                  ("explicit_source_status_incomplete",
                                   {"source_status": "incomplete"}),
                                  ("explicit_source_status_active",
                                   {"source_status": "active"})):
            rows = service.query(limit=100, **kwargs)
            query_views[view_name] = [
                {"title": r["title"], "source_status": r["source_status"],
                 "locations": [{"relative_path": l.get("relative_path"),
                                "error": l.get("error")}
                               for l in (r.get("locations") or [])]}
                for r in rows
            ]
            for row in rows:
                for loc in row.get("locations") or []:
                    rel = loc.get("relative_path")
                    if rel in EXPECTED and rel not in h4:
                        h4[rel] = loc.get("error")
                        h4_view[rel] = view_name
        query_rows = sum(len(v) for v in query_views.values())
        service.close()
    except Exception as exc:  # noqa: BLE001 - recorded, never hidden
        h4["_error"] = f"{type(exc).__name__}: {exc}"

    hops = {}
    verdicts = {}
    for rel, expected in sorted(EXPECTED.items()):
        hops[rel] = {"H1_adapter_evidence": h1.get(rel),
                     "H2_candidate_error": h2.get(rel),
                     "H3_locations_error": h3.get(rel),
                     "H4_query_locations_error": h4.get(rel),
                     "H4_seen_via_view": h4_view.get(rel),
                     "oracle_expected": expected}
        verdicts[rel] = all(v == expected for v in
                            (h1.get(rel), h2.get(rel), h3.get(rel), h4.get(rel)))

    report = {
        "label": label,
        "oracle_expected_source": "oracle.md S1.1 (frozen before first judged run)",
        "expected_strings": EXPECTED,
        "hops": hops,
        "per_probe_all_hops_match_oracle": verdicts,
        "all_hops_match": all(verdicts.values()) and "_error" not in h4,
        "query_views": query_views,
        "query_rows_returned_across_views": query_rows,
        "query_h4_error": h4.get("_error"),
        "cell": str(cwroot),
        "fix_files": {
            "adapter_dispatch.py": sha256_file(
                ATT / "iso/cw/src/company_wiki/source_catalog/adapter_dispatch.py"),
            "scanner.py": sha256_file(
                ATT / "iso/cw/src/company_wiki/source_catalog/scanner.py"),
        },
    }
    write_json(EVID / "reason_chain.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if report["all_hops_match"] else 3


if __name__ == "__main__":
    sys.exit(main())
