"""W06A fixture generator: request + the TEST-ONLY filing-fetch stand-in.

Writes into the attempt:
  samples/request.json          the revenue source-preparation request
  samples/source_bytes.txt      the "already downloaded" original bytes
  samples/handle.json           the capture-ready handle the stand-in returns
  iso/ff/scripts/fetch_filing.py   the stand-in CLI

The stand-in is NOT a provider simulation and NOT a worker: it returns bytes
that are already on disk (the "registered raw / reuse" path) and reports the
review verdict and call counters from samples/handle.json.  It exists so the
REAL source-preparation CLI can be driven end to end without network.

  <py> -X utf8 -B scripts/w06a_make_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"
FF = ATTEMPT / "iso" / "ff"

SOURCE_BYTES = (
    "EMERALD-MINING-2025-ANNUAL-REPORT-BYTES (fixture; already on disk)\n"
)

FETCH_FILING = '''\
"""TEST-ONLY filing-fetch stand-in (attempt I-06-A/a20260919-01).

NOT a provider client, NOT a worker, NO network.  It reproduces the calling
convention the real client uses:

    fetch_filing.py [--allow-download] [--config PATH] --timeout-seconds N
        < request JSON on stdin
        > {"status": "capture_ready", "handle": {...}} on stdout, rc 0

The handle is read verbatim from the JSON file named by the environment
variable W06A_HANDLE_JSON, so every fact moving through the REAL
source-preparation chain (review verdict, call counters, hashes) is the
fixture's, never invented here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="test-only filing-fetch stand-in")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--config", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    args = parser.parse_args(argv)
    request = json.loads(sys.stdin.read() or "{}")
    handle_path = os.environ.get("W06A_HANDLE_JSON")
    if not handle_path:
        sys.stdout.write(json.dumps({
            "status": "failed",
            "error_code": "fixture_not_configured",
            "error": "W06A_HANDLE_JSON is not set",
            "retryable": False,
        }))
        return 1
    handle = json.loads(Path(handle_path).read_text(encoding="utf-8"))
    handle.setdefault("request_echo", {})
    handle["request_echo"] = {
        "as_of_date": request.get("as_of_date"),
        "document_kind": request.get("document_kind"),
        "allow_download": bool(args.allow_download),
        "config": args.config,
        "timeout_seconds": args.timeout_seconds,
    }
    sys.stdout.write(json.dumps({"status": "capture_ready", "handle": handle},
                                ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def main() -> int:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    (FF / "scripts").mkdir(parents=True, exist_ok=True)

    source_path = SAMPLES / "source_bytes.txt"
    source_path.write_text(SOURCE_BYTES, encoding="utf-8", newline="\n")
    snapshot_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()

    request = {
        "as_of_date": "2026-09-19",
        "document_kind": "annual_report",
        "entity": "翡翠矿业",
    }
    (SAMPLES / "request.json").write_text(
        json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    handle = {
        "capture_ready": True,
        "source_id": "urn:cw:source:sha256:emerald-2025-annual",
        "document_id": "urn:cw:doc:emerald-2025-annual",
        "title": "翡翠矿业2025年年度报告",
        "document_kind": "annual_report",
        "published_date": "2026-03-28",
        "retrieved_at": "2026-09-19T00:00:00Z",
        "snapshot_sha256": snapshot_sha,
        "canonical_path": str(source_path),
        "canonical_location_id": "loc-emerald-annual",
        "https_url": "https://example.invalid/emerald/2025-annual",
        "request_id": "urn:rf:request:w06a-0001",
        "provider": "fixture",
        "provider_document_id": "fixture-0001",
        "collector_name": "fixture-collector",
        "collector_version": "1.0.0",
        "resolution_envelope": {
            "schema_version": "1.0",
            "outcome": "reused_exact",
            "policy_hash": "p" * 64,
            "activation_epoch": 7,
            "bundle_status": "available",
            "download_events": 0,
            "prompt_injection_status": "not_reviewed",
            "parser_calls": 0,
            "llm_calls": 0,
            "bundle": {
                "schema_version": "1.0",
                "source": {
                    "document_id": "urn:cw:doc:emerald-2025-annual",
                    "primary_source_id": "urn:cw:source:sha256:emerald-2025-annual",
                    "source_sha256": snapshot_sha,
                    "as_of_date": "2026-03-28",
                },
                "valid_handles": {
                    "normalized": {
                        "reusable": True,
                        "artifact_id": "urn:cw:artifact:sha256:normalized",
                        "artifact_role": "normalized",
                        "content_sha256": "n" * 64,
                        "generator_name": "source_catalog_normalizer",
                        "generator_version": "1.0.0",
                        "path": str(source_path),
                        "source_id": "urn:cw:source:sha256:emerald-2025-annual",
                    }
                },
                "invalid": {},
                "bundle_hash": "b" * 64,
            },
        },
    }
    (SAMPLES / "handle.json").write_text(
        json.dumps(handle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (FF / "scripts" / "fetch_filing.py").write_text(
        FETCH_FILING, encoding="utf-8", newline="\n"
    )
    import subprocess

    head = subprocess.run(
        ["git", "-C", str(FF), "init", "-q"], capture_output=True, text=True
    )
    print(json.dumps({
        "source_bytes_sha256": snapshot_sha,
        "source_bytes_path": str(source_path),
        "handle_path": str(SAMPLES / "handle.json"),
        "request_path": str(SAMPLES / "request.json"),
        "ff_root": str(FF),
        "ff_git_init_rc": head.returncode,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
