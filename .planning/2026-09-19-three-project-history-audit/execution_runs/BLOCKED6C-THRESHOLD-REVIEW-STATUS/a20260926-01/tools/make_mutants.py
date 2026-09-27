"""BLOCKED6C mutation generator (oracle.md section 5, M1..M5, frozen).

Reads the patched validator and writes one mutated copy per pre-registered
mutation into <run>/mut/M*/validate_hypotheses.py. Every edit asserts that its
anchor text occurs EXACTLY once, otherwise the script aborts loudly (a silent
no-op mutation would make the whole J2 judgement worthless).

Mutations are deletions/rewrites of the NEW judgement blocks only; nothing else
in the file is touched.
"""
from __future__ import annotations

import os
import sys

MUTANT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(MUTANT_DIR, "iso_patched", "tools", "validate_hypotheses.py")


def cut_block(text, open_marker, close_marker):
    """Delete everything from the open marker line through the close marker line."""
    i = text.index(open_marker)
    j = text.index(close_marker, i)
    j = j + len(close_marker)
    # swallow the trailing newline of the closing marker line
    if text[j:j + 1] == "\n":
        j += 1
    return text[:i] + text[j:]


def replace_once(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor count=%d (expected 1) for: %r" % (n, old[:70]))
    return text.replace(old, new)


def m1(text):
    # default value flipped: an ABSENT field now resolves to "reviewed"
    return replace_once(text,
                        'DEFAULT_THRESHOLD_REVIEW_STATUS = "not_reviewed"',
                        'DEFAULT_THRESHOLD_REVIEW_STATUS = "reviewed"')


def m2(text):
    # the whole not_reviewed fail-closed branch (B6C-G3) removed
    return cut_block(text, "        # <B6C-G3>", "        # </B6C-G3>")


def m3(text):
    # the PRE-EXISTING threshold_basis closed-set check removed
    return replace_once(
        text,
        '        if tb not in THRESHOLD_BASES:\n'
        '            err("E_THRESHOLD_BASIS_UNKNOWN",\n'
        '                "threshold_basis=%r not in %s" % (tb, sorted(THRESHOLD_BASES)))\n',
        '')


def m4(text):
    # the status closed-set judgement (B6C-G1) removed; the shared assignment
    # above it stays because G2/G3 read those names (deleting it would crash
    # validate() instead of flipping the judgement).
    return replace_once(
        text,
        '        if _trs_present and _trs_raw not in THRESHOLD_REVIEW_STATUSES:\n'
        '            err("E_THRESHOLD_REVIEW_STATUS_UNKNOWN",\n'
        '                "B6C-G1: falsifier.threshold_review_status=%r not in %s"\n'
        '                % (_trs_raw, sorted(THRESHOLD_REVIEW_STATUSES)))\n',
        '')


def m5(text):
    # the A-6.3 seal judgement (B6C-G2) removed
    return replace_once(
        text,
        '        if _trs_raw == "reviewed":\n'
        '            _seal_ok, _seal_why = review_seal_ok(h)\n'
        '            if not _seal_ok:\n'
        '                err("E_THRESHOLD_REVIEW_STATUS_UNSEALED",\n'
        '                    "B6C-G2: threshold_review_status=reviewed without the A-6.3 seal (%s)"\n'
        '                    % _seal_why)\n',
        '')


MUTATIONS = {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5}


def main() -> int:
    base = open(SRC, encoding="utf-8").read()
    for name, fn in MUTATIONS.items():
        out_text = fn(base)
        if out_text == base:
            raise SystemExit("%s produced no change" % name)
        d = os.path.join(MUTANT_DIR, "mut", name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "validate_hypotheses.py")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out_text)
        import hashlib
        print("%s wrote %s bytes sha256=%s delta=%+d"
              % (name, p, hashlib.sha256(out_text.encode("utf-8")).hexdigest(),
                 len(out_text) - len(base)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
