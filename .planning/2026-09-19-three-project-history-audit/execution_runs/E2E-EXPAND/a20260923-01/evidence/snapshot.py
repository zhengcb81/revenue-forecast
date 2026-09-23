"""E2E-EXPAND protocol-level before/after snapshot (SNAP-01 / SNAP-02).

Independent cross-check of the runner's own baseline: real-data hashes,
production catalog STAT-ONLY (never opened), FF config listing, CW
storage-top listing, CW entity file listing, RF repo file listing.

(The PowerShell variant was abandoned: ConvertTo-Json in this host's pwsh is
pathologically slow — 10 strings took 20s. Recorded in decision.md.)

Usage: python snapshot.py <out.json>
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
EXCLUDE_DIRS = ("__pycache__", ".pytest_cache", ".runs")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    out = []
    for p in sorted(root.rglob("*")):
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            out.append(p.relative_to(root).as_posix())
    return sorted(out)


def main() -> int:
    out_path = Path(sys.argv[1])
    catl_raw = CW / ("companies/宁德时代/raw/financial_reports/annual/"
                     "2025-03-14_cninfo_1222806982_2024年年度报告.pdf")
    catl_side = Path(str(catl_raw) + ".source.json")
    targets = {
        "cw_catl_raw": catl_raw,
        "cw_catl_sidecar": catl_side,
        "cw_cn_master": CW / ".source_catalog/security_master/cn.json",
        "cw_hk_master": CW / ".source_catalog/security_master/hk.json",
        "ff_company_wiki_json": FF / "config/company_wiki.json",
    }
    # STAT-ONLY: this suite never opens the production catalog
    catalog_stat = {}
    for name in ("catalog.sqlite3", "catalog.sqlite3-wal",
                 "catalog.sqlite3-shm"):
        p = CW / ".source_catalog" / name
        if p.exists():
            st = p.stat()
            catalog_stat[name] = {"size": st.st_size,
                                  "mtime_ns": st.st_mtime_ns}
    payload = {
        "captured": datetime.now(timezone.utc).isoformat(),
        "hashes": {k: sha256(p) for k, p in targets.items()},
        "prod_catalog_stat": catalog_stat,
        "ff_config_files": rel_files(FF / "config"),
        "cw_storage_top": sorted(
            p.name for p in (CW / ".source_catalog").iterdir()),
        "cw_entity_files": rel_files(CW / "companies/宁德时代"),
        "rf_files": sorted(
            [f"{sub}/{rel}" for sub in ("scripts", "e2e", "tests")
             for rel in rel_files(RF / sub)]
            + [p.name for p in RF.iterdir() if p.is_file()]),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"written {out_path} rf_files={len(payload['rf_files'])} "
          f"cw_entity={len(payload['cw_entity_files'])} "
          f"cw_top={len(payload['cw_storage_top'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
