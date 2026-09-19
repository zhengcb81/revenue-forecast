"""w02c_cli_probe: exercise the REAL modified cli.main() recover entry.

Runs ``ensure --register-existing --recovery-manifest ...`` through
company_wiki.source_catalog.cli.main(argv) inside an isolated scratch
project (HK fixed sample). Proves the frozen CLI wiring (decision.md)
without inventing any additional product command and without any provider
call. The manifest's authorized_caller is the approved I-02-C marker.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples" / "real_roots"
SCRATCH_BASE = Path(tempfile.gettempdir()) / "w02c" / "a20260919-01_cli_probe"

w02c = importlib.import_module("w02c_bootstrap")
w02c.setup("override")

from company_wiki.source_catalog.cli import main as cli_main  # noqa: E402

HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
HK_FILENAME = "2026-04-28_hkexnews_12127452_2025年度報告.pdf"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_project(case: str) -> tuple:
    project = SCRATCH_BASE / case / "project"
    if SCRATCH_BASE.exists():
        shutil.rmtree(SCRATCH_BASE)
    project.mkdir(parents=True)
    companies = project / "companies"
    companies.mkdir()
    catalog_dir = project / ".source_catalog"
    catalog_dir.mkdir()
    config = {
        "schema_version": "1.0",
        "catalog_dir": ".source_catalog",
        "roots": [
            {
                "root_id": "company_raw",
                "path": "companies",
                "kind": "company_raw",
                "priority": 10,
                "adapter_id": "company_raw_v1",
                "read_only": False,
            }
        ],
    }
    (project / "config").mkdir()
    (project / "config" / "source_catalog.yaml").write_text(
        json.dumps(config, ensure_ascii=False), encoding="utf-8"
    )
    (catalog_dir / "runtime_policy.json").write_text(
        json.dumps({"schema_version": "1.0"}), encoding="utf-8"
    )
    # Place the fixed HK sample (raw + sidecar byte-identical).
    dst = companies / "小米集團－Ｗ" / "raw" / "financial_reports" / "annual"
    dst.mkdir(parents=True)
    raw = dst / HK_FILENAME
    shutil.copyfile(SAMPLES / "hk" / HK_FILENAME, raw)
    sidecar_src = Path(str(SAMPLES / "hk" / HK_FILENAME) + ".source.json")
    shutil.copyfile(sidecar_src, raw.with_name(raw.name + ".source.json"))
    manifest = {
        "raw_path": str(raw),
        "sidecar_path": str(raw.with_name(raw.name + ".source.json")),
        "authorized_caller": "I-02-C sample-copy-manifest",
    }
    manifest_path = catalog_dir / "recovery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return project, raw, manifest_path


def main() -> int:
    project, raw, manifest_path = build_project("cli_register")
    before_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    argv = [
        "--config",
        str(project / "config" / "source_catalog.yaml"),
        "ensure",
        "--entity",
        "小米集團－Ｗ",
        "--document-kind",
        "annual_report",
        "--as-of-date",
        "2026-09-18",
        "--security-id",
        "01810",
        "--market",
        "HK",
        "--form-type",
        "FY",
        "--fiscal-year",
        "2025",
        "--fiscal-period",
        "FY",
        "--provider",
        "hkexnews",
        "--provider-document-id",
        "12127452",
        "--register-existing",
        "--recovery-manifest",
        str(manifest_path),
        "--acquisition-config",
        "missing_on_purpose.yaml",
    ]
    rc = cli_main(argv)
    after_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    evidence = {
        "returncode": rc,
        "raw_bytes_unchanged": before_hash == after_hash == HK_SHA,
        "raw_sha256": after_hash,
    }
    (ATTEMPT / "after" / "cli-register-existing.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False))
    return 0 if (rc == 0 and before_hash == after_hash == HK_SHA) else 1


if __name__ == "__main__":
    sys.exit(main())
