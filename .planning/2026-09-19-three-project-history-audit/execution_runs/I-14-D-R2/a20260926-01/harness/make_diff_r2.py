"""I-14-D-R2: emit `changes.diff` for the frozen fix (oracle.md §6/§8.3).

    python make_diff_r2.py --before <pre>/src --after <post>/src --out <attempt>/changes.diff

The patch is produced with difflib over the two byte-identical-except-one-file
sources, in git's own layout (`diff --git a/... b/...` + `index` + `---/+---`),
with POSIX forward-slash paths.  The trees are CRLF, so each content line keeps
its trailing CR as *content* and the patch itself is terminated with LF - the
layout `git apply` expects.  No git command is run: this round performs no git
write of any kind.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import sys
from pathlib import Path

REL = "src/company_wiki/source_catalog/observability.py"


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00%s" % (len(data), data)).hexdigest()


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    pre = Path(args.before) / REL
    post = Path(args.after) / REL
    a_bytes, b_bytes = pre.read_bytes(), post.read_bytes()
    a_lines = a_bytes.decode("utf-8").splitlines(keepends=True)
    b_lines = b_bytes.decode("utf-8").splitlines(keepends=True)

    body = list(difflib.unified_diff(a_lines, b_lines,
                                     fromfile="a/" + REL, tofile="b/" + REL,
                                     n=3, lineterm="\n"))
    head = [
        f"diff --git a/{REL} b/{REL}\n",
        f"index {blob_sha1(a_bytes)[:12]}..{blob_sha1(b_bytes)[:12]} 100644\n",
    ]
    patch = "".join(head + body)
    Path(args.out).write_text(patch, encoding="utf-8", newline="")

    lines = patch.splitlines()
    report = {
        "out": args.out,
        "bytes": len(patch.encode("utf-8")),
        "hunks": sum(1 for line in lines if line.startswith("@@")),
        "files_touched": sorted({line[3:] for line in lines
                                 if line.startswith("+++ ")}),
        "posix_paths_only": all("\\" not in line for line in lines
                                if line.startswith(("--- ", "+++ ", "diff --git"))),
        "before_sha256": hashlib.sha256(a_bytes).hexdigest(),
        "after_sha256": hashlib.sha256(b_bytes).hexdigest(),
        "before_bytes": len(a_bytes),
        "after_bytes": len(b_bytes),
    }
    print(report)
    return 0 if report["posix_paths_only"] and report["hunks"] >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
