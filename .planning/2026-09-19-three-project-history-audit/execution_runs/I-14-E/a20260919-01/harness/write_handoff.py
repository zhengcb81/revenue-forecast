"""I-14-E: write handoff.json with real hashes (never retyped by hand).

status is review_pending: the implementer does not self-sign.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
OUT = ATTEMPT / "handoff.json"


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main() -> int:
    analysis = {}
    path = ATTEMPT / "after" / "analysis.json"
    if path.exists():
        analysis = json.loads(path.read_text(encoding="utf-8"))
    hypotheses = {k: v.get("verdict") for k, v in (analysis.get("hypotheses") or {}).items()}
    bands = {k: (v or {}).get("overall") for k, v in (analysis.get("m_b_bands") or {}).items()}

    payload = {
        "card_id": "I-14-E",
        "card_title": "restart-node timing jitter (load-dependent, not a tree difference)",
        "parent": "I-14",
        "attempt_id": "a20260919-01",
        "date_utc": "2026-09-21",
        "status": "review_pending",
        "implementer": "I-14-E implementer agent; NOT the reviewer",
        "objective": ("characterise the load-dependent timing jitter band of the two worker-restart "
                      "bootstrap nodes, test the load-dependence and tree-independence hypotheses, "
                      "and deliver fail-able cases + an unapplied test-side proposal.  No product "
                      "code and no product test was changed."),
        "completed_steps": [
            "1 claim: attempt dir + standard structure (binding.json, oracle.md, commands.json, "
            "before/after/recovery, harness/, iso/)",
            "2 binding: production anchors hashed (CW HEAD f39bd5a6..., test file 32515aa6..., "
            "supervisor ps1 5c12cd74..., logon ps1 70b4d7d7...); attempt iso venv (python 3.13.9, "
            "package set equal to the frozen band's runner venv)",
            "3 trees: iso/T0 = I-14-C product/src, iso/T4 = I-14-C product_fixed/src, iso/T0b = a "
            "byte-identical second copy of T0 (identity control); T0 vs T4 differ only in "
            "cli.py/observability.py/worker.py",
            "4 frozen band: re-extracted the 24-run x 2-round x 2-tree record from I-14-C r5 "
            "(48/48 runs: surviving stdout byte-identical to the frozen captures, 48/48 launcher "
            "event files present); expected values hand-computed from that record",
            "5 oracle.md frozen BEFORE any measurement run (2026-09-21T20:09:21Z) with hypotheses "
            "H1-H5, the measurement plan and the pass/fail criteria",
            "6 oracle-addendum-A (run counts reduced; ambient-load regime recorded) written BEFORE "
            "the full campaign",
            "7 oracle-addendum-B written after the parent relayed CF-I14F-X1: artifact-presence "
            "discrimination as a measurement precondition, concurrent-activity recording, and the "
            "determinism verdict requirement",
            "8 M-A: 111 independent samples of the two load-sensitive quantities (fake child "
            "launch->first side effect, launch->exit) across quiet/+8/+12 burners, popen and "
            "PowerShell Start-Process forms",
            "9 M-B: 45 node-1 runs (3 trees x 2 rounds x {quiet,cpu8} + 3 trees x 1 round x spawn) "
            "and 16 node-2 runs, interleaved, per-run fresh short basetemps, per-run load probes",
            "10 M-C: 16 direct samples of node 2's three timing budgets (wrapper / events / exit)",
            "11 artifact capture: per-run artifact presence, path lengths and sha256 for all 61 "
            "band runs (no run shows the path/redirect absence signature)",
            "12 concurrent-activity sampling: 70 samples over 40 minutes, capturing other sessions' "
            "pytest campaigns and the persistent chrome-headless-shell load",
            "13 after/analysis.json + after/analysis.md (per-hypothesis verdicts), "
            "after/fail-able-cases.json (2 cases + determinism verdict), "
            "after/proposed-test-side-change.md (unapplied), after/final_hashes.json "
            "(production anchors unchanged)",
        ],
        "next_step_number": 1,
        "next_action": ("Independent reviewer reads oracle.md + addendum A/B, re-derives the "
                        "frozen-band table from evidence/frozen_band_raw_record.json, recomputes one "
                        "M-A statistic and one M-B tally from the raw JSONs, checks one failed run "
                        "against its own launcher-events file, verifies that no production file "
                        "changed (after/final_hashes.json), and writes the conclusion in review.md; "
                        "the implementer must not self-sign."),
        "input_hashes": {
            "CW_HEAD": "f39bd5a64224cd0c7aa098f23f64bf3811fa8939",
            "CW_test_file": "32515aa60d5fbfbca0778ee68e778ada7ff3bcf238f91930bb621d84aec005c1",
            "CW_supervisor_ps1": "5c12cd740cc36abf95f3b9559485472d9d9a760143d27de46e3aaa7b4bbbc311",
            "CW_logon_ps1": "70b4d7d7128567c0a753e684c3d4e8359c6a93bdc3dbefc7c5f93feaadbe5a1c",
            "I-14-C_frozen_frequency_json":
                "68d4e63e64744f099504ee4fa02cb299caa9c404978275ea8f884fbb92763e42",
            "iso_T0_manifest": (json.loads((ATTEMPT / "evidence" / "binding_hashes.json")
                                           .read_text(encoding="utf-8"))["trees"]["T0"]
                                ["manifest_sha256"]),
            "iso_T4_manifest": (json.loads((ATTEMPT / "evidence" / "binding_hashes.json")
                                           .read_text(encoding="utf-8"))["trees"]["T4"]
                                ["manifest_sha256"]),
        },
        "current_source_hashes": {
            "oracle.md": sha(ATTEMPT / "oracle.md"),
            "oracle-addendum-A.md": sha(ATTEMPT / "oracle-addendum-A.md"),
            "oracle-addendum-B.md": sha(ATTEMPT / "oracle-addendum-B.md"),
            "binding.json": sha(ATTEMPT / "binding.json"),
            "evidence/frozen_band_raw_record.json":
                sha(ATTEMPT / "evidence" / "frozen_band_raw_record.json"),
            "evidence/binding_hashes.json": sha(ATTEMPT / "evidence" / "binding_hashes.json"),
            "after/analysis.json": sha(ATTEMPT / "after" / "analysis.json"),
            "after/analysis.md": sha(ATTEMPT / "after" / "analysis.md"),
            "after/fail-able-cases.json": sha(ATTEMPT / "after" / "fail-able-cases.json"),
            "after/final_hashes.json": sha(ATTEMPT / "after" / "final_hashes.json"),
            "after/proposed-test-side-change.md":
                sha(ATTEMPT / "after" / "proposed-test-side-change.md"),
            "commands.json": sha(ATTEMPT / "commands.json"),
        },
        "changed_paths": [
            "execution_runs/I-14-E/a20260919-01/** only (attempt-local evidence, harness, iso "
            "copies and %TEMP%/i14e-* scratch)",
            "NO product code, NO product test, NO launcher, NO config: verified by "
            "after/final_hashes.json (production anchors byte-identical before/after)",
        ],
        "commands_executed": "commands.json (19 transcribed invocations; 5 of them are the "
                             "superseded mangled-path invocations, marked as such)",
        "raw_exit_codes": {
            "collectors": "all rc=0 except the 5 superseded M-B invocations (rc=1, died in 1-4 s "
                          "on the non-ASCII path literal)",
            "node_runner_rcs": {k: v for k, v in {
                "child-quiet": {"0": 1, "1": 17},
                "child-cpu8": {"0": 0, "1": 14, "driver-timeout(None)": 4},
                "child-spawn": {"0": 0, "1": 9},
                "logon-quiet": {"0": 8},
                "logon-cpu8": {"0": 8},
            }.items()},
        },
        "expected_exit_codes": ("collectors 0; product-node rc is pytest's own: 0 = node passed, "
                                "1 = node failed (assertion or the SUT's internal 15 s "
                                "subprocess timeout); rc=None in this attempt means the driver's "
                                "180 s guard fired because the pytest process never returned "
                                "(rung4)"),
        "results": {
            "frozen_band_hand_computed": {
                "per_tree_totals": analysis.get("frozen_band", {}).get("totals_by_tree"),
                "flip": analysis.get("frozen_band", {}).get("flip"),
            },
            "node1_bands": bands,
            "node1_by_tree": {k: (v or {}).get("by_tree")
                              for k, v in (analysis.get("m_b_bands") or {}).items()
                              if k.startswith("child")},
            "hypotheses": hypotheses,
            "determinism_verdict": (json.loads((ATTEMPT / "after" / "fail-able-cases.json")
                                               .read_text(encoding="utf-8"))["determinism_verdict"]
                                    if (ATTEMPT / "after" / "fail-able-cases.json").exists()
                                    else None),
        },
        "open_questions": [
            "Scope conflict to be adjudicated by the owner: the card text says this card fixes the "
            "product test's timing assumption, while this attempt's boundary (production repos "
            "READ-ONLY, zero writes; 'do not change product test timing assumptions') forbids "
            "applying it.  Delivered instead: identification + fail-able cases + an unapplied "
            "proposal (after/proposed-test-side-change.md).",
            "The card's exit criterion (tests no longer randomly red/green under load) is NOT "
            "satisfied by this attempt and is not self-signed.",
            "The machine was NOT quiet during this attempt: two unrelated chrome-headless-shell "
            "processes held ~8.8 of 12 logical cores and other sessions ran pytest campaigns "
            "(concurrent-activity.jsonl).  The 'quiet' arm therefore means 'no load added by this "
            "attempt'; the load-dependence evidence rests on the measured window (M-A) and on the "
            "frozen-band cross-era contrast, not on an arm-to-arm failure-rate difference (both "
            "arms are saturated).",
            "Node 2 disagrees with itself across measurement levels: end-to-end 16/16 passed, "
            "while the direct window probe missed the 15 s events budget in 6/8 loaded samples.  "
            "Reported side by side; a follow-up card would need to resolve it (e.g. by sampling "
            "the wrapper/supervisor start latency inside the node's own run).",
            "M-C's exit_seconds is an upper bound (up to two PowerShell spawns per poll); the real "
            "20 s margin is therefore unmeasured, only known to be small.",
            "The true p99.9 of the child launch latency is not bounded by n=111 samples; the "
            "proposed fix derives the timeout from an in-test measurement instead of a constant "
            "precisely for that reason.",
            "Three leftover fake-worker processes from the driver-guard (rung4) runs were found "
            "and reaped manually at ~22:3x, and one more (pid 12200, an attempt venv child of a "
            "reaped launcher) at the final sweep; run_band.sweep_leftovers was widened "
            "afterwards (mid-campaign harness change, affecting only post-timeout cleanup, not "
            "any measured quantity).  The final sweep left 0 leftover i14e launchers and 0 "
            "leftover i14e fake workers.",
        ],
        "blocked_by": [],
        "evidence_paths": {
            "oracle": ["oracle.md", "oracle-addendum-A.md", "oracle-addendum-B.md"],
            "binding": ["binding.json", "evidence/binding_hashes.json",
                        "evidence/freeze_instant.json"],
            "frozen_band": "evidence/frozen_band_raw_record.json",
            "windows": ["after/child-lifetime-popen-quiet.json",
                        "after/child-lifetime-popen-cpu8.json",
                        "after/child-lifetime-popen-cpu12.json",
                        "after/child-lifetime-startproc-quiet.json",
                        "after/child-lifetime-startproc-cpu8.json",
                        "after/wrapper-latency-quiet.json", "after/wrapper-latency-cpu8.json"],
            "bands": ["after/band-child-quiet.json", "after/band-child-cpu8.json",
                      "after/band-child-spawn.json", "after/band-logon-quiet.json",
                      "after/band-logon-cpu8.json"],
            "band_captures": "after/band-captures-*/ (stdout + launcher events per run)",
            "artifact_presence": ["after/artifacts-child-quiet.json", "after/artifacts-child-cpu8.json",
                                  "after/artifacts-child-spawn.json",
                                  "after/artifacts-logon-quiet.json",
                                  "after/artifacts-logon-cpu8.json",
                                  "after/artifacts-*/ (copied .source_catalog artefacts)"],
            "concurrent_activity": "after/concurrent-activity.jsonl",
            "analysis": ["after/analysis.json", "after/analysis.md"],
            "fail_able_cases": "after/fail-able-cases.json",
            "proposal": "after/proposed-test-side-change.md",
            "hashes": "after/final_hashes.json",
            "logs": ["after/campaign.log", "after/campaign-band.log", "after/finalize.log"],
            "scratch_kept": "%TEMP%/i14e-* (deliberately not deleted; see recovery/README.md)",
        },
        "reviewer_status": "pending (must be set by the independent reviewer; the implementer does "
                           "not self-sign)",
        "scope_declaration": {
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
            "qualification": ("test-timing measurement only: identification, fail-able cases and an "
                              "unapplied test-side proposal; no product runtime code, no product "
                              "test, production repos read-only"),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": payload["status"],
                      "hypotheses": hypotheses,
                      "determinism": payload["results"]["determinism_verdict"]["verdict"]
                      if payload["results"]["determinism_verdict"] else None}, indent=2))
    print("out:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
