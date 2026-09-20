"""I-11-A: freeze the semantics of the before/after state captures.

The two captures are compared for PRODUCTION facts only (repository HEADs,
porcelain status, key-file hashes, PLAN/reviews mtime). The `attempt_inventory`
field is by construction a snapshot of the attempt's own directory at capture time,
so it is informative only for the "after" capture; the before capture is taken
after this attempt's tools already existed. Rather than compare two non-comparable
inventories, the before capture's inventory is dropped here and the reason is
recorded in the file itself.

Usage: python -X utf8 -B tools/finalize_state.py <attempt_root>
"""

from __future__ import annotations

import json
import os
import sys


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    b_path = os.path.join(ev, "state_before.json")
    a_path = os.path.join(ev, "state_after.json")
    b = json.load(open(b_path, encoding="utf-8"))
    a = json.load(open(a_path, encoding="utf-8"))

    b["attempt_inventory_removed"] = {
        "removed_count": len(b.pop("attempt_inventory", [])),
        "reason": ("the before capture was taken after this attempt's tools/ already existed, so its "
                   "directory listing is not a pre-work baseline; production facts (repos/key files/"
                   "reviews) remain the compared surface. See state_after.json for the final inventory."),
    }
    b.pop("attempt_file_count", None)
    a["attempt_inventory_scope"] = ("final inventory of this attempt's own files (iso/venv excluded); "
                                    "informational, not part of the before/after production comparison")

    with open(b_path, "w", encoding="utf-8") as fh:
        json.dump(b, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(a_path, "w", encoding="utf-8") as fh:
        json.dump(a, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    same = all(b["production_repos"][k] == a["production_repos"][k] for k in b["production_repos"])
    print("production repos identical:", same)
    print("before keys:", sorted(b))
    print("after file count:", a.get("attempt_file_count"))
    print("wrote", b_path, "and", a_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
