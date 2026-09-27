"""I-14-E-TESTSIDE-R3: mutation M2-upper applier (R2 oracle.md section 4, row 2).

Applies the frozen fix exactly like ``apply_fix.py fix`` (same anchors, same
generated helpers), then mutates the ONE registered element only:

    semantic upper clamp  t0_seconds + 3.0  ->  t0_seconds + 10.0

Everything else (floor 2.0, coefficient 4, t0 probe, trace recording, call
site) stays byte-identical to the green version.  Every replacement fails
loudly unless its anchor is found exactly once, so a silent no-op cannot
masquerade as an applied mutation.

Reuses apply_fix.py's constants so the criteria code exists in exactly one
place; this file only adds the registered mutation.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_fix as af  # noqa: E402

MUT_TAG = "M2-upper (R2 oracle.md section 4)"

CLAMP_OLD = "    return min(max(2.0, 4.0 * t0_seconds), t0_seconds + 3.0)"
CLAMP_NEW = "    return min(max(2.0, 4.0 * t0_seconds), t0_seconds + 10.0)"


def main(argv: list[str]) -> int:
    if not af.ORIGINAL.exists():
        shutil.copyfile(af.TEST, af.ORIGINAL)
        print(f"pristine original saved -> {af.ORIGINAL} sha256={af.sha(af.ORIGINAL)}")

    text = af.ORIGINAL.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"

    def nl(block: str) -> str:
        return block.replace("\n", newline)

    helpers = nl(af.HELPERS)
    tail = nl(af.HELPERS_ANCHOR_TAIL)
    text = af._replace_once(text, tail, tail + helpers, "helper-insert")
    text = af._replace_once(text, nl(af.CALL_ANCHOR), nl(af.CALL_FIX), "call-site")
    text = af._replace_once(text, nl(CLAMP_OLD), nl(CLAMP_NEW), "m2-upper-clamp")
    af.TEST.write_bytes(text.encode("utf-8"))
    print(f"mode=mut2-upper applied ({MUT_TAG}) -> sha256={af.sha(af.TEST)} "
          f"bytes={af.TEST.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
