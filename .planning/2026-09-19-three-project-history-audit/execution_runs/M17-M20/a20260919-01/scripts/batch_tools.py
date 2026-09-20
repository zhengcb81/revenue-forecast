"""Batch-level tools for the M17-M20 hand-off: write the rc namespace table and validate every JSON.

P2-B (independent review r2): `rc_namespace.json` was not valid JSON (a Python-style implicit string
concatenation had been written into it), and that file is the machine-readable copy of the hard rule
"never aggregate rc values across cards without naming the runner sha256".  This tool therefore
GENERATES the file from a Python dict (so the result is valid by construction), re-reads it with
json.load, and then validates every .json under the batch directory and the four attempts.

Usage (batch-level; writes only inside the batch directory):
  python -X utf8 -B batch_tools.py write-rc-namespace --batch-root <batch> --runs-root <execution_runs>
  python -X utf8 -B batch_tools.py verify-json --batch-root <batch> --runs-root <execution_runs>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

CARDS = ("M17", "M18", "M19", "M20")

NAMESPACES = {
    "M17-M20 a20260919-01 (after the r2 fixes)": {
        "runner_script": "scripts/run_card.py",
        "runner_sha256": None,  # filled from disk at write time
        "exit_codes": {
            "0": "pass",
            "1": "harness error (the runner itself could not produce a verdict)",
            "2": "no verdict: a frozen expectation is missing or unusable (positive expectations, or any case's declared 'expected' in cases.json), or the observed output cannot be faithfully compared with the frozen shape",
            "3": "negative verdict: a judgement was possible and did not hold (positive raised/out of tolerance, continuity mismatch, a negative case raised nothing, or a negative case raised an exception whose exact type name is not the declared one)",
        },
        "declared_expectation_enforcement": "yes, by EXACT exception type name (never isinstance: ModelRegistryError is a ValueError subclass)",
        "case_verdict_taxonomy": "PASS_rejected | FAIL_not_rejected | FAIL_wrong_exception_type | FAIL_import_or_file_error | FAIL_declared_expectation_mismatch | NOT_JUDGED_declaration_unusable (mutually exclusive)",
        "reason_namespace": "negatives_not_rejected:<ids> = nothing was raised; declared_expectation_mismatch:<ids> = an exception was raised whose exact type name is not the declared one; cases_json_declared_expectation_missing:<ids> = the declaration is unusable, so the case is NOT JUDGED and the runner refuses a verdict (rc=2)",
        "precedence": "1 > 2 > 3 > 0",
    },
    "M17-M20 a20260919-01 (r1, before the declared-expectation fix)": {
        "runner_script": "scripts/run_card.py",
        "runner_sha256": "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd",
        "exit_codes": {
            "0": "pass",
            "1": "not defined by that runner",
            "2": "harness/bookkeeping failure - no verdict exists",
            "3": "negative verdict (declared expectation NOT enforced)",
        },
        "declared_expectation_enforcement": "no",
        "precedence": "2 > 3 > 0",
    },
    "M05-M08 a20260919-01": {
        "runner_script": "scripts/run_card.py",
        "runner_sha256": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
        "exit_codes": {
            "0": "pass",
            "1": "not defined by that runner (a bare 1 there is not a harness-error signal)",
            "2": "harness/bookkeeping failure - no verdict exists",
            "3": "negative verdict (declared expectation NOT enforced)",
        },
        "declared_expectation_enforcement": "no",
    },
    "other batches (reported by the r2 review; NOT verified by this batch)": {
        "runner_sha256_by_batch": {
            "M01-M04": "b5fcc685 (no declared-expectation enforcement)",
            "M09-M12": "997c553b (no)",
            "M13-M16": "9e4a6450 (yes, different mechanism)",
            "M21-M24": "d02057de (no; the r2 review notes M21-M24 have since moved to a5ee7599)",
            "M25-M28": "eab01162 (yes, different mechanism)",
            "M29-M31": "9ea69c72 (no)",
        },
        "exit_codes": "NOT VERIFIED BY THIS BATCH - do not infer them from any namespace above",
    },
}

HARD_RULE = ("Never aggregate, average, count or compare raw rc values across cards without naming the "
             "runner sha256 that produced them: the same integer means different things in different "
             "runner generations (2 = harness failure in one, 2 = 'no verdict could be issued' in "
             "another), and only some runners enforce the declared expectation.")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def write_rc_namespace(batch_root: str, runs_root: str) -> int:
    namespaces = json.loads(json.dumps(NAMESPACES))
    key = "M17-M20 a20260919-01 (after the r2 fixes)"
    namespaces[key]["runner_sha256"] = sha256(
        os.path.join(runs_root, "M17", "a20260919-01", "scripts", "run_card.py"))
    doc = {
        "batch_id": "M17-M20",
        "attempt_id": "a20260919-01",
        "purpose": ("rc namespace table: the exit codes of the M-card runners are NOT comparable across "
                    "runner versions"),
        "hard_rule": HARD_RULE,
        "namespaces": namespaces,
        "written_by": "scripts/batch_tools.py write-rc-namespace (batch-level tooling)",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "self_check": "re-read with json.load immediately after writing (see stdout)",
        "adjudicated_by": ("PENDING - owner/dispatcher; this table states facts about artefacts, it does "
                           "not rule on how other batches must be re-run"),
    }
    out = os.path.join(batch_root, "rc_namespace.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    with open(out, "r", encoding="utf-8") as handle:
        back = json.load(handle)  # P2-B self-check
    ok = back["namespaces"][key]["runner_sha256"] == namespaces[key]["runner_sha256"]
    print("rc_namespace.json written:", out)
    print("bytes:", os.path.getsize(out), "sha256:", sha256(out))
    print("json.load re-read OK:", True, "| runner_sha256:", namespaces[key]["runner_sha256"])
    print("self_check_roundtrip_ok:", ok)
    return 0 if ok else 3


def verify_json(batch_root: str, runs_root: str) -> int:
    roots = [batch_root]
    for card in CARDS:
        roots.append(os.path.join(runs_root, card, "a20260919-01"))
    checked = 0
    failures = []
    for root in roots:
        for base, _dirs, files in os.walk(root):
            if os.path.normcase(os.path.join("iso", "venv")) in os.path.normcase(base):
                continue
            for name in files:
                if not name.endswith(".json"):
                    continue
                path = os.path.join(base, name)
                checked += 1
                try:
                    with open(path, "r", encoding="utf-8") as handle:
                        json.load(handle)
                except Exception as exc:  # noqa: BLE001
                    failures.append({"path": path, "error": "%s: %s" % (type(exc).__name__, exc)})
    doc = {
        "scope": "every .json under the batch directory and the four card attempts (iso/venv excluded)",
        "checked": checked,
        "failures": failures,
        "failure_count": len(failures),
        "roots": roots,
        "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out = os.path.join(batch_root, "batch_json_validation.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("json files checked:", checked, "failures:", len(failures))
    for f in failures[:10]:
        print("   FAIL", f["path"], f["error"])
    print("written", out)
    return 0 if not failures else 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("write-rc-namespace", "verify-json"))
    parser.add_argument("--batch-root", required=True)
    parser.add_argument("--runs-root", required=True)
    args = parser.parse_args()
    if args.command == "write-rc-namespace":
        return write_rc_namespace(args.batch_root, args.runs_root)
    return verify_json(args.batch_root, args.runs_root)


if __name__ == "__main__":
    raise SystemExit(main())
