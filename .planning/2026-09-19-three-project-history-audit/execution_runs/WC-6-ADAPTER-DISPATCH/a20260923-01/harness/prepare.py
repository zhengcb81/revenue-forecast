"""WC-6 step 5 helper: (re)build ONE fresh isolated probe cell.

  python prepare.py <label>

Writes ONLY %TEMP%\\wc6\\cells\\probes\\cwroot and
<attempt>/evidence/<label>/{fixture_manifest.json,prepare.json}.

The four probe files/sidecars reproduce I-07-C's UNK-sidecar cell shapes
(I-07-C harness/build_iso.py:226-281), with this card's own synthetic entity
token (inputs/probe_fixture.json).  Rows are created later by the PRODUCT's
own `cli scan`; this builder only makes the schema (product initializer), the
config and the fixture tree.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from wc6_common import (ATT, CASES, EVID, copy_support_files, iso_schema,
                        load_fixture, q, sha256_file, tree_manifest, write_json)


def sc(payload: str, **over) -> str:
    """I-07-C build_iso._sc shape: schema_version first, then overrides."""
    body = {"schema_version": "1.0"}
    body.update(over)
    return json.dumps(body, ensure_ascii=False, indent=1)


def write_config(cwroot: Path, lake: Path) -> dict:
    fx = load_fixture()
    root = fx["root"]
    cfg_dir = cwroot / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = cfg_dir / "source_catalog.yaml"
    text = (
        'schema_version: "1.0"\n'
        + f"catalog_dir: {q(cwroot / '.source_catalog')}\n"
        + "reusable_root_kinds: [directory]\n"
        + "roots:\n"
        + f"  - root_id: {root['root_id']}\n"
        + f"    kind: {root['kind']}\n"
        + f"    adapter_id: {root['adapter_id']}\n"
        + f"    read_only: {str(root['read_only']).lower()}\n"
        + f"    reusable_for_filing: {str(root['reusable_for_filing']).lower()}\n"
        + f"    path: {q(lake)}\n"
        + f"    priority: {root['priority']}\n"
        + f"    privacy_class: {root['privacy_class']}\n"
    )
    cfg.write_text(text, encoding="utf-8")
    # G-4 carrier: same cell, unknown adapter_id -> CFG-01 refusal at load
    bad = cfg_dir / "source_catalog_bad_adapter.yaml"
    bad.write_text(
        'schema_version: "1.0"\n'
        + f"catalog_dir: {q(cwroot / '.source_catalog_bad')}\n"
        + "reusable_root_kinds: [directory]\n"
        + "roots:\n"
        + "  - root_id: wc6_bad_root\n"
        + "    kind: directory\n"
        + "    adapter_id: unknown_layout_v9\n"
        + f"    path: {q(lake)}\n"
        + "    priority: 10\n"
        + "    privacy_class: public\n",
        encoding="utf-8",
    )
    support = copy_support_files(cwroot)
    return {"config": str(cfg), "config_sha256": sha256_file(cfg),
            "bad_config": str(bad), "bad_config_sha256": sha256_file(bad),
            **support}


def build(cell: str) -> dict:
    # FIXED cell path for every arm: the outcome byte-compare (oracle §4) includes
    # locations.absolute_path, so all arms must rebuild the SAME path.  The label
    # only names the evidence directory; the cell itself is always <TEMP>\wc6\cells\probes.
    fx = load_fixture()
    case_dir = CASES / "probes"
    if case_dir.exists():
        shutil.rmtree(case_dir)
    cwroot = case_dir / "cwroot"
    cwroot.mkdir(parents=True)
    lake = cwroot / "lake"
    lake.mkdir()

    texts = fx["texts"]

    def put(name: str, text: str) -> Path:
        p = lake / name
        p.write_text(text, encoding="utf-8")
        return p

    # P1 clean: write payload first, then the sidecar hashing the FILE bytes
    # (I-07-C J2: write_text translates newlines on Windows)
    clean = put("clean_probe.txt", texts["clean_probe.txt"])
    clean.with_name(clean.name + ".source.json").write_text(
        sc("x",
           canonical_entity_id=fx["canonical_entity_id"], market=fx["market"],
           security_id=fx["security_id"], company_name=fx["company_name"],
           document_kind=fx["document_kind"], fiscal_year=fx["fiscal_year"],
           fiscal_period=fx["fiscal_period"], period_end=fx["period_end"],
           content_sha256=sha256_file(clean), provider=fx["provider"],
           provider_document_id=fx["provider_document_id"],
           filing_date=fx["filing_date"], source_title=fx["source_title"],
           source_url=fx["source_url"]),
        encoding="utf-8")

    # P2 no sidecar
    put("no_sidecar_probe.txt", texts["no_sidecar_probe.txt"])
    # P3 unparseable sidecar
    broken = put("broken_sidecar_probe.txt", texts["broken_sidecar_probe.txt"])
    broken.with_name(broken.name + ".source.json").write_text(
        fx["broken_sidecar_text"], encoding="utf-8")
    # P4 declared-hash mismatch + absolute canonical_path
    mismatch = put("mismatch_probe.txt", texts["mismatch_probe.txt"])
    mismatch.with_name(mismatch.name + ".source.json").write_text(
        sc("x", **fx["mismatch_sidecar_overrides"]), encoding="utf-8")

    cfg = write_config(cwroot, lake)
    schema = iso_schema(cwroot)
    fixture = tree_manifest(lake)
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabeled"
    out = EVID / label
    write_json(out / "fixture_manifest.json",
               {"label": label, "tree": fixture,
                "tree_sha256": sha256_file_of_tree(fixture)})
    write_json(out / "prepare.json",
               {"label": label, "cell": str(case_dir), "cwroot": str(cwroot),
                "config": cfg, "schema": schema,
                "probe_files": sorted(fixture)})
    print(json.dumps({"label": label, "probes": len(fixture),
                      "tree_sha256": sha256_file_of_tree(fixture)}))
    return {"label": label}


def sha256_file_of_tree(fixture: dict) -> str:
    import hashlib
    payload = json.dumps(fixture, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: prepare.py <label>", file=sys.stderr)
        raise SystemExit(2)
    sys.exit(0 if build(sys.argv[1]) else 1)
