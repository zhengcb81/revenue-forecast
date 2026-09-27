"""I-14-D-R2: build the four mutation trees of oracle.md §7.

Each mutation is a SINGLE-SITE byte edit applied to a fresh copy of
`iso/product_post`; the post tree itself is never touched (its sha256 is checked
before and after this script runs).  Every anchor must occur exactly once, or the
script fails closed (rc 4) and writes nothing.

    python build_mutations_r2.py --post-src <path> --mut-root <path> --post-sha <sha256>
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REL = Path("company_wiki/source_catalog/observability.py")

SPLIT_CONST = (
    '_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"\r\n'
    '                      r"[ \\t]*\\r?\\n[ \\t]*[^\\s,;&\\"\'|]+")\r\n'
)
VALUE_POST = 'r"|" + _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"'
VALUE_PRE = 'r"|" + _AUTH_BARE_VALUE + r")"'

# id -> (description, anchor, replacement); anchor must occur EXACTLY once
MUTATIONS = {
    "M1_auth_path_unfixed": (
        "remove the _AUTH_SCHEME_SPLIT branch from _AUTH_PATTERN "
        "(only the iso/narrow half stays fixed; the authorization path is not)",
        VALUE_POST,
        VALUE_PRE,
    ),
    "M2_scheme_list_no_bearer_token": (
        "the scheme-word list no longer recognises bearer/token",
        '(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)',
        '(?:basic|digest|oauth|jwt|apikey|api_key|sso)',
    ),
    "M3_scheme_split_multi_line_run": (
        "the post-break value becomes a MULTI-LINE token run (swallows diagnostics)",
        'r"[ \\t]*\\r?\\n[ \\t]*[^\\s,;&\\"\'|]+")',
        'r"(?:[ \\t]*\\r?\\n[ \\t]*[^\\s,;&\\"\'|]+)+")',
    ),
    "M4_split_no_crlf": (
        "the post-break line feed is LF-only (CRLF headers no longer recognised)",
        'r"[ \\t]*\\r?\\n[ \\t]*',
        'r"[ \\t]*\\n[ \\t]*',
    ),
}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--post-src", required=True)
    p.add_argument("--mut-root", required=True)
    p.add_argument("--post-sha", required=True)
    args = p.parse_args(argv)

    post_src = Path(args.post_src)
    target = post_src / REL
    original = target.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    if sha != args.post_sha:
        print(f"FAIL_CLOSED: product_post sha moved: {sha} != {args.post_sha}")
        return 4

    text = original.decode("utf-8")
    for mid, (_desc, anchor, repl) in MUTATIONS.items():
        if text.count(anchor) != 1:
            print(f"FAIL_CLOSED: {mid} anchor count = {text.count(anchor)} (need 1)")
            return 4

    made = []
    for mid, (desc, anchor, repl) in MUTATIONS.items():
        mut_src = Path(args.mut_root) / mid / "src"
        if mut_src.exists():
            shutil.rmtree(mut_src)
        shutil.copytree(post_src, mut_src)
        f = mut_src / REL
        b = f.read_bytes().decode("utf-8")
        assert b.count(anchor) == 1, mid
        f.write_bytes(b.replace(anchor, repl, 1).encode("utf-8"))
        new_sha = hashlib.sha256(f.read_bytes()).hexdigest()
        made.append((mid, desc, new_sha, len(f.read_bytes())))

    after = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"product_post_sha_before={sha}")
    print(f"product_post_sha_after ={after}  unchanged={after == sha}")
    for mid, desc, msha, mlen in made:
        print(f"{mid}: sha256={msha} bytes={mlen} :: {desc}")
    return 0 if after == sha else 4


if __name__ == "__main__":
    sys.exit(main())
