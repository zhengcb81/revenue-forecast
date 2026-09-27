"""T1-F2-FIX semantic mutation arms (non-vacuity proof for the F-2 ruling).

Oracle.md sec 6 freezes the *revert* arms (MUT-F1 / MUT-F2 / MUT-P4, run by
`verify_t1_f2_fix.py mutation`).  This script adds the two arms the dispatch
card asks for on top of them, both against a SCRATCH copy of the fixed SUT
(the SUT itself is never edited):

  MUT-SEM-1  fail-closed -> silent: read an unreadable claim carrier as the
             weakest status instead of the strongest one.  The frozen GREEN
             criteria (S1/S2/S3 must refuse) must turn RED, i.e. the
             fail-closed half of the ruling is load-bearing, not decorative.
  MUT-SEM-2  over-rejection: treat a MISSING status key as if it were a
             malformed carrier.  The frozen STABLE criteria (S7a/S7c must
             accept, S8 must refuse WITHOUT the claim-exceeds code) must turn
             RED while S10 (a claim that really does carry a status) is
             untouched -- that asymmetry is what proves the real fix does NOT
             over-reject the missing-key branch.

  NC-MISSING the missing-key / normal-carrier rows are byte-identical between
             the before phase and the after phase (the negative control the
             card requires: "缺键分支行为字节不变").

Raw CLI output for every probe lands in evidence/after/mutation_semantic/raw/.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent
sys.path.insert(0, str(SCRIPT.parent))

import verify_t1_f2_fix as V          # noqa: E402  (attempt-local module)

PY = sys.executable
OUT = ATTEMPT / "evidence" / "after" / "mutation_semantic"
RAW = OUT / "raw"
SCRATCH = OUT / "scratch"

# frozen criteria, quoted from oracle.md sec 2 (GREEN column) ---------------
CRITERIA = {
    "S1": ("reject_claim", ["R-CLAIM-EXCEEDS"]),
    "S2": ("reject_claim", ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE",
                            "R-FUTURE-CLOCK", "R-SAME-INSTANT"]),
    "S3": ("reject_claim", ["R-CLAIM-EXCEEDS"]),
    "S7a": ("accept_claim", []),
    "S7c": ("accept_claim", []),
    "S8": ("reject_claim", ["R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK",
                            "R-SAME-INSTANT"]),
    "S10": ("accept_claim", []),
}

# rows whose behaviour MUST NOT move (absent key / normal carrier) ----------
MISSING_KEY_ROWS = ("S7a", "S7b", "S7c", "S8", "S9", "S10", "K7")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _probe(sut: Path, sid: str, tag: str) -> dict:
    row = V.invoke_cli(sut, [V.build_case(sid)], RAW, tag)
    return {"rc": row["rc"], "report_written": row["report_written"],
            "cases_decided": row["cases_decided"], "verdict": row["verdict"],
            "refusals": row["refusals"]}


def _holds(sid: str, row: dict) -> bool:
    want_v, want_r = CRITERIA[sid]
    return row["verdict"] == want_v and row["refusals"] == want_r


def _arm(name: str, old: str, new: str, sids: tuple, src: str) -> tuple:
    if src.count(old) != 1:
        raise SystemExit(f"{name}: anchor found {src.count(old)} times, want 1")
    mutant_src = src.replace(old, new)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    path = SCRATCH / f"{name}.py"
    path.write_text(mutant_src, encoding="utf-8")
    rows = {}
    for sid in sids:
        rows[sid] = _probe(path, sid, f"{name}_{sid}")
    return path, rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fixed_path = ATTEMPT / "worktree" / "i14b" / "iso" / "natural_window.py"
    fixed_src = fixed_path.read_text(encoding="utf-8")
    checks: list[dict] = []

    def check(name: str, holds: bool, detail: str = "") -> None:
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    # ---- control: the FIXED SUT satisfies every criterion ----------------
    fixed_rows = {sid: _probe(fixed_path, sid, f"FIXED_{sid}")
                  for sid in CRITERIA}
    for sid in CRITERIA:
        check(f"control: fixed SUT holds frozen criterion for {sid} "
              f"({CRITERIA[sid][0]} {CRITERIA[sid][1]})",
              _holds(sid, fixed_rows[sid]), json.dumps(fixed_rows[sid]))

    # ---- MUT-SEM-1: fail-closed reverted to silent ------------------------
    silent_old = ('        claim = {"status": "complete"}  # T1-F2-FIX F-2 '
                  'fail-closed read surrogate')
    silent_new = ('        claim = {"status": "pending"}  # MUT-SEM-1: '
                  'unreadable carrier read as the weakest claim (silent)')
    p1, r1 = _arm("MUT-SEM-1-fail-closed-to-silent", silent_old, silent_new,
                  ("S1", "S2", "S3"), fixed_src)
    for sid in ("S1", "S2", "S3"):
        check(f"MUT-SEM-1: {sid} frozen GREEN criterion turns RED on the "
              f"mutant (fail-closed half is load-bearing)",
              not _holds(sid, r1[sid]),
              json.dumps({"mutant": r1[sid], "frozen": CRITERIA[sid]}))

    # ---- MUT-SEM-2: missing key also treated as malformed -----------------
    over_old = ('    if not isinstance(claim, dict):\n'
                '        claim = {"status": "complete"}  # T1-F2-FIX F-2 '
                'fail-closed read surrogate')
    over_new = ('    if not isinstance(claim, dict) or "status" not in claim:\n'
                '        claim = {"status": "complete"}  # T1-F2-FIX F-2 '
                'fail-closed read surrogate')
    p2, r2 = _arm("MUT-SEM-2-missing-key-also-rejected", over_old, over_new,
                  ("S7a", "S7c", "S8", "S10"), fixed_src)
    for sid in ("S7a", "S7c", "S8"):
        check(f"MUT-SEM-2: {sid} frozen STABLE criterion turns RED on the "
              f"mutant (over-rejection of the ABSENT key is detected)",
              not _holds(sid, r2[sid]),
              json.dumps({"mutant": r2[sid], "frozen": CRITERIA[sid]}))
    check("MUT-SEM-2: S10 (status key really present) is NOT touched by the "
          "mutant -- the red is specific to the missing-key branch",
          _holds("S10", r2["S10"]), json.dumps(r2["S10"]))

    # ---- NC-MISSING: missing-key branch byte-identical before == after ----
    before = json.loads((ATTEMPT / "evidence" / "before" / "probes" /
                         "family_results.json").read_text(encoding="utf-8"))
    after = json.loads((ATTEMPT / "evidence" / "after" / "probes" /
                        "family_results.json").read_text(encoding="utf-8"))
    fields = ("rc", "report_written", "cases_decided", "verdict", "refusals",
              "verdicts", "computed")
    rows_cmp = {}
    for sid in MISSING_KEY_ROWS:
        b = {k: before["shapes"][sid].get(k) for k in fields}
        a = {k: after["shapes"][sid].get(k) for k in fields}
        rows_cmp[sid] = {"equal": b == a, "before": b, "after": a}
        check(f"NC-MISSING: row {sid} (absent key / normal carrier) "
              f"byte-identical before == after", b == a,
              json.dumps({"before": b, "after": a}, ensure_ascii=False)[:400])

    doc = {
        "card": "T1-F2-FIX",
        "attempt_id": "a20260923-01",
        "note": "extra arms on top of oracle sec 6 MUT-F1/F2/P4; the fixed SUT "
                "is never edited, only SCRATCH copies",
        "fixed_sut_sha256": sha256_file(fixed_path),
        "arms": {
            "MUT-SEM-1-fail-closed-to-silent": {
                "mutant_sha256": sha256_file(p1), "rows": r1},
            "MUT-SEM-2-missing-key-also-rejected": {
                "mutant_sha256": sha256_file(p2), "rows": r2},
        },
        "fixed_control_rows": fixed_rows,
        "missing_key_rows_equal": {k: v["equal"] for k, v in rows_cmp.items()},
        "checks": checks,
        "failed_checks": [c["name"] for c in checks if not c["holds"]],
        "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL",
    }
    (OUT / "results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    print(json.dumps({"semantic_arms": doc["overall"],
                      "checks": len(checks),
                      "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
