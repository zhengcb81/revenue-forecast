"""Prove the round-4 corrections were APPEND-ONLY.

Method: take the current decision.md / review.md, delete exactly the blocks that
sim/patch_r4_docs.py inserted (located by their unique markers), and compare the
sha256 of the reconstructed text with the pre-change snapshot recorded in
recovery/round4-pre-hashes.txt before any edit was made.  If both hashes match,
no other byte of either document changed: nothing was rewritten, nothing deleted.

Exit code 0 = both files reproduce their pre-change hash after block removal.

Run:  & $PY -B sim/verify_r4_appendonly.py
"""

from __future__ import annotations

import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import patch_r4_docs as patch  # noqa: E402

ATTEMPT = patch.ATTEMPT
SNAPSHOT = os.path.join(ATTEMPT, "recovery", "round4-pre-hashes.txt")

TARGETS = {
    "decision.md": [
        (patch.MARK_A, patch.BLOCK_A, "after"),
        (patch.MARK_B, patch.BLOCK_B, "after"),
        (patch.MARK_C, patch.BLOCK_C, "after"),
        (patch.MARK_D, patch.BLOCK_D, "after"),
    ],
    "review.md": [
        (patch.MARK_E, patch.BLOCK_E, "before"),
    ],
}


def pre_hashes():
    table = {}
    with io.open(SNAPSHOT, encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 3 and len(parts[1]) == 64:
                table[parts[0].replace("\\", "/")] = parts[1]
    return table


def main():
    table = pre_hashes()
    ok = True
    print("APPEND-ONLY PROOF (round 4)")
    print("pre-change snapshot: recovery/round4-pre-hashes.txt")
    for name, blocks in sorted(TARGETS.items()):
        path = os.path.join(ATTEMPT, name)
        with io.open(path, "r", encoding="utf-8", newline="") as handle:
            text = handle.read()
        lines = text.split(patch.CRLF)
        for marker, block, where in blocks:
            hits = [i for i, line in enumerate(lines) if marker in line]
            if len(hits) != 1:
                print("  [FAIL] %s: marker found %d times (%s)"
                      % (name, len(hits), marker.encode("ascii", "backslashreplace").decode("ascii")))
                ok = False
                continue
            index = hits[0]
            if where == "after":
                window = lines[index - 1:index + len(block)]
                head = [""]
                tail = []
            else:
                window = lines[index:index + len(block) + 1]
                head = []
                tail = [""]
            expected = head + block + tail
            if window != expected:
                print("  [FAIL] %s: inserted block is not contiguous/verbatim at line %d"
                      % (name, index + 1))
                ok = False
                continue
            if where == "after":
                del lines[index - 1:index + len(block)]
            else:
                del lines[index:index + len(block) + 1]
            print("  [PASS] %s: removed inserted block at line %d (%d lines)"
                  % (name, index + 1, len(block)))
        reconstructed = patch.CRLF.join(lines)
        digest = hashlib.sha256(reconstructed.encode("utf-8")).hexdigest()
        before = table.get(name)
        same = digest == before
        ok &= same
        print("  [%s] %s: reconstructed sha256 == pre-change sha256\n         pre  =%s\n         recon=%s"
              % ("PASS" if same else "FAIL", name, before, digest))
    print("VERDICT: %s" % ("APPEND-ONLY CONFIRMED" if ok else "MISMATCH - inspect manually"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
