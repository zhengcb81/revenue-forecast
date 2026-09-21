"""I-14-F placement runner.

Adapted from I-14-C a20260919-01 harness/run_flake_evidence.py (r5, accepted evidence
driver): same nodes, same stripped env, same per-run capture layout. Differences:
explicit ``--root`` for run dirs (so cwd_len is a controlled, asserted variable),
``--require-cwd-len`` guard, per-run ``basetemp_len``/decision-line capture, and
``--evidence-copy`` to bring %TEMP%-rooted captures back inside the attempt.

Per run: run_dir = <root>/<tag>-<run>; argv =
  <python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <run_dir>\\pytest -q
  <tree>/tests/contract/test_source_catalog_worker_bootstrap.py::<node>
cwd = run_dir. stdout/returncode land inside run_dir; a summary.json lands at --out.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "logon_wrapper_quoted": "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths",
}
SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
DECISION_RE = re.compile(r"CW-BASETEMP-DECISION (\{.*\})")


def _parse_cwd_len_guard(spec: str) -> dict[str, int]:
    guard: dict[str, int] = {}
    for part in spec.split(","):
        name, _, value = part.strip().partition("=")
        if name not in NODES or not value.isdigit():
            raise SystemExit(f"bad --require-cwd-len entry: {part!r}")
        guard[name] = int(value)
    return guard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--tree", required=True, help="isolated product tree root")
    parser.add_argument("--root", required=True, help="parent dir for run dirs")
    parser.add_argument("--tag-prefix", default="P0")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--nodes", default="all", help="comma list or 'all'")
    parser.add_argument("--require-cwd-len", default="", help="e.g. child_without_runtime=167,logon_wrapper_quoted=166")
    parser.add_argument("--out", default="", help="summary.json path (default <root>/summary-placement.json)")
    parser.add_argument("--evidence-copy", default="", help="dir to copy per-run captures into")
    parser.add_argument("--env", action="append", default=[], help="KEY=VALUE added to the run env (repeatable)")
    parser.add_argument("--reuse-ok", action="store_true", help="clear an existing run dir instead of failing")
    args = parser.parse_args(argv)

    tree = Path(args.tree).resolve()
    root = Path(args.root)
    guard = _parse_cwd_len_guard(args.require_cwd_len) if args.require_cwd_len else {}
    node_names = list(NODES) if args.nodes == "all" else args.nodes.split(",")
    for name in node_names:
        if name not in NODES:
            raise SystemExit(f"unknown node: {name}")

    if root.exists() and any(root.iterdir()) and not args.reuse_ok:
        raise SystemExit(f"refusing non-empty run root (fresh-dir discipline): {root}")
    root.mkdir(parents=True, exist_ok=True)
    evidence_copy = Path(args.evidence_copy).resolve() if args.evidence_copy else None
    if evidence_copy is not None:
        evidence_copy.mkdir(parents=True, exist_ok=True)

    env = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "PYTHONPATH": str(tree / "src"),
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
    }
    for item in args.env:
        key, _, value = item.partition("=")
        env[key] = value

    suite_path = tree / SUITE
    summary: dict = {
        "python": args.python,
        "tree": str(tree),
        "root": str(root),
        "suite": str(suite_path),
        "extra_env": dict(item.partition("=")[::2] for item in args.env),
        "guard": guard,
        "results": [],
    }
    for node_id in node_names:
        node_name = NODES[node_id]
        for run in range(1, args.runs + 1):
            tag = f"{args.tag_prefix}-{node_id}-{run}"
            run_dir = root / tag
            if run_dir.exists():
                if not args.reuse_ok:
                    raise SystemExit(f"refusing existing run dir: {run_dir}")
                shutil.rmtree(run_dir)
            run_dir.mkdir(parents=True)
            basetemp = run_dir / "pytest"
            decision_file = run_dir / "basetemp_decision.json"
            run_env = dict(env)
            run_env["CW_BASETEMP_DECISION_FILE"] = str(decision_file)
            proc = subprocess.run(
                [args.python, "-X", "utf8", "-B", "-m", "pytest",
                 "-p", "no:cacheprovider", "--basetemp", str(basetemp),
                 "-q", f"{suite_path}::{node_name}"],
                cwd=str(run_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=run_env,
            )
            text = proc.stdout.decode("utf-8", "replace")
            (run_dir / "stdout.txt").write_text(text, encoding="utf-8")
            (run_dir / "returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
            decision = None
            match = DECISION_RE.search(text)
            if match:
                try:
                    decision = json.loads(match.group(1))
                except json.JSONDecodeError:
                    decision = {"unparsable": match.group(1)}
            if decision_file.exists():
                events = []
                for line in decision_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                decisions = [e for e in events if e.get("event") == "decision"]
                cleanups = [e for e in events if e.get("event") == "cleanup"]
                decision = decisions[-1] if decisions else decision
                if cleanups:
                    decision = dict(decision or {})
                    decision["cleanup"] = cleanups[-1]
                    decision["cleanup_dir_gone"] = not cleanups[-1].get("dir") or \
                        not Path(cleanups[-1]["dir"]).exists()
            passed = "1 passed" in text
            failed = "1 failed" in text or "no tests ran" in text
            verdict = "passed" if passed else "failed" if failed else "unknown"
            row = {
                "node": node_id,
                "run": run,
                "argv": [args.python, "-X", "utf8", "-B", "-m", "pytest",
                         "-p", "no:cacheprovider", "--basetemp", str(basetemp),
                         "-q", f"{suite_path}::{node_name}"],
                "cwd": str(run_dir),
                "cwd_len": len(str(run_dir)),
                "basetemp": str(basetemp),
                "basetemp_len": len(str(basetemp)),
                "returncode": proc.returncode,
                "verdict": verdict,
                "guard_ok": (guard.get(node_id) in (None, len(str(run_dir)))),
                "decision": decision,
                "decision_file": str(decision_file) if decision_file.exists() else None,
                "tail": text.strip().splitlines()[-1] if text.strip() else "",
            }
            summary["results"].append(row)
            print(f"{node_id} run{run} rc={proc.returncode} {verdict} "
                  f"cwd_len={row['cwd_len']} basetemp_len={row['basetemp_len']} "
                  f"relocated={None if decision is None else decision.get('relocated')} "
                  f"guard_ok={row['guard_ok']}", flush=True)
            if evidence_copy is not None:
                shutil.copyfile(run_dir / "stdout.txt", evidence_copy / f"{tag}-stdout.txt")
                shutil.copyfile(run_dir / "returncode.txt", evidence_copy / f"{tag}-returncode.txt")

    out_path = Path(args.out) if args.out else root / "summary-placement.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("summary:", out_path)
    guard_failures = [r for r in summary["results"] if not r["guard_ok"]]
    if guard_failures:
        print(f"GUARD FAILURES: {len(guard_failures)}", file=sys.stderr)
        return 97
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
