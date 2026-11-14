"""Rewrite the package's generated text artifacts with LF line endings.

Git stores LF; a CRLF working copy would make the recorded file hash
irreproducible from the repository bytes.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUFFIXES = {".json", ".jsonl", ".py", ".md", ".txt"}


def main() -> int:
    changed = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        if "__pycache__" in path.parts:
            continue
        raw = path.read_bytes()
        if b"\r\n" not in raw:
            continue
        text = raw.decode("utf-8").replace("\r\n", "\n")
        path.write_bytes(text.encode("utf-8"))
        changed.append(str(path.relative_to(ROOT)))
    print(f"normalized {len(changed)} file(s)")
    for name in changed:
        print(" -", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
