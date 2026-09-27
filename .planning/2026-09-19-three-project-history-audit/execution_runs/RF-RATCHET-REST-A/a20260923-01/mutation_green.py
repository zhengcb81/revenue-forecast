"""RF-RATCHET-REST-A: per-row GREEN + mutation non-vacuity (step 7 evidence).

Runs the ratchet test's OWN code (copied verbatim, only sibling-owned FROZEN
rows re-pinned in a SCRATCH copy of the table — my 3 rows' caps are asserted
byte-identical to the shipped frozen table; no table edit is ever shipped).

Cases (each in its own scratch root with a full copy of the iso scripts/ tree):
  green        : iso scripts as-is (my 3 refactored) -> BOTH ratchet tests PASS
  mut_calc     : overwrite scratch forecast/calc.py with the production original
                 -> frozen test's FIRST failure must name forecast/calc.py
  mut_template : ... generate_input_template.py -> failure must name that file
  mut_targets  : ... research/targets.py -> failure must name that file
Plus, for every mutated file: the two independent CC implementations must both
flip over the frozen cap (disagreement = abort).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ATT = Path(sys.argv[1]).resolve()
ISO = Path(sys.argv[2]).resolve()
RF = Path(sys.argv[3]).resolve()
OUT = ATT / "evidence"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ATT))
from scan_ratchet import load_ratchet, twin_max_complexity  # noqa: E402

mod, _ = load_ratchet(RF)  # real, unmodified ratchet module (numbers + semantics)

MY_ROWS = {
    "forecast/calc.py": 21,
    "generate_input_template.py": 9,
    "research/targets.py": 88,
}
# sibling-owned failing rows, in table order; pin targets = their ACTUAL current
# values (scratch only — raises THEIR row, never mine)
SIBLING_PINS = {
    "analysis/confidence.py": 32,
    "model_registry.py": 28,
    "revenue_core.py": 23,
    "revenue_publication.py": 16,
}
PRODUCTION = {
    "forecast/calc.py": RF / "scripts" / "forecast" / "calc.py",
    "generate_input_template.py": RF / "scripts" / "generate_input_template.py",
    "research/targets.py": RF / "scripts" / "research" / "targets.py",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def make_pinned_table(pins: dict[str, int], new_file_max: int) -> str:
    text = (RF / "tools" / "tests" / "test_complexity_ratchet.py").read_text(encoding="utf-8")
    # pins apply ONLY to sibling rows
    for rel, val in pins.items():
        m = re.search(rf'"{re.escape(rel)}": (\d+),', text)
        assert m, f"row missing from table: {rel}"
        assert rel not in MY_ROWS, "NEVER pin my own rows"
        text = text[: m.start(1)] + str(val) + text[m.end(1):]
    text = re.sub(r"NEW_FILE_MAX = \d+", f"NEW_FILE_MAX = {new_file_max}", text, count=1)
    # hard guarantee: my rows untouched in the scratch table
    for rel, cap in MY_ROWS.items():
        assert f'"{rel}": {cap},' in text, f"my cap changed in scratch table: {rel}"
    return text


def build_case(name: str, pins: dict[str, int], new_file_max: int,
               mutate_rel: str | None) -> Path:
    root = ATT / "scratch" / name
    if root.exists():
        shutil.rmtree(root)
    (root / "tools" / "tests").mkdir(parents=True)
    (root / "tools" / "tests" / "test_complexity_ratchet.py").write_text(
        make_pinned_table(pins, new_file_max), encoding="utf-8")
    shutil.copytree(ISO / "scripts", root / "scripts")
    if mutate_rel:
        shutil.copyfile(PRODUCTION[mutate_rel], root / "scripts" / mutate_rel)
    return root


def run_ratchet(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-B", "tools/tests/test_complexity_ratchet.py", "-v"],
        cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


report: dict[str, dict] = {}

# ---- case 1: GREEN (my 3 rows, real test code, sibling rows pinned) --------
pins_all = dict(SIBLING_PINS)
green_root = build_case("green", pins_all, 30, None)
rc, out = run_ratchet(green_root)
(OUT / "green_unittest.txt").write_text(out, encoding="utf-8")
report["green"] = {"rc": rc,
                   "both_tests_pass": rc == 0 and "OK" in out,
                   "table_pins_only_sibling_rows": sorted(pins_all),
                   "my_caps_in_scratch": {r: c for r, c in MY_ROWS.items()}}
assert rc == 0, "GREEN case must pass:\n" + out[-3000:]

# ---- case 2: full-row scan against the REAL table in the iso copy ---------
# (uses the iso's own unmodified test file: honest full-row readout)
proc = subprocess.run(
    [sys.executable, "-B", str(ATT / "scan_ratchet.py"), str(ISO),
     "--json", str(OUT / "scan_green_iso.json")],
    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
)
(OUT / "scan_green_iso.txt").write_text(proc.stdout + proc.stderr, encoding="utf-8")
scan = json.loads((OUT / "scan_green_iso.json").read_text(encoding="utf-8"))
my_fail = [f for f in scan["failures"] if f["rel"] in MY_ROWS]
assert not my_fail, f"my rows must not fail in iso scan: {my_fail}"
report["scan_green_iso"] = {
    "ratchet_sha256": scan["ratchet_sha256"],
    "agreement_checked": scan["agreement_checked"],
    "my_rows_failing": my_fail,
    "remaining_failing_rows": [f["rel"] for f in scan["failures"]],
}

# ---- cases 3-5: per-file mutation (re-inflate to production original) -----
for rel, cap in MY_ROWS.items():
    # every sibling-failing row that sorts BEFORE my row must be pinned so the
    # unittest abort reaches my row; rows after mine don't matter (abort)
    earlier_pins = {r: v for r, v in pins_all.items() if r < rel}
    case = "mut_" + rel.replace("/", "_").replace(".py", "")
    root = build_case(case, earlier_pins, 30, mutate_rel=rel)

    # own-measurement flip (both implementations must agree AND exceed cap)
    text = (root / "scripts" / rel).read_text(encoding="utf-8")
    theirs = mod._max_complexity(text)
    mine = twin_max_complexity(text)
    assert theirs == mine, f"impl disagreement on mutation: {theirs} vs {mine}"
    assert theirs > cap, f"mutation did not flip over cap: {theirs} <= {cap}"

    rc, out = run_ratchet(root)
    (OUT / f"mutation_{rel.replace('/', '_')}.txt").write_text(out, encoding="utf-8")
    expect = f"{rel} max {theirs} > {cap}"
    # the assertion line of the FIRST (and mine) failing row must name my file
    err_lines = [ln for ln in out.splitlines() if "AssertionError" in ln]
    first = err_lines[0] if err_lines else ""
    assert rc != 0, f"mutation must fail the test: {out[-2000:]}"
    assert expect in out, f"expected failure message {expect!r} not in output:\n{out[-3000:]}"
    assert rel in first, f"first AssertionError does not name my file: {first!r}"
    # ordering proof: no other frozen row failed before mine (only my row's
    # AssertionError appears for the frozen gate)
    assert len(err_lines) == 1 or all(rel in ln or "stays_simple" not in ln
                                      for ln in err_lines), err_lines
    report[f"mutation:{rel}"] = {
        "inflated_cc_both_impls": [theirs, mine],
        "frozen_cap": cap,
        "test_rc": rc,
        "first_failure": first.strip(),
        "expected_message_present": expect,
        "earlier_rows_pinned_scratch_only": sorted(earlier_pins),
    }

(OUT / "mutation_green.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
print("ALL MUTATION/GREEN ASSERTIONS PASSED")
