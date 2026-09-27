"""Minimal unified-diff applier (git-format sections). No git, exact-context.

Modes:
  python apply_diff.py verify <diff> <before_root> <after_root>
      For every file section in <diff>: apply to before_root copy IN MEMORY and
      require byte-equality with after_root's file (round-trip proof).
  python apply_diff.py apply <diff> <target_root> <forbid_list>
      Apply every section to <target_root> in place. Refuses (exit 3) if any
      section path appears in <forbid_list> (one path per line).
Prints a JSON report.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def parse_sections(text: str) -> list[dict]:
    sections: list[dict] = []
    cur: dict | None = None
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*) b/(.*)\n?$", line)
            if not m:
                raise SystemExit(f"bad diff header: {line!r}")
            cur = {"path": m.group(2), "hunks": [], "new_file": False}
            sections.append(cur)
            i += 1
            continue
        if cur is None:
            i += 1  # comments / preheader
            continue
        if line.startswith("--- "):
            if line.startswith("--- /dev/null"):
                cur["new_file"] = True
            i += 1
            continue
        if line.startswith("+++ "):
            i += 1
            continue
        if line.startswith("index "):
            i += 1
            continue
        m = HUNK_RE.match(line)
        if m:
            a_start = int(m.group(1))
            a_count = int(m.group(2) or "1")
            old: list[str] = []
            new: list[str] = []
            i += 1
            while i < len(lines) and (len(old) < a_count or True):
                l = lines[i]
                if l.startswith("diff --git ") or HUNK_RE.match(l):
                    break
                if l.startswith("\\"):  # "\ No newline at end of file"
                    i += 1
                    continue
                if l.startswith("+"):
                    new.append(l[1:])
                elif l.startswith("-"):
                    old.append(l[1:])
                elif l.startswith(" "):
                    old.append(l[1:])
                    new.append(l[1:])
                elif l.startswith("@@"):
                    break
                else:
                    # header comment lines inside section (e.g. '# ...')
                    if l.startswith("#"):
                        i += 1
                        continue
                    break
                i += 1
            cur["hunks"].append({"a_start": a_start, "old": old, "new": new})
            continue
        if line.startswith("#"):
            i += 1
            continue
        i += 1
    return sections


def apply_to_lines(lines: list[str], hunks: list[dict], path: str) -> list[str]:
    # exact-context sequential application (no fuzz)
    out = list(lines)
    offset = 0
    for h in hunks:
        target_start = h["a_start"] - 1 + offset
        old = h["old"]
        if not old and not out:
            # pure insert into empty
            seg_pos = 0
        else:
            # exact search anchored near expected position, else whole file
            seg_pos = None
            window = 200
            lo = max(0, target_start - window)
            hi = min(len(out), target_start + window + 1)
            for pos in range(lo, hi):
                if out[pos : pos + len(old)] == old:
                    # prefer the expected anchor
                    seg_pos = pos
                    if pos == target_start:
                        break
            if seg_pos is None:
                for pos in range(0, len(out) + 1):
                    if out[pos : pos + len(old)] == old:
                        seg_pos = pos
                        break
            if seg_pos is None:
                raise SystemExit(
                    f"CONTEXT MISS in {path}: hunk @@ -{h['a_start']} (first old line {old[:1]!r})"
                )
        out[seg_pos : seg_pos + len(old)] = h["new"]
        offset += len(h["new"]) - len(old)
    return out


def main() -> int:
    mode, diff_path, root = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    # newline="" — NO universal-newline translation: the diff's content lines
    # carry the trees' own line endings (CRLF files -> CRLF diff lines).
    with open(diff_path, encoding="utf-8", newline="") as fh:
        sections = parse_sections(fh.read())
    report = {"mode": mode, "sections": [s["path"] for s in sections], "results": []}

    if mode == "verify":
        after_root = Path(sys.argv[4])
        ok = True
        for s in sections:
            p = s["path"]
            before_p = root / Path(p)
            after_p = after_root / Path(p)
            base = b"" if s["new_file"] else before_p.read_bytes()
            base_lines = (
                base.decode("utf-8").splitlines(keepends=True) if base else []
            )
            if not s["new_file"] and not before_p.exists():
                raise SystemExit(f"missing before file: {p}")
            got = apply_to_lines(base_lines, s["hunks"], p)
            got_bytes = "".join(got).encode("utf-8")
            want = after_p.read_bytes()
            same = got_bytes == want
            ok = ok and same
            report["results"].append(
                {
                    "path": p,
                    "roundtrip_equal": same,
                    "got_sha": digest(got_bytes),
                    "want_sha": digest(want),
                }
            )
        print(json.dumps(report, indent=2))
        return 0 if ok else 4

    if mode == "apply":
        forbid_file = Path(sys.argv[4])
        forbid = {
            ln.strip().replace("\\", "/")
            for ln in forbid_file.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        }
        for s in sections:
            if s["path"] in forbid:
                print(f"FORBIDDEN overlap with own 14: {s['path']}", file=sys.stderr)
                return 3
            p = root / Path(s["path"])
            if s["new_file"]:
                raw = b""
                crlf = False
            else:
                raw = p.read_bytes()
                crlf = b"\r\n" in raw
            # EOL-lenient: normalize target to LF, apply (foreign diffs may be
            # LF-generated against CRLF worktrees), then restore the EOL style.
            text = raw.decode("utf-8").replace("\r\n", "\n")
            base_lines = text.splitlines(keepends=True)
            got = apply_to_lines(base_lines, s["hunks"], s["path"])
            out = "".join(got)
            if crlf:
                out = out.replace("\n", "\r\n").replace("\r\r\n", "\r\n")
            data = out.encode("utf-8")
            p.write_bytes(data)
            report["results"].append(
                {"path": s["path"], "applied": True, "sha": digest(data), "crlf_restored": crlf}
            )
        print(json.dumps(report, indent=2))
        return 0

    raise SystemExit("mode must be verify|apply")


if __name__ == "__main__":
    raise SystemExit(main())
