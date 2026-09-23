"""I-07-B: build the FROZEN provider-simulation fixtures (S-*-3 b/c arms).

Fixture identity is taken from each sample's frozen sidecar (the recorded
provenance of bytes already on disk) + the production raw path as the frozen
payload. Labelled simulated; C-level qualification only (scenario_matrix S-3).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
ATT = Path(__file__).resolve().parents[1]
OUT = ATT / "fixtures"

SAMPLES = {
    "CN-ZIJIN-2025": {
        "raw": CW / "companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
        "market": "CN", "provider": "cninfo", "provider_document_id": "1225023658",
        "fiscal_year": 2025, "filing_date": "2026-03-20", "entity": "紫金矿业",
        "title": "紫金矿业集团股份有限公司2025年年度报告",
        "mime_type": "application/pdf", "staged_name": "1225023658.pdf",
        "adapter_name": "stockinfo-cninfo", "adapter_version": "1.1.0",
        "language": "zh-CN",
        "source_url": "https://www.cninfo.com.cn/new/disclosure/detail?stockCode=601899&announcementId=1225023658",
        "retrieved_at": "2026-07-31T21:23:16Z",
    },
    "HK-XIAOMI-2025": {
        "raw": CW / "companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf",
        "market": "HK", "provider": "hkexnews", "provider_document_id": "12127452",
        "fiscal_year": 2025, "filing_date": "2026-04-28", "entity": "小米集團－Ｗ",
        "title": "小米集團－Ｗ 2025年度報告",
        "mime_type": "application/pdf", "staged_name": "12127452.pdf",
        "adapter_name": "dayu-hkex-cli", "adapter_version": "1.0.0",
        "language": "zh-HK",
        "source_url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/12127452.pdf",
        "retrieved_at": "2026-05-02T10:00:00Z",
    },
    "US-MSFT-2026": {
        "raw": CW / "companies/MICROSOFT CORP/raw/financial_reports/annual/2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
        "market": "US", "provider": "sec", "provider_document_id": "0001193125-26-323660",
        "fiscal_year": 2026, "filing_date": "2026-07-29", "entity": "MICROSOFT CORP",
        "title": "MICROSOFT CORP 10-K 2026-06-30",
        "mime_type": "text/html", "staged_name": "0001193125-26-323660.htm",
        "adapter_name": "dayu-sec-cli", "adapter_version": "1.0.0",
        "language": "en",
        "source_url": "https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/0001193125-26-323660.htm",
        "retrieved_at": "2026-07-31T12:00:00Z",
    },
}


def main() -> int:
    OUT.mkdir(exist_ok=True)
    made = {}
    for name, meta in SAMPLES.items():
        payload = dict(meta)
        payload["candidate_id"] = f"{meta['provider']}:{meta['provider_document_id']}"
        payload["frozen_raw_path"] = str(meta["raw"])
        payload["fixture_id"] = f"frozen-{name}-v1"
        payload["simulation_label"] = ("simulated_in_isolation — frozen provider fixture; "
                                       "NOT a live provider call (oracle R5/C5)")
        payload["byte_size"] = meta["raw"].stat().st_size
        payload.pop("raw")
        p = OUT / f"{name}.provider.json"
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        made[name] = {"path": str(p), "payload_bytes": payload["byte_size"],
                      "payload_exists": meta["raw"].is_file()}
    (OUT / "fixtures_manifest.json").write_text(
        json.dumps(made, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(made, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
