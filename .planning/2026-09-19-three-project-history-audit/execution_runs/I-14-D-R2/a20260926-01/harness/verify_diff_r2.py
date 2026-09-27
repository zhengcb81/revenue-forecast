"""I-14-D-R2: round-trip verification of `changes.diff` (oracle.md §8.3).

    python verify_diff_r2.py --patch <changes.diff> --before <pre file> --after <post file>

Forward  : apply the patch to the pre-image bytes  -> must equal the post-image bytes.
Reverse  : apply the reversed patch to the post-image bytes -> must equal the pre-image bytes.

A tiny unified-diff applier is used on purpose: this round performs no git write
(纪律: 禁 git 写), and `git apply` would need a work tree.  Exit 0 = both directions
byte-identical, 3 = mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse(patch_text: str):
    lines = patch_text.splitlines(keepends=True)
    hunks, i = [], 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        if not m:
            i += 1
            continue
        old_start, old_len = int(m.group(1)), int(m.group(2) or "1")
        ops = []
        i += 1
        while i < len(lines) and not HUNK.match(lines[i]):
            line = lines[i]
            if line.startswith("\\"):          # "\ No newline at end of file"
                i += 1
                continue
            tag, content = line[0], line[1:]
            if tag == " ":
                ops.append((" ", content))
            elif tag == "-":
                ops.append(("-", content))
            elif tag == "+":
                ops.append(("+", content))
            elif line.strip() == "":
                ops.append((" ", "\n"))         # tolerate a bare blank context line
            else:
                raise SystemExit(f"unexpected patch line: {line!r}")
            i += 1
        hunks.append((old_start, old_len, ops))
    return hunks


def _lf_only(text: str) -> str:
    return text.replace("\r\n", "\n")


def apply_patch(patch_text: str, source: str, reverse: bool) -> str:
    """Apply this round's single-file unified diff to `source`.

    forward (reverse=False): source is the PRE image  -> drop '-', emit '+'.
    reverse (reverse=True) : source is the POST image -> drop '+', emit '-'.
    The anchor of each hunk is its context plus the lines that exist in `source`.
    """
    out_lines = source.splitlines(keepends=True)
    cursor, result = 0, []
    anchor_tag = "-" if not reverse else "+"
    for _start, _len, ops in parse(patch_text):
        probe = [c for t, c in ops if t in (" ", anchor_tag)]
        idx = _find(out_lines, cursor, probe)
        if idx is None:
            raise SystemExit("anchor not found (patch does not fit the source)")
        result.extend(out_lines[cursor:idx])
        for tag, content in ops:
            if tag == " ":
                result.append(content)
            elif tag == "-":
                if reverse:
                    result.append(content)      # re-inserted on reverse
            elif tag == "+":
                if not reverse:
                    result.append(content)      # added on forward
        cursor = idx + len(probe)
    result.extend(out_lines[cursor:])
    return "".join(result)


def _find(lines, start, probe):
    n = len(probe)
    for i in range(start, len(lines) - n + 1):
        if lines[i:i + n] == probe:
            return i
    return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--patch", required=True)
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    args = p.parse_args(argv)

    patch = Path(args.patch).read_text(encoding="utf-8", newline="")
    pre = Path(args.before).read_bytes().decode("utf-8")
    post = Path(args.after).read_bytes().decode("utf-8")

    fwd = apply_patch(patch, pre, reverse=False)
    rev = apply_patch(patch, post, reverse=True)

    ok_fwd = fwd == post
    ok_rev = rev == pre
    report = {
        "patch": args.patch,
        "forward_applies_to_post": ok_fwd,
        "reverse_applies_to_pre": ok_rev,
        "pre_sha256": hashlib.sha256(Path(args.before).read_bytes()).hexdigest(),
        "post_sha256": hashlib.sha256(Path(args.after).read_bytes()).hexdigest(),
        "fwd_sha256": hashlib.sha256(fwd.encode("utf-8")).hexdigest(),
        "rev_sha256": hashlib.sha256(rev.encode("utf-8")).hexdigest(),
    }
    print(report)
    return 0 if (ok_fwd and ok_rev) else 3


if __name__ == "__main__":
    sys.exit(main())
