"""I-14-C: run every frozen oracle case against the REAL worker exit and report raw facts.

This script is evidence collection only.  It never asserts on behalf of the oracle;
it records raw returncode / stdout / stderr / JSONL events per case plus a marker grep.

    python run_exit_probe.py --label before --out <attempt>/before \
        --python <iso venv python> --src <CW/src> --tests-dir <CW/tests/contract>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "drive_real_exit.py"
MARKER = "SYNTHETIC_AUDIT_TOKEN"
# r2 (review F-REV-D-01): the `bearer-newline` scenario carries the reviewer's
# synthetic 39-char credential, NOT the marker, so the per-case grep needs it too.
REVIEWER_SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"

# (case id, scenario, expect_marker_absent, extra argv, expected rc, expected business result)
CASES = [
    ("E1", "token-in-message", True, ["--cli-exit"], 3,
     "real exit leaks nothing: event+stderr clean, exception still re-raised"),
    ("E2a", "nested-cause", True, ["--cli-exit"], 3,
     "credential in the first cause is not persisted; stage/code/request_id survive"),
    ("E2a-deep", "nested-cause-deep", True, ["--cli-exit"], 3,
     "two-level cause chain: neither cause message may appear anywhere"),
    ("E2b", "unknown-key-with-token", True, ["--cli-exit"], 3,
     "token= form redacted"),
    ("E2b-residual", "unknown-key", False, ["--cli-exit"], 3,
     "digest= form is OUT of the frozen key set; residual reserved and reported, not hidden"),
    ("E3", "plain", True, ["--cli-exit"], 3,
     "no-secret exception keeps its text and type; nothing swallowed"),
    ("E4a", "quoted-truncation-boundary", True, ["--cli-exit"], 3,
     "LOAD-BEARING for R3: quoted value left unterminated by the 200-char cut"),
    ("E4b", "truncation-boundary", True, ["--cli-exit"], 3,
     "r1 unquoted case, kept as a non-load-bearing regression guard"),
    ("E1-no-cli", "token-in-message", True, [], 3,
     "re-raise path alone (no CLI handler) must be clean too"),
    # r2 (review F-REV-D-01 / RULING 2): the scheme word and the credential are on
    # different lines.  Load-bearing in BOTH directions: pre-fix it persisted the
    # credential, and the base tree deleted `doc=17`.  The persisted message must be
    # exactly `"Authorization: <redacted>\ndoc=17"`.
    ("E6-auth-scheme-newline", "bearer-newline", True, ["--cli-exit"], 3,
     "wrapped Authorization header: credential gone AND doc=17 kept"),
]

TEXT_SUFFIXES = {".jsonl", ".txt", ".json", ".log"}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _scan_dir(root: Path, secret: str = MARKER) -> dict:
    hits = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = _read_text(path)
        if secret in text:
            hits[str(path.relative_to(root))] = text.count(secret)
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--run-root",
        default="",
        help="fresh dir for this pass's run dirs; refuses to reuse a non-empty one "
             "(JSONL is append-only, so reusing a run dir would mix passes)",
    )
    parser.add_argument("--python", required=True)
    parser.add_argument("--src", required=True)
    parser.add_argument("--tests-dir", required=True)
    args = parser.parse_args(argv)

    out_root = Path(args.out)
    run_root = Path(args.run_root) if args.run_root else out_root / "runs"
    if run_root.exists() and any(run_root.iterdir()):
        print(
            "BINDING-REFUSED: run root is not empty, refusing to hide the "
            "previous pass's append-only evidence: " + str(run_root),
            file=sys.stderr,
        )
        return 97
    run_root.mkdir(parents=True, exist_ok=True)

    results = []
    for case_id, scenario, expect_absent, extra, expected_rc, business in CASES:
        # r2: the secret under test is per-case.  E4a's secret is the quoted run of Qs
        # (a marker-based grep would report 0 for it in every tree, which proves nothing);
        # the auth newline-split case carries the reviewer's synthetic credential.
        if scenario == "quoted-truncation-boundary":
            secret = "Q" * 20
        elif scenario == "bearer-newline":
            secret = REVIEWER_SECRET
        else:
            secret = MARKER
        run_dir = run_root / case_id
        run_dir.mkdir(parents=True, exist_ok=True)
        argv_list = [
            args.python, "-X", "utf8", "-B", str(DRIVER),
            "--scenario", scenario,
            "--run-dir", str(run_dir),
            "--src", args.src,
            "--tests-dir", args.tests_dir,
            *extra,
        ]
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            argv_list, cwd=str(run_dir), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
        )
        (run_dir / "stdout.txt").write_bytes(proc.stdout)
        (run_dir / "stderr.txt").write_bytes(proc.stderr)
        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")

        events_path = run_dir / "worker_process_events.jsonl"
        events = []
        if events_path.is_file():
            for line in _read_text(events_path).splitlines():
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        unhandled = next((e for e in events if e.get("event") == "unhandled_exception"), None)

        hits = {
            "stdout": stdout.count(secret),
            "stderr": stderr.count(secret),
            "events_file": _read_text(events_path).count(secret) if events_path.is_file() else 0,
            "other_attempt_files": _scan_dir(run_dir, secret),
        }
        # NB: this probe serialises the case's own argv into its result JSON, and the
        # argv carries the synthetic secret, so `other_attempt_files` is >= 1 for every
        # case by construction.  `persisted_or_printed_hits` therefore EXCLUDES the
        # probe's own JSON files and is the number the exit criterion is about.
        probe_own_outputs = {}
        for path in sorted(out_root.glob("*.json")):
            text = _read_text(path)
            if secret in text:
                probe_own_outputs[str(path)] = text.count(secret)
        own_output_total = sum(probe_own_outputs.values())
        hits["probe_own_result_files"] = probe_own_outputs
        total_hits = hits["stdout"] + hits["stderr"] + hits["events_file"]
        persisted_or_printed = total_hits + sum(
            count for path, count in hits["other_attempt_files"].items()
            if not path.endswith(".json"))
        results.append({
            "case_id": case_id,
            "scenario": scenario,
            "argv": argv_list,
            "cwd": str(run_dir),
            "secret_under_test": secret,
            "secret_len": len(secret),
            "raw_returncode": proc.returncode,
            "expected_returncode": expected_rc,
            "expected_business_result": business,
            "marker_expected_absent": expect_absent,
            "marker_hits": hits,
            "marker_total_hits": total_hits,
            "persisted_or_printed_hits": persisted_or_printed,
            "probe_own_json_hits": own_output_total,
            "marker_absent_ok": (persisted_or_printed == 0) if expect_absent else None,
            "event_order": [e.get("event") for e in events],
            "exception_type": (unhandled or {}).get("exception_type"),
            "message_redacted": (unhandled or {}).get("message_redacted"),
            "message_len": len((unhandled or {}).get("message_redacted") or ""),
            "cause_types": (unhandled or {}).get("cause_types"),
            "redacted_marker_present": "<redacted>" in ((unhandled or {}).get("message_redacted") or ""),
            "diagnostics_in_message": sorted(
                token for token in ("doc=17", "stage=summarize", "code=llm_global_failure",
                                    "request_id=req-1", "request_id=req-SYNTH-0001")
                if token in ((unhandled or {}).get("message_redacted") or "")),
            "stdout_head": stdout[:400],
            "stderr_head": stderr[:600],
            "evidence_dir": str(run_dir),
        })

    summary = {"label": args.label, "marker": MARKER,
               "reviewer_secret": REVIEWER_SECRET,
               "run_root": str(run_root), "cases": results}
    summary_path = out_root / f"probe_results_{args.label}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps(
        {
            "label": args.label,
            "summary": str(summary_path),
            "rows": [
                {
                    "case": c["case_id"],
                    "rc": c["raw_returncode"],
                    "secret_len": c["secret_len"],
                    "secret_total_hits": c["marker_total_hits"],
                    "persisted_or_printed_hits": c["persisted_or_printed_hits"],
                    "probe_own_json_hits": c["probe_own_json_hits"],
                    "secret_absent_ok": c["marker_absent_ok"],
                    "exception_type": c["exception_type"],
                    "msg_len": c["message_len"],
                    "message_redacted": c["message_redacted"],
                }
                for c in results
            ],
        },
        ensure_ascii=True, indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
