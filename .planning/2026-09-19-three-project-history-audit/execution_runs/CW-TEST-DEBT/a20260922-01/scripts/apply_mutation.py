"""CW-TEST-DEBT mutation helper — mirror-local only.

usage: python apply_mutation.py <test-file> <m1|m2>

m1  remove the seed tag line added by E1 from test_readiness_graph.py::_seed
m2  remove the evidence_payload=... argument added by E2 from _write_receipt
    in test_prompt_injection_guard.py

Both edits are anchored exactly; a missing anchor aborts with rc=2 (no silent
no-op mutation).  The CW product tree is never passed to this script.
"""
from __future__ import annotations

import sys
from pathlib import Path

SEED_TAG = '"state_domain": "review",'
PAYLOAD_ARG = "evidence_payload=_EVIDENCE_PAYLOAD,"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    path = Path(argv[1])
    kind = argv[2]
    raw = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"

    if kind == "m1":
        old = (
            '                        "policy_hash": RULESET_HASH,' + nl
            + '                        ' + SEED_TAG + nl
        )
        new = '                        "policy_hash": RULESET_HASH,' + nl
        count = raw.count(SEED_TAG)
        if count != 1:
            print(f"MUTATION ANCHOR ERROR: seed tag occurrences={count}")
            return 2
    elif kind == "m2":
        old = (
            "        source_sha256=source_sha256," + nl
            + "        policy_hash=policy_hash," + nl
            + "        " + PAYLOAD_ARG + nl
        )
        new = (
            "        source_sha256=source_sha256," + nl
            + "        policy_hash=policy_hash," + nl
        )
        # the payload arg must still be present in _write_receipt exactly once
        if raw.count(old) != 1:
            print("MUTATION ANCHOR ERROR: _write_receipt payload arg not unique")
            return 2
    else:
        print(f"unknown mutation {kind!r}")
        return 2

    if old not in raw:
        print("MUTATION ANCHOR ERROR: block not found")
        return 2
    path.write_bytes(raw.replace(old, new, 1).encode("utf-8"))
    print(f"mutated {path.name}: {kind} applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
