"""I-14-E-TESTSIDE: assemble ``handoff.json`` from the attempt's own artefacts.

Top-level contract (hard discipline):
  status = "review_pending"
  implementer_signed = false
plus: nine-step status, raw rc of the three arms, blocked_by, unverified,
sha256+bytes of every deliverable, and the git_diff_non_planning == 0 self-proof.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RF = ATTEMPT.parents[4]

DELIVERABLES = [
    "oracle.md",
    "oracle-addendum-A.md",
    "oracle-addendum-C.md",
    "before/freeze_instant.json",
    "before/hashed_before.json",
    "before/test_file_original.py",
    "before/final_hashes.json",
    "after/hashed_after.json",
    "after/boundary_check.json",
    "after/final_hashes.json",
    "after/changes.diff",
    "after/changes.manifest.json",
    "after/analysis.md",
    "red/band-red.json",
    "red/band-red-attempt1-infra-invalid.json",
    "green/band-green.json",
    "mut/band-mut.json",
    "harness/hashes.py",
    "harness/run_band.py",
    "harness/load.py",
    "harness/apply_fix.py",
    "harness/make_diff.py",
    "harness/tside_probe.py",
    "harness/manual_supervisor_probe.py",
    "harness/openprocess_probe.py",
    "harness/openprocess_probe2.py",
    "harness/write_handoff.py",
    "review.md",
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def git_non_planning() -> dict:
    r = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "HEAD", "--name-only"],
                       cwd=str(RF), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       text=True, encoding="utf-8", errors="replace")
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    non = [l for l in lines if not l.startswith(".planning")]
    return {"command": "git -c core.quotepath=false diff HEAD --name-only",
            "total_changed_paths": len(lines),
            "non_planning_count": len(non),
            "non_planning_paths": non,
            "self_proof": "ALL changed paths are under .planning/ (0 outside)" if not non
                          else "BREACH"}


def arm(path: Path) -> dict:
    band = load(path)
    if not band:
        return {"present": False}
    results = band.get("results", [])
    return {
        "present": True,
        "band": path.relative_to(ATTEMPT).as_posix(),
        "band_sha256": sha(path),
        "band_bytes": path.stat().st_size,
        "condition": band.get("condition"),
        "burners": band.get("burners"),
        "runs": band.get("runs"),
        "raw_returncodes": [r.get("returncode") for r in results],
        "raw_verdicts": [r.get("verdict") for r in results],
        "raw_walls": [r.get("wall_seconds") for r in results],
        "assertion_lines": [r.get("assertion") for r in results],
        "child_started_counts": [r.get("events", {}).get("child_started_count")
                                 for r in results],
        "hang_timeout_seconds_seen": [r.get("events", {}).get("hang_timeout_seconds")
                                      for r in results],
        "tside_traces": [t for r in results for t in r.get("tside_trace", [])],
        "tally": band.get("tally"),
        "ambient_sample": band.get("ambient_sample"),
        "spawn_latency_by_pass": band.get("spawn_latency_by_pass"),
        "load_probe_per_run": [r.get("load_probe") for r in results],
        "basetemp_decision_lines": [ln for r in results
                                    for ln in r.get("basetemp_decision_lines", [])],
        "driver_timeout_seconds": band.get("driver_timeout_seconds"),
        "started_utc": band.get("started_utc"),
        "finished_utc": band.get("finished_utc"),
    }


def main() -> int:
    deliverables = []
    for rel in DELIVERABLES:
        path = ATTEMPT / rel
        if path.is_file():
            deliverables.append({"path": rel, "bytes": path.stat().st_size,
                                 "sha256": sha(path)})
        else:
            deliverables.append({"path": rel, "missing": True})

    boundary = load(ATTEMPT / "after" / "boundary_check.json")
    diff_manifest = load(ATTEMPT / "after" / "changes.manifest.json")
    freeze = load(ATTEMPT / "before" / "freeze_instant.json")

    nine_steps = [
        {"step": 1, "name": "先冻结 oracle（expected 手算自源卡原始数据）",
         "status": "done",
         "evidence": ["oracle.md", "before/freeze_instant.json",
                      f"oracle_sha256={freeze.get('oracle_sha256')}",
                      "冻结先于任何红/绿/变异 pytest 运行"],
         "note": "追加式 erratum：oracle-addendum-A（basetemp 落点）、"
                 "oracle-addendum-C（会话环境阻断）；主文一字未改"},
        {"step": 2, "name": "边界自证（iso src/scripts 与真仓逐字节不变）",
         "status": "done",
         "evidence": ["before/hashed_before.json", "after/hashed_after.json",
                      "before/final_hashes.json", "after/final_hashes.json",
                      "after/boundary_check.json"],
         "verdict": boundary.get("verdict")},
        {"step": 3, "name": "红→绿（同负载条件）",
         "status": "partial",
         "evidence": ["red/band-red.json", "green/band-green.json"],
         "note": "两臂均在源卡 cpu8 条件下跑了冻结的 N=6；但启动器在看门狗之前即"
                 "`launcher_exception`，时序机制未被触发 ⇒ 红的**形态**与绿均不可证"
                 "（oracle-addendum-C §C3）"},
        {"step": 4, "name": "变异证明（至少一个变异体把新判据打红）",
         "status": "not_demonstrable",
         "evidence": ["mut/band-mut.json"],
         "note": "M1（导出公式退回写死 0.5 s）已按冻结协议跑 N=6 并全红，但与"
                 "绿臂同因失败、无判别力 ⇒ 不构成变异证明"},
        {"step": 5, "name": "负载条件独立测量记录",
         "status": "done",
         "evidence": ["red/band-red.json", "green/band-green.json", "mut/band-mut.json"],
         "note": "每臂 3 次 3 s 进程 CPU 差分（before/with_load/after）+ 每次运行的 "
                 "sleep20 超调、30 万次循环耗时 + 每 pass spawn 延迟"},
        {"step": 6, "name": "changes.diff（只含 tests/**，逐文件披露）",
         "status": "done",
         "evidence": ["after/changes.diff", "after/changes.manifest.json"],
         "file_count": diff_manifest.get("file_count"),
         "all_paths_under_tests": diff_manifest.get("all_paths_under_tests")},
        {"step": 7, "name": "handoff：review_pending / 不代签 / blocked_by / unverified",
         "status": "done",
         "evidence": ["handoff.json"]},
        {"step": 8, "name": "交付证据入本 attempt 目录",
         "status": "done",
         "evidence": [d["path"] for d in deliverables if not d.get("missing")]},
        {"step": 9, "name": "只读自证 + 报父派复审",
         "status": "done",
         "evidence": ["after/boundary_check.json", "report sent to parent agent"],
         "git_diff_non_planning": git_non_planning()["non_planning_count"]},
    ]

    payload = {
        "card": "I-14-E-TESTSIDE",
        "attempt": "a20260924-01",
        "parent_card": "I-14",
        "source_card": "I-14-E/a20260919-01 (unchanged: no byte, no status)",
        "authorization": "OWNER_DECISIONS.md §二十五 (owner 2026-09-24 option A)",
        "status": "review_pending",
        "implementer_signed": False,
        "signed_by": None,
        "signature_note": "ACCEPT may only be signed by an independent reviewer; "
                          "this implementer does not self-sign and does not promote.",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),

        "chosen_fix": {
            "proposal": "建议1 (source card recommended) + semantic upper bound",
            "formula": "H = -WorkerHangTimeoutSeconds = min(max(2.0, 4*t0), t0 + 3.0)",
            "t0": "launch -> first side effect (fake_worker_count.txt) measured in the "
                  "same test with the supervisor's own clock (Start-Process-based)",
            "why": "lower bound covers the worst observed tail (2.486 s) because every "
                   "cpu8 t0 sample in the source card was >= 0.642 s; upper bound keeps "
                   ">= 2 s before behaviour #1's 5 s sleep ends so the watchdog still "
                   "fires (bare 4*t0 breaks for t0 >= 1.667 s, inside the observed band "
                   "(cpu8 Q1 p90 = 2.133 s))",
            "rejected_proposals": {
                "建议3 (loosen == 2 to >= 2)": "card article 4 classifies it as "
                    "post-hoc loosening and requires a written justification from the "
                    "test maintainer that this card does not have; it would also destroy "
                    "the mutation's discriminating power",
                "建议2 alone": "source card measured that it does not solve the problem "
                    "by itself ($Runtime is still null between Start-Process and the "
                    "runtime write, so the uptime branch is still taken)",
                "node 2 (15/15/20 s budgets)": "source card M-B measured 16/16 passing "
                    "end-to-end (quiet 8/8, cpu8 8/8) and its own H5 verdict is 'no jitter "
                    "band observed' -> no red can be reproduced -> per discipline no "
                    "change is applied, registered as unverified",
            },
            "changed_parameter_count": 1,
            "product_code_changed": "none (iso/src, iso/scripts and the production repo "
                                    "are byte-identical before/after)",
        },

        "nine_steps": nine_steps,
        "arms": {
            "red_pre_fix": arm(ATTEMPT / "red" / "band-red.json"),
            "green_post_fix": arm(ATTEMPT / "green" / "band-green.json"),
            "mutation_m1": arm(ATTEMPT / "mut" / "band-mut.json"),
            "discarded_infra_attempt": {
                "band": "red/band-red-attempt1-infra-invalid.json",
                "reason": "pytest basetemp created with mode=0o700 was unlistable in this "
                          "session (CPython documents that mode as ignored on Windows); "
                          "all 6 runs errored in the tmp_path fixture. Disclosed in "
                          "oracle-addendum-C §C4, artefacts kept.",
                "raw_returncodes": [1, 1, 1, 1, 1, 1],
            },
        },

        "blocked_by": [
            {"id": "ENV-OPENPROCESS-ALLACCESS-DENIED",
             "condition": "this session's token cannot OpenProcess(PROCESS_ALL_ACCESS, ...) "
                          "for any target (winerror=5), so PowerShell's "
                          "Start-Process -RedirectStandard* -PassThru returns a Process "
                          "whose .Handle is null",
             "effect": "source_catalog_worker.ps1:341 [CompanyWiki.KillOnCloseJob]::Assign "
                       "throws -> launcher_exception -> supervisor exit 1 before the "
                       "watchdog runs; child_started count is 0 in every run",
             "evidence": ["harness/openprocess_probe.py output (ALL_ACCESS denied / "
                          "QUERY_LIMITED ok, recorded in this handoff's probe_runs)",
                          "harness/manual_supervisor_probe.py (2/2 launcher_exception, "
                          "no pytest involved)",
                          "red|green|mut band files: child_started_count = 0 in all 18 runs"],
             "scope": "session permission scope; approvals are disabled in this session, "
                      "so it cannot be widened from inside",
             "what_it_blocks": ["red mechanism reproduction", "green demonstration",
                                "mutation discrimination"],
             "unblock_recipe": "re-run the three arms exactly as frozen in oracle.md §4 in "
                               "a session whose token can open its own children with "
                               "PROCESS_ALL_ACCESS; the oracle does not need re-freezing "
                               "because every expected value comes from the source card's "
                               "raw data"}],

        "unverified": [
            "green: 6/6 under cpu8 NOT demonstrated (all 6 runs failed on the "
            "environmental launcher_exception, not on the timing mechanism)",
            "mutation M1: red NOT demonstrated as a discriminating signal (fails for the "
            "same environmental reason as the green arm)",
            "red: the frozen expectation (assert N == 2 / TimeoutExpired form) was NOT "
            "reproduced; the observed red form is launcher_exception (oracle-addendum-C §C3)",
            "node 2 (logon wrapper 15/15/20 s budgets): not applied, no reproducible red "
            "(source card M-B 16/16 green); source card's M-C window measurements still "
            "show thin margin (events 6/8 >= 15 s, exit max 21.593 >= 20 s)",
            "product qualification: this card gives test-side timing change evidence only; "
            "disclosure_adaptation=unmapped, accuracy=unproven",
        ],

        "boundary": boundary,
        "git_diff_non_planning": git_non_planning(),
        "changes": {
            "diff": "after/changes.diff",
            "diff_bytes": (ATTEMPT / "after" / "changes.diff").stat().st_size
                          if (ATTEMPT / "after" / "changes.diff").is_file() else None,
            "diff_sha256": sha(ATTEMPT / "after" / "changes.diff")
                           if (ATTEMPT / "after" / "changes.diff").is_file() else None,
            "file_count": diff_manifest.get("file_count"),
            "files": diff_manifest.get("files"),
            "only_tests": diff_manifest.get("all_paths_under_tests"),
        },
        "deliverables": deliverables,
        "open_questions_for_reviewer": [
            "oracle-addendum-A §A3: pytest's basetemp/cwd scratch lives under %TEMP% "
            "(as the source card's M-B did) because pytest resolves --basetemp to its "
            "long path (tmpdir.py:159) and the attempt dir's long path exceeds MAX_PATH; "
            "is that deviation acceptable?",
            "harness/tside_probe.py dir-mode shim (forces mode=0o777, restoring CPython's "
            "documented Windows semantics) is applied to all three arms identically; "
            "confirm that is neutral for this node",
            "t0 measured in this session (0.194-0.483 s) is smaller than the source card's "
            "startproc band (0.508-2.109 s), so H hit the 2.0 floor in all 6 green runs; "
            "confirm the floor justification still holds under a session where the "
            "watchdog can actually run",
        ],
    }

    out = ATTEMPT / "handoff.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "implementer_signed": payload["implementer_signed"],
        "steps": {s["step"]: s["status"] for s in nine_steps},
        "git_diff_non_planning": payload["git_diff_non_planning"]["non_planning_count"],
        "deliverables_missing": [d["path"] for d in deliverables if d.get("missing")],
        "out": str(out),
        "bytes": out.stat().st_size,
        "sha256": sha(out),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
