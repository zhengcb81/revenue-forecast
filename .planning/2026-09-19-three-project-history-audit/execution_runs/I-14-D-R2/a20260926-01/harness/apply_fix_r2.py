"""I-14-D-R2: apply the frozen fix (oracle.md §6) to a COPY of the pre-image tree.

    python apply_fix_r2.py --src <tree>/src --pre-image-sha <sha256>

Fail-closed by construction:
  * the file's sha256 must equal the frozen pre-image sha BEFORE anything is written,
    otherwise the script aborts with rc 4 and writes nothing;
  * each replacement must match exactly once, otherwise rc 4 and nothing is written;
  * the pre-edit bytes are copied to --backup first, so the rollback is a copy-back.

Only `src/company_wiki/source_catalog/observability.py` is ever opened for writing.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

AUTH_CONST_OLD = (
    '_AUTH_BARE_VALUE = r"[^\\s,;&\\"\'|]+(?:[ \\t]+[^\\s,;&\\"\'|]+)*"\r\n'
    '\r\n'
    '_AUTH_PATTERN = re.compile(\r\n'
)

AUTH_CONST_NEW = (
    '_AUTH_BARE_VALUE = r"[^\\s,;&\\"\'|]+(?:[ \\t]+[^\\s,;&\\"\'|]+)*"\r\n'
    '\r\n'
    '# I-14-D-R2 (review F-REV-D-01 / RULING 2): a credential can be wrapped across\r\n'
    '# ONE line break - a folded header, or the scheme word on its own line - and the\r\n'
    '# line carrying the secret has no `key=` prefix, so _AUTH_BARE_VALUE (inline\r\n'
    '# whitespace only) and the assignment scanner both miss it: the r1 narrowing\r\n'
    '# persisted the full credential in the append-only event log.  Fail CLOSED:\r\n'
    '# behind a *known* scheme word, one line break plus the first following token is\r\n'
    '# consumed inside the match and redacted; the break AFTER that token stays\r\n'
    '# outside the match, so the diagnostics on the following lines survive (the C13\r\n'
    '# half of this card).\r\n'
    '_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"\r\n'
    '                      r"[ \\t]*\\r?\\n[ \\t]*[^\\s,;&\\"\'|]+")\r\n'
    '_AUTH_PATTERN = re.compile(\r\n'
)

VALUE_OLD = 'r"|" + _AUTH_BARE_VALUE + r")"'
VALUE_NEW = 'r"|" + _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"'

REL = Path("company_wiki/source_catalog/observability.py")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--pre-image-sha", required=True)
    p.add_argument("--backup", required=True)
    args = p.parse_args(argv)

    target = Path(args.src) / REL
    original = target.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    if sha != args.pre_image_sha:
        print(f"FAIL_CLOSED: pre-image sha mismatch: {sha} != {args.pre_image_sha}; "
              "nothing written")
        return 4

    text = original.decode("utf-8")
    if text.count(AUTH_CONST_OLD) != 1:
        print(f"FAIL_CLOSED: auth anchor count = {text.count(AUTH_CONST_OLD)} (need 1); "
              "nothing written")
        return 4
    if text.count(VALUE_OLD) != 1:
        print(f"FAIL_CLOSED: value anchor count = {text.count(VALUE_OLD)} (need 1); "
              "nothing written")
        return 4

    edited = text.replace(AUTH_CONST_OLD, AUTH_CONST_NEW, 1).replace(
        VALUE_OLD, VALUE_NEW, 1)

    backup = Path(args.backup)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(target, backup)                      # rollback copy, written first
    target.write_bytes(edited.encode("utf-8"))

    new_bytes = target.read_bytes()
    print(f"pre_sha256={sha} pre_bytes={len(original)}")
    print(f"post_sha256={hashlib.sha256(new_bytes).hexdigest()} post_bytes={len(new_bytes)}")
    print(f"delta_bytes={len(new_bytes) - len(original)}")
    print(f"backup={backup}")
    crlf = new_bytes.count(b"\r\n")
    lf_only = new_bytes.count(b"\n") - crlf
    print(f"crlf={crlf} lf_only={lf_only}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
