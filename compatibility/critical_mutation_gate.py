"""FC-1005: critical-mutation kill gate.

The eight critical mutation classes from the Phase-10 spec must each have at
least one KILLED mutation with evidence.  Evidence sources (union):
  1. implementer receipts' ``mutation.details`` (keyword-matched per class);
  2. an explicit evidence file (``assurance/fc/FC-1005/critical_mutation_evidence.md``)
     carrying per-class records (used for mutations verified live, like the
     FC-1005 latest re-resolve kill).

Exit 0 only when every class has >= 1 evidence entry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = (ROOT, ROOT.parent / "company-wiki", ROOT.parent / "filing-fetch")

CLASSES = {
    "root_special_case": ["root_id", "root_kind", "root", "adapter"],
    "epoch_condition": ["epoch", "cohort", "flag"],
    "hash_check": ["hash", "sha256", "content_sha"],
    "download_authorization": ["download", "authoriz", "allow_download"],
    "latest_reresolve": ["re-resolve", "reresolve", "re_resolve", "latest"],
    "artifact_invalidation": ["artifact", "invalid", "binding", "bindable"],
    "zero_call_event": ["zero", "call", "journal", "producer_event", "side_effect"],
    "path_containment": ["path", "containment", "outside", "contain"],
}
EVIDENCE_FILE = ROOT / "assurance" / "fc" / "FC-1005" / "critical_mutation_evidence.md"


def collect_receipt_evidence() -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {k: [] for k in CLASSES}
    for root in SIBLINGS:
        for path in (root / "assurance" / "fc").glob("FC-*/11_*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            mut = payload.get("mutation") or {}
            if not mut.get("killed"):
                continue
            details = str(mut.get("details") or "") + " " + str(mut.get("id") or "")
            low = details.lower()
            fc = str(payload.get("fc_id") or path.parent.name)
            for cls, kws in CLASSES.items():
                if any(k in low for k in kws):
                    evidence[cls].append(f"{fc}: {details[:90]}")
    return evidence


def collect_file_evidence() -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {k: [] for k in CLASSES}
    if not EVIDENCE_FILE.is_file():
        return evidence
    text = EVIDENCE_FILE.read_text(encoding="utf-8")
    for cls in CLASSES:
        m = re.search(rf"## {re.escape(cls)}\b(.*?)(?=\n## |\Z)", text, re.S)
        if m and m.group(1).strip():
            evidence[cls].append(m.group(1).strip()[:90])
    return evidence


def gate_report() -> dict:
    receipt_ev = collect_receipt_evidence()
    file_ev = collect_file_evidence()
    gaps: list[str] = []
    matrix: dict[str, dict] = {}
    for cls in CLASSES:
        n = len(receipt_ev[cls]) + len(file_ev[cls])
        matrix[cls] = {
            "receipt_entries": len(receipt_ev[cls]),
            "file_entries": len(file_ev[cls]),
            "total": n,
        }
        if n == 0:
            gaps.append(cls)
    return {"gaps": gaps, "matrix": matrix}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = gate_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for cls, m in report["matrix"].items():
            status = "OK" if m["total"] else "MISSING"
            print(f"  {status:<8} {cls}: {m['total']} entries")
        if report["gaps"]:
            print("CRITICAL MUTATION GAPS:", ", ".join(report["gaps"]))
    return 1 if report["gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
