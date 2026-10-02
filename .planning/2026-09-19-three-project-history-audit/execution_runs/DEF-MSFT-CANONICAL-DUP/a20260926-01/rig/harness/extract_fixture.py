#!/usr/bin/env python3
"""Extract the production fixture payload (request/candidate/receipt) from the
__095935f968b5 provenance sidecar in company-wiki (read-only), and copy the
small rig config/policy fixtures into rig/harness/fixture/."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = HERE.parent.parent
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RIGW = CARD / "rig" / "w"

BASE_NAME = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm"
SUFFIX_NAME = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30__095935f968b5.htm"

fixture = HERE / "fixture"
(fixture / "config").mkdir(parents=True, exist_ok=True)
(fixture / "source_catalog" / "security_master").mkdir(parents=True, exist_ok=True)

for name in ("source_catalog.yaml", "source_acquisition.yaml",
             "source_catalog_worker.yaml", "minimal_config.yaml"):
    shutil.copyfile(RIGW / "config" / name, fixture / "config" / name)

shutil.copyfile(RIGW / ".source_catalog" / "runtime_policy.json",
                fixture / "source_catalog" / "runtime_policy.json")
for name in ("cn.json", "hk.json", "us.json"):
    shutil.copyfile(RIGW / ".source_catalog" / "security_master" / name,
                    fixture / "source_catalog" / "security_master" / name)

sidecar = PROD / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual" / (
    SUFFIX_NAME + ".source.json"
)
payload = json.loads(sidecar.read_text(encoding="utf-8"))
out = {
    "source_sidecar": str(sidecar),
    "request": payload["request"],
    "candidate": payload["candidate"],
    "receipt": payload["receipt"],
}
(fixture / "fixture_payload.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
)

# also record which production bytes are used, for verification.json
def sha(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


annual = PROD / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
base_file = annual / BASE_NAME
suffix_file = annual / SUFFIX_NAME
staged_file = PROD / ".source_catalog" / "staging" / (
    "1eb6c299311836a2be1bf989e399c54ffa061513a532a9f5748ee742ab6d1838"
) / "msft-20260630.htm"
manifest = {
    "base_file": {"path": str(base_file), "sha256": sha(base_file),
                  "bytes": base_file.stat().st_size},
    "suffix_file": {"path": str(suffix_file), "sha256": sha(suffix_file),
                    "bytes": suffix_file.stat().st_size},
    "staged_bytes": {"path": str(staged_file), "sha256": sha(staged_file),
                     "bytes": staged_file.stat().st_size},
    "sidecar": str(sidecar),
}
(fixture / "source_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("fixture ready")
