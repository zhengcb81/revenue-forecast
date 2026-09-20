"""Recompute the sha256 of every deliverable of this attempt (run last).

Writes a UTF-8 receipt so the reviewer can re-hash the package with one command.

Self-reference rule (round-2 finding 4.1): a file cannot declare its own hash.
This inventory therefore prints `SELF-REFERENCE (not declarable here)` instead
of a hex for itself and for changes.diff (which declares the other files), so no
stale self-declared value can ever be mistaken for a downstream anchor.

argv: <out.txt> [--root <attempt>]
exit: 0 = receipt written, 2 = usage
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SKIP_DIRS = {"venv", "__pycache__", "scratch"}
SELF_REFERENTIAL = {"after/product_hashes.txt", "changes.diff"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: refresh_hashes.py <out.txt> [--root <attempt>]", file=sys.stderr)
        return 2
    out = Path(args[0])
    root = None
    if "--root" in sys.argv:
        root = Path(sys.argv[sys.argv.index("--root") + 1])
    if root is None:
        root = Path(__file__).resolve().parents[1]

    lines = ["I-09-A deliverable hashes", "root=%s" % root, ""]
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files.append((rel.as_posix(), path))
    for rel, path in files:
        # prefix-agnostic: the rule must hold whether --root is the attempt dir
        # itself or its parent (both invocations exist in this attempt's history).
        own = rel.split("/", 1)[1] if "/" in rel else rel
        if rel in SELF_REFERENTIAL or own in SELF_REFERENTIAL:
            # size omitted on purpose (round-3 optional observation): both files
            # are regenerated after every edit, so a printed size would be stale.
            lines.append(
                "SELF-REFERENCE (not declarable here)  %s  size n/a "
                "(read it from the filesystem)" % rel
            )
        else:
            lines.append("%s  %s  %d" % (sha256(path), rel, path.stat().st_size))
    lines.append("")
    lines.append("files=%d" % len(files))
    lines.append(
        "self_referential=%s (their true hashes must be taken from the filesystem "
        "by the reviewer, never from a declaration inside themselves)"
        % ",".join(sorted(SELF_REFERENTIAL))
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote %s files=%d" % (out.name, len(files)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
