"""Align the machine-readable handoff with the six-route and snapshot record."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    path = ROOT / "handoff.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload["not_delivered"]:
        if row["id"] == "alibaba-input-and-job":
            row["reason"] = (
                "six routes, all driven through source_preparation -> filing-fetch -> company-wiki: "
                "exact reuse_only -> source query market mismatch; exact fetch_if_missing -> operation "
                "market mismatch; FY2025 reuse_only -> source_blocked local_metadata_gap; latest_as_of "
                "reuse_only -> ensure blocked local_metadata_incomplete; latest_as_of fetch_if_missing -> "
                "ensure blocked local_metadata_incomplete; US 20-F fetch_if_missing -> ensure exited 1 "
                "(provider_failed). Zero downloads on every route. See evidence/route1..6-*.stderr.json."
            )
    for row in payload["package_compliance"]:
        if row["clause"] == "§5.2 两份真实作业终态 + JobView 留档":
            row["detail"] = (
                "one succeeded JobView with cost 0.00 / known; the delivered result is additionally frozen "
                "through revenue_backtest.py create (evidence/mongodb-fy2025-snapshot.json) and diagnosed "
                "through research_support_diagnostics.py; Alibaba absent"
            )
        if row["clause"] == "§5.6 NOT_RUN 逐条带原因":
            row["detail"] = "handoff.json not_delivered ×3 + findings F-01…F-16 (six Alibaba routes, one evidence file each)"
    payload["package_compliance"] = [
        row for row in payload["package_compliance"] if row["clause"] != "模块接口纪律（操作者指令）"
    ]
    payload["package_compliance"].append(
        {
            "clause": "模块接口纪律（操作者指令）",
            "status": "PASS",
            "detail": (
                "every input, job, snapshot, diagnostic and blocker record was produced by calling the "
                "repository's own CLIs (source_preparation, revenue_backtest, research_support_diagnostics, "
                "rf_job_cli, publication_registry) or filing-fetch/company-wiki; the one out-of-band idea "
                "(self-download + official import) was rejected and is recorded as findings F-15"
            ),
        }
    )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "compliance": {
                    s: sum(1 for row in payload["package_compliance"] if row["status"] == s)
                    for s in ("PASS", "PARTIAL", "NOT_RUN")
                },
                "rows": len(payload["package_compliance"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
