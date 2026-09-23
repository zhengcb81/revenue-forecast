"""I-07-C clause-1 per-root verification (attempt-support, not a product
command): independently re-hash BOTH X04 root copies and cross-check them
against the manifest pin, the build-time copy record and the catalog's
per-location rows (content sha equal + distinct root locations).

Writes evidence/x04_hash_verify.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from i07c_common import (CASES, EVID, load_manifest, read_json,
                         sample_smallest, sha256_file, write_json)


def main() -> int:
    sample = sample_smallest()
    cwroot = CASES / "X04-multiroot" / "cwroot"
    roots = ("companies", "companies_mirror")
    root_ids = ("companies_root_a", "companies_root_b")
    rehash = []
    for root_dir, root_id in zip(roots, root_ids):
        rel = Path(root_dir) / sample["entity_dir"] / "raw" \
            / "financial_reports" / sample["kind_dir"] / sample["file_name"]
        raw_path = cwroot / rel
        side_path = cwroot / (str(rel) + ".source.json")
        rehash.append({
            "root_id": root_id,
            "root_dir": root_dir,
            "raw_path": str(raw_path),
            "raw_sha256": sha256_file(raw_path),
            "raw_bytes": raw_path.stat().st_size,
            "sidecar_path": str(side_path),
            "sidecar_sha256": sha256_file(side_path),
        })
    dump = read_json(EVID / "X04-multiroot" / "scan1" / "catalog_dump.json")
    filing_locs = [l for l in dump["locations"]
                   if l["relative_path"].endswith(sample["file_name"])]
    payload = {
        "sample_id": sample["id"],
        "manifest_raw_sha256": sample["raw_sha256"],
        "rehash": rehash,
        "content_sha_equal_between_roots":
            rehash[0]["raw_sha256"] == rehash[1]["raw_sha256"],
        "both_equal_manifest_pin":
            all(r["raw_sha256"] == sample["raw_sha256"] for r in rehash),
        "distinct_root_locations": sorted({l["root_id"] for l in filing_locs}),
        "filing_location_rows": [
            {"root_id": l["root_id"], "relative_path": l["relative_path"],
             "source_id": l["source_id"], "document_id": l["document_id"],
             "observed_size": l["observed_size"], "role": l["role"]}
            for l in filing_locs],
        "distinct_source_ids_across_roots":
            sorted({l["source_id"] for l in filing_locs}),
        "distinct_document_ids_across_roots":
            sorted({l["document_id"] for l in filing_locs}),
        "sources_rows_for_that_content":
            [s for s in dump["sources"]
             if s["content_sha256"] == sample["raw_sha256"]],
        "documents_rows_total": len(dump["documents"]),
    }
    payload["measured_conclusion"] = (
        "same bytes in two roots => %d source row(s), %d document row(s), "
        "%d location row(s) across roots %s" % (
            len(payload["sources_rows_for_that_content"]),
            payload["documents_rows_total"], len(filing_locs),
            payload["distinct_root_locations"]))
    write_json(EVID / "x04_hash_verify.json", payload)
    print(json.dumps({k: payload[k] for k in (
        "content_sha_equal_between_roots", "both_equal_manifest_pin",
        "distinct_root_locations", "measured_conclusion")},
        ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
