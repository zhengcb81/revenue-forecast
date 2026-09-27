"""Summarise the A05 read-only manifest run for the B09/B.AR record (read-only)."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = json.loads((HERE / "a05-readonly-manifest-run.json").read_text(encoding="utf-8"))


def stdout_of(entry_id: str) -> str:
    for item in RUN["results"]:
        if item["id"] == entry_id and item.get("stdout_file"):
            return (HERE / item["stdout_file"]).read_text(encoding="utf-8")
    return ""


lines: list[str] = []
lines.append(f"catalog status: {stdout_of('A05-1').strip()}")
lines.append(f"size-report: {stdout_of('A06-1').strip()[:400]}")
lines.append(f"runtime-policy: {stdout_of('A06-2').strip()[:400]}")

filings = json.loads(stdout_of("A05-2b"))
lines.append("")
lines.append(f"filing candidates (annual_report): {len(filings)}")
for item in filings[:12]:
    path = str(item.get("canonical_path") or "")
    lines.append(f"  {item.get('document_id', '')[-24:]}  {item.get('document_kind')}  "
                 f"bytes={item.get('byte_size')}  ...{path[-90:]}")

evidence = stdout_of("A05-4b")
lines.append("")
lines.append(f"evidence-list output bytes: {len(evidence)}")
lines.append(evidence[:1200])

sections_attempts = []
for item in RUN["results"]:
    if item["id"] in ("A05-5", "A05-5b"):
        for attempt in item.get("attempts", []):
            sections_attempts.append(attempt.get("stderr_tail", "")[:120])
lines.append("")
lines.append(f"sections-list attempts: {len(sections_attempts)}; "
             f"distinct errors: {sorted(set(sections_attempts))[:3]}")

out = HERE / "b09-bar-inputs.txt"
out.write_text("\n".join(lines), encoding="utf-8", newline="")
print(f"wrote {out} ({len(lines)} lines)")
