"""Prove the round-4 AND round-5 corrections were APPEND-ONLY (chain proof).

Round 5 adds blocks to decision.md / oracle.md / review.md and pastes the reviewer's
verdict at the end of review.md.  This script unwinds the whole chain on the current
files and compares against two recorded snapshots:

    round5-pre = the state after round 4  (recovery/round5-pre-hashes.txt)
    round4-pre = the state before round 4 (recovery/round4-pre-hashes.txt)

Unwinding order per file:
    1. strip the round-5 appendix (review.md only) and remove the round-5 blocks
       -> must equal round5-pre   (round 5 changed nothing else)
    2. remove the round-4 blocks
       -> must equal round4-pre   (round 4 changed nothing else)

If both stages match byte-for-byte, no existing line was ever rewritten or deleted
in either round.

Note: sim/verify_r4_appendonly.py validates only the round-4 stage and therefore no
longer reproduces round4-pre on the current files; THIS script is its superset and
the check to run from round 5 onward.

Run:  & $PY -B sim/verify_r5_appendonly.py     (exit 0 = chain confirmed)
"""

from __future__ import annotations

import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import patch_r4_docs as r4  # noqa: E402
import patch_r5_docs as r5  # noqa: E402

ATTEMPT = r5.ATTEMPT
CRLF = r5.CRLF

ROUND5 = [
    ("decision.md", [(r5.MARK_D1, r5.BLOCK_D1, "after")], []),
    ("oracle.md", [(r5.MARK_O1, r5.BLOCK_O1, "after")], []),
    ("review.md", [(r5.MARK_R1, r5.BLOCK_R1, "after"),
                   (r5.MARK_R5, r5.BLOCK_R5, "after")], ["appendix"]),
]

ROUND4 = [
    ("decision.md", [(r4.MARK_A, r4.BLOCK_A, "after"),
                     (r4.MARK_B, r4.BLOCK_B, "after"),
                     (r4.MARK_C, r4.BLOCK_C, "after"),
                     (r4.MARK_D, r4.BLOCK_D, "after")]),
    ("review.md", [(r4.MARK_E, r4.BLOCK_E, "before")]),
]


def snapshots():
    table = {}
    for name, path in (("round4", os.path.join(ATTEMPT, "recovery", "round4-pre-hashes.txt")),
                       ("round5", os.path.join(ATTEMPT, "recovery", "round5-pre-hashes.txt"))):
        rows = {}
        with io.open(path, encoding="utf-8") as handle:
            for line in handle:
                parts = line.split()
                if len(parts) == 3 and len(parts[1]) == 64:
                    rows[parts[0].replace("\\", "/")] = parts[1]
        table[name] = rows
    return table


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_appendix(text, appendix):
    if not text.endswith(appendix):
        return None
    return text[:len(text) - len(CRLF) - len(appendix)]


def remove_blocks(text, blocks, eol):
    lines = text.split(eol)
    for marker, block, where in blocks:
        hits = [i for i, line in enumerate(lines) if marker in line]
        if len(hits) != 1:
            return None, "marker %r found %d times" % (marker[:24], len(hits))
        index = hits[0]
        if where == "after":
            window = lines[index - 1:index + len(block)]
            if window != [""] + block:
                return None, "block at line %d is not contiguous/verbatim" % (index + 1)
            del lines[index - 1:index + len(block)]
        else:
            window = lines[index:index + len(block) + 1]
            if window != block + [""]:
                return None, "block at line %d is not contiguous/verbatim" % (index + 1)
            del lines[index:index + len(block) + 1]
    return eol.join(lines), ""


def main():
    table = snapshots()
    verdict, report_digest, _ = r5.read_verdict_block()
    appendix = r5.build_appendix(verdict, report_digest)

    ok = True
    print("APPEND-ONLY CHAIN PROOF (rounds 4 + 5)")
    print("snapshots: recovery/round4-pre-hashes.txt, recovery/round5-pre-hashes.txt")
    print("")

    for name in ("decision.md", "oracle.md", "review.md"):
        path = os.path.join(ATTEMPT, name)
        with io.open(path, "r", encoding="utf-8", newline="") as handle:
            text = handle.read()

        stage = text
        for target, blocks, extra in ROUND5:
            if target != name:
                continue
            if "appendix" in extra:
                stripped = strip_appendix(stage, appendix)
                if stripped is None:
                    print("  [FAIL] %s: the appended verdict is not at EOF verbatim" % name)
                    ok = False
                else:
                    stage = stripped
                    print("  [PASS] %s: stripped the appended reviewer verdict (%d lines)"
                          % (name, len(verdict)))
            stage, error = remove_blocks(stage, blocks, CRLF)
            if stage is None:
                print("  [FAIL] %s (round 5): %s" % (name, error))
                ok = False
                break
            print("  [PASS] %s: removed %d round-5 block(s)" % (name, len(blocks)))

        if stage is not None:
            got = digest(stage)
            want = table["round5"].get(name)
            same = got == want
            ok &= same
            print("  [%s] %s after round-5 unwind == round5-pre\n         want=%s\n         got =%s"
                  % ("PASS" if same else "FAIL", name, want, got))

        for target, blocks in ROUND4:
            if target != name or stage is None:
                continue
            stage, error = remove_blocks(stage, blocks, CRLF)
            if stage is None:
                print("  [FAIL] %s (round 4): %s" % (name, error))
                ok = False
                break
            print("  [PASS] %s: removed %d round-4 block(s)" % (name, len(blocks)))

        if stage is not None:
            got = digest(stage)
            want = table["round4"].get(name)
            same = got == want
            ok &= same
            print("  [%s] %s after round-4 unwind == round4-pre (the original reviewed bytes)\n"
                  "         want=%s\n         got =%s" % ("PASS" if same else "FAIL", name, want, got))
        print("")

    print("VERDICT: %s"
          % ("APPEND-ONLY CONFIRMED FOR ROUNDS 4 AND 5" if ok else "MISMATCH - inspect manually"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
