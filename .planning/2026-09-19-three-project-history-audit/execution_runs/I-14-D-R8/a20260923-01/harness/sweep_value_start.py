"""WC-1 / I-14-D-R8: BIDIRECTIONAL value-start sweep (oracle.md 5b).

For each of the 95 printable ASCII chars c: input = "Authorization: Bot\\n" + c + S39.
"closed" := the 39-char credential is absent from redact_text's output.
old = r8_base module, new = r8_fixed module (both loaded by file path).

Frozen criteria:
  old_closed \\ new_closed == []                      (nothing that closed re-opens)
  new_closed \\ old_closed == {, ; & | " '} exactly    (the six F-REV-R3-05 forms)

Run:  python -B harness/sweep_value_start.py  -> evidence/value_start_sweep.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
OBS_REL = Path("company_wiki") / "source_catalog" / "observability.py"
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
EXPECTED_NEW_OLD = [",", ";", "&", "|", '"', "'"]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclass _is_type resolves cls.__module__ here
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old = load(ATT / "iso" / "r8_base" / OBS_REL, "obs_old_vsweep")
    new = load(ATT / "iso" / "r8_fixed" / OBS_REL, "obs_new_vsweep")

    rows = []
    closed_old, closed_new = [], []
    for code in range(0x20, 0x7F):
        c = chr(code)
        text = "Authorization: Bot\n" + c + S39
        out_old = old.redact_text(text)
        out_new = new.redact_text(text)
        o_closed = S39 not in out_old
        n_closed = S39 not in out_new
        rows.append({"char": c, "code": code, "old_closed": o_closed,
                     "new_closed": n_closed, "old_out": out_old, "new_out": out_new})
        if o_closed:
            closed_old.append(c)
        if n_closed:
            closed_new.append(c)

    old_minus_new = [c for c in closed_old if c not in closed_new]
    new_minus_old = [c for c in closed_new if c not in closed_old]
    criteria = {
        "old_minus_new_empty": old_minus_new == [],
        # SET comparison -- oracle.md 5b freezes the six forms as a set
        "new_minus_old_is_exactly_the_six_forms":
            set(new_minus_old) == set(EXPECTED_NEW_OLD),
        "new_closes_all_95_printable": len(closed_new) == 95,
    }
    report = {
        "criterion": "REM-79 bidirectional difference at the after-break value-start "
                     "position, frozen domain oracle.md 5b (95 printable ASCII)",
        "domain_size": 95,
        "closed_old_count": len(closed_old),
        "closed_new_count": len(closed_new),
        "old_minus_new": old_minus_new,
        "new_minus_old": new_minus_old,
        "still_open_after_fix": [r["char"] for r in rows if not r["new_closed"]],
        "criteria": criteria,
        "verdict": "pass" if all(criteria.values()) else "FAIL",
        "rows": rows,
    }
    out = ATT / "evidence" / "value_start_sweep.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("domain_size", "closed_old_count", "closed_new_count",
                       "old_minus_new", "new_minus_old", "still_open_after_fix",
                       "criteria", "verdict")}, indent=2))
    return 0 if report["verdict"] == "pass" else 3


if __name__ == "__main__":
    sys.exit(main())
