"""Analyze the canonical_writer preimage -> fixed transition.

Writes:
  rig/diff_asfound_to_fixed.patch   (unified diff)
  rig/diff_preimage_to_asfound.patch
  rig/diff_report.txt               (shas + hunk summary)
All paths are built from this file's own location (no Chinese literals typed
into shell command lines).
"""
from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load(name: str) -> bytes:
    return (OUT / name).read_bytes()


def as_lines(data: bytes) -> list[str]:
    # normalize line endings: fixed.py is CRLF on disk, the as-found copy is LF
    text = data.decode("utf-8").replace("\r\n", "\n")
    return text.splitlines(keepends=True)


report: list[str] = []
files = ["canonical_writer.preimage.py", "canonical_writer.preimage_asfound.py",
         "canonical_writer.fixed.py"]
raw: dict[str, bytes] = {}
for name in files:
    data = load(name)
    raw[name] = data
    crlf = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    lf = data.replace(b"\r\n", b"\n")
    report.append(f"{name}: bytes={len(data)} sha256={sha(data)}")
    report.append(f"    sha256(normalized-LF)={sha(lf)}")
    report.append(f"    sha256(normalized-CRLF)={sha(crlf)}")

live = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\canonical_writer.py")
live_data = live.read_bytes()
report.append(f"LIVE canonical_writer.py: bytes={len(live_data)} sha256={sha(live_data)}")
report.append(f"LIVE == fixed: {live_data == raw['canonical_writer.fixed.py']}")

EXPECTED_ASFOUND = "4BC653725FEBCC755E3A01AC48227A6B0799C4C262968356B356F8CB42D3C6BC"
af = raw["canonical_writer.preimage_asfound.py"]
report.append(f"preimage_asfound sha == EXPECTED(4BC65372..): {sha(af) == EXPECTED_ASFOUND}")


def diff(a_name: str, b_name: str, out_name: str) -> None:
    a = as_lines(raw[a_name])
    b = as_lines(raw[b_name])
    d = list(difflib.unified_diff(a, b, fromfile=a_name, tofile=b_name, n=3))
    (HERE / out_name).write_text("".join(d), encoding="utf-8")
    adds = sum(1 for line in d if line.startswith("+") and not line.startswith("+++"))
    dels = sum(1 for line in d if line.startswith("-") and not line.startswith("---"))
    hunks = sum(1 for line in d if line.startswith("@@"))
    report.append(f"diff {a_name} -> {b_name}: hunks={hunks} +{adds} -{dels} -> {out_name}")


diff("canonical_writer.preimage_asfound.py", "canonical_writer.fixed.py",
     "diff_asfound_to_fixed.patch")
diff("canonical_writer.preimage.py", "canonical_writer.preimage_asfound.py",
     "diff_preimage_to_asfound.patch")

# line-number anchors for each hunk of the main diff
a_lines = as_lines(raw["canonical_writer.preimage_asfound.py"])
b_lines = as_lines(raw["canonical_writer.fixed.py"])
sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
report.append("--- main diff opcodes (asfound -> fixed, line endings normalized) ---")
CAP = 60
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        report.append(f"[equal] asfound L{i1+1}-{i2} == fixed L{j1+1}-{j2} ({i2-i1} lines)")
        continue
    report.append(f"[{tag}] asfound L{i1+1}-{i2} -> fixed L{j1+1}-{j2} "
                  f"(-{i2-i1} +{j2-j1})")
    shown = 0
    for line in a_lines[i1:i2]:
        if shown >= CAP:
            report.append(f"    ... ({i2-i1-shown} more '-' lines)")
            break
        report.append("    - " + line.rstrip("\r\n"))
        shown += 1
    shown = 0
    for line in b_lines[j1:j2]:
        if shown >= CAP:
            report.append(f"    ... ({j2-j1-shown} more '+' lines)")
            break
        report.append("    + " + line.rstrip("\r\n"))
        shown += 1

(HERE / "diff_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("wrote diff_report.txt")
