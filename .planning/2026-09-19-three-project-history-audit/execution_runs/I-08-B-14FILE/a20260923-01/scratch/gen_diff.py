"""Generate this card's changes.diff (before_tree -> after_tree) for EXACTLY the
authorized 14 paths, and FAIL LOUDLY if any other path differs (frozen oracle S.5).

No git. Pure python. Usage:
  python gen_diff.py <before_tree> <after_tree> <out.diff> <expected_list_file>
expected_list_file: one product-relative path per line (the 14).
Prints a JSON summary to stdout.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        if p.suffix == ".pyc":
            continue
        out["/".join(rel_parts)] = p
    return out


def unified(path: str, a_text: str, b_text: str) -> str:
    import difflib

    a_lines = a_text.splitlines(keepends=True)
    b_lines = b_text.splitlines(keepends=True)
    # normalize to LF for hunk generation; content equality is judged on bytes
    diff = list(
        difflib.unified_diff(
            a_lines, b_lines, fromfile=f"a/{path}", tofile=f"b/{path}", n=3
        )
    )
    if not diff:
        return ""
    body = "".join(diff)
    return f"diff --git a/{path} b/{path}\n{body}"


def main() -> int:
    before, after, out_path, expected_file = map(Path, sys.argv[1:5])
    expected = [
        line.strip().replace("\\", "/")
        for line in expected_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exp_set = set(expected)

    b_map = walk(before)
    a_map = walk(after)

    added = sorted(set(a_map) - set(b_map))
    deleted = sorted(set(b_map) - set(a_map))
    modified = sorted(
        rel
        for rel in set(a_map) & set(b_map)
        if digest(a_map[rel]) != digest(b_map[rel])
    )

    observed = set(added) | set(deleted) | set(modified)
    extras = sorted(observed - exp_set)
    missing = sorted(exp_set - observed)

    parts: list[str] = []
    per_file: dict[str, dict] = {}
    for rel in expected:
        b_has, a_has = rel in b_map, rel in a_map
        if b_has and a_has:
            bt = b_map[rel].read_bytes()
            at = a_map[rel].read_bytes()
            try:
                bs, as_ = bt.decode("utf-8"), at.decode("utf-8")
            except UnicodeDecodeError:
                raise SystemExit(f"NON-UTF8 file in diff scope: {rel}")
            # byte-oriented diff on exact text (preserve original newlines)
            chunk = unified(rel, bs, as_)
            per_file[rel] = {
                "kind": "edit",
                "before_sha256": hashlib.sha256(bt).hexdigest(),
                "after_sha256": hashlib.sha256(at).hexdigest(),
            }
        elif a_has and not b_has:
            at = a_map[rel].read_bytes()
            as_ = at.decode("utf-8")
            # full-add diff: every line added
            import difflib

            lines = as_.splitlines(keepends=True)
            n = len(lines)
            hdr = (
                f"diff --git a/{rel} b/{rel}\n"
                f"--- /dev/null\n"
                f"+++ b/{rel}\n"
                f"@@ -0,0 +1,{n} @@\n"
            )
            chunk = hdr + "".join("+" + ln for ln in lines)
            per_file[rel] = {
                "kind": "add",
                "before_sha256": None,
                "after_sha256": hashlib.sha256(at).hexdigest(),
            }
        else:
            raise SystemExit(f"expected file MISSING in after_tree: {rel}")
        if not chunk.endswith("\n"):
            chunk += "\n"
        parts.append(chunk)

    header = (
        "# I-08-B-14FILE / a20260923-01 -- authorized 14-file delivery\n"
        "# base: live RF product tree (before_tree, byte-verified) -> after: I-08-B carrier bytes\n"
        f"# files: {len(expected)} (9 edited + 5 added); extras={extras}; missing={missing}\n"
    )
    text = header + "".join(parts)
    out_path.write_text(text, encoding="utf-8", newline="")

    summary = {
        "files_expected": len(expected),
        "added": added,
        "deleted": deleted,
        "modified": modified,
        "extras": extras,
        "missing_expected_diff": missing,
        "changes_diff_bytes": out_path.stat().st_size,
        "changes_diff_sha256": digest(out_path),
        "per_file": per_file,
    }
    print(json.dumps(summary, indent=2))
    if extras or missing:
        print("SCOPE VIOLATION: diff contains paths outside the authorized 14", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
