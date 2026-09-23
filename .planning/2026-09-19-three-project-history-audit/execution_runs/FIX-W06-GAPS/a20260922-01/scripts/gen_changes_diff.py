"""Generate changes.diff (repo/attempt-prefixed exact hunks) for FIX-W06-GAPS."""
from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

A = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
         r"\2026-09-19-three-project-history-audit\execution_runs"
         r"\FIX-W06-GAPS\a20260922-01")

SECTIONS = [
    ("repo:revenue-forecast", "APPLIED (test-only surface, parent-authorized)", [
        ("tests/test_fc905b_trusted_receipt.py",
         A / "before" / "rf" / "test_fc905b_trusted_receipt.py",
         A / "iso" / "rf" / "test_fc905b_trusted_receipt.py"),
        ("tests/test_message_contract_pins.py", None,
         A / "iso" / "rf" / "test_message_contract_pins.py"),
    ]),
    ("repo:company-wiki", "PROPOSED ONLY — product source READ-ONLY, not applied", [
        ("src/company_wiki/source_catalog/prompt_injection.py",
         A / "before" / "cw" / "prompt_injection.py",
         A / "iso" / "pi_pkg" / "prompt_injection.py"),
        ("src/company_wiki/source_catalog/prompt_injection_guard.py",
         A / "before" / "cw" / "prompt_injection_guard.py",
         A / "iso" / "pi_pkg" / "prompt_injection_guard.py"),
        ("src/company_wiki/source_catalog/readiness_graph.py",
         A / "before" / "cw" / "readiness_graph.py",
         A / "iso" / "pi_pkg" / "readiness_graph.py"),
    ]),
    ("attempt:FIX-W06-GAPS/a20260922-01", "attempt-local copies (fix in COPIES)", [
        ("iso/candidate/processing_demand_store.py",
         A / "before" / "candidate" / "processing_demand_store.py",
         A / "iso" / "candidate" / "processing_demand_store.py"),
        ("iso/candidate/w06a_candidate_patch.py",
         A / "before" / "candidate" / "w06a_candidate_patch.py",
         A / "iso" / "candidate" / "w06a_candidate_patch.py"),
        ("iso/candidate/w06a_apply_candidate.py",
         A / "before" / "candidate" / "w06a_apply_candidate.py",
         A / "iso" / "candidate" / "w06a_apply_candidate.py"),
        ("iso/candidate/test_candidate_message_pins.py", None,
         A / "iso" / "candidate" / "test_candidate_message_pins.py"),
    ]),
]

out: list[str] = [
    "# changes.diff — FIX-W06-GAPS a20260922-01 (exact unified hunks)",
    "# scope: repair ONLY; originals pinned in before/ (byte-identical) and in",
    "# before/MANIFEST.json.  Production source (revenue-forecast scripts/,",
    "# company-wiki src/) untouched — the company-wiki hunks below are the",
    "# PROPOSED product-side application of the iso fixes (reviewer applies).",
    "",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


for header, note, pairs in SECTIONS:
    out.append(f"## {header}  [{note}]")
    out.append("")
    for label, before, after in pairs:
        out.append(f"### {label}")
        out.append(f"# after sha256: {sha(after)}")
        if before is not None:
            out.append(f"# before sha256: {sha(before)}")
        out.append("")
        b_lines = before.read_text(encoding="utf-8").splitlines(keepends=True) if before else []
        a_lines = after.read_text(encoding="utf-8").splitlines(keepends=True)
        diff = difflib.unified_diff(
            b_lines, a_lines,
            fromfile=f"a/{label}" if before else "/dev/null",
            tofile=f"b/{label}", n=3)
        out.extend(line.rstrip("\n") for line in diff)
        out.append("")

(A / "changes.diff").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"changes.diff written: {len(out)} lines")
