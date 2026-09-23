"""I-07-C before/after no-mutation witness.

  python snapshot.py before   -> evidence/snapshot_before.json
  python snapshot.py after    -> evidence/snapshot_after.json (+ diff verdict)
  python snapshot.py iso      -> evidence/iso_final.json (isolated trees)

Covers: product anchor hashes, the 3 manifest samples (raw+sidecar, full sha),
production catalog identity (size+mtime; a full sha256 of a 49.7GB file is not
feasible and is recorded as such), and a manifest of every real external root
(file count/total bytes/max mtime; full sha only when the root is small).
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from i07c_common import (ATT, CASES, CW, EVID, FF, MANIFEST, PROD_CATALOG,
                         PROD_CONFIG, RF, read_json, samples, sha256_file,
                         write_json)

ANCHORS = [
    CW / "src/company_wiki/source_catalog/adapter_dispatch.py",
    CW / "src/company_wiki/source_catalog/adapters/registry.py",
    CW / "src/company_wiki/source_catalog/adapters/sidecar.py",
    CW / "src/company_wiki/source_catalog/adapters/dayu.py",
    CW / "src/company_wiki/source_catalog/adapters/company_raw.py",
    CW / "src/company_wiki/source_catalog/config.py",
    CW / "src/company_wiki/source_catalog/scanner.py",
    CW / "src/company_wiki/source_catalog/cli.py",
    CW / "src/company_wiki/source_catalog/resolver.py",
    CW / "src/company_wiki/source_catalog/store.py",
    CW / "src/company_wiki/source_catalog/admission.py",
    CW / "src/company_wiki/source_contract/source_manifest.py",
    PROD_CONFIG,
    RF / "scripts/source_preparation.py",
    RF / "scripts/revenue_forecast.py",
    FF / "scripts/fetch_filing.py",
]

REAL_ROOTS = [
    CW / "companies",
    CW / "future_lake",
    Path(r"C:\Users\郑曾波\Projects\dayu-agent\workspace\portfolio"),
    Path(r"C:\Users\郑曾波\Dropbox\Stock"),
]

SMALL_ROOT_FULL_SHA_LIMIT = 10 * 1024 * 1024  # full sha only for roots <= 10 MB


def anchor_table() -> dict:
    table = {}
    for path in ANCHORS:
        key = str(path)
        if path.is_file():
            table[key] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        else:
            table[key] = {"missing": True}
    return table


def sample_table() -> dict:
    table = {}
    for s in samples():
        for kind in ("raw", "sidecar"):
            path = s[kind]
            rec = {"path": str(path), "manifest_pin": s["raw_sha256"] if kind == "raw" else None}
            if path.is_file():
                rec.update({"bytes": path.stat().st_size, "sha256": sha256_file(path)})
            else:
                rec["missing"] = True
            table[f"{s['id']}:{kind}"] = rec
    return table


def root_table() -> dict:
    table = {}
    for root in REAL_ROOTS:
        key = str(root)
        if not root.is_dir():
            table[key] = {"exists": False}
            continue
        count = 0
        total = 0
        max_mtime = 0.0
        small_files = []
        for p in root.rglob("*"):
            if p.is_file():
                count += 1
                st = p.stat()
                total += st.st_size
                max_mtime = max(max_mtime, st.st_mtime)
                if total <= SMALL_ROOT_FULL_SHA_LIMIT:
                    small_files.append(p)
        rec = {"exists": True, "file_count": count, "total_bytes": total,
               "max_mtime": max_mtime,
               "full_sha_policy": "hashed" if total <= SMALL_ROOT_FULL_SHA_LIMIT
                                  else "NOT hashed (size: count+bytes+mtime manifest instead)"}
        if total <= SMALL_ROOT_FULL_SHA_LIMIT:
            rec["files"] = {str(p.relative_to(root)): sha256_file(p)
                            for p in sorted(small_files)}
        table[key] = rec
    return table


def prod_catalog_identity() -> dict:
    if not PROD_CATALOG.is_file():
        return {"exists": False}
    st = PROD_CATALOG.stat()
    return {"exists": True, "bytes": st.st_size, "mtime": st.st_mtime,
            "full_sha256": None,
            "why_no_full_sha": "production catalog is 49.7GB; identity = size+mtime "
                               "(read-only census, if run, uses mode=ro)"}


def take(tag: str) -> dict:
    return {"tag": tag,
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "anchors": anchor_table(),
            "samples": sample_table(),
            "real_external_roots": root_table(),
            "production_catalog": prod_catalog_identity()}


def diff(before: dict, after: dict) -> dict:
    def changed(a: dict, b: dict) -> list[str]:
        keys = sorted(set(a) | set(b))
        return [k for k in keys if a.get(k) != b.get(k)]

    return {
        "anchors_changed": changed(before["anchors"], after["anchors"]),
        "samples_changed": changed(before["samples"], after["samples"]),
        "real_roots_changed": changed(before["real_external_roots"],
                                      after["real_external_roots"]),
        "production_catalog_changed":
            before["production_catalog"] != after["production_catalog"],
    }


def iso_tree() -> dict:
    tree = {}
    if CASES.is_dir():
        for p in sorted(CASES.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(CASES))
                try:
                    tree[rel] = {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
                except OSError as exc:
                    tree[rel] = {"error": str(exc)}
    return {"cases_root": str(CASES), "file_count": len(tree), "files": tree}


def main() -> int:
    mode = sys.argv[1]
    if mode in ("before", "after"):
        snap = take(mode)
        out = EVID / f"snapshot_{mode}.json"
        write_json(out, snap)
        if mode == "after":
            before = read_json(EVID / "snapshot_before.json")
            verdict = diff(before, snap)
            verdict["no_mutation"] = (
                not verdict["anchors_changed"]
                and not verdict["samples_changed"]
                and not verdict["production_catalog_changed"]
            )
            write_json(EVID / "snapshot_verdict.json", verdict)
            print(f"written {out} verdict={verdict}")
        else:
            print(f"written {out} anchors={len(snap['anchors'])}")
        return 0
    if mode == "iso":
        payload = iso_tree()
        out = EVID / "iso_final.json"
        write_json(out, payload)
        print(f"written {out} files={payload['file_count']}")
        return 0
    print(f"unknown mode {mode!r}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
