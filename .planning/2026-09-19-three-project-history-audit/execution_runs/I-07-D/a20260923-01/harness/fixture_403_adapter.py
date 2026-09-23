"""I-07-D frozen HTTP403 provider fixture (F01, point (a)).

Serves as the cn adapter through the product's OWN config seam: the F01
cell's `config/source_acquisition.yaml` cn-adapter `command` points here, so
`company_wiki.source_catalog.adapter_process.JsonCommandAdapter._run` executes
this script as the provider subprocess (the exact seam filing-fetch's own
tests use: filing-fetch/tests/e2e_support/spy_adapter.py, "no network, no
mocks").  The product's failure parser (adapter_process.py:155-178) reads the
structured stderr below and sets exc.error_code / exc.retryable itself.

json_command_v1 protocol:
  argv:  <python> <fixture> <discover|fetch> [--staging-dir DIR]
  stdin: canonical JSON request payload
  discover -> stdout one JSON {schema_version:"1.0", status:"ok",
             adapter:{name,version}, candidates:[...]} , exit 0
  fetch    -> LAST stderr line = structured 1.0 failure JSON, exit 1

Every invocation appends one JSON line to $I07D_FIXTURE_LOG
(trigger-count evidence; oracle §3 F01 requires fetch lines >= 1).

Retryable semantics: error.retryable = true mirrors the frozen CN403
precedent (card_I-04-E F-E2: upstream retryable=true must be preserved
verbatim, never rewritten to false).
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ADAPTER_NAME = "stockinfo-cninfo"
ADAPTER_VERSION = "1.1.0"

# The production CN candidate (verbatim identity fields from the production
# documents.metadata_json acquisition candidate, read-only observation in
# I-07-B evidence/prod_rows_dump.json).  discover succeeds so that close-gap
# proceeds to fetch — where the 403 fires (the CN403 download-precedent shape).
CANDIDATE = {
    "candidate_id": "cninfo:1225023658",
    "provider": "cninfo",
    "provider_document_id": "1225023658",
    "market": "CN",
    "entity": "紫金矿业",
    "title": "紫金矿业集团股份有限公司2025年年度报告",
    "source_url": "https://static.cninfo.com.cn/finalpage/2026-03-21/1225023658.PDF",
    "document_kind": "annual_report",
    "filing_date": "2026-03-20",
    "fiscal_year": 2025,
    "form_type": "annual_report",
    "fiscal_period": "FY",
    "language": "zh-CN",
    "amended": False,
    "schema_version": "1.0",
}


def _log(action: str, extra: dict) -> None:
    path = os.environ.get("I07D_FIXTURE_LOG")
    if not path:
        path = str(Path(__file__).resolve().parent.parent / "evidence" /
                   "cases" / "F01" / "fixture_log.jsonl")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    rec = {"t": round(time.time(), 3),
           "at": datetime.now(timezone.utc).isoformat(),
           "pid": os.getpid(), "action": action,
           "argv": sys.argv[1:], "cwd": os.getcwd(), **extra}
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:  # noqa: BLE001
        payload = {}

    if action == "discover":
        _log("discover", {"outcome": "ok", "request": {k: payload.get(k) for k in
             ("market", "document_kind", "fiscal_year", "entity")}})
        response = {
            "schema_version": "1.0",
            "status": "ok",
            "adapter": {"name": ADAPTER_NAME, "version": ADAPTER_VERSION},
            "candidates": [CANDIDATE],
        }
        sys.stdout.write(json.dumps(response, ensure_ascii=False))
        sys.stdout.write("\n")
        return 0

    if action == "fetch":
        _log("fetch", {"outcome": "http_403",
                       "staging_dir_arg": sys.argv[3] if len(sys.argv) > 3 else None,
                       "candidate_id": payload.get("candidate_id")})
        failure = {
            "schema_version": "1.0",
            "status": "failed",
            "error": {
                "code": "http_403",
                "retryable": True,
                "message": "HTTP 403 Forbidden from provider (frozen I-07-D fault fixture)",
            },
            "adapter": {"name": ADAPTER_NAME, "version": ADAPTER_VERSION},
        }
        sys.stderr.write(json.dumps(failure, ensure_ascii=False) + "\n")
        sys.stderr.flush()
        return 1

    _log("unknown", {"outcome": "bad_action"})
    sys.stderr.write(json.dumps({
        "schema_version": "1.0", "status": "failed",
        "error": {"code": "bad_action", "retryable": False,
                  "message": f"unknown action {action!r}"},
        "adapter": {"name": ADAPTER_NAME, "version": ADAPTER_VERSION},
    }, ensure_ascii=False) + "\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
