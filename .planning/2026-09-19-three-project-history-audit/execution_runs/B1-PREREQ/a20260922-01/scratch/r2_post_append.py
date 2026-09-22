"""Post-append verification of SRC oracle Revision r7 (record into evidence/r2).

Checks on the POST-append bytes: all six pinned prefixes, marker offsets and
single-occurrence for r2..r7, LF separator at 47538, before/after size+hash.
Also copies the append proof into evidence/r2/.

Usage: python r2_post_append.py <oracle.md> <append_proof.json> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

oracle = Path(sys.argv[1]).resolve()
proof_path = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3]).resolve()
out.mkdir(parents=True, exist_ok=True)

PREFIX_PINS = {
    27697: "81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281",
    31081: "60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4",
    35840: "231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523",
    39287: "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae",
    43298: "910ca4a8109b28afb739f4a7463dbf26e13fe85c296e115d806768bcb3bd3231",
    47538: "a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d",
}

proof = json.loads(proof_path.read_text(encoding="utf-8"))
shutil.copyfile(proof_path, out / "r2_08_append_r7_proof.json")

raw = oracle.read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731

prefixes = {
    str(n): {"expected": h, "measured": sha(raw[:n]), "match": sha(raw[:n]) == h}
    for n, h in PREFIX_PINS.items()
}
marker_counts = {
    m: len(re.findall(re.escape(m.encode()), raw))
    for m in [
        "## Revision r2", "## Revision r3", "## Revision r4",
        "## Revision r5", "## Revision r6",
        "## Revision r7 — F4/REM-43 gap restated",
    ]
}
bare_r7_count = raw.count(b"## Revision r7")

report = {
    "claim": "F-REV-B1P-01 required correction #1: SRC oracle Revision r7 appended; r1-r6 byte ranges untouched (all six pins re-match on the post-append bytes)",
    "before": {
        "bytes": proof["pre_bytes"],
        "sha256": proof["pre_sha256"],
        "freeze_pin_prefix_47538": PREFIX_PINS[47538],
        "matches_freeze_binding_post_r6_state": proof["pre_sha256"] == PREFIX_PINS[47538],
    },
    "after": {
        "bytes": len(raw),
        "sha256": sha(raw),
        "expected_from_dry_run": "57911 / 6e344a208f8fc43992d339693d74c51122b505d17c368a67f5899dbd43a222dc",
        "matches_dry_run_expectation": len(raw) == 57911
        and sha(raw) == "6e344a208f8fc43992d339693d74c51122b505d17c368a67f5899dbd43a222dc",
    },
    "revision_text": {
        "bytes": proof["revision_bytes"],
        "sha256": proof["revision_sha256"],
        "path": proof["revision_file"],
    },
    "prefix_checks_on_post_bytes": prefixes,
    "all_six_prefixes_match": all(v["match"] for v in prefixes.values()),
    "marker_offsets": {
        m: [mm.start() for mm in re.finditer(re.escape(m.encode()), raw)]
        for m in [
            "## Revision r2", "## Revision r3", "## Revision r4",
            "## Revision r5", "## Revision r6", "## Revision r7",
        ]
    },
    "marker_counts_exactly_one_each": marker_counts,
    "bare_heading_prefix_count_r7": bare_r7_count,
    "byte_at_47538_is_lf": raw[47538:47539] == b"\n",
    "marker_at_pre_plus_1": proof["append_marker_offset"] == 47539
    and raw[47539:47539 + 16].startswith(b"## Revision r7"),
    "append_proof_path": "scratch/append_oracle_r7.stdout.json",
    "freeze_chain_implication": (
        "freeze.json entry src_oracle_pre_r5 pins the full file at 47538/a8f192f1 "
        "AND prefix_bytes 39287/fadf8a5e...; final_integrity_check_v2.c_chain "
        "special-cases that entry with a prefix check, so the r7 append keeps "
        "freeze_chain_verifies passing ([0:39287] still fadf8a5e..., and the "
        "freeze-time full state 47538/a8f192f1 is preserved as the [0:47538] prefix)."
    ),
}
ok = (
    report["all_six_prefixes_match"]
    and report["after"]["matches_dry_run_expectation"]
    and report["byte_at_47538_is_lf"]
    and report["marker_at_pre_plus_1"]
    and bare_r7_count == 1
    and all(v == 1 for v in marker_counts.values())
)
report["all_checks_pass"] = ok
(out / "r2_09_post_append_verification.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps(report, indent=2, ensure_ascii=False))
sys.exit(0 if ok else 1)
