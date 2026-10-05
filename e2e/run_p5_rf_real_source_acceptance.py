"""Manual default RF CLI on a fixed actual PDF; all state is temporary.

Identity and publication metadata are labelled fixtures, not live verification.
No provider download or model call; no writes to original data/configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SHA = "d64c410832f22f5127277bad6dc357c664aede523561af99150c494857fd3aa5"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(raw, scratch, ff, cwp):
    assert digest(raw) == SHA
    before = sorted(path.name for path in scratch.iterdir())
    spec = importlib.util.spec_from_file_location("p5_rf_cli_fixture", ROOT / "tests/test_p5_source_default_cli_e2e.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    with tempfile.TemporaryDirectory(prefix="real-", dir=scratch) as temporary:
        test_root = Path(temporary)
        wiki, _ = fixture._build_wiki(test_root, ff, cwp)
        isolated = sys.modules["p5_ff_isolated_wiki"]
        master = isolated._synthetic_security_master("cn")
        master["records"][0].update(canonical_name="中微公司", aliases=["AMEC"], market="CN", exchange="SSE", ticker="688012", security_id="688012", identifiers={"org_id": "fixture-amec"})
        (wiki.catalog_dir / "security_master/cn.json").write_text(json.dumps(master, ensure_ascii=False), encoding="utf-8")
        copy = wiki.root / "companies/中微公司/raw/financial_reports/annual/2025.pdf"
        copy.parent.mkdir(parents=True)
        shutil.copy2(raw, copy)
        sidecar = dict(schema_version="1.0", market="CN", security_id="688012", company_name="中微公司", source_title="中微公司2025年年度报告", published_date="2026-03-30", fiscal_year=2025, form_type="FY", provider="cninfo", provider_document_id="fixture-amec-2025", source_url="https://www.cninfo.com.cn/fixture-amec-2025", retrieved_at="2026-09-27T00:00:00Z", adapter_name="p5-rf-real-fixture", adapter_version="1.0.0")
        copy.with_name(copy.name + ".source.json").write_text(json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")
        wiki.scan()
        derived = fixture._seed_legacy_artifacts(wiki)
        request = dict(schema_version="1.1", company_query="中微公司", market="CN", document_kind="annual_report", fiscal_year=2025, as_of_date="2026-10-06")
        def read():
            proc = fixture._run_cli(wiki, ff, cwp, request)
            assert proc.returncode == 0, proc.stderr[-800:]
            record = json.loads(proc.stdout)
            assert record["capture"]["snapshot_sha256"] == SHA
            assert record["reuse_receipt"]["artifact_read"] == []
            assert record["reuse_receipt"]["download_calls"] == 0
            assert record["reuse_receipt"]["parser_calls"] is None
            return record
        first = read()
        con = sqlite3.connect(wiki.catalog_dir / "catalog.sqlite3")
        try:
            facts_before = [con.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall() for table in ("sources", "documents", "locations")]
            assert con.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 3
            con.execute("DELETE FROM artifacts")
            con.commit()
            shutil.rmtree(derived)
            second = read()
            assert first["source_id"] == second["source_id"]
            assert facts_before == [con.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall() for table in ("sources", "documents", "locations")]
            copy.write_bytes(copy.read_bytes() + b"tamper")
            bad = fixture._run_cli(wiki, ff, cwp, request)
            assert bad.returncode != 0 and "source reader refused" in bad.stderr
            shutil.copy2(raw, copy)
            healed = read()
            assert healed["source_id"] == first["source_id"]
            assert digest(copy) == SHA
        finally:
            con.close()
    assert not Path(temporary).exists()
    assert before == sorted(path.name for path in scratch.iterdir())
    assert digest(raw) == SHA
    return dict(status="ok", original_sha256=SHA, byte_size=raw.stat().st_size, default_cli_reads=3, tamper_refusals=1, legacy_files_deleted=3, legacy_rows_deleted=3, source_facts_unchanged=True, scratch_restored=True, identity_metadata="synthetic fixture", provider_http_calls=0, model_calls=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-file", type=Path, required=True)
    parser.add_argument("--scratch-root", type=Path, required=True)
    parser.add_argument("--ff-root", type=Path, required=True)
    parser.add_argument("--cwp-root", type=Path, required=True)
    args = parser.parse_args()
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    result = run(args.raw_file.resolve(strict=True), args.scratch_root.resolve(strict=True), args.ff_root.resolve(strict=True), args.cwp_root.resolve(strict=True))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
