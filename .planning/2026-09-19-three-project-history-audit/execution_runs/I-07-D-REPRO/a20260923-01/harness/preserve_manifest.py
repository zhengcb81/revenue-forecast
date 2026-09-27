"""I-07-D-REPRO preservation manifest (D3 fix, §72/REM-93 retention rule).

Records (sha256, version-domain, preservation-site) triplets for every file copied
from the %TEMP% scratch tree into this attempt's preservation root, and asserts the
byte-link to the frozen identity constants (raw ffd73376… / sidecar 8228741d…).

Usage: python preserve_manifest.py <CASE>
Reads : <ATT>/evidence/preserved/temp/i07d/cases/<CASE>/**  (already copied)
Writes: <ATT>/evidence/raws_manifest.json  (one entry set per case, idempotent)

This tool is NEW in this attempt (the only new harness file); it does not touch the
reused harness or any product tree.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
PRESERVED_ROOT = ATT / "evidence" / "preserved" / "temp" / "i07d" / "cases"
MANIFEST = ATT / "evidence" / "raws_manifest.json"
VERSION_DOMAIN = ("re-run a20260923-01 of I-07-D F02/F03/F04 judged semantics "
                  "(I-07-D attempt a20260923-01 READ-ONLY reference)")
EXPECT_RAW = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
EXPECT_SIDECAR = "8228741d299164380bde36a83df1267b59e9b46721bea7d8efee857aeeb8da71"


def sha256_file(path: Path) -> str:
    # Windows LongPathsEnabled=0 on this host: attempt path + canonical raw names
    # exceed MAX_PATH 260, so byte access goes through the \\?\ prefix (plain
    # read_bytes/is_file fail with FileNotFoundError past 260 — observed 2026-09-24).
    lp = path if str(path).startswith("\\\\?\\") else Path("\\\\?\\" + str(path))
    h = hashlib.sha256()
    with lp.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_file_lp(path: Path) -> bool:
    lp = path if str(path).startswith("\\\\?\\") else Path("\\\\?\\" + str(path))
    return lp.is_file()


def size_lp(path: Path) -> int:
    lp = path if str(path).startswith("\\\\?\\") else Path("\\\\?\\" + str(path))
    return lp.stat().st_size


def main() -> int:
    case = sys.argv[1]
    root = PRESERVED_ROOT / case
    if not root.is_dir():
        print(json.dumps({"case": case, "error": "preserved root missing", "root": str(root)}))
        return 1
    entries = []
    raw_hits, sidecar_hits = [], []
    lp_root = Path("\\\\?\\" + str(root))
    for p in sorted(lp_root.rglob("*")):
        if not p.is_file():
            continue
        plain = Path(str(p)[4:] if str(p).startswith("\\\\?\\") else str(p))
        digest = sha256_file(plain)
        rel = str(p.relative_to(lp_root))
        entries.append({
            "sha256": digest,
            "version_domain": VERSION_DOMAIN,
            "preservation_site": str(plain.relative_to(ATT)).replace("\\", "/"),
            "rel_in_cell": rel,
            "bytes": p.stat().st_size,
        })
        if digest == EXPECT_RAW:
            raw_hits.append(rel)
        if digest == EXPECT_SIDECAR:
            sidecar_hits.append(rel)
    doc = {}
    if MANIFEST.exists():
        doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    doc.setdefault("policy", "REMEDIATION_REGISTER §72(3) + REM-93: judged-run raw preserved "
                             "in attempt/evidence; %TEMP% scratch only; triplet "
                             "(sha256, version-domain, preservation-site) per lesson-11")
    doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    doc["cases"] = doc.get("cases", {})
    doc["cases"][case] = {
        "preserved_at": datetime.now(timezone.utc).isoformat(),
        "preserved_root": str(root.relative_to(ATT)).replace("\\", "/"),
        "file_count": len(entries),
        "files": entries,
        "raw_byte_link": {
            "expected_raw_sha256": EXPECT_RAW,
            "matches_in_preserved": raw_hits,
            "expected_sidecar_sha256": EXPECT_SIDECAR if case in ("F02", "F03") else None,
            "sidecar_matches_in_preserved": sidecar_hits,
            "sidecar_expectation_note": (
                "F02/F03 (state2): sidecar is the production-copied .source.json, frozen "
                "sha 8228741d…; F04 (state3): the .source.json is PRODUCT-GENERATED import "
                "provenance written by canonical_writer at raw commit (I-07-D pinned its "
                "EXISTENCE (provenance_committed) and asserted only the raw content sha — "
                "the provenance bytes are a different artifact from the state2 sidecar and "
                "have no frozen hash; its sha is recorded in files[] as its own triplet)"),
            "link_to_I-07-D_transcription": "I-07-D decision/verdict record raw sha "
                                            "ffd73376…2da7c == preserved bytes here",
        },
    }
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ok = bool(raw_hits) and (bool(sidecar_hits) or case not in ("F02", "F03"))
    print(json.dumps({"case": case, "files": len(entries), "raw_found": raw_hits,
                      "sidecar_found": sidecar_hits, "byte_link_ok": ok}, ensure_ascii=False))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
