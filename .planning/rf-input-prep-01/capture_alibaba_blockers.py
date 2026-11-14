"""Replay every Alibaba acquisition route through the sanctioned entry.

Entry point: revenue-forecast `source_preparation.py` -> `filing_fetch_client`
-> the filing-fetch skill -> company-wiki. No other acquisition path is used:
the owner's instruction is that filing-fetch and company-wiki own acquisition,
so this script only drives that chain and records what it returns.

Each route keeps its own stdout/stderr evidence file; every route is bounded by
explicit acquisition limits where the request permits them, and none of them
performs a download (all return before/at the metadata gate).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
EVIDENCE = ROOT / "evidence"
CWP_CATALOG = "C:/Users/郑曾波/Projects/company-wiki/config/source_catalog.yaml"

LIMITS = {"max_bytes": 8000000, "timeout_seconds": 120, "max_cost_usd": "0.00"}


def base(**overrides: object) -> dict:
    request = {
        "schema_version": "2.0",
        "company_query": "阿里巴巴－Ｗ",
        "market": "HK",
        "document_kind": "annual_report",
        "as_of_date": "2026-11-08",
    }
    request.update(overrides)
    return request


ROUTES: dict[str, dict] = {
    "route1-hk-fy2026-reuse": base(mode="exact", fiscal_year=2026, filing_intent="reuse_only"),
    "route2-hk-fy2026-fetch-if-missing": base(
        mode="exact", fiscal_year=2026, filing_intent="fetch_if_missing",
        acquisition_limits=dict(LIMITS),
    ),
    "route3-hk-fy2025-reuse": base(mode="exact", fiscal_year=2025, filing_intent="reuse_only"),
    "route5-hk-latest-as-of-reuse": base(
        mode="latest_as_of", filing_intent="reuse_only",
        acquisition_limits=dict(LIMITS),
    ),
    "route6-hk-latest-as-of-fetch-if-missing": base(
        mode="latest_as_of", filing_intent="fetch_if_missing",
        acquisition_limits=dict(LIMITS),
    ),
    "route4-us-fy2026-fetch-if-missing": {
        "schema_version": "2.0",
        "company_query": "BABA",
        "market": "US",
        "document_kind": "annual_report",
        "mode": "exact",
        "fiscal_year": 2026,
        "as_of_date": "2026-11-08",
        "filing_intent": "fetch_if_missing",
        "acquisition_limits": dict(LIMITS),
    },
}


def summarise(raw: str) -> dict:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"parse": "not_json", "raw_head": raw[:300]}
    ff = payload.get("filing_fetch_result") or {}
    filing = ff.get("filing") or {}
    return {
        "status": ff.get("status"),
        "reason": filing.get("reason"),
        "calls": ff.get("calls"),
        "downloads": ff.get("downloads"),
        "upstream_cause": filing.get("upstream_cause"),
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    summary = []
    for label, request in ROUTES.items():
        request_path = ROOT / "requests" / f"{label}.json"
        request_path.write_text(json.dumps(request, ensure_ascii=False) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [
                sys.executable, "-B",
                str(WORKTREE / "scripts" / "source_preparation.py"),
                "--result-envelope",
                "--request-file", str(request_path),
                "--company-wiki-catalog-config", CWP_CATALOG,
                "--source-reader-receipt-version", "2.2",
                "--timeout-seconds", "180",
            ],
            capture_output=True, cwd=str(WORKTREE),
        )
        stdout_bytes = proc.stdout
        stderr_text = proc.stderr.decode("utf-8", "replace").strip()
        (EVIDENCE / f"{label}.stdout.json").write_bytes(stdout_bytes)
        (EVIDENCE / f"{label}.stderr.json").write_text(stderr_text + "\n", encoding="utf-8")
        summary.append(
            {
                "route": label,
                "request_file": str(request_path.relative_to(WORKTREE)),
                "exit_code": proc.returncode,
                "stdout_bytes": len(stdout_bytes),
                "stderr_artifact": str((EVIDENCE / f"{label}.stderr.json").relative_to(WORKTREE)),
                "observed": summarise(stderr_text),
            }
        )
    (EVIDENCE / "alibaba-routes.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for row in summary:
        print(json.dumps({"route": row["route"], "exit": row["exit_code"], **row["observed"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
