"""B.VR (B06) independent review probe - read-only against the product repo.

Everything runs on TEMP fixtures (tmp_path style) or on copies of module code.
No product file, no test file and no production catalog is written.
Output: b06_review_probe.json next to this file.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import time
import traceback
from dataclasses import replace
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FILING = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
sys.path.insert(0, str(WIKI / "src"))

RESULTS: dict[str, object] = {}


def cap(name: str, fn) -> None:
    try:
        RESULTS[name] = {"ok": True, "value": fn()}
    except Exception as exc:  # noqa: BLE001
        RESULTS[name] = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "trace": traceback.format_exc().splitlines()[-4:],
        }


from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    _metadata_conflict_reason,
    _qualification_gaps,
    _qualification_label,
    build_resolution_envelope,
    ResolutionEnvelope,
    SourceRequest,
    SourceResolver,
)

BODY = b"%PDF-1.4 r4b06-review-payload"
DIGEST = hashlib.sha256(BODY).hexdigest()


def sidecar(**overrides) -> dict:
    payload = {
        "schema_version": "1.0",
        "canonical_entity_id": "ent-acme",
        "display_name": "Acme",
        "market": "US",
        "security_id": "ACME",
        "source_title": "Acme 2025 Annual Report",
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "period_end": "2025-12-31",
        "filing_date": "2026-02-20",
        "form_type": "10-K",
        "provider": "sec",
        "provider_document_id": "doc-1",
        "source_url": "https://sec.gov/x/2025",
        "content_sha256": DIGEST,
        "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar",
        "collector_version": "1.0",
    }
    payload.update(overrides)
    return payload


def write_copy(directory: Path, sc: dict, name: str = "2025.pdf", body: bytes = BODY) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    target.write_bytes(body)
    (directory / f"{name}.source.json").write_text(
        json.dumps(sc, ensure_ascii=False), encoding="utf-8"
    )
    return target


def root(root_id: str, path: Path, kind: str, priority: int) -> RootSpec:
    return RootSpec(
        root_id,
        path,
        kind,
        priority=priority,
        adapter_id="company_raw_v1" if kind == "company_raw" else "sidecar_filing_v1",
        read_only=kind != "company_raw",
        reusable_for_filing=True,
        canonical_write_target="companies" if kind == "company_raw" else None,
    )


def catalog(tmp: Path, roots: list[RootSpec]) -> SourceCatalog:
    cat = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw", "directory"),
            roots=tuple(roots),
        )
    )
    cat.scan()
    return cat


def request(**overrides) -> SourceRequest:
    base = dict(
        entity="Acme",
        market="US",
        security_id="ACME",
        document_kind="annual_report",
        form_type="10-K",
        fiscal_year=2025,
        provider="sec",
        provider_document_id="doc-1",
        as_of_date="2026-08-10",
        mode="exact",
    )
    base.update(overrides)
    return SourceRequest(**base)


def qualified(tmp: Path, sc: dict):
    base = tmp / "companies"
    write_copy(base / "Acme" / "raw" / "financial_reports" / "annual", sc)
    cat = catalog(tmp, [root("company_raw", base, "company_raw", 10)])
    res = SourceResolver(cat).resolve(request())
    env = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    return cat, res, env


# ---------------------------------------------------------------- claim 1 ---
def c1_additive() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-add-"))
    cat, res, env = qualified(tmp, sidecar())
    field = ResolutionEnvelope.__dataclass_fields__["qualification"]
    empty = build_resolution_envelope(
        replace(res, matches=()), store=cat.store, project_root=tmp
    )
    return {
        "default_is_none": field.default is None,
        "field_type": str(field.type),
        "no_handle_qualification": empty.qualification,
        "served_label": env.qualification,
        "schema_version": env.to_dict()["envelope_schema_version"],
        "to_dict_has_key": "qualification" in env.to_dict(),
        "to_dict_keys": sorted(env.to_dict()),
        "handle_facts": {
            "entity_ids": list(res.matches[0].entity_ids),
            "fiscal_year": res.matches[0].fiscal_year,
            "published_date": res.matches[0].published_date,
            "https_url": res.matches[0].https_url,
            "capture_ready": res.matches[0].capture_ready,
            "missing_capture_fields": list(res.matches[0].missing_capture_fields),
            "hashes_64": len(res.matches[0].content_sha256) == 64,
            "source_id": res.matches[0].source_id,
        },
    }


# ------------------------------------------------- claim 4 (reachability) ---
def c4_missing_url() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-nourl-"))
    base = tmp / "companies"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(source_url=None),
    )
    cat = catalog(tmp, [root("company_raw", base, "company_raw", 10)])
    res = SourceResolver(cat).resolve(request())
    env = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    return {
        "status": res.status.value,
        "matches": len(res.matches),
        "trace": list(res.debug_trace),
        "qualification": env.qualification,
        "outcome": env.outcome,
    }


def c4_no_fiscal_year() -> dict:
    """A served document with NO fiscal year: the year is removed from the
    sidecar AND from the title (the resolver derives a year from title tokens),
    while the capture date stays so the handle is still capture_ready."""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-nofy-"))
    base = tmp / "companies"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(
            source_title="Acme Annual Report",
            fiscal_year=None,
            period_end=None,
            filing_date="2026-02-20",
        ),
        name="report.pdf",
    )
    cat = catalog(tmp, [root("company_raw", base, "company_raw", 10)])
    res = SourceResolver(cat).resolve(request(fiscal_year=None))
    env = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    h = res.matches[0] if res.matches else None
    res_la = SourceResolver(cat).resolve(
        request(fiscal_year=None, mode="latest_as_of")
    )
    env_la = build_resolution_envelope(res_la, store=cat.store, project_root=tmp)
    return {
        "exact_mode": {
            "status": res.status.value,
            "matches": len(res.matches),
            "handle_fiscal_year": None if h is None else h.fiscal_year,
            "handle_published_date": None if h is None else h.published_date,
            "handle_capture_ready": None if h is None else h.capture_ready,
            "qualification": env.qualification,
            "outcome": env.outcome,
        },
        "latest_as_of_mode": {
            "status": res_la.status.value,
            "matches": len(res_la.matches),
            "qualification": env_la.qualification,
            "outcome": env_la.outcome,
        },
        "plan_rule_expectation": "b06-plan.md s2/s4: no fiscal_year => blocked/period_missing",
    }


def c4_identity_via_db_surgery() -> dict:
    """`identity_missing`: no document_entities rows.  Pipeline always inserts at
    least `unresolved:<root>` (scanner.py:1026-1033), so this needs DB surgery on
    a TEMP catalog to see whether the rule is even wired to the envelope."""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-noid-"))
    cat, res, env = qualified(tmp, sidecar())
    with cat.store.transaction() as con:
        removed = con.execute("DELETE FROM document_entities").rowcount
    res2 = SourceResolver(cat).resolve(request())
    env2 = build_resolution_envelope(res2, store=cat.store, project_root=tmp)
    return {
        "entity_rows_removed": removed,
        "status": res2.status.value,
        "matches": len(res2.matches),
        "handle_entity_ids": [list(m.entity_ids) for m in res2.matches],
        "qualification_after_surgery": env2.qualification,
        "baseline_qualification": env.qualification,
        "pipeline_always_links_an_entity": True,
    }


def c4_identity_no_entity_row_from_scan() -> dict:
    """Try to get an empty entity_ids through the SCANNER (no surgery): sidecar
    without canonical_entity_id, path that yields no company name."""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-scan-"))
    base = tmp / "companies"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(canonical_entity_id=None, display_name=None),
    )
    cat = catalog(tmp, [root("company_raw", base, "company_raw", 10)])
    res = SourceResolver(cat).resolve(request())
    rows = cat.store.fetchall("SELECT * FROM document_entities")
    return {
        "status": res.status.value,
        "matches": len(res.matches),
        "entity_rows": [dict(r) for r in rows],
        "handle_entity_ids": [list(m.entity_ids) for m in res.matches],
    }


def c4_forged_handle_preview() -> dict:
    """Can the ENVELOPE BUILDER emit preview?  (forged handle = no in-package
    producer can make it)."""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-prev-"))
    cat, res, env = qualified(tmp, sidecar())
    forged = replace(
        res.matches[0], https_url=None, missing_capture_fields=("https_url",)
    )
    env2 = build_resolution_envelope(
        replace(res, matches=(forged,)), store=cat.store, project_root=tmp
    )
    return {"qualification": env2.qualification, "outcome": env2.outcome}


def c4_two_matches_label() -> dict:
    """AMBIGUOUS resolutions carry several matches (resolver.py:1488-1505).  What
    label rides such an envelope?"""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-amb-"))
    cat, res, env = qualified(tmp, sidecar())
    h = res.matches[0]
    env2 = build_resolution_envelope(
        replace(res, matches=(h, replace(h, canonical_location_id="second"))),
        store=cat.store,
        project_root=tmp,
    )
    return {
        "qualification": env2.qualification,
        "note": "matches[0] qualified even though the response is not a single selection",
    }


# ------------------------------------------------------- claim 5 (fuzz) ----
class FakeStore:
    def __init__(self, payload, raise_on_fetch=False, row=None):
        self._payload = payload
        self._raise = raise_on_fetch
        self._row = row

    def fetchone(self, sql, params=()):  # noqa: ANN001
        if self._raise:
            raise RuntimeError("injected fetchone failure")
        if self._row is not None:
            return self._row
        return {"metadata_json": self._payload}


def c5_fuzz() -> dict:
    big = '{"r4_provenance": {"fields": {"pad": {"value": "' + "x" * 10_000_000 + '"}}}}'
    shapes = {
        "payload_list": "[]",
        "payload_string": '"a string"',
        "payload_null": "null",
        "payload_int": "17",
        "payload_bytes": b'{"r4_provenance": {"fields": {"title": {"conflicts": ["x"]}}}}',
        "payload_bytes_bad": b"{not json",
        "not_json": "{not json",
        "reserved_string": '{"r4_provenance": "not an object"}',
        "reserved_list": '{"r4_provenance": []}',
        "reserved_null": '{"r4_provenance": null}',
        "fields_list_empty": '{"r4_provenance": {"fields": []}}',
        "fields_list_of_pairs": '{"r4_provenance": {"fields": [["title", {"conflicts": ["x"]}]]}}',
        "fields_string": '{"r4_provenance": {"fields": "nope"}}',
        "fields_null": '{"r4_provenance": {"fields": null}}',
        "record_string": '{"r4_provenance": {"fields": {"title": "not a record"}}}',
        "record_list_of_dicts": '{"r4_provenance": {"fields": {"title": [{"conflicts": ["x"]}]}}}',
        "record_nested_list": '{"r4_provenance": {"fields": {"title": [[{"conflicts": ["x"]}]]}}}',
        "conflicts_string": '{"r4_provenance": {"fields": {"title": {"conflicts": "yes"}}}}',
        "conflicts_dict": '{"r4_provenance": {"fields": {"title": {"conflicts": {"a": 1}}}}}',
        "conflicts_empty_list": '{"r4_provenance": {"fields": {"title": {"conflicts": []}}}}',
        "conflicts_zero": '{"r4_provenance": {"fields": {"title": {"conflicts": 0}}}}',
        "conflicts_none": '{"r4_provenance": {"fields": {"title": {"conflicts": None}}}}',
        "fields_nonstr_keys": '{"r4_provenance": {"fields": {"title": {"conflicts": ["x"]}}}}',
        "empty_object": "{}",
        "empty_string": "",
        "null_string": "null",
        "big_10mb": big,
    }
    results = {}
    for name, payload in shapes.items():
        started = time.perf_counter()
        try:
            value = _metadata_conflict_reason(FakeStore(payload), "doc-1")
            results[name] = {
                "result": value,
                "elapsed_s": round(time.perf_counter() - started, 4),
            }
        except Exception as exc:  # noqa: BLE001
            results[name] = {
                "RAISED": f"{type(exc).__name__}: {exc}",
                "elapsed_s": round(time.perf_counter() - started, 4),
            }
    edge = {}
    for name, store, docid in (
        ("store_none", None, "doc-1"),
        ("document_id_none", FakeStore("{}"), None),
        ("document_id_empty", FakeStore("{}"), ""),
        ("row_none", FakeStore("{}", row=None), "doc-1"),
        ("fetchone_raises", FakeStore("{}", raise_on_fetch=True), "doc-1"),
        ("row_without_column", FakeStore("{}", row={"other": 1}), "doc-1"),
    ):
        try:
            edge[name] = _metadata_conflict_reason(store, docid)
        except Exception as exc:  # noqa: BLE001
            edge[name] = f"RAISED {type(exc).__name__}: {exc}"
    return {"shapes": results, "edges": edge}


# --------------------------------------- claim 3 (read side agreement) -----
def c3_read_side_agreement() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-read-"))
    base = tmp / "companies"
    dropbox = tmp / "Dropbox" / "Stock"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(source_title="Acme 2025 Annual Report"),
    )
    cat = catalog(
        tmp,
        [
            root("company_raw", base, "company_raw", 10),
            root("dropbox_stock", dropbox, "directory", 10),
        ],
    )
    write_copy(dropbox, sidecar(source_title="Acme 2025 Annual Report (restated)"))
    cat.scan()
    res = SourceResolver(cat).resolve(request())
    env = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    candidates = cat.query_filing_candidates(
        document_kind="annual_report", source_statuses=("active",)
    )
    doc_id = res.matches[0].document_id
    row = [c for c in candidates if c["document_id"] == doc_id]
    out = {
        "envelope_label": env.qualification,
        "envelope_outcome": env.outcome,
        "read_side_metadata_status": row[0]["metadata_status"] if row else None,
        "read_side_conflicts": row[0]["conflicts"] if row else None,
        "document_id": doc_id,
    }
    # malformed shared-column content: same column, same document
    malformed = {}
    for name, payload in (
        ("fields_list_empty", '{"r4_provenance": {"fields": []}}'),
        ("fields_list_of_pairs", '{"r4_provenance": {"fields": [["title", {"conflicts": ["x"]}]]}}'),
        ("reserved_string", '{"r4_provenance": "not an object"}'),
        ("not_json", "{not json"),
        ("record_string", '{"r4_provenance": {"fields": {"title": "not a record"}}}'),
    ):
        with cat.store.transaction() as con:
            con.execute(
                "UPDATE documents SET metadata_json=? WHERE document_id=?",
                (payload, doc_id),
            )
        try:
            rows = cat.query_filing_candidates(
                document_kind="annual_report", source_statuses=("active",)
            )
            hit = [c for c in rows if c["document_id"] == doc_id]
            read_side = hit[0]["metadata_status"] if hit else "not_returned"
        except Exception as exc:  # noqa: BLE001
            read_side = f"RAISED {type(exc).__name__}: {exc}"
        try:
            b06 = _metadata_conflict_reason(cat.store, doc_id)
            label = _qualification_label(_qualification_gaps(res.matches[0]), b06)
        except Exception as exc:  # noqa: BLE001
            label = f"RAISED {type(exc).__name__}: {exc}"
        malformed[name] = {
            "read_side_metadata_status": read_side,
            "b06_conflict_reason": b06,
            "b06_label": label,
        }
    out["malformed_shared_column"] = malformed
    return out


def c3_store_none_label() -> dict:
    """No store => no conflict evidence => what label?"""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-nostore-"))
    base = tmp / "companies"
    dropbox = tmp / "Dropbox" / "Stock"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(source_title="Acme 2025 Annual Report"),
    )
    cat = catalog(
        tmp,
        [
            root("company_raw", base, "company_raw", 10),
            root("dropbox_stock", dropbox, "directory", 10),
        ],
    )
    write_copy(dropbox, sidecar(source_title="Acme 2025 Annual Report (restated)"))
    cat.scan()
    res = SourceResolver(cat).resolve(request())
    with_store = build_resolution_envelope(res, store=cat.store, project_root=tmp)
    no_store = build_resolution_envelope(res, store=None, project_root=tmp)
    return {
        "with_store": with_store.qualification,
        "store_none": no_store.qualification,
        "read_side_status": cat.query_filing_candidates(
            document_kind="annual_report", source_statuses=("active",)
        )[0]["metadata_status"],
    }


# --------------------------------------------- claim 2 (consumer side) -----
def c2_consumer() -> dict:
    sys.path.insert(0, str(FILING / "scripts"))
    import filing_contracts as fc  # noqa: PLC0415

    tmp = Path(tempfile.mkdtemp(prefix="b06rv-cons-"))
    cat, res, env = qualified(tmp, sidecar())
    payload = env.to_dict()
    payload["qualification"] = {
        "label": "blocked",
        "gaps": [],
        "reason": "field conflict recorded for: title",
    }
    out = {
        "consumer_outcomes": sorted(fc.RESOLUTION_ENVELOPE_OUTCOMES),
        "has_blocked": "blocked" in fc.RESOLUTION_ENVELOPE_OUTCOMES,
        "schema_version_expected": fc.RESOLUTION_ENVELOPE_SCHEMA_VERSION,
    }
    try:
        normalized = fc.validate_resolution_envelope(payload)
        out["blocked_qualification_accepted"] = True
        out["qualification_survives_normalization"] = normalized.get("qualification")
        out["outcome_unchanged"] = normalized.get("outcome")
    except Exception as exc:  # noqa: BLE001
        out["blocked_qualification_accepted"] = f"RAISED {type(exc).__name__}: {exc}"
    bad = dict(payload)
    bad["outcome"] = "blocked"
    try:
        fc.validate_resolution_envelope(bad)
        out["outcome_blocked_accepted"] = True
    except Exception as exc:  # noqa: BLE001
        out["outcome_blocked_accepted"] = f"RAISED {type(exc).__name__}: {exc}"
    return out


def c2b_blocked_looks_like_success() -> dict:
    """Question b: with a real bundle attached, what do the OTHER envelope keys
    say about a conflict-blocked response?"""
    tmp = Path(tempfile.mkdtemp(prefix="b06rv-looks-"))
    base = tmp / "companies"
    dropbox = tmp / "Dropbox" / "Stock"
    write_copy(
        base / "Acme" / "raw" / "financial_reports" / "annual",
        sidecar(source_title="Acme 2025 Annual Report"),
    )
    cat = catalog(
        tmp,
        [
            root("company_raw", base, "company_raw", 10),
            root("dropbox_stock", dropbox, "directory", 10),
        ],
    )
    write_copy(dropbox, sidecar(source_title="Acme 2025 Annual Report (restated)"))
    cat.scan()
    res = SourceResolver(cat).resolve(request())
    bundle = cat.bundle_for_resolution(res)
    env = build_resolution_envelope(
        res,
        store=cat.store,
        bundle=bundle,
        journal=None,
        project_root=tmp,
    )
    payload = env.to_dict()
    return {
        "qualification": payload["qualification"],
        "outcome": payload["outcome"],
        "download_events": payload["download_events"],
        "bundle_status": payload["bundle_status"],
        "bundle_hash_present": bool(payload["bundle_hash"]),
        "prompt_injection_status": payload["prompt_injection_status"],
        "handle_capture_ready": res.matches[0].capture_ready,
        "handle_missing_fields": list(res.matches[0].missing_capture_fields),
        "read_side_metadata_status": cat.query_filing_candidates(
            document_kind="annual_report", source_statuses=("active",)
        )[0]["metadata_status"],
    }


def main() -> None:
    for name, fn in (
        ("claim1_additive", c1_additive),
        ("claim4_missing_url", c4_missing_url),
        ("claim4_no_fiscal_year", c4_no_fiscal_year),
        ("claim4_identity_db_surgery", c4_identity_via_db_surgery),
        ("claim4_identity_from_scan", c4_identity_no_entity_row_from_scan),
        ("claim4_forged_handle_preview", c4_forged_handle_preview),
        ("claim4_two_matches_label", c4_two_matches_label),
        ("claim5_fuzz_conflict_reader", c5_fuzz),
        ("claim3_read_side_agreement", c3_read_side_agreement),
        ("claim3_store_none_label", c3_store_none_label),
        ("claim2_consumer_validator", c2_consumer),
        ("claim2b_blocked_looks_like_success", c2b_blocked_looks_like_success),
    ):
        cap(name, fn)
    target = Path(__file__).with_name("b06_review_probe.json")
    target.write_text(
        json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("wrote", target)


if __name__ == "__main__":
    main()
