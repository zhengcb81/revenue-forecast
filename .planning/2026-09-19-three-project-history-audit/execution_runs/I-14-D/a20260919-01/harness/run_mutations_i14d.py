"""I-14-D r2: run the revised mutation plan (M1..M4) and record every raw rc.

Each mutation tree is a byte copy of `iso/product_narrow` with exactly one localized
edit (harness/apply_i14d_narrow.py --op <specimen>), so the deltas are honest single-
site derivations.  This driver only RUNS the harnesses and records rcs + the facts
they print; the expected matrix lives in oracle.md and is re-checked by the reviewer.

    python run_mutations_i14d.py --python <venv python> --out-root <attempt>/mutations

Matrix (r2):

    M1 mut_greedy      scanner loop UN-narrowed           -> assignment path loses C13
    M2 mut_authnl      auth token join [ \\t]+ -> \\s+     -> auth line-bound is load-bearing
    M3 mut_auth1_r2    auth value = strict single token   -> naive narrowing LEAKS
    M4 mut_authsplit   scheme branch removed              -> the r2 fix LEAKS (F-REV-D-01)

M4 is the arm the first pass lacked: it covers the LEAK direction of the auth
newline-split family instead of only the C13 direction.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
VENV_PY = ATT / "iso" / "venv" / "Scripts" / "python.exe"
CW_TESTS = Path(os.environ.get("I14C_CW_ROOT",
                               r"C:\Users\郑曾波\Projects\company-wiki")) / "tests" / "contract"

# specimen op -> iso tree name
MUTANTS = [
    ("M1", "mut_greedy", "product_mut_greedy"),
    ("M2", "mut_authnl", "product_mut_authnl"),
    ("M3", "mut_auth1_r2", "product_mut_auth1_r2"),
    ("M4", "mut_authsplit", "product_mut_authsplit"),
]


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(argv, cwd=str(cwd), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=str(VENV_PY))
    parser.add_argument("--out-root", default=str(ATT / "mutations"))
    parser.add_argument("--only", default="", help="comma-separated mutant ids")
    args = parser.parse_args(argv)

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    wanted = [m.strip() for m in args.only.split(",") if m.strip()]

    report: dict = {"python": args.python, "out_root": str(out_root), "mutants": {}}
    for mid, op, tree in MUTANTS:
        if wanted and mid not in wanted:
            continue
        src = ATT / "iso" / tree / "src"
        entry: dict = {"op": op, "tree": tree, "src": str(src)}
        if not src.is_dir():
            entry["missing_tree"] = True
            report["mutants"][mid] = entry
            continue

        oracle = out_root / f"oracle_{op}.json"
        rule = out_root / f"rule_table_{op}.json"
        probe = out_root / f"authsplit_probe_{op}.json"

        proc = _run([args.python, "-X", "utf8", "-B",
                     str(HERE / "run_i14d_oracle.py"), "--src", str(src),
                     "--label", op, "--out", str(oracle)], ATT)
        entry["oracle_rc"] = proc.returncode
        entry["oracle_stdout_head"] = proc.stdout.decode("utf-8", "replace")[:1200]
        if oracle.is_file():
            data = json.loads(oracle.read_text(encoding="utf-8"))
            entry["oracle_narrow_must_failed"] = data.get("narrow_must_failed")
            entry["oracle_keep_must_failed"] = data.get("keep_must_failed")
            entry["oracle_verdict"] = data.get("verdict")

        proc = _run([args.python, "-X", "utf8", "-B",
                     str(HERE / "run_rule_table_i14d.py"), "--src", str(src),
                     "--label", op, "--out", str(rule)], ATT)
        entry["rule_table_rc"] = proc.returncode
        if rule.is_file():
            data = json.loads(rule.read_text(encoding="utf-8"))
            entry["rule_table_entries"] = data.get("entries")
            entry["credential_leaks"] = data.get("credential_leaks")
            entry["credential_secret_leaks"] = data.get("credential_secret_leaks")
            entry["touched_but_should_not_be"] = data.get("touched_but_should_not_be")
            entry["fidelity_failures"] = [f["id"] for f in data.get("fidelity_failures", [])]
            entry["rule_table_verdict"] = data.get("verdict")

        proc = _run([args.python, "-X", "utf8", "-B",
                     str(HERE / "authsplit_probe.py"), "--src", str(src),
                     "--label", op, "--out", str(probe)], ATT)
        entry["authsplit_probe_rc"] = proc.returncode
        if probe.is_file():
            data = json.loads(probe.read_text(encoding="utf-8"))
            entry["authsplit_probe_leaks"] = data.get("credential_leaks")
            entry["authsplit_probe_verdict"] = data.get("verdict")

        # the real exit, through the unchanged product doubles
        run_root = out_root / f"runs-{op}"
        if not run_root.exists() or not any(run_root.iterdir()):
            proc = _run([args.python, "-X", "utf8", "-B",
                         str(HERE / "run_exit_probe.py"), "--label", op,
                         "--out", str(out_root), "--run-root", str(run_root),
                         "--python", args.python, "--src", str(src),
                         "--tests-dir", str(CW_TESTS)], ATT)
            entry["exit_probe_rc"] = proc.returncode
            summary = out_root / f"probe_results_{op}.json"
            if summary.is_file():
                data = json.loads(summary.read_text(encoding="utf-8"))
                entry["exit_probe_rows"] = [
                    {"case": c["case_id"], "rc": c["raw_returncode"],
                     "secret_absent_ok": c["marker_absent_ok"],
                     "msg": c["message_redacted"]}
                    for c in data["cases"]
                ]
        else:
            entry["exit_probe_rc"] = "skipped: run root already populated"

        report["mutants"][mid] = entry
        print(json.dumps({mid: {k: v for k, v in entry.items()
                                if k != "oracle_stdout_head"}},
                         ensure_ascii=True, indent=2))

    out = out_root / "mutation_matrix.json"
    out.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
