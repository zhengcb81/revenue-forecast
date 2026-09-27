#!/usr/bin/env python
"""I-10-A harness: read-only dependency evidence sweep (measurement, never derivation).

Hashes every frozen input and extracts, VERBATIM, the status fields of the
dependency evidence face:
  * I-00-B argv/cwd contract files
  * I-07-B a20260923-01 handoff/decision/review/reviewer_report (+sidecar pin)
  * M01..M31 a20260919-01 handoff.json + evidence/M*/qualification.json
  * the 3 source raws + their sidecars

Writes two JSON files under --out. Reads only; the only writes are those files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PLAN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit")
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")

INPUTS = {
    "PLAN/execution_v2/card_I-10-A.md": PLAN / "execution_v2/card_I-10-A.md",
    "PLAN/execution_v2/research_cards.md": PLAN / "execution_v2/research_cards.md",
    "PLAN/execution_v2/common_research_cards.md": PLAN / "execution_v2/common_research_cards.md",
    "PLAN/execution_v2/common_root_cards.md": PLAN / "execution_v2/common_root_cards.md",
    "PLAN/execution_v2/review_and_handoff.md": PLAN / "execution_v2/review_and_handoff.md",
    "PLAN/execution_v2/START_HERE.md": PLAN / "execution_v2/START_HERE.md",
    "PLAN/execution_v2/model_cards.md": PLAN / "execution_v2/model_cards.md",
    "PLAN/execution_v2/common_model_cards.md": PLAN / "execution_v2/common_model_cards.md",
    "PLAN/execution_v2/sample_manifest.json": PLAN / "execution_v2/sample_manifest.json",
    "PLAN/execution_v2/scenario_matrix.md": PLAN / "execution_v2/scenario_matrix.md",
    "PLAN/execution_runs/I-00-B/a20260919-01/binding.json": PLAN / "execution_runs/I-00-B/a20260919-01/binding.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/commands.json": PLAN / "execution_runs/I-00-B/a20260919-01/commands.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/anchor_refresh_20260923.json": PLAN / "execution_runs/I-00-B/a20260919-01/anchor_refresh_20260923.json",
    "PLAN/execution_runs/I-07-B/a20260923-01/handoff.json": PLAN / "execution_runs/I-07-B/a20260923-01/handoff.json",
    "PLAN/execution_runs/I-07-B/a20260923-01/decision.md": PLAN / "execution_runs/I-07-B/a20260923-01/decision.md",
    "PLAN/execution_runs/I-07-B/a20260923-01/review.md": PLAN / "execution_runs/I-07-B/a20260923-01/review.md",
    "PLAN/execution_runs/I-07-B/a20260923-01/reviewer_report.md": PLAN / "execution_runs/I-07-B/a20260923-01/reviewer_report.md",
    "PLAN/execution_runs/I-07-B/a20260923-01/reviewer_report.sha256": PLAN / "execution_runs/I-07-B/a20260923-01/reviewer_report.sha256",
    "RF/scripts/model_registry.py": RF / "scripts/model_registry.py",
    "RF/scripts/model_extensions.py": RF / "scripts/model_extensions.py",
    "RF/scripts/forecast/segments.py": RF / "scripts/forecast/segments.py",
    "RF/scripts/forecast/calc.py": RF / "scripts/forecast/calc.py",
    "RF/scripts/revenue_constraints.py": RF / "scripts/revenue_constraints.py",
}

SOURCES = {
    "CN-ZIJIN-2025": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
    "HK-XIAOMI-2025": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf",
    "US-MSFT-2026": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
}

FROZEN_MANIFEST = {
    "CN-ZIJIN-2025": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
    "HK-XIAOMI-2025": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
    "US-MSFT-2026": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
}


def sha256_of(path: Path) -> dict:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return {"sha256": h.hexdigest(), "bytes": n}


def try_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # recorded, never hidden
        return None, f"{type(exc).__name__}: {exc}"


def formula_state(qual: dict) -> str:
    formula = qual.get("formula") if isinstance(qual, dict) else None
    if isinstance(formula, dict):
        for key in ("status", "state"):
            if isinstance(formula.get(key), str):
                return formula[key]
    return "MISSING"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    input_hashes = {}
    for label, path in INPUTS.items():
        if not path.is_file():
            input_hashes[label] = {"missing": True, "path": str(path)}
            continue
        entry = sha256_of(path)
        entry["path"] = str(path)
        input_hashes[label] = entry

    sources = {}
    for sid, path in SOURCES.items():
        entry = sha256_of(path) if path.is_file() else {"missing": True}
        entry["path"] = str(path)
        entry["frozen_manifest_sha256"] = FROZEN_MANIFEST[sid]
        entry["matches_frozen_manifest"] = entry.get("sha256") == FROZEN_MANIFEST[sid]
        sidecar = Path(str(path) + ".source.json")
        if sidecar.is_file():
            entry["sidecar"] = sha256_of(sidecar)
            entry["sidecar"]["path"] = str(sidecar)
        sources[sid] = entry

    m_rows = []
    for i in range(1, 32):
        mid = f"M{i:02d}"
        base = PLAN / "execution_runs" / mid / "a20260919-01"
        row = {"card_id": mid, "attempt": "a20260919-01"}
        handoff = base / "handoff.json"
        qual = base / "evidence" / mid / "qualification.json"
        if handoff.is_file():
            row["handoff"] = sha256_of(handoff)
            row["handoff"]["path"] = str(handoff)
            parsed, err = try_json(handoff)
            row["handoff"]["status"] = parsed.get("status") if parsed else None
            row["handoff"]["model_id"] = parsed.get("model_id") if parsed else None
            if err:
                row["handoff"]["parse_error"] = err
        else:
            row["handoff"] = {"missing": True}
        if qual.is_file():
            row["qualification"] = sha256_of(qual)
            row["qualification"]["path"] = str(qual)
            parsed, err = try_json(qual)
            row["qualification"]["formula_state"] = formula_state(parsed) if parsed else None
            row["qualification"]["model_id"] = parsed.get("model_id") if parsed else None
            if parsed and isinstance(parsed.get("disclosure_adaptation"), dict):
                row["qualification"]["disclosure_adaptation_state"] = (
                    parsed["disclosure_adaptation"].get("status")
                    or parsed["disclosure_adaptation"].get("state")
                )
            if parsed and isinstance(parsed.get("accuracy"), dict):
                row["qualification"]["accuracy_state"] = (
                    parsed["accuracy"].get("status") or parsed["accuracy"].get("state")
                )
            if err:
                row["qualification"]["parse_error"] = err
        else:
            row["qualification"] = {"missing": True}
        m_rows.append(row)

    formula_states = [r.get("qualification", {}).get("formula_state") for r in m_rows]
    summary = {
        "card_count": len(m_rows),
        "formula_accepted_scoped_count": sum(1 for s in formula_states if s == "accepted_scoped"),
        "formula_other": {
            f"M{i+1:02d}": s for i, s in enumerate(formula_states) if s != "accepted_scoped"
        },
    }

    (out / "input_hashes.json").write_text(
        json.dumps({"inputs": input_hashes, "sources": sources}, ensure_ascii=False, indent=1)
        + "\n",
        encoding="utf-8",
    )
    (out / "m31_qualification_sweep.json").write_text(
        json.dumps({"summary": summary, "cards": m_rows}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    print(
        "sources_match=",
        {k: v["matches_frozen_manifest"] for k, v in sources.items()},
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
