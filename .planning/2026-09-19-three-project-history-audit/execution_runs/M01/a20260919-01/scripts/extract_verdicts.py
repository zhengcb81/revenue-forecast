"""Extract the four paste-ready verdict blocks from the point-review report.

The report is the reviewer's artefact; this script copies the M01-M04 blocks
verbatim out of section 12 so that nothing is transcribed by hand (and therefore
nothing can be distorted in transcription).

ASCII-only stdout.
"""

from __future__ import annotations

import io
import os
import re

REPORT = r"C:\Users\郑曾波\AppData\Local\Temp\m0104-review-20260920-035508\REPORT.md"
PLAN = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast", ".planning",
                    "2026-09-19-three-project-history-audit")
OUT = os.path.join(PLAN, "execution_runs", "_r4_inputs")

FENCE = "`" * 3


def main():
    text = io.open(REPORT, encoding="utf-8").read()
    s12 = text[text.index("## 12."):text.index("## 13.")]
    pattern = re.compile(r"### (M0\d) \u7528\s*\n\s*" + FENCE + r"markdown\n(.*?)\n" + FENCE, re.S)
    blocks = pattern.findall(s12)
    print("report bytes:", len(text.encode("utf-8")))
    print("blocks found:", [c for c, _ in blocks])
    os.makedirs(OUT, exist_ok=True)
    for card, body in blocks:
        path = os.path.join(OUT, "verdict_%s.md" % card)
        io.open(path, "w", encoding="utf-8", newline="\n").write(body.rstrip("\n") + "\n")
        lines = body.strip().split("\n")
        print("  %s: %d chars, %d lines, first=%r" % (card, len(body), len(lines), lines[0][:46]))
        print("      last=%r" % lines[-1][:70])
    print("wrote to", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
