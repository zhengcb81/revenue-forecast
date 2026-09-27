#!/usr/bin/env python
"""I-10-A harness: before/after hash snapshot (measurement only).

Hashes: the production product anchors, their isolated copies, the three source
raws + sidecars, and the frozen plan inputs. Used twice (before/ after) so the
product zero-change claim rests on measured hashes, not assertion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

PLAN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit")
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
ATT = PLAN / "execution_runs/I-10-A/a20260923-01"

PRODUCT_ANCHORS = {
    "RF/scripts/model_registry.py": RF / "scripts/model_registry.py",
    "RF/scripts/model_extensions.py": RF / "scripts/model_extensions.py",
    "RF/scripts/forecast/segments.py": RF / "scripts/forecast/segments.py",
    "RF/scripts/forecast/calc.py": RF / "scripts/forecast/calc.py",
    "RF/scripts/revenue_constraints.py": RF / "scripts/revenue_constraints.py",
}
ISO_COPIES = {
    "iso/rf/scripts/model_registry.py": ATT / "iso/rf/scripts/model_registry.py",
    "iso/rf/scripts/model_extensions.py": ATT / "iso/rf/scripts/model_extensions.py",
    "iso/rf/scripts/forecast/segments.py": ATT / "iso/rf/scripts/forecast/segments.py",
    "iso/rf/scripts/forecast/calc.py": ATT / "iso/rf/scripts/forecast/calc.py",
    "iso/rf/scripts/revenue_constraints.py": ATT / "iso/rf/scripts/revenue_constraints.py",
    "iso/rf/scripts/contracts/constants.py": ATT / "iso/rf/scripts/contracts/constants.py",
    "iso/rf/scripts/contracts/document.py": ATT / "iso/rf/scripts/contracts/document.py",
    "iso/rf/scripts/contracts/evidence.py": ATT / "iso/rf/scripts/contracts/evidence.py",
}
SOURCES = {
    "CN-ZIJIN-2025.raw": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
    "CN-ZIJIN-2025.sidecar": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf.source.json",
    "HK-XIAOMI-2025.raw": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf",
    "HK-XIAOMI-2025.sidecar": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf.source.json",
    "US-MSFT-2026.raw": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
    "US-MSFT-2026.sidecar": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm.source.json",
}
PLAN_INPUTS = {
    "PLAN/execution_v2/card_I-10-A.md": PLAN / "execution_v2/card_I-10-A.md",
    "PLAN/execution_v2/research_cards.md": PLAN / "execution_v2/research_cards.md",
    "PLAN/execution_v2/common_research_cards.md": PLAN / "execution_v2/common_research_cards.md",
    "PLAN/execution_v2/common_root_cards.md": PLAN / "execution_v2/common_root_cards.md",
    "PLAN/execution_v2/review_and_handoff.md": PLAN / "execution_v2/review_and_handoff.md",
    "PLAN/execution_v2/START_HERE.md": PLAN / "execution_v2/START_HERE.md",
    "PLAN/execution_v2/model_cards.md": PLAN / "execution_v2/model_cards.md",
    "PLAN/execution_v2/sample_manifest.json": PLAN / "execution_v2/sample_manifest.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/binding.json": PLAN / "execution_runs/I-00-B/a20260919-01/binding.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/commands.json": PLAN / "execution_runs/I-00-B/a20260919-01/commands.json",
    "PLAN/execution_runs/I-07-B/a20260923-01/handoff.json": PLAN / "execution_runs/I-07-B/a20260923-01/handoff.json",
    "PLAN/execution_runs/I-07-B/a20260923-01/reviewer_report.md": PLAN / "execution_runs/I-07-B/a20260923-01/reviewer_report.md",
}


def sha256_of(path: Path) -> dict:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return {"sha256": h.hexdigest(), "bytes": n, "mtime_ns": path.stat().st_mtime_ns}


def scan(group: dict) -> dict:
    out = {}
    for label, path in group.items():
        out[label] = sha256_of(path) if path.is_file() else {"missing": True, "path": str(path)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    payload = {
        "captured_at_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "product_anchors": scan(PRODUCT_ANCHORS),
        "iso_copies": scan(ISO_COPIES),
        "sources": scan(SOURCES),
        "plan_inputs": scan(PLAN_INPUTS),
    }
    iso_match = {}
    for key, iso_key in [
        ("RF/scripts/model_registry.py", "iso/rf/scripts/model_registry.py"),
        ("RF/scripts/model_extensions.py", "iso/rf/scripts/model_extensions.py"),
        ("RF/scripts/forecast/segments.py", "iso/rf/scripts/forecast/segments.py"),
        ("RF/scripts/forecast/calc.py", "iso/rf/scripts/forecast/calc.py"),
        ("RF/scripts/revenue_constraints.py", "iso/rf/scripts/revenue_constraints.py"),
    ]:
        a = payload["product_anchors"][key].get("sha256")
        b = payload["iso_copies"][iso_key].get("sha256")
        iso_match[key] = {"production": a, "iso": b, "identical": a == b}
    payload["iso_vs_production"] = iso_match
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
