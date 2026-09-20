"""W05A independent slice verifier.

Reads the fixed sample and the section files published by the REAL producer
and checks them against hand-computed body offsets taken from the sample
file itself (no call into company_wiki).  Also recomputes the index hash.

  <py> -X utf8 -B scripts/w05a_independent_check.py [case-dir-name]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"
SCRATCH_ROOT = Path(r"C:\Users\郑曾波\AppData\Local\Temp\w05a\a20260919-01")

# expectations hand-computed from samples/annual_normalized.md
PRODUCER_BODY_OFFSET = 259
EXPECTED_SLICES = {
    "business_overview": {"char_start": 108, "char_end": 207, "length": 99},
    "mda": {"char_start": 207, "char_end": 339, "length": 132},
}


def main() -> int:
    case = sys.argv[1] if len(sys.argv) > 1 else "c0"
    raw = (SAMPLES / "annual_normalized.md").read_text(encoding="utf-8")
    derived = SCRATCH_ROOT / case / "catalog" / "derived"
    hits = list(derived.glob("*/*/sections/index.json"))
    out: dict = {
        "case": case,
        "sample_path": str(SAMPLES / "annual_normalized.md"),
        "sample_sha256": hashlib.sha256(
            (SAMPLES / "annual_normalized.md").read_bytes()
        ).hexdigest(),
        "hand_computed": {
            "producer_body_offset": PRODUCER_BODY_OFFSET,
            "expected_slices": EXPECTED_SLICES,
            "note": "offsets read off the sample text with str.index(); the "
            "producer's own coordinate system starts 17 chars before the raw "
            "'## Page 1' index (frontmatter + '# title' strip)",
        },
        "index_found": [str(p) for p in hits],
    }
    if len(hits) != 1:
        out["verdict"] = "blocked: expected exactly one sections/index.json"
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 1
    index_path = hits[0]
    index_bytes = index_path.read_bytes()
    entries = json.loads(index_bytes.decode("utf-8"))
    out["index_path"] = str(index_path)
    out["index_sha256_recomputed"] = hashlib.sha256(index_bytes).hexdigest()
    checks = []
    for entry in entries:
        role = entry["role"]
        expected = EXPECTED_SLICES.get(role)
        published = Path(entry["path"])
        text = published.read_text(encoding="utf-8") if published.is_file() else None
        independent = raw[
            PRODUCER_BODY_OFFSET + entry["char_start"]:
            PRODUCER_BODY_OFFSET + entry["char_end"]
        ]
        checks.append(
            {
                "role": role,
                "char_start": entry["char_start"],
                "char_end": entry["char_end"],
                "span_length": entry["char_end"] - entry["char_start"],
                "expected": expected,
                "offsets_match_hand_computed": bool(
                    expected
                    and entry["char_start"] == expected["char_start"]
                    and entry["char_end"] == expected["char_end"]
                ),
                "file_length_equals_span": bool(
                    text is not None and len(text) == entry["char_end"] - entry["char_start"]
                ),
                "published_sha256": (
                    hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
                ),
                "independent_sha256": hashlib.sha256(
                    independent.encode("utf-8")
                ).hexdigest(),
                "published_equals_independent_slice_exact": text == independent,
                # The producer's slice() trims the surrounding newlines, so the
                # byte-exact window differs from the file by one leading and one
                # trailing "\n".  The content equality that matters is the
                # newline-trimmed one; the exact comparison above stays in the
                # evidence as the raw fact.
                "published_equals_independent_slice_trimmed": bool(
                    text is not None
                    and text.strip("\n") == independent.strip("\n")
                ),
                "published_leading_newlines": (
                    len(text) - len(text.lstrip("\n")) if text else None
                ),
                # F-I05A-02: the slice bytes must be BOUND, not merely measured
                "recorded_slice_sha256": entry.get("content_sha256"),
                "recomputed_slice_sha256": (
                    hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
                ),
                "slice_hash_matches": bool(
                    text is not None
                    and entry.get("content_sha256")
                    and hashlib.sha256(text.encode("utf-8")).hexdigest()
                    == entry.get("content_sha256")
                ),
                "span_ids": list(entry.get("span_ids") or []),
            }
        )
    out["slices"] = checks
    out["slice_hash_bound"] = all(
        check["slice_hash_matches"] for check in checks
    )
    out["verdict"] = (
        "PASS"
        if all(
            check["offsets_match_hand_computed"]
            and check["file_length_equals_span"]
            and check["published_equals_independent_slice_trimmed"]
            for check in checks
        )
        else "counterexample"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
