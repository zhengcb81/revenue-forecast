"""I-14-C r5: append the r5 command records to commands.json, with the RAW exit codes.

commands.json is the deliverable's command ledger, so its return codes must come from the runs
themselves and not from prose.  ``harness/run_r5_commands.py`` writes ``r5/commands-r5-rc.json``
(one entry per invocation, with the observed exit code and the evidence paths); this script folds
those invocations into commands.json, grouping invocations that share an id (the five-tree table
runs, the three CLI shapes, the four compat-control runs) under one entry whose
``raw_returncode`` is an object keyed by variant.

Absolute paths are rewritten to the placeholders the earlier rounds used (``<attempt>``,
``<iso-python>``, ``CW``) so the ledger is readable and machine-independent.  Existing r1..r4
entries are preserved; only entries whose id starts with ``CMD-I14C-R5`` are replaced, and the
file's key order is kept.

    python sync_commands_json.py --attempt <attempt> --commands <attempt>/commands.json \
        --rc <attempt>/r5/commands-r5-rc.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BUSINESS = {
    "CMD-I14C-R5-RULETABLE": (
        "rc 0/2/3 by the run_card convention: T0 cannot_adjudicate (no helper), T1 negative "
        "(leaks+fidelity), T2 pass, T3 specimen negative (0 leaks but fidelity failures), "
        "T4 pass - a green line now requires exact output fidelity, not just marker absence"
    ),
    "CMD-I14C-R5-DIAG": (
        "same convention on the 30-entry diagnostic corpus: registered pre-existing "
        "over-redactions are measured (known_over_redaction), a NEW over-redaction or a leak is "
        "negative; T0 cannot_adjudicate, T1 negative, T2/T4 pass, T3 negative via fidelity"
    ),
    "CMD-I14C-R5-COUNTS": (
        "mechanical counts written to r5/counts.json (rule table 44, diagnostics 30, fidelity "
        "cases 28, exact nodeids 28, total nodeids 82); exits 3 if the two pair counts disagree"
    ),
    "CMD-I14C-R5-PROBE": (
        "all acceptance cases 0 marker hits; E2b/E4a/E4b message lengths and E2b-residual "
        "unchanged by the line-ending normalisation"
    ),
    "CMD-I14C-R5-SUITE": "82 passed (fidelity pairs, F-07 deadline, E5a/b/c, order-swap control)",
    "CMD-I14C-R5-SUITE-OUTSIDE": (
        "82 passed from a %TEMP% cwd with NO I14C_RUN_ROOT declared: the reviewer can re-run the "
        "17 subprocess-backed cases themselves"
    ),
    "CMD-I14C-R5-CLI": (
        "E5a: rc=1, stderr marker hits 0, envelope identifies the config file; E5b: rc=1, 1 hit "
        "(C7 residual); E5c: rc=2, 1 hit (C6 residual); catalogs_created [] everywhere"
    ),
    "CMD-I14C-R5-COMPAT": (
        "backward compatibility: rc=1 with the enumerated environment/timing failures, all of "
        "which also fail on the pristine tree (see CMD-I14C-R5-COMPAT-ANALYSIS)"
    ),
    "CMD-I14C-R5-COMPAT-CONTROL": (
        "same suite twice per tree: the failing COUNT is not stable (timing nodes drop in and "
        "out), which is why the verdict uses the union criterion, not the per-run set"
    ),
    "CMD-I14C-R5-COMPAT-ANALYSIS": (
        "T4's failing-node union is a subset of T0's and only_on_T4 is empty: no compat failure "
        "is card-specific"
    ),
    "CMD-I14C-R5-GUARD": (
        "all 8 cases as expected: product paths (src, .source_catalog, revenue-forecast outside "
        ".planning) refused with 97 even when a scratch root is declared; declared scratch runs "
        "proceed (rc 3 = the driver's RE_RAISED sentinel); undeclared %TEMP% refused with 97"
    ),
    "CMD-I14C-R5-DIFF": "6 hunks, 15083 bytes, POSIX paths only",
    "CMD-I14C-R5-GITAPPLY": (
        "git apply --check and apply -p1 succeed and the three files are byte-identical to "
        "iso/product_fixed (GIT_APPLY_REPRODUCES_T4 true)"
    ),
    "CMD-I14C-R5-FLAKE": (
        "deep attempt-path basetemp: both nodes fail on BOTH trees (WinError 206 / "
        "FileNotFoundError); short basetemp: T0 6/6, T4 4/6 - the asymmetry is noise, see "
        "CMD-I14C-R5-FLAKE-FREQ"
    ),
    "CMD-I14C-R5-FLAKE-FREQ": (
        "interleaved frequency estimate (12 runs per tree x 2 passes): the tree with more "
        "failures flips between passes, i.e. a load-dependent flake on the product's own test, "
        "not a tree difference"
    ),
}

EXPECTED = {
    "CMD-I14C-R5-RULETABLE": {"product": 2, "product_r1": 3, "product_r2": 0,
                              "product_r3": 3, "product_fixed": 0},
    "CMD-I14C-R5-DIAG": {"product": 2, "product_r1": 3, "product_r2": 0,
                         "product_r3": 3, "product_fixed": 0},
    "CMD-I14C-R5-COUNTS": 0,
    "CMD-I14C-R5-PROBE": 0,
    "CMD-I14C-R5-SUITE": 0,
    "CMD-I14C-R5-SUITE-OUTSIDE": 0,
    "CMD-I14C-R5-CLI": 0,
    "CMD-I14C-R5-COMPAT": 1,
    "CMD-I14C-R5-COMPAT-CONTROL": 1,
    "CMD-I14C-R5-COMPAT-ANALYSIS": 0,
    "CMD-I14C-R5-GUARD": 0,
    "CMD-I14C-R5-DIFF": 0,
    "CMD-I14C-R5-GITAPPLY": 0,
    "CMD-I14C-R5-FLAKE": 0,
    "CMD-I14C-R5-FLAKE-FREQ": 0,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--commands", required=True)
    parser.add_argument("--rc", required=True)
    parser.add_argument("--repo", default=r"C:\Users\郑曾波\Projects\revenue-forecast")
    parser.add_argument("--company-wiki", default=r"C:\Users\郑曾波\Projects\company-wiki")
    parser.add_argument("--company-wiki-tests", default=r"C:\Users\郑曾波\Projects\company-wiki\tests\contract")
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    commands_path = Path(args.commands)
    rc = json.loads(Path(args.rc).read_text(encoding="utf-8"))
    ledger = json.loads(commands_path.read_text(encoding="utf-8"))

    def placeholders(text: str) -> str:
        return (text
                .replace(str(attempt / "iso" / "venv" / "Scripts" / "python.exe"), "<iso-python>")
                .replace(str(attempt), "<attempt>")
                .replace(args.company_wiki_tests, "CW/tests/contract")
                .replace(args.company_wiki, "CW")
                .replace(args.repo, "RF"))

    order: list[str] = []
    grouped: dict[str, dict] = {}
    for entry in rc["commands"]:
        cmd_id = entry["id"]
        variant = entry.get("variant")
        if cmd_id not in grouped:
            order.append(cmd_id)
            grouped[cmd_id] = {
                "id": cmd_id,
                "purpose": entry["purpose"],
                "cwd": placeholders(entry["cwd"]),
                "argv": [placeholders(part) for part in entry["argv"]],
                "env": {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
                "allowed_write_roots": ["<attempt>/r5"],
                "network": "disabled",
                "timeout_seconds": 900,
                "raw_returncode": {},
                "evidence": [],
                "variants": {},
            }
        target = grouped[cmd_id]
        if variant:
            target["raw_returncode"][variant] = entry["raw_returncode"]
            target["variants"][variant] = {
                "cwd": placeholders(entry["cwd"]),
                "argv": [placeholders(part) for part in entry["argv"]],
                "seconds": entry["seconds"],
            }
        else:
            target["raw_returncode"] = entry["raw_returncode"]
        if entry.get("stdout_evidence"):
            target["evidence"].append(entry["stdout_evidence"])
        if entry.get("stderr_evidence"):
            target["evidence"].append(entry["stderr_evidence"])

    for cmd_id in order:
        entry = grouped[cmd_id]
        entry["expected_returncode"] = EXPECTED.get(cmd_id)
        entry["expected_business_result"] = BUSINESS.get(cmd_id, "")
        entry["evidence"] = sorted(set(entry["evidence"]))
        entry["observed_as_expected"] = all(
            bool(e["as_expected"]) for e in rc["commands"] if e["id"] == cmd_id
        )

    kept = [e for e in ledger["commands"] if not str(e.get("id", "")).startswith("CMD-I14C-R5")]
    ledger["commands"] = kept + [grouped[cmd_id] for cmd_id in order]
    ledger["r5_run_script"] = "harness/run_r5_commands.py"
    ledger["r5_exit_code_convention"] = rc["exit_code_convention"]
    ledger["r5_all_as_expected"] = rc["all_as_expected"]
    ledger["r5_compat_control"] = rc.get("compat_control", {})
    commands_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"commands.json: {len(kept)} kept + {len(order)} r5 entries")
    for cmd_id in order:
        entry = grouped[cmd_id]
        print(f"  {cmd_id}: raw={entry['raw_returncode']} expected={entry['expected_returncode']} "
              f"as_expected={entry['observed_as_expected']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
