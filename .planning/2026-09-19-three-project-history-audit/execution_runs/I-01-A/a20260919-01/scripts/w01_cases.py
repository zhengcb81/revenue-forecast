"""w01_cases: source-level runner for the five frozen oracle families.

Usage:
  python w01_cases.py --code prod|override --case <name> --work <fresh-run-dir>

Each case: copies the sample tree to <work>/project (scratch included), runs
  (a) the config_doctor.diagnose API on the sample, and
  (b) a REAL (store-writing) SourceCatalog scan of the copy config into the
      copy's own scratch catalog (isolated; no production DB),
  plus reads back locations/documents per root ("resolve by identity").
Writes one JSON to stdout.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w01_bootstrap  # noqa: E402

SAMPLES = HERE.parent / "samples"

CASES = {
    "P1": "cfg_good",
    "P2": "cfg_fifth",
    "N1": "cfg_real",
    "N2-unknown_adapter": "n2_unknown_adapter",
    "N2-no_scanner_impl": "n2_no_scanner_impl",
    "N2-version_unsupported": "n2_version_unsupported",
    "N2-unknown_profile": "n2_unknown_profile",
    "N3-readonly_write_target": "n3_readonly_write_target",
    "N3-profile_mismatch": "n3_profile_mismatch",
}


def _db_rows(db_path: Path, root_id: str) -> dict:
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        locations = [
            dict(row)
            for row in connection.execute(
                """SELECT relative_path,role,document_id,location_status,error
                FROM locations WHERE root_id=? ORDER BY relative_path""",
                (root_id,),
            )
        ]
        documents = [
            dict(row)
            for row in connection.execute(
                """SELECT DISTINCT d.document_id,d.title,d.document_kind
                FROM locations l JOIN documents d ON d.document_id=l.document_id
                WHERE l.root_id=? ORDER BY d.title""",
                (root_id,),
            )
        ]
    finally:
        connection.close()
    return {"locations": locations, "documents": documents}


def run(code: str, case: str, work: Path) -> dict:
    sample = SAMPLES / CASES[case]
    w = Path(work) / "project"
    if w.exists():
        shutil.rmtree(w)
    shutil.copytree(sample, w, dirs_exist_ok=True)
    config_path = w / "source_catalog.yaml"
    result: dict = {"case": case, "code": code, "sample": sample.name}

    # (a) doctor (source-level diagnose API)
    import config_doctor

    try:
        problems = list(config_doctor.diagnose(config_path, project_root=w))
        result["doctor"] = {"ok": True, "problems": problems}
    except Exception as exc:  # noqa: BLE001
        result["doctor"] = {"ok": False, "exception": f"{type(exc).__name__}: {exc}"}

    # (b) real scan of the copy config into the copy scratch catalog
    from company_wiki.source_catalog.config import load_catalog_config
    from company_wiki.source_catalog.scanner import (
        CatalogStore,
        scan_catalog,
        v2_scan_shadow_from_snapshot,
    )

    try:
        config = load_catalog_config(config_path, project_root=w)
    except Exception as exc:  # noqa: BLE001
        result["scan"] = {
            "ok": False,
            "config_load_error": f"{type(exc).__name__}: {exc}",
        }
        return result
    shadow = v2_scan_shadow_from_snapshot(config.catalog_dir)
    result["scan_stage"] = {"v2_scan_shadow_from_snapshot": shadow}
    store = CatalogStore(config.database_path)
    try:
        report = scan_catalog(config, store, dry_run=False, v2_scan_shadow=shadow)
        payload = report.to_dict()
        payload.pop("run_id", None)
        result["scan"] = {"ok": True, "report": payload}
        per_root = {}
        for root in config.roots:
            per_root[root.root_id] = _db_rows(config.database_path, root.root_id)
        result["per_root_persisted"] = per_root
    except Exception as exc:  # noqa: BLE001
        result["scan"] = {"ok": False, "exception": f"{type(exc).__name__}: {exc}"}
    finally:
        try:
            store.close()
        except AttributeError:
            pass
    return result


if __name__ == "__main__":
    import shutil

    parser = argparse.ArgumentParser()
    parser.add_argument("--code", choices=("prod", "override"), required=True)
    parser.add_argument("--case", required=True, help="P1|P2|N1|N2-*|N3-*")
    parser.add_argument("--work", required=True, help="fresh empty run directory")
    args = parser.parse_args()
    Path(args.work).mkdir(parents=True, exist_ok=True)
    w01_bootstrap.setup(args.code)
    payload = run(args.code, args.case, Path(args.work))
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
