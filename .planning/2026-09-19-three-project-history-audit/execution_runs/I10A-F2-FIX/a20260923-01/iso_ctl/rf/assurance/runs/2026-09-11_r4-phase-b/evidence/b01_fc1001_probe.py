"""Why did FC-1001's `sidecar_missing` real-data case start failing after B01?

The pre-push gate of revenue-forecast runs tests/test_fc1001_isolated_lake.py
against the production catalog.  After B01 (resolver aligns its reuse decision
with policy._effective_reusable) this case fails:

    FAILED tests/test_fc1001_isolated_lake.py::test_corruption_variants_fail_closed[sidecar_missing]
    AssertionError: sidecar-missing dropbox doc must not resolve

This probe isolates the cause WITHOUT editing any product or test file.  It
rebuilds the same fixture (IsolatedLake seed=fc1001, corruption
"sidecar_missing"), opens it with the SAME synthetic CatalogConfig the test
builds, and resolves the same request under four combinations:

    rule = "effective" (shipped after B01) | "kind_only" (shipped before B01)
    config = "as_test"  (no reusable_root_kinds -> CatalogConfig default)
             "as_prod"  (reusable_root_kinds = the shipped config's list)

Read-only w.r.t. everything: the fixture lives in a temp directory and the
catalog is only queried.  Writes one JSON next to this script.

Usage: python evidence/b01_fc1001_probe.py
"""

from __future__ import annotations

import dataclasses
import json
import re
import sqlite3
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path(__file__).resolve().parents[4]
WIKI = REVENUE.parent / "company-wiki"
sys.path.insert(0, str(REVENUE / "tests"))
sys.path.insert(0, str(REVENUE / "scripts"))
sys.path.insert(0, str(WIKI / "src"))

import company_wiki.source_catalog.resolver as resolver_mod  # noqa: E402
from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
    SourceRequest,
    SourceResolver,
)
from e2e_support.isolated_lake import IsolatedLake  # noqa: E402

TEST_FILE = REVENUE / "tests" / "test_fc1001_isolated_lake.py"
SHIPPED_KINDS = ("company_raw", "dayu_portfolio", "directory")


def entity_from_test() -> str:
    """Read the entity literal the sidecar_missing branch uses (never printed)."""
    text = TEST_FILE.read_text(encoding="utf-8")
    marker = 'if variant == "sidecar_missing":'
    if marker not in text:
        raise SystemExit("could not find the sidecar_missing branch in the case")
    branch = text.split(marker, 1)[1]
    match = re.search(r'SourceRequest\(entity="([^"]+)"', branch)
    if not match:
        raise SystemExit("could not read the entity literal from the branch")
    return match.group(1)


def effective_rule(spec, config):
    """The shipped rule (policy._effective_reusable, unchanged by B01)."""
    if spec.reusable_for_filing is not None:
        return bool(spec.reusable_for_filing)
    return spec.kind in config.reusable_root_kinds


def kind_only_rule(spec, config):
    """The rule the resolver used BEFORE B01."""
    return spec.kind in config.reusable_root_kinds


def build_config(tmp: Path, catalog_dir: Path, kinds, sidecar_suffixes=None) -> CatalogConfig:
    field = next(f.name for f in dataclasses.fields(CatalogConfig) if "reusable" in f.name)
    root_kwargs = {
        "priority": 30, "adapter_id": "sidecar_filing_v1", "read_only": True,
        "reusable_for_filing": True,
    }
    if sidecar_suffixes is not None:
        root_kwargs["sidecar_suffixes"] = sidecar_suffixes
    kwargs = {
        "project_root": tmp / "lake" / "project",
        "catalog_dir": catalog_dir,
        "roots": (
            RootSpec("dropbox_stock", tmp / "lake" / "Dropbox" / "Stock", "directory",
                     **root_kwargs),
        ),
    }
    if kinds is not None:
        kwargs[field] = kinds
    return CatalogConfig(**kwargs)


def reset_lake(tmp: Path):
    manifest = IsolatedLake(tmp, seed="fc1001").build()
    lake = IsolatedLake(tmp, seed="fc1001")
    lake.corrupt("sidecar_missing", manifest)
    return manifest, lake


def catalog_facts(manifest, tmp: Path) -> dict:
    con = sqlite3.connect(f"file:{manifest.catalog_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        locations = []
        for row in con.execute(
            "SELECT root_id, location_status, role, relative_path, source_id, "
            "document_id, metadata_json FROM locations WHERE root_id='dropbox_stock'"
        ):
            item = dict(row)
            try:
                meta = json.loads(item.pop("metadata_json") or "{}")
            except ValueError:
                meta = {}
            item["rank_like_keys"] = {
                key: value for key, value in meta.items() if "rank" in key.lower()
            }
            locations.append(item)
        doc_ids = sorted({row["document_id"] for row in con.execute(
            "SELECT document_id FROM locations WHERE root_id='dropbox_stock'")})
        entities = {}
        for doc_id in doc_ids:
            entities[doc_id] = con.execute(
                "SELECT COUNT(*) FROM document_entities WHERE document_id=?", (doc_id,)
            ).fetchone()[0]
    finally:
        con.close()
    dropbox_root = tmp / "lake" / "Dropbox" / "Stock"
    sidecars = sorted(p.name for p in dropbox_root.rglob("*.source.json")) if dropbox_root.exists() else []
    return {
        "dropbox_locations": locations,
        "dropbox_documents": len(doc_ids),
        "document_entities_rows": entities,
        "dropbox_sidecar_files_left_on_disk": sidecars,
        "expected_sidecars_for_dropbox": sorted(
            entry.sidecar_rel for entry in manifest.entries if entry.root_id == "dropbox_stock"
        ),
    }


def run_scenario(label: str, rule_name: str, rule, kinds, entity: str, tmp: Path,
                 rescan: bool = False, sidecar_suffixes=None) -> dict:
    resolver_mod._effective_reusable = rule
    manifest, lake = reset_lake(tmp)
    config = build_config(tmp, manifest.catalog_path.parent, kinds,
                          sidecar_suffixes=sidecar_suffixes)
    catalog = SourceCatalog(config)
    if rescan:
        # The corrupted state is then what the INDEX sees too: this is the
        # pipeline-level rule (scan establishes identity), as opposed to asking
        # the read layer to re-check a sidecar it never reads.
        catalog.scan()
    request = SourceRequest(entity=entity, document_kind="semi_annual_report",
                            as_of_date="2026-08-12", market="CN", fiscal_year=2020)
    result = SourceResolver(catalog, runtime_policy=None).resolve(request)
    trace = list(result.debug_trace or ())
    handles = list(result.matches or ())
    return {
        "scenario": label,
        "reuse_rule": rule_name,
        "rescanned_after_corruption": rescan,
        "reusable_root_kinds": list(config.reusable_root_kinds),
        "declared_reusable_for_filing": True,
        "matches": len(handles),
        "first_handle": (
            {
                name: getattr(handles[0], name)
                for name in ("document_id", "source_id", "content_sha256", "location_id",
                             "canonical_location_id", "capture_ready", "download_required",
                             "provider_document_id")
                if hasattr(handles[0], name)
            }
            if handles else None
        ),
        "trace_len": len(trace),
        "trace_has_no_reusable_root_location": any(
            "no_reusable_root_location" in line for line in trace),
        "trace_has_entity_gate_rejected": any("entity_gate_rejected" in line for line in trace),
        "trace": trace,
        "catalog_facts": catalog_facts(manifest, tmp),
    }


def main() -> int:
    entity = entity_from_test()
    scenarios = []
    with tempfile.TemporaryDirectory(prefix="b01-fc1001-", ignore_cleanup_errors=True) as work:
        for rule_name, rule in (("effective (shipped after B01)", effective_rule),
                                ("kind_only (shipped before B01)", kind_only_rule)):
            for config_name, kinds in (("as_test (CatalogConfig default)", None),
                                       ("as_prod (shipped kind list)", SHIPPED_KINDS)):
                label = f"{rule_name} | config {config_name}"
                tmp = Path(work) / re.sub(r"[^a-z0-9]+", "-", label.lower())
                tmp.mkdir(parents=True)
                scenarios.append(run_scenario(label, rule_name, rule, kinds, entity, tmp))
        # Does the property the case names hold once the INDEX sees the
        # corrupted state (i.e. is "re-scan after corruption" a workable fix)?
        label = "effective (shipped after B01) | config as_prod | re-scan after corruption"
        tmp = Path(work) / "rescan"
        tmp.mkdir(parents=True)
        scenarios.append(run_scenario(label, "effective (shipped after B01)", effective_rule,
                                      SHIPPED_KINDS, entity, tmp, rescan=True))
        # ... and once the root DECLARES its sidecar suffix (what FC-501 identity
        # actually keys on), does the scan retire the document?
        label = ("effective | config as_prod + sidecar_suffixes declared | re-scan after corruption")
        tmp = Path(work) / "rescan-sidecar"
        tmp.mkdir(parents=True)
        scenarios.append(run_scenario(label, "effective (shipped after B01)", effective_rule,
                                      SHIPPED_KINDS, entity, tmp, rescan=True,
                                      sidecar_suffixes=(".source.json",)))
    resolver_mod._effective_reusable = effective_rule

    payload = {
        "probe": "evidence/b01_fc1001_probe.py",
        "question": ("does B01's alignment change FC-1001's sidecar_missing verdict, and what did "
                     "that verdict actually depend on?"),
        "fixture": "tests/e2e_support/isolated_lake.py, seed=fc1001, corruption=sidecar_missing",
        "request": "SourceRequest(document_kind=semi_annual_report, as_of_date=2026-08-12, market=CN, fiscal_year=2020)",
        "scenarios": scenarios,
        "conclusion": ("see the README-style summary in evidence/b01-implementation.md section 6"),
    }
    out = RUN / "evidence" / "b01-fc1001-probe.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for row in scenarios:
        print("---")
        print("scenario      :", row["scenario"].encode("ascii", "replace").decode())
        print("kinds         :", row["reusable_root_kinds"])
        print("matches       :", row["matches"])
        print("gate rejected :", row["trace_has_no_reusable_root_location"])
        print("entity gate   :", row["trace_has_entity_gate_rejected"])
        print("facts         : dropbox_locations=%d entities_rows=%s sidecars_left=%d" % (
            len(row["catalog_facts"]["dropbox_locations"]),
            sum(row["catalog_facts"]["document_entities_rows"].values()),
            len(row["catalog_facts"]["dropbox_sidecar_files_left_on_disk"])))
    print("wrote", out.relative_to(RUN).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
