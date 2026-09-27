"""WC-6 family comparator: before == after outcomes, per test id.

  python compare_family.py <labelA> <labelB>

Exit codes: 0 = identical per-test outcome lists; 3 = any difference.
"""
from __future__ import annotations

import json
import sys

from wc6_common import EVID, write_json


def load(label: str) -> dict:
    return json.loads((EVID / f"{label}_family_outcomes.json").read_text(encoding="utf-8"))


def main() -> int:
    a, b = sys.argv[1], sys.argv[2]
    da, db = load(a), load(b)
    ma = {o["id"]: o["status"] for o in da["outcomes"]}
    mb = {o["id"]: o["status"] for o in db["outcomes"]}
    only_a = sorted(set(ma) - set(mb))
    only_b = sorted(set(mb) - set(ma))
    changed = sorted(k for k in set(ma) & set(mb) if ma[k] != mb[k])
    identical = not only_a and not only_b and not changed
    report = {
        "label_a": a, "label_b": b,
        "outcome_count_a": len(ma), "outcome_count_b": len(mb),
        "summary_a": da["summary"], "summary_b": db["summary"],
        "only_in_a": only_a, "only_in_b": only_b,
        "status_changed": [{"id": k, "a": ma[k], "b": mb[k]} for k in changed],
        "per_test_outcomes_identical": identical,
        "raw_rc_a": da["raw_rc"], "raw_rc_b": db["raw_rc"],
    }
    write_json(EVID / f"compare_family_{a}_vs_{b}.json", report)
    print(json.dumps(report, indent=1))
    return 0 if identical else 3


if __name__ == "__main__":
    sys.exit(main())
