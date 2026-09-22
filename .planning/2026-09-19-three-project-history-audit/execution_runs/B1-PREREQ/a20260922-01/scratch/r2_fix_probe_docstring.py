"""F-REV-B1P-03: correct the probe module docstring (variant (b) wording) and
record the byte history. Record-only: the ONLY byte change is inside the module
docstring; every byte from the first code statement onward must be identical.

- preserves a byte-exact copy of the frozen (executed) probe under evidence/r2/
- asserts the pre-edit sha256 == the freeze.json pin 5c9f4508...
- replaces exactly one docstring line; proves prefix/suffix identity
- writes evidence/r2/r2_10_probe_docstring_fix.json

Usage: python r2_fix_probe_docstring.py <probe.py> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

PROBE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

PRE_BYTES = 10365
PRE_SHA = "5c9f4508198963d225eb4331734629210105dbcbd985decb4409d7524ef70bb7"  # freeze.json my_probe_e21
OLD = b"      (b) full self-consistent recompute of every self-hash chain."
NEW = b"      (b) the original value restored \xe2\x80\x94 a control, NOT a recompute (oracle \xc2\xa73.3)."
FROZEN_COPY = OUT / "probe_e21_binding.py.frozen_pre_r2_5c9f4508.py"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    before = PROBE.read_bytes()
    assert len(before) == PRE_BYTES, f"pre bytes {len(before)} != {PRE_BYTES}"
    assert sha(before) == PRE_SHA, f"pre sha {sha(before)} != {PRE_SHA}"
    assert before.count(OLD) == 1, f"old docstring line count {before.count(OLD)} != 1"
    assert NEW not in before, "new line already present"

    shutil.copyfile(PROBE, FROZEN_COPY)
    assert FROZEN_COPY.read_bytes() == before

    after = before.replace(OLD, NEW, 1)
    PROBE.write_bytes(after)

    # byte-identity outside the docstring: everything from the first code
    # statement onward is shared verbatim
    anchor = b'from __future__ import annotations'
    i_b, i_a = before.index(anchor), after.index(anchor)
    suffix_b, suffix_a = before[i_b:], after[i_a:]
    idx = before.index(OLD)
    # longest common prefix (untouched head, ends inside the shared "      (b) " stem)
    n = 0
    while n < min(len(before), len(after)) and before[n] == after[n]:
        n += 1

    report = {
        "finding": "F-REV-B1P-03 (LOW): module docstring line 19 misdescribed variant (b)",
        "file": str(PROBE),
        "byte_history": {
            "frozen_executed_state": {
                "bytes": len(before),
                "sha256": sha(before),
                "matches_freeze_json_my_probe_e21_pin": sha(before) == PRE_SHA,
                "preserved_copy": str(FROZEN_COPY),
                "preserved_copy_sha256": sha(FROZEN_COPY.read_bytes()),
                "role": "the bytes that were frozen pre-run and that produced evidence/probe_e21.stdout.txt",
            },
            "r2_state": {
                "bytes": len(after),
                "sha256": sha(after),
                "delta_bytes": len(after) - len(before),
            },
        },
        "exact_change": {
            "old_line": OLD.decode("utf-8"),
            "new_line": NEW.decode("utf-8"),
            "occurrences_before": 1,
            "scope": "module docstring only",
        },
        "identity_proofs": {
            "suffix_from_first_code_statement_identical": suffix_b == suffix_a,
            "suffix_anchor": anchor.decode(),
            "shared_prefix_bytes": n,
            "old_line_offset": idx,
            "bytes_before_old_line_identical": before[:idx] == after[:idx],
            "bytes_after_old_line_identical": before[idx + len(OLD):] == after[idx + len(NEW):],
            "code_below_docstring_untouched": suffix_b == suffix_a,
            "no_other_byte_changed": after == before[:idx] + NEW + before[idx + len(OLD):],
        },
        "freeze_chain_consequence": (
            "freeze.json entry my_probe_e21 pins 10365/5c9f4508... (the frozen "
            "state above). The on-disk probe now differs by this docstring fix, so "
            "a re-run of final_integrity_check_v2.c_chain would report a live-hash "
            "mismatch for entry my_probe_e21. DISCLOSED, not hidden: the pinned "
            "bytes are preserved byte-for-byte at evidence/r2/"
            "probe_e21_binding.py.frozen_pre_r2_5c9f4508.py and every code byte "
            "below the docstring is proven identical. The evidence itself "
            "(evidence/probe_e21.*, SHA256SUMS.txt) is untouched; no probe re-run "
            "(reviewer: 'no re-run needed').",
        ),
        "reviewer_said": "Fix in any future reissue of the probe; no re-run needed (F-REV-B1P-03). Commissioned now by the parent for this record-only r2 round.",
    }
    ok = (
        report["identity_proofs"]["code_below_docstring_untouched"]
        and report["identity_proofs"]["no_other_byte_changed"]
        and report["identity_proofs"]["bytes_before_old_line_identical"]
        and report["identity_proofs"]["bytes_after_old_line_identical"]
        and report["byte_history"]["frozen_executed_state"]["matches_freeze_json_my_probe_e21_pin"]
    )
    report["all_checks_pass"] = ok
    (OUT / "r2_10_probe_docstring_fix.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
