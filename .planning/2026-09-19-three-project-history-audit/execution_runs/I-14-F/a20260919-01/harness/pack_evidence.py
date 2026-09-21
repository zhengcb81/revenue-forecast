"""I-14-F: build after/evidence_index.json + after/commands.json + changes.diff.

Run with the iso venv python. Reads every summary-placement.json inside the attempt
(including after/external-summaries) plus the unit runs, classifies each row, and writes
the adjudication table. Also emits the two-file changes.diff for the added tree files.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
NODE_SHORT = {
    "child_without_runtime": "child",
    "logon_wrapper_quoted": "logon",
}


def classify(text: str) -> str:
    if "WinError 206" in text:
        return "WinError206"
    if "Errno 2" in text and "worker_launcher_events" in text:
        return "FileNotFound-launcher-events"
    if "TimeoutExpired" in text:
        return "timeout15s-band"
    if "assert 1 == 0" in text:
        return "launcher-rc1-quiet"
    if "== 2" in text and "assert" in text:
        return "restart-band"
    if "1 passed" in text:
        return "pass"
    if "ModuleNotFoundError" in text:
        return "ModuleNotFound"
    return "other"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    rows = []
    summaries = sorted(ATT.rglob("summary-placement.json")) + sorted(
        (ATT / "after" / "external-summaries").glob("*.json"))
    for summary in summaries:
        rel = summary.relative_to(ATT)
        data = json.loads(summary.read_text(encoding="utf-8"))
        moved_root = None
        if str(rel) == "after\\falsified-normal-r1\\summary-placement.json":
            moved_root = ATT / "after" / "falsified-normal-r1"
        for r in data["results"]:
            run_dir = Path(r["cwd"])
            if moved_root is not None:
                run_dir = moved_root / run_dir.name
            stdout_path = run_dir / "stdout.txt"
            text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
            dec = r.get("decision") or {}
            rows.append({
                "summary": str(rel),
                "node": NODE_SHORT.get(r["node"], r["node"]),
                "run": r["run"],
                "cwd_len": r["cwd_len"],
                "basetemp_len": r["basetemp_len"],
                "returncode": r["returncode"],
                "verdict": r["verdict"],
                "guard_ok": r["guard_ok"],
                "relocated": dec.get("relocated"),
                "decision_reason": dec.get("reason"),
                "cleanup": bool(dec.get("cleanup") and dec["cleanup"].get("removed")),
                "signature": classify(text),
            })
    unit_runs = []
    for name in ("after\\unit-P0-run1", "after\\unit-P0-run3", "after\\unit-P0-run4"):
        p = ATT / name / "stdout.txt"
        if p.exists():
            lines = [l for l in p.read_text(encoding="utf-8", errors="replace").splitlines()
                     if " passed" in l or " failed" in l]
            unit_runs.append({"run": name, "result": lines[-1] if lines else "no-summary-line"})

    index = {
        "placement_runs": rows,
        "unit_runs": unit_runs,
        "notes": [
            "signatures: WinError206 / FileNotFound-launcher-events = the frozen deep-path family (adjudicating);"
            " timeout15s-band / restart-band / launcher-rc1-quiet = the I-14-E load-dependent restart band (non-adjudicating, oracle §6)",
            "external load confound: concurrent pytest campaigns (other sessions) were observed on this machine;"
            " band frequency in this attempt (~50% for child_without_runtime) is far above the I-14-E 25% band and correlates with wall-clock time, not placement",
        ],
    }
    (ATT / "after" / "evidence_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # changes.diff: the two files ADDED to the isolated tree (all-additions diff)
    added = [
        ATT / "iso" / "tree" / "conftest.py",
        ATT / "iso" / "tree" / "tests" / "contract" / "test_short_basetemp_convention.py",
    ]
    diffs = []
    for f in added:
        text = f.read_text(encoding="utf-8").splitlines(keepends=True)
        rel = f.relative_to(ATT / "iso" / "tree").as_posix()
        diffs.append("".join(difflib.unified_diff(
            [], text, fromfile="/dev/null", tofile=f"a/{rel}")))
    (ATT / "changes.diff").write_text("".join(diffs), encoding="utf-8")

    commands = {
        "card": "I-14-F",
        "attempt": "a20260919-01",
        "rc_legend": {"0": "pass", "1": "test/harness failure", "2": "no verdict/negative accepted", "3": "negative not rejected", "97": "driver guard mismatch"},
        "commands": rows,
        "unit_runs": unit_runs,
    }
    (ATT / "commands.json").write_text(
        json.dumps(commands, indent=2, ensure_ascii=False), encoding="utf-8")

    hashes = {}
    for f in added + [
        ATT / "harness" / "run_placement.py",
        ATT / "changes.diff",
        ATT / "after" / "evidence_index.json",
    ]:
        hashes[str(f.relative_to(ATT))] = sha256(f)
    (ATT / "after" / "final_hashes.json").write_text(
        json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"indexed {len(rows)} runs, {len(unit_runs)} unit runs")
    for row in rows:
        print(f"{row['summary'][:58]:60s} {row['node']:6s} rc={row['returncode']} "
              f"cwd={row['cwd_len']:3d} rel={str(row['relocated']):5s} {row['signature']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
