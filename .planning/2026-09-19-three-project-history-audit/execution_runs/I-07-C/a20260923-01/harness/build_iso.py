"""I-07-C isolation builder: ONE isolated company-wiki root per cell.

  python build_iso.py <cell>

Writes ONLY under %TEMP%\\i07c\\cells\\<cell>\\cwroot and
<attempt>/evidence/iso_initial/<cell>.json.

Rows in every isolated catalog are created by the PRODUCT's own scan later;
this builder only creates the schema (product initializer), the config, the
root directories and the ASSETS. Assets are either (a) byte-identical copies of
manifest-pinned samples, or (b) clearly labelled synthetic isolated payloads
for the fifth-root cell (inputs/fifth_root_company.json).
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from i07c_common import (AS_OF, ATT, CASES, CELLS, EVID, INPUTS, copy_checked,
                         copy_support_files, iso_schema, read_json,
                         resolve_entity_from_sidecar, sample_by_market,
                         sample_smallest, sha256_file, write_json)

HEADER = 'schema_version: "1.0"\n'


def q(path: Path) -> str:
    """Single-quoted YAML scalar: backslashes are literal."""
    return "'" + str(path).replace("'", "''") + "'"


def write_config(cwroot: Path, roots_yaml: str, reusable: str) -> dict:
    cfg_dir = cwroot / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = cfg_dir / "source_catalog.yaml"
    text = (HEADER
            + f"catalog_dir: {q(cwroot / '.source_catalog')}\n"
            + f"reusable_root_kinds: [{reusable}]\n"
            + "roots:\n" + roots_yaml)
    cfg.write_text(text, encoding="utf-8")
    support = copy_support_files(cwroot)
    return {"config": str(cfg), "config_sha256": sha256_file(cfg), **support}


def new_cwroot(cell: str) -> Path:
    case_dir = CASES / cell
    if case_dir.exists():
        shutil.rmtree(case_dir)
    cwroot = case_dir / "cwroot"
    cwroot.mkdir(parents=True)
    return cwroot


def rel_request(cell: str, entity: str, kind: str = "annual_report") -> dict:
    req = {"requests": [{"entity": entity, "document_kind": kind,
                         "as_of_date": AS_OF}]}
    write_json(CASES / cell / "resolve_request.json", req)
    return req


def copy_sample_into(sample: dict, cwroot: Path, roots: list[str]) -> dict:
    """Copy raw+sidecar into each company_raw root dir: <root>/<entity>/raw/..."""
    recs = []
    for root_dir in roots:
        base = (cwroot / root_dir / sample["entity_dir"] / "raw"
                / "financial_reports" / sample["kind_dir"])
        recs.append(copy_checked(sample["raw"], base / sample["file_name"]))
        recs.append(copy_checked(sample["sidecar"],
                                 base / (sample["file_name"] + ".source.json")))
    return {"copies": recs,
            "all_match": all(r["match"] for r in recs),
            "manifest_raw_sha256": sample["raw_sha256"]}


def iso_snapshot(case_dir: Path) -> list[dict]:
    out = []
    for p in sorted(case_dir.rglob("*")):
        if p.is_file():
            out.append({"rel": str(p.relative_to(case_dir)),
                        "bytes": p.stat().st_size, "sha256": sha256_file(p)})
    return out


# ---------------------------------------------------------------- cell builders

def build_x04(cwroot: Path) -> dict:
    """Clause 1: TWO company_raw roots holding byte-identical filing bytes."""
    sample = sample_smallest()
    roots = ("companies", "companies_mirror")
    roots_yaml = ""
    for idx, (name, prio) in enumerate((("companies_root_a", 10),
                                        ("companies_root_b", 20))):
        roots_yaml += (f"  - root_id: {name}\n"
                       f"    kind: company_raw\n"
                       f"    path: {q(cwroot / roots[idx])}\n"
                       f"    priority: {prio}\n"
                       f"    privacy_class: public\n")
    for r in roots:
        (cwroot / r).mkdir(parents=True, exist_ok=True)
    cfg = write_config(cwroot, roots_yaml, "company_raw")
    assets = copy_sample_into(sample, cwroot, list(roots))
    entity = resolve_entity_from_sidecar(
        cwroot / "companies" / sample["entity_dir"] / "raw" / "financial_reports"
        / sample["kind_dir"] / (sample["file_name"] + ".source.json"),
        fallback=sample["entity_dir"])
    req = rel_request("X04-multiroot", entity)
    return {"sample": {k: str(v) if isinstance(v, Path) else v for k, v in sample.items()},
            "config": cfg, "assets": assets, "resolve_request": req,
            "construction": "two kind=company_raw roots, byte-identical raw+sidecar copies"}


def build_x05(cwroot: Path) -> dict:
    """Clause 2: four production-shaped roots + a fifth, hitherto-unnamed
    isomorphic root carrying a non-fixture company (data file input)."""
    data = read_json(INPUTS / "fifth_root_company.json")
    root_id = data["fifth_root_id"]
    dirs = {"company_raw": "companies", "dayu_portfolio": "dayu_portfolio",
            "dropbox_stock": "dropbox_stock", "future_lake": "future_lake",
            root_id: root_id}
    for d in dirs.values():
        (cwroot / d).mkdir(parents=True, exist_ok=True)
    roots_yaml = (
        "  - root_id: company_raw\n"
        "    kind: company_raw\n"
        f"    path: {q(cwroot / 'companies')}\n"
        "    priority: 10\n"
        "    privacy_class: public\n"
        "  - root_id: dayu_portfolio\n"
        "    kind: dayu_portfolio\n"
        f"    path: {q(cwroot / 'dayu_portfolio')}\n"
        "    priority: 20\n"
        "    privacy_class: public\n"
        "  - root_id: dropbox_stock\n"
        "    kind: directory\n"
        f"    path: {q(cwroot / 'dropbox_stock')}\n"
        "    priority: 30\n"
        "    privacy_class: public\n"
        "  - root_id: future_lake\n"
        "    kind: directory\n"
        "    adapter_id: sidecar_filing_v1\n"
        "    read_only: true\n"
        "    reusable_for_filing: true\n"
        f"    path: {q(cwroot / 'future_lake')}\n"
        "    priority: 40\n"
        "    privacy_class: public\n"
        f"  - root_id: {root_id}\n"
        "    kind: directory\n"
        "    adapter_id: sidecar_filing_v1\n"
        "    admission_profile_id: financial_evidence_v1\n"
        "    read_only: true\n"
        "    reusable_for_filing: true\n"
        f"    path: {q(cwroot / root_id)}\n"
        "    priority: 50\n"
        "    privacy_class: public\n"
    )
    cfg = write_config(cwroot, roots_yaml, "company_raw, dayu_portfolio, directory")

    company_dir = cwroot / root_id / data["company_dir_name"]
    company_dir.mkdir(parents=True, exist_ok=True)
    payload = company_dir / data["payload_file_name"]
    payload_text = (
        "ISOLATED SYNTHETIC PAYLOAD - card I-07-C cell X05.\n"
        "This file is NOT a real financial filing. It exists only to exercise the\n"
        "supported adapter/profile scan+resolve mechanics on a hitherto-unnamed\n"
        "isomorphic root. No financial fact about any company is asserted.\n")
    payload.write_text(payload_text, encoding="utf-8")
    payload_sha = sha256_file(payload)
    sidecar = {
        "schema_version": "1.0",
        "canonical_entity_id": data["canonical_entity_id"],
        "market": data["market"],
        "security_id": data["security_id"],
        "company_name": data["company_name"],
        "display_name": data["company_name"],
        "document_kind": data["document_kind"],
        "fiscal_year": data["fiscal_year"],
        "fiscal_period": data["fiscal_period"],
        "period_end": data["period_end"],
        "content_sha256": payload_sha,
        "provider": data["provider"],
        "provider_document_id": data["provider_document_id"],
        "source_url": data["source_url"],
        "filing_date": data["filing_date"],
        "source_title": data["source_title"],
        "synthetic_isolated_fixture": True,
        "provenance": data["honesty_note"],
    }
    sc_path = payload.with_name(payload.name + ".source.json")
    sc_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    req = rel_request("X05-fifthroot", data["company_name"])
    return {"config": cfg, "fifth_root_id": root_id,
            "fifth_root_dir": str(cwroot / root_id),
            "payload": {"path": str(payload), "sha256": payload_sha,
                        "bytes": payload.stat().st_size,
                        "synthetic_isolated_fixture": True},
            "sidecar": {"path": str(sc_path), "sha256": sha256_file(sc_path)},
            "company_name_source": "inputs/fifth_root_company.json (data file, disclosed)",
            "resolve_request": req,
            "production_shape_preserved": "four production root ids/kinds/adapters kept; only paths rebound to isolation"}


def build_unk_adapter(cwroot: Path) -> dict:
    root_dir = cwroot / "unk_lake"
    root_dir.mkdir(parents=True, exist_ok=True)
    (root_dir / "payload.txt").write_text("adapter never reached\n", encoding="utf-8")
    roots_yaml = ("  - root_id: unk_adapter_root\n"
                  "    kind: directory\n"
                  "    adapter_id: unknown_layout_v9\n"
                  f"    path: {q(root_dir)}\n"
                  "    priority: 10\n"
                  "    privacy_class: public\n")
    cfg = write_config(cwroot, roots_yaml, "directory")
    return {"config": cfg, "expected": "config load refuses unknown adapter_id (CFG-01)"}


def _sc(payload: str, **over) -> str:
    body = {"schema_version": "1.0"}
    body.update(over)
    return json.dumps(body, ensure_ascii=False, indent=1)


def build_unk_sidecar(cwroot: Path) -> dict:
    lake = cwroot / "malformed_lake"
    lake.mkdir(parents=True, exist_ok=True)
    files = {}

    def put(name: str, text: str, sidecar_text: str | None) -> None:
        p = lake / name
        p.write_text(text, encoding="utf-8")
        if sidecar_text is not None:
            p.with_name(p.name + ".source.json").write_text(sidecar_text,
                                                            encoding="utf-8")
        files[name] = {"sha256": sha256_file(p),
                       "sidecar": sidecar_text is not None}

    import hashlib  # noqa: F401  (kept: payloads are hashed from FILE bytes below)
    good_text = "clean probe payload with a complete adapter-contract sidecar\n"
    put("clean_probe.txt", good_text, None)  # sidecar written after the file so
    # the declared hash is taken from the FILE bytes (write_text translates
    # newlines on Windows; hashing the pre-write string declared a wrong hash
    # and the product correctly demoted the candidate - scan1 evidence kept)
    clean_path = lake / "clean_probe.txt"
    clean_path.write_text(good_text, encoding="utf-8")
    clean_path.with_name(clean_path.name + ".source.json").write_text(
        _sc("x",
            canonical_entity_id="isolated-i07c-unk-1", market="US",
            security_id="ISO1", company_name="I07C Isolated Probe Co",
            document_kind="annual_report", fiscal_year=2025, fiscal_period="FY",
            period_end="2025-12-31",
            content_sha256=hashlib.sha256(clean_path.read_bytes()).hexdigest(),
            provider="example-filing", provider_document_id="i07c-unk-clean",
            filing_date="2026-02-12", source_title="clean probe"),
        encoding="utf-8")
    files["clean_probe.txt"] = {"sha256": sha256_file(clean_path),
                                "sidecar": True}
    put("no_sidecar_probe.txt", "payload without any sidecar\n", None)
    put("broken_sidecar_probe.txt", "payload whose sidecar is not JSON\n",
        "{not valid json,")
    mismatch_text = "payload whose sidecar declares another hash and an absolute path\n"
    put("mismatch_probe.txt", mismatch_text,
        _sc("x", market="US", security_id="ISO2",
            content_sha256="0" * 64,
            canonical_path="C:\\escape\\target.pdf",
            document_kind="annual_report", fiscal_year=2025,
            period_end="2025-12-31", provider="example-filing",
            provider_document_id="i07c-unk-mismatch"))
    roots_yaml = ("  - root_id: malformed_lake_root\n"
                  "    kind: directory\n"
                  "    adapter_id: sidecar_filing_v1\n"
                  "    read_only: true\n"
                  "    reusable_for_filing: true\n"
                  f"    path: {q(lake)}\n"
                  "    priority: 10\n"
                  "    privacy_class: public\n")
    cfg = write_config(cwroot, roots_yaml, "directory")
    return {"config": cfg, "files": files,
            "expected": "explicit remediation per file; no filename-guessed identity/kind"}


def build_unk_kind(cwroot: Path) -> dict:
    lake = cwroot / "unk_layout"
    probe_dir = lake / "probe_dir"
    probe_dir.mkdir(parents=True, exist_ok=True)
    bait = probe_dir / "2025_annual_report_guess_probe.pdf"
    bait.write_text("unknown layout probe payload\n", encoding="utf-8")
    roots_yaml = ("  - root_id: unk_layout_root\n"
                  "    kind: unknown_layout_probe\n"
                  f"    path: {q(lake)}\n"
                  "    priority: 10\n"
                  "    privacy_class: public\n")
    cfg = write_config(cwroot, roots_yaml, "directory")
    return {"config": cfg, "probe": {"path": str(bait), "sha256": sha256_file(bait)},
            "frozen_expectation": "card clause 3: explicit unsupported, NO guessing; "
                                  "any identity/kind guessed from this layout is a FINDING"}


def build_x01(cwroot: Path) -> dict:
    """companies-only: the ONLY root is company_raw holding one frozen sample."""
    sample = sample_by_market("CN")
    (cwroot / "companies").mkdir(parents=True, exist_ok=True)
    roots_yaml = ("  - root_id: company_raw\n"
                  "    kind: company_raw\n"
                  f"    path: {q(cwroot / 'companies')}\n"
                  "    priority: 10\n"
                  "    privacy_class: public\n")
    cfg = write_config(cwroot, roots_yaml, "company_raw")
    assets = copy_sample_into(sample, cwroot, ["companies"])
    sidecar = (cwroot / "companies" / sample["entity_dir"] / "raw"
               / "financial_reports" / sample["kind_dir"]
               / (sample["file_name"] + ".source.json"))
    entity = resolve_entity_from_sidecar(sidecar, fallback=sample["entity_dir"])
    req = rel_request("X01-companies-only", entity)
    return {"sample": {k: str(v) if isinstance(v, Path) else v for k, v in sample.items()},
            "config": cfg, "assets": assets, "resolve_request": req,
            "level": "isolated construction only - production companies-only is NOT signed here"}


def build_x02(cwroot: Path) -> dict:
    """dayu-only: the ONLY root is dayu_portfolio holding an isomorphic
    portfolio/<ticker>/filings/<id>/ tree built from a frozen sample's REAL
    bytes, with meta.json facts derived from that sample's real sidecar."""
    sample = sample_by_market("US")
    sidecar = read_json(sample["sidecar"])
    ticker = str(sidecar.get("security_id") or sidecar.get("ticker") or "").strip()
    if not ticker:
        raise SystemExit("sample sidecar has no security_id/ticker for the dayu ticker dir")
    filing_id = "i07c-iso-filing-1"
    group = cwroot / "dayu_portfolio" / ticker / "filings" / filing_id
    group.mkdir(parents=True, exist_ok=True)
    dst_file = group / sample["file_name"]
    copies = [copy_checked(sample["raw"], dst_file)]

    filing_meta = {
        "document_id": sidecar.get("provider_document_id"),
        "form_type": sidecar.get("form_type"),
        "fiscal_year": sidecar.get("fiscal_year"),
        "fiscal_period": sidecar.get("fiscal_period"),
        "filing_date": sidecar.get("filing_date"),
        "source_url": sidecar.get("source_url"),
        "source_title": sidecar.get("source_title") or sidecar.get("title"),
        "source_language": sidecar.get("language"),
        "source_provider": sidecar.get("provider"),
        "ticker": ticker,
        "company_name": sidecar.get("company_name") or sidecar.get("entity"),
        "ingest_complete": True,
        "provenance": "I-07-C isolated dayu-shaped construction; meta.json facts "
                      "derived from the manifest sample's real sidecar; real bytes copied",
    }
    (group / "meta.json").write_text(
        json.dumps(filing_meta, ensure_ascii=False, indent=1), encoding="utf-8")
    entity_meta = {"market": sidecar.get("market"), "ticker": ticker,
                   "company_name": sidecar.get("company_name") or sidecar.get("entity"),
                   "provenance": "I-07-C isolated construction (entity-level meta)"}
    (cwroot / "dayu_portfolio" / ticker / "meta.json").write_text(
        json.dumps(entity_meta, ensure_ascii=False, indent=1), encoding="utf-8")

    roots_yaml = ("  - root_id: dayu_portfolio\n"
                  "    kind: dayu_portfolio\n"
                  f"    path: {q(cwroot / 'dayu_portfolio')}\n"
                  "    priority: 20\n"
                  "    privacy_class: public\n")
    cfg = write_config(cwroot, roots_yaml, "dayu_portfolio")
    req = rel_request("X02-dayu-only", ticker)
    return {"sample": {k: str(v) if isinstance(v, Path) else v for k, v in sample.items()},
            "config": cfg, "copies": copies, "filing_meta": filing_meta,
            "entity_meta": entity_meta, "resolve_request": req,
            "level": "isolated construction only - production dayu-only has no frozen identity"}


BUILDERS = {
    "X04-multiroot": build_x04,
    "X05-fifthroot": build_x05,
    "UNK-adapter": build_unk_adapter,
    "UNK-sidecar": build_unk_sidecar,
    "UNK-kind": build_unk_kind,
    "X01-companies-only": build_x01,
    "X02-dayu-only": build_x02,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in BUILDERS:
        print(f"usage: build_iso.py <{'|'.join(BUILDERS)}>", file=sys.stderr)
        return 1
    cell = sys.argv[1]
    cwroot = new_cwroot(cell)
    manifest = {"cell": cell, "built_at_utc": datetime.now(timezone.utc).isoformat(),
                "schema": iso_schema(cwroot)}
    manifest.update(BUILDERS[cell](cwroot))
    case_dir = cwroot.parent
    manifest["case_dir"] = str(case_dir)
    manifest["location"] = "%TEMP%\\i07c\\cells (MAX_PATH isolation root)"
    manifest["iso_snapshot"] = iso_snapshot(case_dir)
    write_json(EVID / "iso_initial" / f"{cell}.json", manifest)
    print(json.dumps({"written": str(EVID / "iso_initial" / f"{cell}.json"),
                      "cell": cell,
                      "tables": manifest["schema"]["table_count"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
