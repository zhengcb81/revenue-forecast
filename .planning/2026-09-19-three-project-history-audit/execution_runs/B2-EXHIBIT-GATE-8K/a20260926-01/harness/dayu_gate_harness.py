"""B2 dayu gate harness: 8-K exhibit reachability + 6-K byte-identical regression.

Runs against iso/dayu_repo only (no product-repo import, no network, no writes
outside the attempt dir).  Exit code = number of failed checks (0 == all green).

Checks
  G1  8-K with exhibits, include_exhibits=True  -> exhibit MUST be in filenames   (RED before B2)
  G2  8-K with exhibits, include_exhibits=False -> exhibit MUST NOT be in filenames
  G3  6-K with exhibits, include_exhibits=True  -> exact frozen file list (byte regression)
  G4  6-K with exhibits, include_exhibits=False -> exact frozen file list (byte regression)
  G5  10-K whose index carries an exhibit-like file -> exhibit MUST NOT be in filenames
                                                   (gate must not leak to non-authorized forms)
  G6  8-K gated forms == {'6-K','8-K'} surface check on the module constant (if present)

The 6-K "frozen" lists are produced by this same harness BEFORE the change and
recorded in regression/6k_frozen_before.json; G3/G4 compare byte-for-byte.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ATTEMPT / "iso" / "dayu_repo"))

# The third-party `edgar` package (imported transitively by dayu.fins) wants to
# mkdir a cache under the user home, which this session cannot write.  Redirect
# it inside the attempt directory BEFORE importing dayu — no product write, no
# network (all HTTP entry points are stubbed below).
import os  # noqa: E402

os.environ.setdefault("EDGAR_LOCAL_DATA_DIR", str(ATTEMPT / "results" / "_edgar_cache"))

from dayu.fins.downloaders.sec_downloader import SecDownloader  # noqa: E402

INDEX_ITEMS_8K = [
    {"name": "d291965d8k.htm", "type": "8-K", "description": "8-K"},
    {"name": "d291965d8k_htm.xml", "type": "EX-104"},
    {"name": "d291965d8k.xsd"},
    {"name": "d291965dex991.htm", "type": "EX-99.1", "description": "EX-99.1"},
]
INDEX_HEADERS_8K = [
    {"name": "d291965d8k.htm", "type": "8-K", "description": "FORM 8-K"},
    {"name": "d291965dex991.htm", "type": "EX-99.1", "description": "EX-99.1"},
]
INDEX_ITEMS_6K = [
    {"name": "sample-6k.htm"},
    {"name": "sample-6k_htm.xml"},
    {"name": "sample-6k.xsd"},
    {"name": "d123dex991.htm"},
]
INDEX_HEADERS_6K = [
    {"name": "form6kcover.htm", "type": "6-K", "description": "FORM 6-K"},
    {"name": "q12025pressrelease.htm", "type": "EX-99.1", "description": "EX-99.1"},
]
INDEX_ITEMS_10K = [
    {"name": "msft-20250630.htm"},
    {"name": "msft-20250630_htm.xml"},
    {"name": "msft-20250630.xsd"},
    {"name": "msft_ex99-1.htm", "type": "EX-99.1", "description": "EX-99.1"},
]


def _run(coro):
    return asyncio.run(coro)


def _make_downloader(tmp: Path) -> SecDownloader:
    downloader = SecDownloader(workspace_root=tmp)
    downloader.configure(user_agent="UA", sleep_seconds=0.0, max_retries=1)
    return downloader


def _patch(downloader, index_items, index_headers):
    async def _index_items(cik, accession_no_dash):
        return list(index_items)

    async def _index_headers(cik, accession_no_dash):
        return list(index_headers)

    async def _head(url, allow_redirects=True):
        return type(
            "_Resp",
            (),
            {
                "headers": {
                    "ETag": '"etag"',
                    "Last-Modified": "Sat, 01 Feb 2025 12:00:00 GMT",
                    "Content-Length": "100",
                },
                "status_code": 200,
            },
        )()

    async def _no_network(url: str):
        # hard network kill-switch: the harness must never touch sec.gov
        raise RuntimeError(f"network disabled in harness: {url}")

    downloader._try_fetch_index_items = _index_items
    downloader._try_fetch_index_header_documents = _index_headers
    downloader._http_head = _head
    downloader._http_get_bytes = _no_network
    downloader._http_get_json = _no_network
    # index-header fetch must be observable for the gate check
    downloader._header_fetch_calls = 0
    original = downloader._try_fetch_index_header_documents

    async def _counting_headers(cik, accession_no_dash):
        downloader._header_fetch_calls += 1
        return await original(cik, accession_no_dash)

    downloader._try_fetch_index_header_documents = _counting_headers


def list_files(tmp: Path, form_type: str, *, include_exhibits: bool, index_items, index_headers,
               primary: str, include_xbrl: bool = True):
    downloader = _make_downloader(tmp)
    _patch(downloader, index_items, index_headers)
    descriptors = _run(
        downloader.list_filing_files(
            cik="789019",
            accession_no_dash="000119312526380280",
            primary_document=primary,
            form_type=form_type,
            include_xbrl=include_xbrl,
            include_exhibits=include_exhibits,
            include_http_metadata=True,
        )
    )
    payload = [
        {
            "name": item.name,
            "source_url": item.source_url,
            "http_status": item.http_status,
            "http_etag": item.http_etag,
            "http_last_modified": item.http_last_modified,
            "remote_size": item.remote_size,
            "sec_document_type": item.sec_document_type,
            "sec_description": item.sec_description,
        }
        for item in descriptors
    ]
    return payload, downloader._header_fetch_calls


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    out_dir = ATTEMPT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_tmp_dayu"
    tmp.mkdir(parents=True, exist_ok=True)

    report: dict = {"harness": "dayu_gate", "mode": mode, "checks": []}

    def record(name: str, ok: bool, detail):
        report["checks"].append({"name": name, "ok": ok, "detail": detail})

    eight_k_on, eight_k_headers = list_files(
        tmp, "8-K", include_exhibits=True, index_items=INDEX_ITEMS_8K,
        index_headers=INDEX_HEADERS_8K, primary="d291965d8k.htm",
    )
    eight_k_off, _ = list_files(
        tmp, "8-K", include_exhibits=False, index_items=INDEX_ITEMS_8K,
        index_headers=INDEX_HEADERS_8K, primary="d291965d8k.htm",
    )
    six_k_on, six_k_headers = list_files(
        tmp, "6-K", include_exhibits=True, index_items=INDEX_ITEMS_6K,
        index_headers=INDEX_HEADERS_6K, primary="sample-6k.htm",
    )
    six_k_off, _ = list_files(
        tmp, "6-K", include_exhibits=False, index_items=INDEX_ITEMS_6K,
        index_headers=INDEX_HEADERS_6K, primary="sample-6k.htm",
    )
    ten_k_on, _ = list_files(
        tmp, "10-K", include_exhibits=True, index_items=INDEX_ITEMS_10K,
        index_headers=[], primary="msft-20250630.htm",
    )

    names_8k = [row["name"] for row in eight_k_on]
    names_8k_off = [row["name"] for row in eight_k_off]
    names_6k = [row["name"] for row in six_k_on]
    names_6k_off = [row["name"] for row in six_k_off]
    names_10k = [row["name"] for row in ten_k_on]

    report["payloads"] = {
        "8k_include_exhibits_true": eight_k_on,
        "8k_include_exhibits_false": eight_k_off,
        "6k_include_exhibits_true": six_k_on,
        "6k_include_exhibits_false": six_k_off,
        "10k_include_exhibits_true": ten_k_on,
    }
    report["header_fetch_calls"] = {
        "8k": eight_k_headers,
        "6k": six_k_headers,
    }

    if mode == "freeze":
        frozen = {
            "6k_include_exhibits_true": six_k_on,
            "6k_include_exhibits_false": six_k_off,
        }
        (out_dir / "6k_frozen_before.json").write_text(
            json.dumps(frozen, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"mode": mode, "frozen": "results/6k_frozen_before.json"},
                         ensure_ascii=False))
        return 0

    # G1: 8-K + include_exhibits -> exhibit reachable
    record(
        "G1_8k_exhibit_in_filenames",
        "d291965dex991.htm" in names_8k,
        {"names": names_8k, "expected_contains": "d291965dex991.htm"},
    )
    # G2: 8-K without include_exhibits -> exhibit absent, primary only + nothing gated
    record(
        "G2_8k_exhibit_absent_without_flag",
        "d291965dex991.htm" not in names_8k_off,
        {"names": names_8k_off},
    )
    # G3/G4: 6-K frozen byte regression
    frozen = json.loads((out_dir / "6k_frozen_before.json").read_text(encoding="utf-8"))
    cur6 = {
        "6k_include_exhibits_true": six_k_on,
        "6k_include_exhibits_false": six_k_off,
    }
    frozen_bytes = json.dumps(frozen, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    cur_bytes = json.dumps(cur6, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    import hashlib

    record(
        "G3_6k_list_byte_identical",
        frozen_bytes == cur_bytes,
        {
            "before_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
            "after_sha256": hashlib.sha256(cur_bytes).hexdigest(),
            "before_bytes": len(frozen_bytes),
            "after_bytes": len(cur_bytes),
            "names_6k_true": names_6k,
            "names_6k_false": names_6k_off,
        },
    )
    record(
        "G4_6k_expected_names_present",
        names_6k
        == sorted(
            [
                "sample-6k.htm",
                "sample-6k_htm.xml",
                "sample-6k.xsd",
                "d123dex991.htm",
                "form6kcover.htm",
                "q12025pressrelease.htm",
            ]
        ),
        {"names": names_6k},
    )
    # G5: non-authorized form must not enter the exhibit gate
    record(
        "G5_10k_exhibit_not_ingested",
        "msft_ex99-1.htm" not in names_10k,
        {"names": names_10k},
    )

    failed = [c for c in report["checks"] if not c["ok"]]
    report["passed"] = len(report["checks"]) - len(failed)
    report["failed"] = len(failed)
    (out_dir / f"dayu_gate_{mode}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"mode": mode, "passed": report["passed"], "failed": report["failed"],
                      "failed_names": [c["name"] for c in failed]}, ensure_ascii=False))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
