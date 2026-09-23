#!/usr/bin/env python
"""F-EE1 two-end mint verification (oracle §1, frozen evidence pins).

Recomputes BOTH request_id mints from the live E2E-EXPAND evidence using the
REAL company-wiki code (iso copy): the ORIGINAL caller request identity (E1,
journal row key) and the canonical_writer exact_request identity (E2,
resolution key).  A match on both ends proves the divergence root cause with
the product's own hash function (resolver.py:625-629 _json_hash), offline.

argv: --iso-cw-src PATH --evidence-dir PATH(jsonl/txt from E2E s1) --out PATH
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

JOURNAL_ROW_ID = (
    "urn:company-wiki:source-request:sha256:"
    "e8177b377da8fc80f8e72695535cf97a5282d9261549634523705bbdd8d53ecb"
)
RESOLUTION_ID = (
    "urn:company-wiki:source-request:sha256:"
    "47c3a925dc2ac33af0b343f187aba417961013837bf4304697234834c5e7e993"
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso-cw-src", type=Path, required=True)
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    sys.path.insert(0, str(args.iso_cw_src))
    from company_wiki.source_catalog import SourceRequest  # noqa: E402

    journal_rows = json.loads(
        (args.evidence_dir / "journal_rows.json").read_text(encoding="utf-8"))
    envelope = json.loads(
        (args.evidence_dir / "envelope.json").read_text(encoding="utf-8"))
    stdout = json.loads(
        (args.evidence_dir / "s1_fetch1_stdout.txt").read_text(encoding="utf-8"))
    request_file = json.loads(
        (args.evidence_dir / "request.json").read_text(encoding="utf-8"))
    handle = stdout["handle"]

    observed = {
        "journal_row_request_id": journal_rows[0]["request_id"],
        "journal_row_outcome": journal_rows[0]["outcome"],
        "envelope_handle_request_id": envelope["handle_request_id"],
        "envelope_outcome": envelope["outcome"],
        "envelope_download_events": envelope["download_events"],
        "ff_response_downloads": stdout["downloads"],
        "ff_response_status": stdout["status"],
        "ff_handle_request_id": handle["request_id"],
        "handle_provider": handle["provider"],
        "handle_provider_document_id": handle["provider_document_id"],
        "handle_form_type": handle["form_type"],
        "handle_fiscal_period": handle["fiscal_period"],
        "handle_language": handle["language"],
        "source_request_json": request_file,
    }

    # E1 — the identity the JOURNAL row was minted from: the caller's original
    # request as FF normalized it (fetch_filing.py:706-715 adds entity/market/
    # security_id from identify; mode absent -> None, cli --mode default None).
    original = SourceRequest(
        entity="宁德时代",
        market="CN",
        security_id="300750",
        document_kind="annual_report",
        fiscal_year=2025,
        as_of_date="2026-09-23",
    )

    # E2 — the identity the RESOLUTION was minted from: canonical_writer.py
    # :194-207 exact_request (candidate fills form_type/fiscal_period/language/
    # provider/provider_document_id; mode NOT carried -> None). Candidate field
    # values come from the handle (written from the sidecar, which records the
    # candidate verbatim: canonical_writer.py:359-364).
    exact = SourceRequest(
        entity="宁德时代",
        market="CN",
        security_id="300750",
        document_kind="annual_report",
        form_type=handle["form_type"],
        fiscal_year=2025,
        fiscal_period=handle["fiscal_period"],
        language=handle["language"],
        provider=handle["provider"],
        provider_document_id=handle["provider_document_id"],
        as_of_date="2026-09-23",
    )

    result = {
        "observed": observed,
        "e1_journal_mint": {
            "identity_dict": original.identity_dict(),
            "recomputed_request_id": original.request_id,
            "evidence_request_id": observed["journal_row_request_id"],
            "match": original.request_id == observed["journal_row_request_id"]
            == JOURNAL_ROW_ID,
        },
        "e2_resolution_mint": {
            "identity_dict": exact.identity_dict(),
            "recomputed_request_id": exact.request_id,
            "evidence_request_id": envelope["handle_request_id"],
            "match": exact.request_id == envelope["handle_request_id"]
            == RESOLUTION_ID,
        },
        "divergence_fields": sorted(
            key
            for key in original.identity_dict()
            if original.identity_dict()[key] != exact.identity_dict()[key]
        ),
    }
    result["both_ends_proven"] = bool(
        result["e1_journal_mint"]["match"] and result["e2_resolution_mint"]["match"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "e1_match": result["e1_journal_mint"]["match"],
        "e2_match": result["e2_resolution_mint"]["match"],
        "divergence_fields": result["divergence_fields"],
        "both_ends_proven": result["both_ends_proven"],
    }, ensure_ascii=False))
    return 0 if result["both_ends_proven"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
