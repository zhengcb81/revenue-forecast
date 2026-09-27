"""WC-6 step 2/3: pin live CW sources, carriers and the register; verify the
iso copy is byte-identical to the live pre-image (READ-ONLY: never writes CW).

argv: pin_sources.py <mode: before|after>
  before -> evidence/source_pins_before.json   (pins + iso==live proof)
  after  -> evidence/source_pins_after.json    (CW live must equal the before pins)
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
PLAN = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit"
)
I07C = PLAN / "execution_runs" / "I-07-C" / "a20260923-01"
ISO_CW = ATT / "iso" / "cw"

#: files this card may touch (iso copy only) + the contract carriers
KEY_SOURCES = [
    "src/company_wiki/source_catalog/adapter_dispatch.py",
    "src/company_wiki/source_catalog/scanner.py",
    "src/company_wiki/source_catalog/adapters/sidecar.py",
    "src/company_wiki/source_catalog/adapters/interface.py",
    "src/company_wiki/source_catalog/config.py",
    "src/company_wiki/source_catalog/store.py",
    "src/company_wiki/source_catalog/service.py",
]
CARRIERS = {
    "i07c_decision": I07C / "decision.md",
    "i07c_review": I07C / "review.md",
    "i07c_reviewer_report": I07C / "reviewer_report.md",
    "i07c_oracle": I07C / "oracle.md",
    "i07c_handoff": I07C / "handoff.json",
    "remediation_register": PLAN / "REMEDIATION_REGISTER.md",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


#: sub-trees this card copies into iso (src for the fix, tests for the family)
SUBTREES = ("src", "tests")
#: extra live files whose bytes must not move (product config / policy)
EXTRA_FILES = (
    "config/source_catalog.yaml",
    "config/source_acquisition.yaml",
    "config/source_catalog_worker.yaml",
)


def manifest(root: Path) -> dict[str, dict]:
    """sha256 manifest of <root>/<subtree>/**/*.{py,json,yaml,ini} — bounded:
    only the two copied sub-trees, never the whole repo (which holds a .venv)."""
    out: dict[str, dict] = {}
    for sub in SUBTREES:
        base = root / sub
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            rel = path.relative_to(root).as_posix()
            out[rel] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    for rel in EXTRA_FILES:
        path = root / rel
        if path.is_file():
            out[rel] = {"sha256": sha256(path), "bytes": path.stat().st_size}
    return out


def main() -> int:
    mode = sys.argv[1]
    live = manifest(CW)
    iso = manifest(ISO_CW)
    mismatched = sorted(
        rel for rel, meta in live.items()
        if rel not in iso or iso[rel]["sha256"] != meta["sha256"]
    )
    extra = sorted(rel for rel in iso if rel not in live)
    evidence = {
        "mode": mode,
        "cw_root": str(CW),
        "iso_cw_root": str(ISO_CW),
        "live_file_count": len(live),
        "iso_file_count": len(iso),
        "iso_equals_live": mismatched == [] and extra == [],
        "iso_vs_live_mismatched": mismatched,
        "iso_vs_live_iso_only": extra,
        "key_sources": {
            rel: {
                "sha256": live[rel]["sha256"],
                "bytes": live[rel]["bytes"],
                "iso_sha256": iso.get(rel, {}).get("sha256"),
            }
            for rel in KEY_SOURCES
        },
        "carriers": {
            name: {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}
            for name, path in CARRIERS.items()
        },
        "manifest_sha256": hashlib.sha256(
            json.dumps(live, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest(),
    }
    out = ATT / "evidence" / f"source_pins_{mode}.json"
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in (
        "mode", "live_file_count", "iso_file_count", "iso_equals_live",
        "iso_vs_live_mismatched", "iso_vs_live_iso_only", "manifest_sha256")}, indent=2))
    if mode == "before" and not evidence["iso_equals_live"]:
        print("FATAL: iso copy is not byte-identical to the live pre-image")
        return 3
    if mode == "after":
        before = json.loads((ATT / "evidence" / "source_pins_before.json").read_text(encoding="utf-8"))
        drift = [
            rel for rel, meta in before["key_sources"].items()
            if live[rel]["sha256"] != meta["sha256"]
        ]
        evidence["live_key_sources_drifted_vs_before"] = drift
        out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"live_key_sources_drifted_vs_before": drift}, indent=2))
        if drift:
            print("FATAL: live CW sources drifted during this attempt")
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
