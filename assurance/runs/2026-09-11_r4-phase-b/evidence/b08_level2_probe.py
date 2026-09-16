"""B08 level-2 real-byte probe: query -> resolve -> read VERIFIED bytes, twice.

Runs against the ISOLATED catalog built by b08_level2_run.py (which references a real
production directory read-only).  It exercises the parts of L02/L03/L12 that need real
bytes, and re-checks the zero-side-effect evidence afterwards:

  * query_filing_candidates on the isolated catalog (real documents, real locations),
  * SourceResolver.resolve -> handle, then read_verified_bytes (B03's entry point) TWICE
    with the requested content_sha256, recording status/reason/bytes/digest match,
  * a tamper check: read with a WRONG expected hash must be an explicit failure, never
    bytes (the B03 contract),
  * before/after state of the real directory and the production catalog.

ASCII-only console output (this console mangles CJK paths).

    python b08_level2_probe.py [--isolated-root PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import b08_isolated_env as env  # noqa: E402

WIKI_SRC = env.WIKI_SRC
DEFAULT_ISOLATED = Path(env.tempfile.gettempdir()) / "b08-level2-isolated"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--isolated-root", type=Path, default=DEFAULT_ISOLATED)
    parser.add_argument("--out", type=Path, default=HERE / "b08-level2-probe.json")
    args = parser.parse_args(argv)

    isolated = args.isolated_root.resolve()
    database = isolated / ".source_catalog" / "catalog.sqlite3"
    if not database.is_file():
        raise SystemExit(f"no isolated catalog at {database} - run b08_level2_run.py first")

    evidence = json.loads((HERE / "b08-level2-evidence.json").read_text(encoding="utf-8"))
    real_root = Path(evidence["real_root"])

    sys.path.insert(0, str(WIKI_SRC))
    from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: PLC0415
    from company_wiki.source_catalog.models import RootSpec  # noqa: PLC0415
    from company_wiki.source_catalog.resolver import (  # noqa: PLC0415
        SourceRequest,
        SourceResolver,
    )

    spec = RootSpec("r4b08_real_sample", real_root, "directory", priority=10,
                    adapter_id="sidecar_filing_v1", read_only=True,
                    reusable_for_filing=True, canonical_write_target=None)
    config = CatalogConfig(project_root=isolated, catalog_dir=isolated / ".source_catalog",
                           reusable_root_kinds=("directory",), roots=(spec,))
    catalog = SourceCatalog(config)

    before_real = env._real_root_state(real_root)
    before_production = env._production_state()

    candidates = catalog.query_filing_candidates(
        document_kind="annual_report", source_statuses=("active",)
    )
    probe: dict = {"candidates": len(candidates)}

    document = None
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT d.document_id, d.title, d.document_kind, s.content_sha256, "
            "l.absolute_path, d.metadata_json FROM documents d "
            "LEFT JOIN sources s ON s.source_id = d.primary_source_id "
            "LEFT JOIN locations l ON l.document_id = d.document_id "
            "WHERE d.document_kind = 'annual_report' AND l.absolute_path IS NOT NULL "
            "ORDER BY d.document_id LIMIT 1"
        ).fetchone()
        entity_row = None
        if row is not None:
            entity_row = connection.execute(
                "SELECT e.name FROM document_entities de JOIN entities e "
                "ON e.entity_id = de.entity_id WHERE de.document_id = ? "
                "AND e.name NOT LIKE 'Unresolved%' LIMIT 1", (row[0],)
            ).fetchone()
    if row is not None:
        acquisition = {}
        try:
            acquisition = (json.loads(row[5] or "{}").get("acquisition") or {})
        except (TypeError, ValueError):
            acquisition = {}
        # The issuer NAME the resolver's entity gate can anchor on lives in the sidecar
        # metadata (`acquisition.company_name`).  The catalog's `entities` table does NOT
        # have it: a non-`company_raw` root gets `Unresolved (<root_id>)` because the
        # scanner derives entity names from PATHS only (`scanner._infer_company`), never
        # from the sidecar.  Recorded as a finding; the gate itself accepts the metadata
        # name (resolver._entity_matches unions metadata ticker/security_id/company_name).
        company_name = acquisition.get("company_name") or (
            (acquisition.get("candidate") or {}).get("entity")
        )
        document = {"document_id": row[0], "title": str(row[1])[:60],
                    "document_kind": row[2], "content_sha256": row[3],
                    "path_name_len": len(Path(str(row[4])).name),
                    "entity": entity_row[0] if entity_row else None,
                    "company_name": company_name,
                    "company_name_len": len(company_name) if company_name else 0,
                    "company_name_sha256_16": (env.hashlib.sha256(
                        company_name.encode("utf-8")).hexdigest()[:16]
                        if company_name else None),
                    "market": acquisition.get("market"),
                    "security_id": acquisition.get("security_id"),
                    "entity_source": ("sidecar_metadata_acquisition_company_name"
                                      if company_name else "none")}
        probe["document"] = document

    if document is not None and document["company_name"]:
        # The request mirrors the document's OWN verified identity.  Two earlier versions
        # of this probe were vacuous: a fabricated entity (`r4b08`) and the catalog's
        # unresolved entity row both match nothing, so the read path never ran.
        # market/security_id stay None on purpose: with a request identity present the
        # resolver fail-closes on a candidate whose metadata lacks market
        # (_identity_matches -> "missing_fail_closed"), which would test that gate instead
        # of the byte-read path this probe exists for.
        request = SourceRequest(
            entity=document["company_name"],
            market=None,
            security_id=None,
            document_kind="annual_report",
            form_type=None,
            fiscal_year=None,
            provider=None,
            provider_document_id=None,
            as_of_date="2026-12-31",
            mode="latest_as_of",
        )
        request_id = request.request_id
        probe["request"] = {"entity_sha256_16": document["company_name_sha256_16"],
                            "entity_len": document["company_name_len"],
                            "document_kind": "annual_report", "market": None,
                            "security_id": None, "mode": "latest_as_of",
                            "as_of_date": "2026-12-31", "request_id": request_id}
        resolution = SourceResolver(catalog).resolve(request)
        probe["resolution_status"] = str(getattr(resolution, "status", ""))
        probe["resolution_reason"] = str(getattr(resolution, "reason", ""))[:120]
        probe["resolution_matches"] = len(resolution.matches)
        probe["resolution_trace_head"] = [str(item)[:80] for item in
                                          (getattr(resolution, "debug_trace", ()) or ())[:6]]
        if resolution.matches:
            handle = resolution.matches[0]
            probe["handle_document_matches_row"] = handle.document_id == document["document_id"]
            # Independent baseline: the digest recorded when the REAL file itself was
            # hashed (b08_isolated_env._real_root_state, before/after the scan).  The
            # bytes the resolver serves must reproduce THIS digest - not merely its own
            # catalog claim - for the read to count as a verified real-byte read.
            real_digests = {entry["sha256"] for entry in
                            evidence["real_root_before"]["files"].values()}
            reads = []
            for attempt in (1, 2):
                result = SourceResolver(catalog).read_verified_bytes(
                    handle, expected_content_sha256=document["content_sha256"]
                )
                data = getattr(result, "data", None)
                reads.append({
                    "attempt": attempt,
                    "status": str(getattr(result, "status", "")),
                    "ok": bool(getattr(result, "ok", False)),
                    "reason": str(getattr(result, "reason", ""))[:80],
                    "detail": str(getattr(result, "detail", ""))[:80],
                    "bytes": len(data) if data else 0,
                    "byte_size": getattr(result, "byte_size", None),
                    "bytes_source": str(getattr(result, "bytes_source", ""))[:60],
                    "data_sha256_16": (env.hashlib.sha256(data).hexdigest()[:16]
                                       if data else None),
                    "digest_ok": bool(data) and (
                        env.hashlib.sha256(data).hexdigest()
                        == document["content_sha256"]),
                    "digest_in_real_root_snapshot": bool(data) and (
                        env.hashlib.sha256(data).hexdigest() in real_digests),
                })
            probe["verified_reads"] = reads
            tampered = SourceResolver(catalog).read_verified_bytes(
                handle, expected_content_sha256="0" * 64
            )
            tamper_data = getattr(tampered, "data", None)
            probe["tamper_probe"] = {
                "status": str(getattr(tampered, "status", "")),
                "ok": bool(getattr(tampered, "ok", False)),
                "reason": str(getattr(tampered, "reason", ""))[:80],
                "detail": str(getattr(tampered, "detail", ""))[:80],
                "bytes": len(tamper_data) if tamper_data else 0,
                "no_bytes_returned": tamper_data is None,
            }
            # L06 (PARTIAL, deliberately): the read path while ANOTHER reader holds the
            # real file open.  A read handle only, because a write handle would require
            # opening production bytes for writing - not authorized.  So this proves
            # reader coexistence under a shared read, NOT the B-DR-07 writer boundary;
            # the report must not claim more than this.
            location_path = Path(str(row[4]))
            with location_path.open("rb") as held:
                held.read(4096)
                occupied = SourceResolver(catalog).read_verified_bytes(
                    handle, expected_content_sha256=document["content_sha256"]
                )
            occupied_data = getattr(occupied, "data", None)
            probe["open_while_reader_holds_file"] = {
                "status": str(getattr(occupied, "status", "")),
                "ok": bool(getattr(occupied, "ok", False)),
                "bytes": len(occupied_data) if occupied_data else 0,
                "digest_ok": bool(occupied_data) and (
                    env.hashlib.sha256(occupied_data).hexdigest()
                    == document["content_sha256"]),
                "held_handle_mode": "rb (read-only; no production write open)",
            }

    after_real = env._real_root_state(real_root)
    after_production = env._production_state()
    payload = {
        "probe": probe,
        "real_root_unchanged": before_real == after_real,
        "production_catalog_unchanged": before_production == after_production,
        # Verbatim states, so the equality above is checkable from the file instead of
        # being a bare boolean (metadata ONLY - the production database is never opened).
        "real_root_before": before_real,
        "real_root_after": after_real,
        "production_catalog_before": before_production,
        "production_catalog_after": after_production,
        "real_files_hashed": before_real["file_count"],
        "isolated_root": str(isolated),
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    # ensure_ascii for the CONSOLE only: this console is GBK and would mangle the CJK
    # identity values, while the evidence file keeps them verbatim.
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
