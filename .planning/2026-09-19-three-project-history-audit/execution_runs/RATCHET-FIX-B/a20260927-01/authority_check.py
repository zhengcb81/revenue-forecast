"""The AUTHORITATIVE metric, exactly as the dispatch specifies.

importlib-loads tests/contract/test_fc1204_complexity_ratchet.py and reports
_max_complexity() + FROZEN_MAX for each B-group file, with the pass verdict.
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

TARGETS = {"producer_events.py": 1, "identity_cli.py": 6,
           "artifact_read_model.py": 10}
SRC = REPO / "src" / "company_wiki" / "source_catalog"
allok = True
for name, target in TARGETS.items():
    actual = m._max_complexity((SRC / name).read_text(encoding="utf-8"))
    frozen = m.FROZEN_MAX.get(name)
    ok = actual <= target
    allok = allok and ok
    print(f"{name:26s} _max_complexity={actual}  target<={target}  "
          f"frozen={frozen}  -> {'PASS' if ok else 'FAIL'}")
print("AUTHORITY CHECK:", "ALL PASS" if allok else "FAIL")
