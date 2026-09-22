"""Build the fix-round MUTATION test file (anti-vacuity, direction 2).

mutation = the frozen r4 suite with EXACTLY TWO edits: the e11 and e13 bodies
are reverted to their superseded r1/r3 pinned-gap expectations (attack
ACCEPTED). Everything else — including e1's tree-conditional positive control
and the RF_IMPORT_ROOT override — is byte-identical to the frozen r4 file.

Run:  C:\\Miniconda\\python.exe -B scratch\\fixround\\make_mutation.py
Exit: 0 iff both literals were found and replaced exactly once.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parents[1]
SRC = ATTEMPT / "test_i08c_consumer_rejection.py"
OUT_DIR = HERE / "mutation"
OUT = OUT_DIR / "test_i08c_mutation_pinned_gap.py"

R4_E11_TAIL = (
    '    with pytest.raises(ForecastInputError, match="attestation_missing_record"):\n'
    "        validate_publication_receipt(flipped)\n"
    '    with pytest.raises(ForecastInputError, match="attestation_missing_record"):\n'
    "        validate_forecast_output(flipped)\n"
)
MUT_E11_TAIL = (
    "    validate_publication_receipt(flipped)  # SUPERSEDED r1/r3: gap pinned as accepted\n"
    "    validate_forecast_output(flipped)      # SUPERSEDED r1/r3: gap pinned as accepted\n"
)

R4_E13_TAIL = (
    "    validate_publication_receipt(forged)  # F2 limitation: receipt layer is hash-consistency only\n"
    '    with pytest.raises(ForecastInputError, match="segment base revenue mismatch"):\n'
    "        validate_forecast_output(forged)\n"
)
MUT_E13_TAIL = (
    "    validate_publication_receipt(forged)\n"
    "    validate_forecast_output(forged)  # SUPERSEDED r1/r3: gap pinned as accepted\n"
)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    src_bytes = SRC.read_bytes()
    src = src_bytes.decode("utf-8")

    checks = {
        "r4_e11_tail_found_once": src.count(R4_E11_TAIL) == 1,
        "r4_e13_tail_found_once": src.count(R4_E13_TAIL) == 1,
    }
    if not all(checks.values()):
        print({"ok": False, "checks": checks})
        return 1

    mut = src.replace(R4_E11_TAIL, MUT_E11_TAIL, 1).replace(
        R4_E13_TAIL, MUT_E13_TAIL, 1
    )
    post = {
        "mutation_e11_tail_present": MUT_E11_TAIL in mut,
        "mutation_e13_tail_present": MUT_E13_TAIL in mut,
        "r4_e11_tail_gone": R4_E11_TAIL not in mut,
        "r4_e13_tail_gone": R4_E13_TAIL not in mut,
        "e13_rejection_match_gone": 'match="segment base revenue mismatch"' not in mut,
        "e11_rejection_match_gone": 'match="attestation_missing_record"' not in mut,
        "e1_positive_control_kept": 'hasattr(_rp, "validate_publication_attestation")' in mut,
        "import_root_override_kept": 'os.environ.get("RF_IMPORT_ROOT")' in mut,
    }
    if not all(post.values()):
        print({"ok": False, "checks": {**checks, **post}})
        return 1

    out_bytes = mut.encode("utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(out_bytes)
    print(
        {
            "ok": True,
            "source": str(SRC),
            "source_bytes": len(src_bytes),
            "source_sha256": sha256(src_bytes),
            "mutation": str(OUT),
            "mutation_bytes": len(out_bytes),
            "mutation_sha256": sha256(out_bytes),
            "edits": ["e11 tail -> superseded pinned-gap body", "e13 tail -> superseded pinned-gap body"],
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
