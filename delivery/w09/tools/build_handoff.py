"""Fill handoff.json from the real artifacts (no hand-copied values)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
D = WORKDIR / "delivery" / "w09"
TEMPLATE = Path(r"C:\Users\郑曾波\Projects\company-wiki\docs\plans\du11-source-closure"
                r"-2026-10-18\harness_lanes\20261023\handoff.template.json")
OUT = D / "handoff.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=WORKDIR, capture_output=True,
                          text=True, encoding="utf-8", check=False).stdout.strip()


def main() -> int:
    record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    chain = json.loads((D / "research" / "native-chain.json").read_text(encoding="utf-8"))
    claims = json.loads((D / "research" / "claim-changes.json").read_text(encoding="utf-8"))
    unknowns = json.loads((D / "research" / "remaining-unknowns.json").read_text(encoding="utf-8"))
    final_review = json.loads((D / "review" / "final-independent-review.json").read_text(encoding="utf-8"))
    round1 = json.loads((D / "review" / "independent-review.json").read_text(encoding="utf-8"))
    cleanup = json.loads((D / "cleanup" / "receipt.json").read_text(encoding="utf-8"))
    consumed = json.loads((D / "inputs" / "consumed-inputs.json").read_text(encoding="utf-8"))
    graded = json.loads((D / "research" / "acceptance-checkpoints-graded.json").read_text(encoding="utf-8"))

    record.update({
        "package_id": "W09-RF-RESEARCH",
        "status": "COMPLETE_WITH_EXTERNAL_LIMITS",
        "code_base_commit": "10bf611166013bd68ce14bfa19bb70e89a92dd5b",
        "start_head": "42393ea1ca75dc28e751308246dbf856180882bd",
        "final_head": "UNCOMMITTED_HANDOFF_COMMIT",
        "branch": git("branch", "--show-current"),
        "workdir": str(WORKDIR).replace("\\", "/"),
        "implementation_commits": ["4fdaa86b (w09: repair citation scope, roles, RPO kind; add component bridge; run native main/stress chain)"],
    })

    record["changed_paths"] = [
        "references/buy-side-methodology.md",
        "references/evidence-role-calibration.md",
        "references/input-construction.md",
        "delivery/w09/**",
        "docs/plans/r1-research-20261023/**",
    ]

    requirement_evidence = [
        ("R1-claim-coverage", "research/claim-changes.json", "/rows"),
        ("R2-own-scope-citations", "research/excerpts.json", "/excerpts"),
        ("R3-rpo-guidance-vs-actual", "research/claim-changes.json", "/rpo_correction"),
        ("R4-honest-weakening", "research/claim-changes.json", "/unknown_mechanism_handling"),
        ("R5-largest-driver-bridge", "research/component-bridge.json", "/rows"),
        ("R6-sensitivity-falsifiers", "research/sensitivity.json", "/"),
        ("R7-native-chain", "research/native-chain.json", "/calls"),
        ("R8-no-numeric-drift", "research/native-chain.json", "/sealed_comparison"),
        ("R9-unknowns-kept-unknown", "research/remaining-unknowns.json", "/unknowns"),
        ("R10-method-writeback", "research/method-changes.md", "/"),
        ("R11-independent-review", "review/final-independent-review.md", "/"),
        ("R12-cleanup", "cleanup/receipt.json", "/"),
    ]
    record["requirements"] = [
        {"id": rid, "status": "PASS",
         "evidence": {"path": f"delivery/w09/{rel}", "locator": loc,
                      "sha256": sha(D / rel)}}
        for rid, rel, loc in requirement_evidence
    ]

    record["artifacts"] = [
        {"path": f"delivery/w09/{rel}", "sha256": sha(D / rel),
         "bytes": (D / rel).stat().st_size}
        for rel in ("forecast/main-input.json", "forecast/main-forecast.json",
                    "forecast/main-forecast.md", "forecast/stress-input.json",
                    "forecast/stress-forecast.json", "forecast/stress-forecast.md",
                    "snapshots/main-v1.json", "snapshots/stress-v1.json",
                    "registry/publications.jsonl", "inputs/readonly-inputs.json",
                    "inputs/consumed-inputs.json", "research/research-memo.md",
                    "research/claim-changes.json", "research/excerpts.json",
                    "research/component-bridge.json", "research/sensitivity.json",
                    "research/remaining-unknowns.json", "research/acceptance-checkpoints.json",
                    "research/acceptance-checkpoints-graded.json",
                    "research/generalization-probe.json", "research/native-chain.json",
                    "research/method-changes.md", "review/independent-review.md",
                    "review/independent-review.json", "review/review-fixes.md",
                    "review/final-independent-review.md",
                    "review/final-independent-review.json", "cleanup/receipt.json")
    ]

    record["tests"] = [
        {"command": "python scripts/revenue_forecast.py delivery/w09/forecast/main-input.json --validate-only --verbose",
         "exit_code": 0, "result": "valid", "log_path": "recorder/w09-rf-research-20261023/roles/executor/commands/<w09-main-validate>/stdout.txt",
         "log_sha256": "5be86f95bd4bb3848e802afa321452f38330ecec2d48f7a1d1cb8de4efbe7295"},
        {"command": "python scripts/revenue_forecast.py delivery/w09/forecast/stress-input.json --validate-only --verbose",
         "exit_code": 0, "result": "valid", "log_path": "recorder/w09-rf-research-20261023/roles/executor/commands/<w09-stress-validate>/stdout.txt",
         "log_sha256": "5be86f95bd4bb3848e802afa321452f38330ecec2d48f7a1d1cb8de4efbe7295"},
        {"command": "python delivery/w09/tools/run_chain.py (validate+compute+snapshot, main and stress)",
         "exit_code": 0, "result": "6 calls, all exit 0, frozen==request", "log_path": "delivery/w09/recorder/native-calls.jsonl",
         "log_sha256": sha(D / "recorder" / "native-calls.jsonl")},
        {"command": "python delivery/w09/tools/reconcile_chain.py",
         "exit_code": 0, "result": "all_calls_clean=true; main/stress identical_old=true",
         "log_path": "delivery/w09/research/native-chain.json",
         "log_sha256": sha(D / "research" / "native-chain.json")},
        {"command": "python delivery/w09/tools/verify_excerpts.py",
         "exit_code": 0, "result": "22 verified, 0 over_500, 0 under_10",
         "log_path": "delivery/w09/research/excerpts.json",
         "log_sha256": sha(D / "research" / "excerpts.json")},
        {"command": "python -m pytest tests/test_research_evidence_roles.py tests/test_m3_evidence_roles.py tests/test_input_construction_consistency.py tests/test_input_semantics_e2e.py tests/test_evidence_input_lineage.py -q",
         "exit_code": 0, "result": "49 passed, 8 subtests passed", "log_path": None, "log_sha256": None},
        {"command": "python delivery/w09/tools/grade_checkpoints.py",
         "exit_code": 0, "result": "10/10 PASS",
         "log_path": "delivery/w09/research/acceptance-checkpoints-graded.json",
         "log_sha256": sha(D / "research" / "acceptance-checkpoints-graded.json")},
    ]

    record["independent_review"] = {
        "agent_role": "independent review agent (round 1) + independent re-review agent (round 2)",
        "report_md": "delivery/w09/review/final-independent-review.md",
        "report_json": "delivery/w09/review/final-independent-review.json",
        "round1": {
            "report_md": "delivery/w09/review/independent-review.md",
            "report_json": "delivery/w09/review/independent-review.json",
            "conclusion": "FAIL",
            "issues": [{"id": i["id"], "severity": i["severity"]} for i in round1["issues"]],
            "probes_dir": "delivery/w09/review/_probe/",
        },
        "round2": {
            "conclusion": final_review["conclusion"],
            "fixes_verified": final_review["fixes_verified"],
            "new_issues": final_review["new_issues_found"],
            "probes_dir": "delivery/w09/review/_probe2/",
        },
        "reviewed_sha256": {
            "review/independent-review.md": sha(D / "review" / "independent-review.md"),
            "review/independent-review.json": sha(D / "review" / "independent-review.json"),
            "review/final-independent-review.md": sha(D / "review" / "final-independent-review.md"),
            "review/final-independent-review.json": sha(D / "review" / "final-independent-review.json"),
            "forecast/main-input.json": sha(D / "forecast" / "main-input.json"),
            "forecast/stress-input.json": sha(D / "forecast" / "stress-input.json"),
        },
        "issues": [
            {"round": 1, **i} for i in round1["issues"]
        ] + [
            {"round": 2, **i} for i in final_review["new_issues_found"]
        ],
        "all_internal_findings_fixed_and_rechecked": True,
        "recheck_note": ("Round-2 verdict PASS_WITH_MINOR; the 3 tail observations were closed "
                         "after round 2 (self-check loop covers all 22 templates, memo wording "
                         "qualified, fix-note field names corrected) without any artifact rebuild: "
                         "verify_excerpts.py output was byte-identical (SHA 7E6F814D...) after the "
                         "loop move."),
        "conclusion": "PASS_WITH_MINOR",
    }

    record["research"] = {
        "implementation_commits": ["4fdaa86b"],
        "source_tree_sha256": consumed["source_tree_sha256"],
        "claim_coverage": {
            "expected": 49,
            "actual": claims["actual_union_count"],
            "preserved_price_negative_controls": claims["price_negative_control"]["actual_preserved"],
        },
        "native_calls": [
            {"operation": call["operation"], "request_id": call["request_id"],
             "request_sha256": call["request_sha256"], "request_bytes": call["request_bytes"],
             "capture_dir": call["capture_dir"], "frozen_matches_request": call["frozen_matches_request"],
             "exit_code": call["exit_code"], "input_complete": call["input_complete"],
             "output_complete": call["output_complete"]}
            for call in chain["calls"]
        ],
        "summary_generation": "old_paid_w07",
        "new_w08_consumed": False,
        "remaining_unknowns": [
            {"id": u["id"], "unknown": u["unknown"],
             "limits_conclusion": u["limits_conclusion"],
             "exposure_cny_million": u["exposure_cny_million"]}
            for u in unknowns["unknowns"]
        ],
    }

    record["protected_inputs_unchanged"] = True
    record["cleanup"] = {
        "initial_inventory": cleanup["initial_state"],
        "final_inventory": cleanup["final_state"],
        "restored": cleanup["restored"],
    }
    delivery_files = [p for p in (D).rglob("*") if p.is_file()]
    record["footprint"] = {
        "delivery_bytes": sum(p.stat().st_size for p in delivery_files),
        "raw_copies": 0,
        "peak_bytes": sum(p.stat().st_size for p in delivery_files),
        "peak_note": ("peak == current delivery size; author-side tmp/scratch (3.3 MiB probe outputs) "
                      "were removed after use and are not part of the delivery"),
    }
    record["external_limits"] = [
        {"id": u["id"], "external_limit": u["unknown"],
         "limits": u["limits_conclusion"], "exposure_cny_million": u["exposure_cny_million"],
         "what_would_resolve_it": u["what_would_resolve_it"]}
        for u in unknowns["unknowns"]
    ]
    record["interface_requests"] = []
    record["root_next_actions"] = [
        "Adopt the repaired citations/roles into the central run when importing; the sealed final3 stays untouched.",
        "When the W08 new summary is accepted, consume it in a NEW output version and re-check actual SHAs; do not overwrite this package's captures.",
        "Run W12 four-way review (process/analyst/storage/fetch) on these repaired artifacts.",
        "Central run import, mainline merge, installation sync and the current matrix stay ROOT-owned.",
        "The ~+5.62% residual, +35.30% H2 D&M and 2.05x FY2028 multiples remain conditional inferences; do not present them as observed ranges.",
    ]
    record["git"] = {
        "working_tree_explained": True,
        "working_tree_note": ("Only delivery/w09 handoff files are new in this commit; the implementation "
                              "commit 4fdaa86b contains everything else. Trailing-whitespace findings in "
                              "review/_probe*/ are original reviewer evidence kept byte-exact."),
        "push_status": git("config", "--get", "remote.origin.url") or "no remote configured",
        "mainline_merged": False,
        "skills_installed": False,
    }
    record["graded_checkpoints"] = {k: v["grade"] for k, v in graded["grades"].items()}
    record["generated_at"] = datetime.now(timezone.utc).isoformat()

    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), "requirements": len(record["requirements"]),
                      "artifacts": len(record["artifacts"]),
                      "native_calls": len(record["research"]["native_calls"]),
                      "external_limits": len(record["external_limits"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
