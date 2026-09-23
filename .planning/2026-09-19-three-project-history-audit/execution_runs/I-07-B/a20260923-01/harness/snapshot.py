"""I-07-B snapshot tool: before/after state capture.

Modes:
  python snapshot.py before   -> evidence/snapshot_before.json
  python snapshot.py after    -> evidence/snapshot_after.json
  python snapshot.py iso      -> evidence/iso_state.json

Captures (all read-only):
  * sha256 of the frozen production/source anchors (I-00-B anchor table + the
    chain entry files actually used by this card)
  * production catalog identity (bytes, mtime, -wal/-shm presence) — never opened
    for write; stat only
  * production raw/sidecar/derived-artifact hashes of the three frozen samples
  * production config hashes
  * (iso mode) the isolated tree: file list + hashes + isolated catalog row counts
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
PROD_CATALOG = CW / ".source_catalog" / "catalog.sqlite3"
ATT = Path(__file__).resolve().parents[1]

ANCHORS = {
    "RF/scripts/source_preparation.py": RF / "scripts" / "source_preparation.py",
    "RF/scripts/filing_fetch_client.py": RF / "scripts" / "filing_fetch_client.py",
    "RF/scripts/company_wiki_source.py": RF / "scripts" / "company_wiki_source.py",
    "RF/scripts/revenue_forecast.py": RF / "scripts" / "revenue_forecast.py",
    "RF/scripts/processing_demand.py": RF / "scripts" / "processing_demand.py",
    "RF/config/company_wiki.json": RF / "config" / "company_wiki.json",
    "RF/config/filing_fetch.json": RF / "config" / "filing_fetch.json",
    "FF/scripts/fetch_filing.py": FF / "scripts" / "fetch_filing.py",
    "CW/src/company_wiki/source_catalog/cli.py": CW / "src/company_wiki/source_catalog/cli.py",
    "CW/src/company_wiki/source_catalog/service.py": CW / "src/company_wiki/source_catalog/service.py",
    "CW/src/company_wiki/source_catalog/store.py": CW / "src/company_wiki/source_catalog/store.py",
    "CW/src/company_wiki/source_catalog/scanner.py": CW / "src/company_wiki/source_catalog/scanner.py",
    "CW/src/company_wiki/source_catalog/resolver.py": CW / "src/company_wiki/source_catalog/resolver.py",
    "CW/src/company_wiki/source_catalog/worker.py": CW / "src/company_wiki/source_catalog/worker.py",
    "CW/src/company_wiki/source_catalog/config.py": CW / "src/company_wiki/source_catalog/config.py",
    "CW/src/company_wiki/source_catalog/prompt_injection.py": CW / "src/company_wiki/source_catalog/prompt_injection.py",
    "CW/src/company_wiki/source_catalog/security_identity.py": CW / "src/company_wiki/source_catalog/security_identity.py",
    "CW/src/company_wiki/source_catalog/acquisition.py": CW / "src/company_wiki/source_catalog/acquisition.py",
    "CW/config/source_catalog.yaml": CW / "config" / "source_catalog.yaml",
    "CW/config/source_acquisition.yaml": CW / "config" / "source_acquisition.yaml",
    "PLAN/execution_v2/card_I-07-B.md": ATT.parents[1] / "execution_v2" / "card_I-07-B.md",
    "PLAN/execution_v2/scenario_matrix.md": ATT.parents[1] / "execution_v2" / "scenario_matrix.md",
    "PLAN/execution_v2/sample_manifest.json": ATT.parents[1] / "execution_v2" / "sample_manifest.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/commands.json": ATT.parents[1] / "execution_runs/I-00-B/a20260919-01/commands.json",
    "PLAN/execution_runs/I-00-B/a20260919-01/binding.json": ATT.parents[1] / "execution_runs/I-00-B/a20260919-01/binding.json",
    "PLAN/execution_runs/I-07-A/a20260919-01/after/state_matrix.json": ATT.parents[1] / "execution_runs/I-07-A/a20260919-01/after/state_matrix.json",
}

SAMPLES = {
    "CN-ZIJIN-2025": {
        "raw": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
        "sidecar": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf.source.json",
        "derived": [
            CW / ".source_catalog/derived/01/01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d/normalized.md",
            CW / ".source_catalog/derived/01/01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d/summary.md",
        ],
        "raw_sha256": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "sidecar_sha256": "7f7570fe6565698f1962a9301b5e47dbe76fb3a5e8dfa5663a48fc3793bf20b5",
        "bytes": 79925886,
    },
    "HK-XIAOMI-2025": {
        "raw": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf",
        "sidecar": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf.source.json",
        "derived": [],
        "raw_sha256": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "sidecar_sha256": "8228741d299164380bde36a83df1267b59e9b46721bea7d8efee857aeeb8da71",
        "bytes": 4405561,
    },
    "US-MSFT-2026": {
        "raw": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
        "sidecar": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm.source.json",
        "derived": [],
        "raw_sha256": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "sidecar_sha256": "1cbfb1a2ed055fa199806a5d01b96f325396506c472ebfabb80474ec712abb6a",
        "bytes": 8585615,
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_ident(path: Path) -> dict:
    try:
        st = path.stat()
    except OSError as exc:
        return {"error": str(exc)}
    return {"bytes": st.st_size, "mtime_ns": st.st_mtime_ns,
            "mtime_iso": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}


def anchors() -> dict:
    out = {}
    for key, path in ANCHORS.items():
        if path.is_file():
            out[key] = {"path": str(path), "sha256": sha256_file(path), **stat_ident(path)}
        else:
            out[key] = {"path": str(path), "missing": True}
    return out


def samples() -> dict:
    out = {}
    for name, meta in SAMPLES.items():
        entry = {"raw": str(meta["raw"]), "sidecar": str(meta["sidecar"])}
        for field in ("raw", "sidecar"):
            p = Path(meta[field])
            entry[field + "_exists"] = p.is_file()
            if p.is_file():
                entry[field + "_sha256"] = sha256_file(p)
                entry[field + "_bytes"] = p.stat().st_size
        entry["raw_sha256_expected"] = meta["raw_sha256"]
        entry["sidecar_sha256_expected"] = meta["sidecar_sha256"]
        entry["raw_match"] = entry.get("raw_sha256") == meta["raw_sha256"]
        entry["sidecar_match"] = entry.get("sidecar_sha256") == meta["sidecar_sha256"]
        entry["derived"] = [
            {"path": str(d), "exists": d.is_file(),
             "sha256": sha256_file(d) if d.is_file() else None}
            for d in meta["derived"]
        ]
        out[name] = entry
    return out


def catalog_ident() -> dict:
    return {
        "path": str(PROD_CATALOG),
        **stat_ident(PROD_CATALOG),
        "wal": stat_ident(Path(str(PROD_CATALOG) + "-wal")),
        "shm": stat_ident(Path(str(PROD_CATALOG) + "-shm")),
        "access": "stat only in this tool (no open); query-only probes are separate and read-only",
    }


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    out_path = ATT / "evidence" / f"snapshot_{mode}.json"
    payload = {
        "mode": mode,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "anchors": anchors(),
        "production_catalog": catalog_ident(),
        "production_samples": samples(),
        "production_porcelain_note": "git is NOT run by this card (no-git command rule)",
    }
    if mode == "iso":
        import os
        iso = ATT / "iso"
        temp_cases = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07b" / "cases"
        files = []
        for root in (iso, temp_cases):
            if not root.exists():
                continue
            for p in sorted(root.rglob("*")):
                if p.is_file() and "venv" not in p.parts:
                    files.append({"root": str(root),
                                  "rel": str(p.relative_to(root)),
                                  "bytes": p.stat().st_size,
                                  "sha256": sha256_file(p)})
        payload["iso_files"] = files
        payload["temp_cases_root"] = str(temp_cases)
        cat = ATT / "iso" / "base" / "cwroot" / ".source_catalog" / "catalog.sqlite3"
        if cat.is_file():
            con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
            con.execute("PRAGMA query_only=ON")
            tabs = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            payload["iso_catalog"] = {
                "path": str(cat), **stat_ident(cat), "tables": tabs,
                "rowcounts": {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                              for t in tabs},
                "table_count": len(tabs),
            }
            con.close()
        payload["iso_catalog_note"] = ("production-isomorphic requirement: I-07-A "
                                       "prohibition — iso table set must match production's 18")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"written": str(out_path), "mode": mode,
                      "anchor_count": len(payload["anchors"]),
                      "raw_all_match": all(v.get("raw_match") for v in payload["production_samples"].values()),
                      "sidecar_all_match": all(v.get("sidecar_match") for v in payload["production_samples"].values())},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
