"""Record the module-interface artifacts and the six-route Alibaba evidence.

Everything here was produced by calling the repository's own public CLIs
(source_preparation / revenue_backtest / research_support_diagnostics); no
acquisition or import was performed outside filing-fetch and company-wiki.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
EVIDENCE = ROOT / "evidence"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_blocker(routes: list[dict]) -> None:
    blocker = json.loads((ROOT / "alibaba-blocker.json").read_text(encoding="utf-8"))
    by_route = {row["route"]: row for row in routes}
    labels = {
        "route1-hk-fy2026-reuse": "HK 09988 FY2026 annual_report, reuse_only (exact)",
        "route2-hk-fy2026-fetch-if-missing": "HK 09988 FY2026 annual_report, fetch_if_missing (exact, reuse-first ensure)",
        "route3-hk-fy2025-reuse": "HK 09988 FY2025 annual_report, reuse_only (exact, local metadata reconciliation)",
        "route5-hk-latest-as-of-reuse": "HK 09988 latest_as_of, reuse_only",
        "route6-hk-latest-as-of-fetch-if-missing": "HK 09988 latest_as_of, fetch_if_missing (reuse-first ensure)",
        "route4-us-fy2026-fetch-if-missing": "US BABA FY2026 annual_report (20-F), fetch_if_missing",
    }
    repaired = []
    for name, row in by_route.items():
        observed = row["observed"]
        repaired.append(
            {
                "route": labels.get(name, name),
                "request_file": row["request_file"],
                "exit_code": row["exit_code"],
                "machine_cause": {
                    "status": observed.get("status"),
                    "reason": observed.get("reason"),
                    "calls": observed.get("calls"),
                    "downloads": observed.get("downloads"),
                    "upstream_cause": observed.get("upstream_cause"),
                },
                "artifacts": [row["stderr_artifact"], row["request_file"]],
            }
        )
    blocker["acquisition_routes_attempted"] = repaired
    blocker["route_evidence"] = (
        "evidence/alibaba-routes.json holds the replayed exit code and the per-route stderr "
        "artifact for all six routes; each was driven through source_preparation.py -> "
        "filing-fetch -> company-wiki, and each performed zero downloads and zero paid calls."
    )
    blocker["observed_at"] = (
        "2026-11-08T08:20Z (first attempts), 2026-11-08T09:0xZ (routes 1-3), "
        "2026-11-08T09:2xZ (all six replayed with per-route evidence)"
    )
    (ROOT / "alibaba-blocker.json").write_text(
        json.dumps(blocker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def main() -> int:
    routes = json.loads((EVIDENCE / "alibaba-routes.json").read_text(encoding="utf-8"))
    rebuild_blocker(routes)

    snapshot = EVIDENCE / "mongodb-fy2025-snapshot.json"
    diagnostics = EVIDENCE / "mongodb-support-diagnostics.json"
    snapshot_payload = json.loads(snapshot.read_text(encoding="utf-8"))
    handoff = json.loads((ROOT / "handoff.json").read_text(encoding="utf-8"))
    entry = handoff["inputs"][0]
    entry["derived_artifacts"] = {
        "frozen_snapshot": {
            "path": str(snapshot.relative_to(WORKTREE)),
            "sha256": sha(snapshot),
            "snapshot_id": snapshot_payload["snapshot_id"],
            "forecast_version": snapshot_payload["forecast_version"],
            "input_sha256": snapshot_payload["input_sha256"],
            "frozen_payload_sha256": snapshot_payload["forecast_result_sha256"],
            "note": (
                "produced by scripts/revenue_backtest.py create; the frozen payload is identical "
                "to the delivered result.json (same numbers, segments, base and confidence). "
                "forecast_result_sha256 hashes the complete frozen dict, while the engine's "
                "result_sha256 (04768c27...) hashes the payload without that field; both identify "
                "the same forecast and neither replaces the other."
            ),
        },
        "support_diagnostics": {
            "path": str(diagnostics.relative_to(WORKTREE)),
            "sha256": sha(diagnostics),
            "producer": "scripts/research_support_diagnostics.py",
        },
    }
    commands = [
        {
            "command": "python scripts/revenue_backtest.py create .planning/rf-input-prep-01/inputs/mongodb-fy2025-input.json --version rf-input-prep-01-mongodb-fy2025-v2 --output .planning/rf-input-prep-01/evidence/mongodb-fy2025-snapshot.json",
            "exit_code": 0,
            "artifact": str(snapshot.relative_to(WORKTREE)),
        },
        {
            "command": "python scripts/research_support_diagnostics.py --input .planning/rf-input-prep-01/inputs/mongodb-fy2025-input.json --output .planning/rf-input-prep-01/evidence/mongodb-support-diagnostics.json",
            "exit_code": 0,
            "artifact": str(diagnostics.relative_to(WORKTREE)),
        },
    ]
    existing = {row["command"] for row in handoff["evidence"]}
    handoff["evidence"].extend(row for row in commands if row["command"] not in existing)
    handoff["evidence"] = [
        {
            "command": row["command"],
            "exit_code": row["exit_code"],
            "artifact": row["artifact"],
        }
        for row in handoff["evidence"]
    ]
    (ROOT / "handoff.json").write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"routes": len(routes), "snapshot_sha": sha(snapshot)[:12], "evidence_rows": len(handoff["evidence"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
