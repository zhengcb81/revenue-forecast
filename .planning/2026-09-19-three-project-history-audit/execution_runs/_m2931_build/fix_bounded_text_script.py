"""Repair apply_bounded_text_pass.py after tooling mangled two spots.

The edit tooling produced (a) a truncated final line (`raise SystemE`) and (b) lost the `triple()`
helper while the two warning constants still open with a literal three-quote sequence.  Both are
fixed here textually, then the result is compiled to prove it parses.

Usage:
  python -X utf8 -B fix_bounded_text_script.py --path <apply_bounded_text_pass.py>
"""

from __future__ import annotations

import argparse
import hashlib
import py_compile
import os

TRIPLE = chr(34) * 3
BROKEN_TAIL = "    raise SystemE"
FIXED_TAIL = '    raise SystemExit(main())'

HELPER_ANCHOR = "def sha256(path):"
HELPER_TEXT = (
    "def triple():\n"
    '    """The three-character docstring delimiter, built at runtime so this file never contains a\n'
    '    triple-quoted literal nested inside another triple-quoted literal."""\n'
    "    return chr(34) * 3\n"
    "\n"
    "\n"
)

OLD_PACK = "PACK_WARNING = " + TRIPLE
NEW_PACK = "PACK_WARNING = ''" + TRIPLE
OLD_WB = "WRITE_BINDING_WARNING = " + TRIPLE
NEW_WB = "WRITE_BINDING_WARNING = ''" + TRIPLE


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    path = os.path.abspath(args.path)
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    before = sha256(path)
    changes = []

    if text.rstrip().endswith(BROKEN_TAIL):
        text = text.rstrip()[: -len(BROKEN_TAIL)] + FIXED_TAIL + "\n"
        changes.append("restored the truncated final line")
    if "def triple()" not in text:
        text = text.replace(HELPER_ANCHOR, HELPER_TEXT + HELPER_ANCHOR, 1)
        changes.append("re-added the triple() helper")
    if OLD_PACK in text:
        text = text.replace(OLD_PACK, NEW_PACK, 1)
        changes.append("PACK_WARNING opens on one line (no bare three-quote token)")
    if OLD_WB in text:
        text = text.replace(OLD_WB, NEW_WB, 1)
        changes.append("WRITE_BINDING_WARNING opens on one line")

    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("repairs:", changes)
    print("sha256 %s -> %s" % (before[:16], sha256(path)[:16]))
    py_compile.compile(path, doraise=True)
    print("py_compile: OK")
    # prove the two constants are now real strings
    namespace = {}
    source = open(path, "r", encoding="utf-8").read()
    for name in ("PACK_WARNING", "WRITE_BINDING_WARNING"):
        start = source.index(name + " = ")
        end = source.index("\n\n", start)
        fragment = source[start:end]
        exec(compile(fragment, path, "exec"), namespace)  # noqa: S102
        print("%s length %d" % (name, len(namespace[name])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
