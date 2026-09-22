"""I-14-F-R1: build after/evidence_index.json + commands.json + changes.diff + final_hashes.json.

Run with the iso venv python AFTER all phases. Reads every summary-placement.json inside the
attempt plus the unit runs, classifies each row, and writes the adjudication table.

Differs from I-14-F's packer where the reviewer found defects:
  * commands.json entries carry REAL argv + cwd per run (I-14-F F-6 / CF-I14F-7 corrected for
    this attempt; I-14-F's own commands.json stays sealed and gets an erratum instead).
  * unit runs are discovered generically (unit-run*/stdout.txt), not a hardcoded list.
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
    if "assert 3 == 2" in text:
        return "restart-band"
    if "assert 2 == 1" in text or "assert 1 == 2" in text:
        return "restart-band"
    return "other"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_of(rel: str, data: dict) -> str:
    if data.get("phase"):
        return data["phase"]
    r = rel.replace("\\", "/")
    if r.startswith("before/"):
        return "RED"
    if r.startswith("after/deep"):  # after/deep/** and after/deep-rerun/**
        return "GREEN"
    if r.startswith("after/mut"):
        return "MUTATION"
    if r.startswith("after/sizes"):
        return "SIZES"
    return "other"


def main() -> int:
    rows = []
    for summary in sorted(ATT.rglob("summary-placement.json")):
        rel = summary.relative_to(ATT)
        data = json.loads(summary.read_text(encoding="utf-8"))
        phase = phase_of(str(rel), data)
        for r in data["results"]:
            run_dir = Path(r["cwd"])
            stdout_path = run_dir / "stdout.txt"
            text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
            dec = r.get("decision") or {}
            rows.append({
                "phase": phase,
                "summary": str(rel),
                "node": NODE_SHORT.get(r["node"], r["node"]),
                "run": r.get("run"),
                "argv": r.get("argv"),
                "cwd": r["cwd"],
                "cwd_len": r["cwd_len"],
                "basetemp": r.get("basetemp"),
                "basetemp_len": r["basetemp_len"],
                "returncode": r["returncode"],
                "verdict": r["verdict"],
                "guard_ok": r["guard_ok"],
                "relocated": dec.get("relocated"),
                "decision_reason": dec.get("reason"),
                "generation_reserve": dec.get("generation_reserve"),
                "threshold": dec.get("threshold"),
                "cleanup": bool(dec.get("cleanup") and dec["cleanup"].get("removed")),
                "signature": classify(text),
            })
    unit_runs = []
    for d in sorted((ATT / "after").glob("unit-run*")):
        p = d / "stdout.txt"
        if p.exists():
            lines = [l for l in p.read_text(encoding="utf-8", errors="replace").splitlines()
                     if " passed" in l or " failed" in l or "ERROR at setup" in l]
            unit_runs.append({"run": str(d.relative_to(ATT)),
                              "result": lines[-1] if lines else "no-summary-line"})

    index = {
        "placement_runs": rows,
        "unit_runs": unit_runs,
        "notes": [
            "criterion under test: owner §16 E-1 GENERATION_RESERVE=150 ⇒ relocate iff len(resolved_basetemp) > 60",
            "signatures: WinError206 / FileNotFound-launcher-events = the frozen deep-path family (adjudicating);"
            " timeout15s-band / restart-band / launcher-rc1-quiet = the I-14-E load-dependent restart band"
            " (non-adjudicating, oracle §9; artifact-level adjudication per CF-I14F-X1 when a disabled/RED"
            " basetemp survives)",
            "flips: basetemps 61–86 relocate under owner §16 E-1; written reason at every flip:"
            " 'owner §16 E-1 chose 150/60; this control's unrouted expectation is superseded'",
            "argv + cwd are recorded per run in commands.json (I-14-F F-6 corrected for THIS attempt)",
        ],
    }
    (ATT / "after" / "evidence_index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # changes.diff: the two tree files relative to pristine (all-additions vs red-tree)
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
        "card": "I-14-F-R1",
        "attempt": "a20260922-01",
        "rc_legend": {"0": "pass", "1": "test/harness failure", "2": "no verdict/negative accepted",
                      "3": "negative not rejected", "97": "driver geometry guard"},
        "note": "each entry carries the REAL argv and cwd of the run (fixes, for this attempt only,"
                " the pattern I-14-F's sealed commands.json lacked per F-6/CF-I14F-7)",
        "commands": rows,
        "unit_runs": unit_runs,
    }
    (ATT / "commands.json").write_text(
        json.dumps(commands, indent=2, ensure_ascii=False), encoding="utf-8")

    hashes = {}
    for f in added + [
        ATT / "harness" / "run_placement.py",
        ATT / "harness" / "check_lengths.py",
        ATT / "harness" / "measure_artifacts.py",
        ATT / "changes.diff",
        ATT / "oracle.md",
        ATT / "oracle.sha256",
        ATT / "binding.json",
        ATT / "commands.json",
        ATT / "decision.md",
        ATT / "handoff.json",
        ATT / "review.md",
        ATT / "after" / "evidence_index.json",
        ATT / "after" / "readonly-check.txt",
    ]:
        if f.exists():
            hashes[str(f.relative_to(ATT))] = sha256(f)
    (ATT / "after" / "final_hashes.json").write_text(
        json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"indexed {len(rows)} placement runs, {len(unit_runs)} unit runs")
    for row in rows:
        argv0 = (row["argv"] or ["?"])[-1]
        print(f"{row['phase']:10s} {row['node']:6s} run{row['run']} rc={row['returncode']} "
              f"cwd={row['cwd_len']:3d} bt={row['basetemp_len']:3d} rel={str(row['relocated']):5s} "
              f"guard={row['guard_ok']} {row['signature']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
