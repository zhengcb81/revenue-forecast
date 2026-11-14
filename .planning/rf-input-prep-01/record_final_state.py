"""Add the detailed closure record to handoff.json (idempotent)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = "0993abb305dc86a2197b8b2aee10a3b8d8339949"
HANDOFF_COMMIT = "0afcb16fdfcb0d20be16c175860378c9994286c1"
REVIEW_COMMIT = "42bee755f3385f9b95504a8857c1bdaa542792a7"

FINAL_STATE = {
    "delivery_verdict": "partial_delivery",
    "gap_resolved": False,
    "gap_id": "G-m5-EXT-01",
    "review": {"open_p1": 0, "open_p2": 0, "open_p3": 4, "rounds": 4},
    "commits": {
        "baseline": "d347c4ab43c847432ea354446cfea2947bf81d28",
        "content": CONTENT,
        "handoff": HANDOFF_COMMIT,
        "review_record": REVIEW_COMMIT,
    },
    "why_content_commit": (
        "a commit cannot contain its own SHA; the pinned content commit resolves the input, the job "
        "artifact copies, the frozen snapshot, the diagnostics and every Alibaba route record, while "
        "the handoff record itself is maintained by later commits on the same branch"
    ),
    "independent_verification": {
        "content_commit_resolves": True,
        "snapshot_blob_sha256": "4798e682d65c7ccec31742bb5095eb19e832175f942a9f6d4139b79d51007e4c",
        "snapshot_blob_bytes": 398344,
        "input_blob_sha256": "d82f9b45cefddfba5d52e2abf1e35dba553a1722b1d181818dda78ba0236a993",
        "input_blob_bytes": 146551,
        "input_validate_only": "valid",
        "changed_files_since_baseline": 118,
        "changed_files_inside_package": 118,
        "worktree_clean": True,
    },
}

KEY_HASHES = [
    {"object": "input document", "path": "inputs/mongodb-fy2025-input.json",
     "sha256": "d82f9b45cefddfba5d52e2abf1e35dba553a1722b1d181818dda78ba0236a993", "bytes": 146551},
    {"object": "input (engine canonical)", "path": "inputs/mongodb-fy2025-input.json",
     "sha256": "6169ea8aca81638d83026153474d584ca19be38c166bb71ab0ae4e76924cde59", "bytes": None},
    {"object": "computed result copy",
     "path": "evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__result.json",
     "sha256": "c0dce8c3df7e49431a351de67d15847db40a4ffd7bfa140cf378db437b017963", "bytes": 326471},
    {"object": "rendered report",
     "path": "evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__report.md",
     "sha256": "0bae0856fd4e658b456b1808bec06da937d08c5fa76b2d8e421a76fcbba20e63", "bytes": 53291},
    {"object": "frozen snapshot", "path": "evidence/mongodb-fy2025-snapshot.json",
     "sha256": "4798e682d65c7ccec31742bb5095eb19e832175f942a9f6d4139b79d51007e4c", "bytes": 398344},
    {"object": "support diagnostics", "path": "evidence/mongodb-support-diagnostics.json",
     "sha256": "564b72f09ecb", "bytes": 9347},
]

INTERFACES = [
    {"action": "template field coverage", "interface": "scripts/generate_input_template.py",
     "artifact": "evidence/template-skeleton.json"},
    {"action": "input lint / hash sync / full validation",
     "interface": "scripts/lint_input.py, scripts/fix_hashes.py, scripts/revenue_forecast.py --validate-only",
     "artifact": "evidence/mdb-validation-chain.json"},
    {"action": "source preparation (MongoDB)",
     "interface": "scripts/source_preparation.py -> filing-fetch -> company-wiki",
     "artifact": "requests/mongodb-envelope.json"},
    {"action": "source acquisition attempts (Alibaba, six routes)",
     "interface": "scripts/source_preparation.py -> filing-fetch -> company-wiki",
     "artifact": "evidence/alibaba-routes.json"},
    {"action": "job orchestration", "interface": "scripts/rf_job_cli.py (submit/act/get-status/list-jobs)",
     "artifact": "evidence/mdb2-submit.stdout.json, evidence/mdb2-status.stdout.json, evidence/mdb2-list.stdout.json"},
    {"action": "publication audit", "interface": "scripts/publication_registry.py audit",
     "artifact": "evidence/job-rfjob-20261108-eb9f2a3ed336/registry__publications.jsonl"},
    {"action": "forecast freeze", "interface": "scripts/revenue_backtest.py create",
     "artifact": "evidence/mongodb-fy2025-snapshot.json"},
    {"action": "evidence support diagnostics", "interface": "scripts/research_support_diagnostics.py",
     "artifact": "evidence/mongodb-support-diagnostics.json"},
    {"action": "catalog read check", "interface": "scripts/report_catalog_cli.py list-reports",
     "artifact": "findings.md F-03 (exit 2 owner_root_missing)"},
]

REJECTED = {
    "route": "self-download of the SEC 20-F plus company-wiki `official import`",
    "state": "evaluated, not used",
    "what_was_actually_done": "only the SEC submissions metadata index was queried; no filing bytes were fetched and nothing was written to the catalog",
    "why_rejected": "acquisition belongs to filing-fetch -> company-wiki; a harness-side downloader bypasses the module boundary even if it could pass validation",
    "record": "findings.md F-15",
}

NEXT_ACTIONS = [
    {"id": "alibaba-acquisition", "owner": "company-wiki owner (market projection) / filing-fetch owner (null-market binding) / environment (dayu-us-sdk)",
     "unblock": "any of the six routes returns found with capture_ready=true",
     "my_next_step": "rebuild the input as an Alibaba variant of build_mdb_input.py and run the same input -> job -> report chain"},
    {"id": "catalog-admission", "owner": "owner / D00 delivery protocol",
     "unblock": "a B34 trusted research-admission package (recorder/run/step-ledger/terminal/review receipt)",
     "my_next_step": "run import-research-attempt then import-research-publication, then list-reports --entity-id with the report id and result_sha256"},
    {"id": "merge-main", "owner": "RF owner",
     "unblock": "main D-line closure plus scripts/ regression",
     "my_next_step": "execute the merge task recorded in task_plan.md"},
    {"id": "management-targets", "owner": "this package's follow-up",
     "unblock": "an official results release or call original acquired through the sanctioned route",
     "my_next_step": "build the target ledger with independent_benchmark and re-run the job"},
]


def main() -> int:
    path = ROOT / "handoff.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["final_state"] = FINAL_STATE
    payload["key_hashes"] = KEY_HASHES
    payload["module_interface_actions"] = INTERFACES
    payload["rejected_acquisition_route"] = REJECTED
    payload["next_owner_actions"] = NEXT_ACTIONS
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"keys": len(payload), "interfaces": len(INTERFACES), "next_actions": len(NEXT_ACTIONS)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
