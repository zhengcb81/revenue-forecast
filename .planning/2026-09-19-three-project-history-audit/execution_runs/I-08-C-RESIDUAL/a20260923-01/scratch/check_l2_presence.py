"""I08CR-c3 — L2/F2 check E-L2.1: presence of the R13-equivalent node and of M6 in
the mutation table (B1 SRC oracle r6 region). Read-only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]
B1 = PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01"
B1P = PLAN / "execution_runs" / "B1-PREREQ" / "a20260922-01"

NODE = B1P / "test_r13_equiv_rem41.py"
R13_REVIEWER = B1 / "reviewer" / "test_r13_reviewer_node.py"
ORACLE = B1 / "oracle.md"

EXPECT_NODES = [
    "def test_rem41_a_present_record_is_verified_even_when_label_is_unattested",
    "def test_rem41b_positive_control_valid_record_unattested_is_accepted",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out = {}
    text = NODE.read_text(encoding="utf-8")
    out["r13_equivalent_node_file"] = {
        "path": str(NODE),
        "sha256": sha(NODE),
        "bytes": NODE.stat().st_size,
        "nodes": {n: (n in text) for n in EXPECT_NODES},
        "imports_fixtures_from_frozen_module": "from test_b1_rem import" in text,
    }
    out["reviewer_original_r13"] = {
        "path": str(R13_REVIEWER),
        "sha256": sha(R13_REVIEWER),
        "present": R13_REVIEWER.exists(),
    }

    data = ORACLE.read_bytes()
    region_r6_r7 = data[43299:]
    hits = []
    start = 0
    while True:
        i = region_r6_r7.find(b"M6", start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1
    out["m6_in_oracle_r6_plus_region"] = {
        "byte_offset_of_r6_marker": 43299,
        "m6_occurrences_in_r6_r7_region": len(hits),
        "first_offsets_relative": hits[:10],
    }
    # context lines around the first hit for line-audit
    if hits:
        seg = region_r6_r7[max(0, hits[0] - 400) : hits[0] + 400]
        out["m6_first_hit_context"] = seg.decode("utf-8", "replace")

    ok = (
        all(out["r13_equivalent_node_file"]["nodes"].values())
        and out["r13_equivalent_node_file"]["imports_fixtures_from_frozen_module"]
        and out["m6_in_oracle_r6_plus_region"]["m6_occurrences_in_r6_r7_region"] > 0
    )
    out["all_ok"] = ok
    (EVID / "E_L2_presence.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("L2_E-L2.1_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
