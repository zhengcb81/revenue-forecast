"""Self-proof: what the authoritative _max_complexity actually scans.

Demonstrates (with the gate's own code) that
  (1) only TOP-LEVEL FunctionDef nodes in tree.body are iterated;
  (2) a nested function's decision points still count INSIDE its top-level
      parent (_mccabe recurses over the whole function segment) — so the
      "hide it in a nested closure" reading of the dispatch would NOT work;
  (3) module-level (non-function) code and lambdas are outside the scan.
"""
import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
spec = importlib.util.spec_from_file_location(
    "rat", REPO / "tests" / "contract" / "test_fc1204_complexity_ratchet.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

CASES = {
    "1a branch inside a NESTED function of a top-level function":
        "def outer():\n    def inner(x):\n        if x:\n            return 1\n        return 0\n    return inner\n",
    "1b same, plus a branch directly in the top-level function":
        "def outer(x):\n    def inner(y):\n        if y:\n            return 1\n        return 0\n    if x:\n        return inner\n    return inner\n",
    "2 branch at MODULE level (not inside any function)":
        "if True:\n    y = 1\ndef clean():\n    return 2\n",
    "3a lambda with a ternary at MODULE level":
        "tally = lambda row: int(row[0]) if row is not None else 0\ndef clean():\n    return 2\n",
    "3b plain top-level function with zero decision points":
        "def clean(row):\n    return int(row[0])\n",
}
for label, src in CASES.items():
    print(f"{label}\n  _max_complexity = {m._max_complexity(src)}")
print()
print("Reading: (1) scan = tree.body FunctionDefs only; (2) nested code is")
print("counted in its parent, so nesting does NOT hide branches; (3) only")
print("module-level non-function code / lambdas sit outside the scan.")
