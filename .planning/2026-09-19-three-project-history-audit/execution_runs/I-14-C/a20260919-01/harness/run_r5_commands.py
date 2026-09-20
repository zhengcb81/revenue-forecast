"""I-14-C r5: run every r5 command in one pass and record its RAW exit code.

``commands.json`` promises raw return codes.  Instead of transcribing them by hand (which is
how r4 ended up with prose numbers that disagreed with the code), this script executes the r5
command set itself and writes ``r5/commands-r5-rc.json`` plus a flat transcript.  Each command's
stdout/stderr goes to the same evidence path the attempt already cites, so the artefact and the
exit code always come from one execution.

Exit codes of the TABLE scripts are the point of F-I14C-R4-06/07:
    0 = pass, 2 = cannot adjudicate (helper absent), 3 = negative verdict.

    python run_r5_commands.py --attempt <attempt> --python <iso-python> --repo <company-wiki>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TREES = ("product", "product_r1", "product_r2", "product_r3", "product_fixed")
# tree -> the verdict the frozen r5 expectations require
EXPECTED_TABLE = {
    "product": 2,
    "product_r1": 3,
    "product_r2": 0,
    "product_r3": 3,
    "product_fixed": 0,
}
SUITE_TIMEOUT = 900


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    python = str(Path(args.python).resolve())
    repo = Path(args.repo).resolve()
    harness = attempt / "harness"
    r5 = attempt / "r5"
    tests = repo / "tests" / "contract"

    base_env = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "USERPROFILE": os.environ.get("USERPROFILE", ""),
    }

    transcript: list[str] = []
    entries: list[dict] = []

    def record(cmd_id: str, purpose: str, cmd: list[str], cwd: Path, stdout_path: Path,
               stderr_path: Path | None = None, env: dict | None = None,
               expected: object = None, variant: str | None = None) -> int:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        proc = subprocess.run(
            cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env if env is not None else base_env, timeout=SUITE_TIMEOUT,
        )
        elapsed = round(time.time() - started, 2)
        stdout_path.write_bytes(proc.stdout)
        if stderr_path is not None:
            stderr_path.parent.mkdir(parents=True, exist_ok=True)
            stderr_path.write_bytes(proc.stderr)
        out_text = proc.stdout.decode("utf-8", "replace").strip()
        err_text = proc.stderr.decode("utf-8", "replace").strip()
        out_lines = out_text.splitlines()
        err_lines = err_text.splitlines()
        entry = {
            "id": cmd_id,
            "variant": variant,
            "purpose": purpose,
            "cwd": str(cwd),
            "argv": cmd,
            "raw_returncode": proc.returncode,
            "expected_returncode": expected,
            "as_expected": expected is None or proc.returncode == expected,
            "seconds": elapsed,
            "stdout_evidence": str(stdout_path.relative_to(attempt)),
            "stderr_evidence": (
                str(stderr_path.relative_to(attempt)) if stderr_path is not None else None
            ),
            "stdout_tail": out_lines[-1][:200] if out_lines else "",
            "stderr_tail": err_lines[-1][:200] if err_lines else "",
        }
        entries.append(entry)
        line = (f"{cmd_id}{'/' + variant if variant else ''}: rc={proc.returncode} "
                f"expected={expected} as_expected={entry['as_expected']} "
                f"({elapsed}s) {entry['stdout_tail']}")
        transcript.append(line)
        print(line, flush=True)
        return proc.returncode

    # 1) rule table, five trees -------------------------------------------------------
    for tree in TREES:
        record(
            "CMD-I14C-R5-RULETABLE",
            "r5: rule table with exact-output fidelity, 44 entries, 0/2/3 convention",
            [python, "-X", "utf8", "-B", str(harness / "run_rule_table.py"),
             "--src", str(attempt / "iso" / tree / "src"), "--label", tree,
             "--out", str(r5 / f"rule_table_{tree}.json")],
            cwd=attempt,
            stdout_path=r5 / f"rule_table_{tree}.stdout.txt",
            expected=EXPECTED_TABLE[tree],
            variant=tree,
        )

    # 2) diagnostic corpus, five trees -------------------------------------------------
    for tree in TREES:
        record(
            "CMD-I14C-R5-DIAG",
            "r5: 30-entry diagnostic corpus (over-redaction scope), 0/2/3 convention",
            [python, "-X", "utf8", "-B", str(harness / "run_diagnostic_table.py"),
             "--src", str(attempt / "iso" / tree / "src"), "--label", tree,
             "--out", str(r5 / f"diagnostics_{tree}.json")],
            cwd=attempt,
            stdout_path=r5 / f"diagnostics_{tree}.stdout.txt",
            expected=EXPECTED_TABLE[tree],
            variant=tree,
        )

    # 3) mechanical counts -------------------------------------------------------------
    record(
        "CMD-I14C-R5-COUNTS",
        "r5: derive every reported count from the artefacts (single source of truth)",
        [python, "-X", "utf8", "-B", str(harness / "report_counts.py"),
         "--attempt", str(attempt), "--python", python, "--out", str(r5 / "counts.json")],
        cwd=attempt,
        stdout_path=r5 / "counts.stdout.txt",
        expected=0,
    )

    # 4) per-file probe.  The probe refuses to reuse a non-empty run root, because its JSONL is
    # append-only and a reused root would mix passes - so each pass gets its own run root and
    # the earlier ones stay on disk as evidence (nothing is deleted).
    probe_run_root = r5 / f"runs-r5-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    record(
        "CMD-I14C-R5-PROBE",
        "r5: per-file probe E1..E4b with per-case marker and length baselines",
        [python, "-X", "utf8", "-B", str(harness / "run_exit_probe.py"),
         "--label", "r5-after", "--out", str(r5),
         "--run-root", str(probe_run_root), "--python", python,
         "--src", str(attempt / "iso" / "product_fixed" / "src"),
         "--tests-dir", str(tests)],
        cwd=attempt,
        stdout_path=r5 / "probe-r5-after.txt",
        expected=0,
    )

    # 5) full suite inside the attempt --------------------------------------------------
    record(
        "CMD-I14C-R5-SUITE",
        "r5: full 82-case suite (fidelity, F-07 deadline, E5a/b/c, order-swap control)",
        [python, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
         "--basetemp", str(r5 / "cmd-r5-suite" / "pytest"), "-q",
         str(harness / "tests" / "test_i14c_real_exit_redaction.py")],
        cwd=r5 / "cmd-r5-suite",
        stdout_path=r5 / "cmd-r5-suite" / "stdout.txt",
        stderr_path=r5 / "cmd-r5-suite" / "stderr.txt",
        expected=0,
    )

    # 6) full suite OUTSIDE execution_runs, no env var (reviewer "unable to verify" #1) --
    outside = Path(tempfile.mkdtemp(prefix="i14c-r5-outside-"))
    record(
        "CMD-I14C-R5-SUITE-OUTSIDE",
        "r5: the same suite from a %TEMP% cwd with NO I14C_RUN_ROOT (independent re-run)",
        [python, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
         "--basetemp", str(outside / "pytest"), "-q",
         str(harness / "tests" / "test_i14c_real_exit_redaction.py")],
        cwd=outside,
        stdout_path=r5 / "cmd-r5-outside-execution-runs.txt",
        expected=0,
    )

    # 7) real CLI ----------------------------------------------------------------------
    for shape in ("E5a", "E5b", "E5c"):
        run_dir = r5 / f"cli-r5-{shape}"
        record(
            "CMD-I14C-R5-CLI",
            f"r5: real CLI exit {shape} against the fixed tree",
            [python, "-X", "utf8", "-B", str(harness / "run_real_cli_exit.py"),
             "--shape", shape, "--run-dir", str(run_dir),
             "--src", str(attempt / "iso" / "product_fixed" / "src"),
             "--python", python],
            cwd=attempt,
            stdout_path=run_dir / "driver_stdout.txt",
            stderr_path=run_dir / "driver_stderr.txt",
            expected=0,
            variant=shape,
        )

    # 8) backward compatibility ---------------------------------------------------------
    compat_cwd = r5 / "cmd-compat"
    record(
        "CMD-I14C-R5-COMPAT",
        "r5: backward compatibility of the worker bootstrap + observability contracts",
        [python, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
         "--basetemp", str(compat_cwd / "pytest"), "-q",
         str(tests / "test_source_catalog_worker_bootstrap.py"),
         str(tests / "test_observability.py")],
        cwd=compat_cwd,
        stdout_path=compat_cwd / "stdout.txt",
        stderr_path=compat_cwd / "stderr.txt",
        env={**base_env, "PYTHONPATH": str(attempt / "iso" / "product_fixed" / "src")},
    )

    # 9) compat control: the same suite on BOTH trees, twice, failure sets compared -----
    compat_sets: dict[str, list[str]] = {}
    for tree in ("product", "product_fixed"):
        for nth in (1, 2):
            control_cwd = r5 / f"compat-control-{tree}-{nth}"
            record(
                "CMD-I14C-R5-COMPAT-CONTROL",
                "r5: control - identical failure SET on T0 and T4 proves the failures are "
                "cwd/environment-dependent, not card-caused",
                [python, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
                 "--basetemp", str(control_cwd / "pytest"), "-q",
                 str(tests / "test_source_catalog_worker_bootstrap.py"),
                 str(tests / "test_observability.py")],
                cwd=control_cwd,
                stdout_path=control_cwd / "stdout.txt",
                stderr_path=control_cwd / "stderr.txt",
                env={**base_env, "PYTHONPATH": str(attempt / "iso" / tree / "src")},
                variant=f"{tree}-{nth}",
            )
            text = (control_cwd / "stdout.txt").read_text(encoding="utf-8", errors="replace")
            compat_sets[f"{tree}-{nth}"] = sorted(
                line.split("::")[-1].strip()
                for line in text.splitlines()
                if line.startswith("FAILED ")
            )
    # The per-run SET is NOT stable: measured counts were 4, 5, 4, 5 (and 3 for the plain T4
    # run) because two restart nodes are timing-flaky.  The criterion that survives flakiness is
    # set EQUALITY OF THE UNIONS: if every node that fails on T4 also fails on the pristine tree,
    # nothing is card-specific.  harness/analyze_compat_control.py computes that from these same
    # stdout files (r5/compat-control-analysis.json).
    union = {
        tree: sorted({node for key, nodes in compat_sets.items() if key.startswith(tree)
                      for node in nodes})
        for tree in ("product", "product_fixed")
    }
    compat_control = {
        "failure_sets": compat_sets,
        "per_run_counts": {k: len(v) for k, v in compat_sets.items()},
        "union_T0": union["product"],
        "union_T4": union["product_fixed"],
        "unions_equal": union["product"] == union["product_fixed"],
        "only_on_T4": sorted(set(union["product_fixed"]) - set(union["product"])),
        "analysis": "r5/compat-control-analysis.json",
    }
    transcript.append(
        "compat-control: unions equal across T0/T4="
        f"{compat_control['unions_equal']} (n={len(union['product_fixed'])}, "
        f"per-run counts {compat_control['per_run_counts']})"
    )
    print(transcript[-1], flush=True)

    # 9b) the union/T4-only analysis runs AFTER the frequency measurement (step 14), because it
    # uses that evidence to check any node that happens to fail only on T4 in these few runs.

    # 10) guard refusal matrix ----------------------------------------------------------
    record(
        "CMD-I14C-R5-GUARD",
        "r5: binding-guard refusal matrix (product paths refused, declared scratch allowed)",
        [python, "-X", "utf8", "-B", str(harness / "run_guard_matrix.py")],
        cwd=attempt,
        stdout_path=r5 / "guard" / "matrix.stdout.txt",
        expected=0,
    )

    # 11) POSIX diff --------------------------------------------------------------------
    record(
        "CMD-I14C-R5-DIFF",
        "r5: regenerate the deliverable diff with git-native POSIX paths",
        [python, "-X", "utf8", "-B", str(harness / "make_posix_diff.py"),
         "--before", str(attempt / "iso" / "product"),
         "--after", str(attempt / "iso" / "product_fixed"),
         "--out", str(attempt / "r5-changes.diff"),
         "--scratch", str(r5 / "diff-repo")],
        cwd=attempt,
        stdout_path=r5 / "posix-diff.stdout.txt",
        expected=0,
    )

    # 12) git apply round trip ----------------------------------------------------------
    record(
        "CMD-I14C-R5-GITAPPLY",
        "r5: prove the diff applies with git apply -p1 and reproduces the fixed tree",
        [python, "-X", "utf8", "-B", str(harness / "verify_git_apply.py"),
         "--repo", str(r5 / "diff-apply-check" / "tree"),
         "--before", str(attempt / "iso" / "product"),
         "--after", str(attempt / "iso" / "product_fixed"),
         "--diff", str(attempt / "r5-changes.diff"),
         "--out", str(r5 / "git_apply_verification.json")],
        cwd=attempt,
        stdout_path=r5 / "git_apply_verification.stdout.txt",
        expected=0,
    )

    # 13) flake evidence: deep basetemp, both nodes, 3 runs per tree ---------------------
    record(
        "CMD-I14C-R5-FLAKE",
        "r5: flake evidence at the deep attempt basetemp (per-run stdout and exit code)",
        [python, "-X", "utf8", "-B", str(harness / "run_flake_evidence.py"),
         "--attempt", str(attempt), "--python", python, "--repo", str(repo)],
        cwd=attempt,
        stdout_path=r5 / "flake-evidence.stdout.txt",
        expected=0,
    )

    # 13b) the same two nodes at a SHORT %TEMP% basetemp: the control that separates "path too
    # long" from "the card broke something" (both nodes pass on both trees).
    record(
        "CMD-I14C-R5-FLAKE-SHORT",
        "r5: flake control at a short %TEMP% basetemp (cwd 74/75 chars)",
        [python, "-X", "utf8", "-B", str(harness / "run_flake_evidence.py"),
         "--attempt", str(attempt), "--python", python, "--repo", str(repo),
         "--basetemp-root", "%TEMP%/i14c-flake-short",
         "--out-root", str(r5 / "flake-evidence" / "short-basetemp")],
        cwd=attempt,
        stdout_path=r5 / "flake-evidence" / "short-basetemp.stdout.txt",
        expected=0,
    )
    # 14) flake frequency, interleaved, at a short basetemp -----------------------------
    record(
        "CMD-I14C-R5-FLAKE-FREQ",
        "r5: interleaved frequency estimate (12 runs per tree x 2 passes) of the restart node",
        [python, "-X", "utf8", "-B", str(harness / "run_flake_frequency.py"),
         "--attempt", str(attempt), "--python", python, "--repo", str(repo),
         "--node", "child_without_runtime", "--runs", "12", "--passes", "2",
         "--basetemp-root", "%TEMP%/i14c-flake-freq",
         "--out", str(r5 / "flake-evidence" / "frequency-child_without_runtime.json")],
        cwd=attempt,
        stdout_path=r5 / "flake-evidence" / "frequency-child_without_runtime.txt",
        expected=0,
    )

    # 15) compat attribution: unions + T0 evidence for any node that only failed on T4 -------
    record(
        "CMD-I14C-R5-COMPAT-ANALYSIS",
        "r5: attribute the compat failures - per-run sets, unions, and T0 evidence for any "
        "T4-only node taken from the interleaved frequency measurement above",
        [python, "-X", "utf8", "-B", str(harness / "analyze_compat_control.py"),
         "--attempt", str(attempt), "--out", str(r5 / "compat-control-analysis.json"),
         "--frequency", str(r5 / "flake-evidence" / "frequency-child_without_runtime.json")],
        cwd=attempt,
        stdout_path=r5 / "compat-control-analysis.txt",
        expected=0,
    )

    payload = {
        "script": "harness/run_r5_commands.py",
        "attempt": str(attempt),
        "python": python,
        "repo": repo,
        "network": "disabled",
        "exit_code_convention": {"0": "pass", "2": "cannot_adjudicate", "3": "negative_verdict"},
        "compat_control": compat_control,
        "commands": entries,
        "all_as_expected": all(bool(e["as_expected"]) for e in entries),
    }
    (r5 / "commands-r5-rc.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    (r5 / "commands-r5-rc.txt").write_text("\n".join(transcript) + "\n", encoding="utf-8")
    print(f"all_as_expected={payload['all_as_expected']}")
    return 0 if payload["all_as_expected"] else 3


if __name__ == "__main__":
    sys.exit(main())
