"""B2 company-wiki dayu_cli_adapter harness: exhibit asset copying.

Runs against iso/cw_repo only (no product-repo import, no network, no writes
outside the attempt dir).  Exit code = number of failed checks (0 == all green).

Scenarios (each in its own short tmp tree; the fake dayu CLI writes the meta)
  8k_on    US 8-K, meta carries primary + EX-99.1 exhibit + XBRL sidecar
           -> staged set must be exactly {primary, exhibit}      (RED before B2)
  8k_off   same meta, include_exhibits disabled at the module flag
           -> staged set must be exactly {primary}
  6k       US 6-K, meta carries primary + exhibit
           -> staged set must be exactly {primary}               (6-K byte regression)
  10k      US 10-K, meta carries primary + exhibit-like file + XBRL
           -> staged set must be exactly {primary}               (gate must not leak)
  landing  canonical_writer._destination_subdirectory('current_report') == Path('other')
           -> raw/other/ declaration of §三十一 (read-only call, no write)

Also asserts the DownloadReceipt for the primary stays unchanged
(staged name, content_sha256, byte_size, mime_type, source_url, http_status).

Environment shims (harness only — NO product code is touched):
  * EDGAR_LOCAL_DATA_DIR redirected into the attempt dir (session cannot write $HOME).
  * tempfile.mkdtemp re-created with the default mode: CPython's os.mkdir(path, 0o700)
    yields a directory this sandbox then refuses to read (WinError 5), which kills
    `DayuCliDownloadAdapter.discover()` before any of its logic runs.
  * short fixture dir names to stay inside the Win32 260-char path budget.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ATTEMPT / "iso" / "cw_repo" / "src"))

# keep any third-party cache inside the attempt dir (session cannot write $HOME)
os.environ.setdefault("EDGAR_LOCAL_DATA_DIR", str(ATTEMPT / "results" / "_edgar_cache"))

import tempfile as _tempfile  # noqa: E402

_real_mkdtemp = _tempfile.mkdtemp


def _sandbox_mkdtemp(suffix=None, prefix=None, dir=None):
    suffix = "" if suffix is None else suffix
    prefix = _tempfile.template if prefix is None else prefix
    directory = _tempfile.gettempdir() if dir is None else dir
    for _ in range(_tempfile.TMP_MAX):
        name = f"{prefix}{next(_tempfile._get_candidate_names())}{suffix}"
        candidate = os.path.join(directory, name)
        try:
            os.mkdir(candidate)  # default mode: 0o700 dirs are unreadable here
        except FileExistsError:
            continue
        return candidate
    raise FileExistsError("no usable temp dir name found")


_tempfile.mkdtemp = _sandbox_mkdtemp

FAKE_CLI = r'''
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
if not args or args[0] != "download":
    raise SystemExit(31)

def value(name: str) -> str:
    return args[args.index(name) + 1]

base = Path(value("--base"))
ticker = value("--ticker")
record = Path(os.environ["FAKE_DAYU_RECORD"])
record.write_text(json.dumps(args, ensure_ascii=False), encoding="utf-8")
spec = json.loads(os.environ["FAKE_DAYU_META"])
filing = base / "portfolio" / ticker / "filings" / spec["document_id"]
filing.mkdir(parents=True)
files = []
for entry in spec["files"]:
    target = filing / entry["name"]
    target.write_bytes(entry["bytes"].encode("utf-8"))
    files.append({
        "name": entry["name"],
        "size": target.stat().st_size,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "content_type": entry.get("content_type"),
        "source_url": entry.get("source_url", spec["source_url_prefix"] + entry["name"]),
    })
meta = {
    "document_id": spec["document_id"],
    "accession_number": spec["accession_number"],
    "ticker": ticker,
    "company_id": spec["company_id"],
    "form_type": spec["form_type"],
    "fiscal_year": spec["fiscal_year"],
    "fiscal_period": spec["fiscal_period"],
    "report_date": spec["report_date"],
    "filing_date": spec["filing_date"],
    "ingest_complete": True,
    "is_deleted": False,
    "primary_document": spec["primary_document"],
    "amended": False,
    "files": files,
}
(filing / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
print("download ok")
'''


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spec(form_type: str) -> dict:
    exhibit = {
        "name": "d291965dex991.htm",
        "bytes": "<html><body>Exhibit 99.1 FY27 segments</body></html>",
        "content_type": "text/html",
    }
    xbrl = {
        "name": "d291965d8k_htm.xml",
        "bytes": "<xbrl/>",
        "content_type": "application/xml",
    }
    tenk_exhibit = {
        "name": "msft_ex99-1.htm",
        "bytes": "<html><body>EX-99.1 attachment</body></html>",
        "content_type": "text/html",
    }
    tenk_xbrl = {
        "name": "msft-20250630_htm.xml",
        "bytes": "<xbrl/>",
        "content_type": "application/xml",
    }
    base = {
        "8-K": {
            "document_id": "fil_8k",
            "accession_number": "0001193125-26-380280",
            "form_type": "8-K",
            "primary_document": "d291965d8k.htm",
            "files": [
                {"name": "d291965d8k.htm", "bytes": "<html><body>8-K primary</body></html>",
                 "content_type": "text/html"},
                exhibit,
                xbrl,
            ],
            "filing_date": "2026-09-02",
        },
        "6-K": {
            "document_id": "fil_6k",
            "accession_number": "0001104659-24-051955",
            "form_type": "6-K",
            "primary_document": "tm2412704d1_6k.htm",
            "files": [
                {"name": "tm2412704d1_6k.htm", "bytes": "<html><body>6-K primary</body></html>",
                 "content_type": "text/html"},
                {"name": "tm2412704d1_ex99-1.htm",
                 "bytes": "<html><body>6-K exhibit</body></html>",
                 "content_type": "text/html"},
            ],
            "filing_date": "2024-02-06",
        },
        "10-K": {
            "document_id": "fil_10k",
            "accession_number": "0000789019-25-000011",
            "form_type": "10-K",
            "primary_document": "msft-20250630.htm",
            "files": [
                {"name": "msft-20250630.htm", "bytes": "<html><body>10-K primary</body></html>",
                 "content_type": "text/html"},
                tenk_exhibit,
                tenk_xbrl,
            ],
            "filing_date": "2025-07-30",
        },
    }[form_type]
    base.update(
        {
            "company_id": "789019",
            "fiscal_year": 2025,
            "fiscal_period": "FY",
            "report_date": "2025-06-30",
            "source_url_prefix": "https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/",
        }
    )
    return base


def _run_scenario(root: Path, label: str, form_type: str, *, include_exhibits_flag) -> dict:
    import company_wiki.source_catalog.dayu_cli_adapter as adapter_mod
    from company_wiki.source_catalog import DayuCliDownloadAdapter, SourceRequest

    saved = getattr(adapter_mod, "_INCLUDE_EXHIBITS", None)
    scenario_root = root / label
    scenario_root.mkdir(parents=True, exist_ok=True)
    script = scenario_root / "fake_dayu.py"
    script.write_text(FAKE_CLI, encoding="utf-8")
    config = scenario_root / "cfg"
    config.mkdir(exist_ok=True)
    record = scenario_root / "invocation.json"
    workspace_parent = scenario_root / "dayu-workspaces"
    staging = scenario_root / "staging"
    os.environ["FAKE_DAYU_MARKET"] = "US"
    os.environ["FAKE_DAYU_RECORD"] = str(record)
    os.environ["FAKE_DAYU_META"] = json.dumps(_spec(form_type), ensure_ascii=False)
    if saved is not None:
        adapter_mod._INCLUDE_EXHIBITS = bool(include_exhibits_flag)
    try:
        adapter = DayuCliDownloadAdapter(
            name="dayu-sec-cli",
            version="1.0.0",
            market="US",
            command=(sys.executable, str(script)),
            project_root=scenario_root,
            config_root=config,
            workspace_parent=workspace_parent,
            timeout_seconds=30,
        )
        request = SourceRequest(
            entity="MICROSOFT CORP",
            market="US",
            security_id="MSFT",
            document_kind="current_report",
            form_type=form_type,
            fiscal_year=2025,
            as_of_date="2026-09-30",
            allow_download=True,
        )
        candidates = adapter.discover(request)
        candidate = candidates[0] if len(candidates) == 1 else None
        receipt = adapter.fetch(candidate, staging) if candidate is not None else None
        staged = sorted(p.name for p in staging.iterdir()) if staging.exists() else []
        staged_hashes = {name: _sha256(staging / name) for name in staged} if staged else {}
        return {
            "form_type": form_type,
            "include_exhibits_flag": include_exhibits_flag,
            "candidates": len(candidates),
            "candidate": None if candidate is None else {
                "candidate_id": candidate.candidate_id,
                "form_type": candidate.form_type,
                "source_url": candidate.source_url,
                "adapter_payload_json": candidate.adapter_payload_json,
            },
            "receipt": None if receipt is None else {
                "staged_name": Path(receipt.staged_path).name,
                "staged_hash_matches_receipt": (
                    _sha256(Path(receipt.staged_path)) == receipt.content_sha256
                ),
                "content_sha256": receipt.content_sha256,
                "byte_size": receipt.byte_size,
                "mime_type": receipt.mime_type,
                "source_url": receipt.source_url,
                "http_status": receipt.http_status,
            },
            "staged_files": staged,
            "staged_hashes": staged_hashes,
        }
    finally:
        if saved is not None:
            adapter_mod._INCLUDE_EXHIBITS = saved


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    out_dir = ATTEMPT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    root = ATTEMPT / "tmp"
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    tmp_root = str(root)

    import company_wiki.source_catalog.dayu_cli_adapter as adapter_mod

    has_flag = hasattr(adapter_mod, "_INCLUDE_EXHIBITS")
    flag_on = bool(getattr(adapter_mod, "_INCLUDE_EXHIBITS", True))

    results = {
        "8k_on": _run_scenario(root, "c8on", "8-K", include_exhibits_flag=flag_on),
        "6k": _run_scenario(root, "c6", "6-K", include_exhibits_flag=flag_on),
        "10k": _run_scenario(root, "c10", "10-K", include_exhibits_flag=flag_on),
    }
    if has_flag:
        results["8k_off"] = _run_scenario(root, "c8off", "8-K", include_exhibits_flag=False)

    # landing declaration (§三十一): read-only call, no file is written
    from company_wiki.source_catalog.canonical_writer import _destination_subdirectory

    landing = str(_destination_subdirectory("current_report"))

    if mode == "freeze":
        frozen = {
            "6k": results["6k"],
            "10k": results["10k"],
            "8k_off": results.get("8k_off"),
        }
        (out_dir / "adapter_frozen_before.json").write_text(
            json.dumps(frozen, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"mode": mode, "staged_8k": results["8k_on"]["staged_files"],
                          "staged_6k": results["6k"]["staged_files"],
                          "staged_10k": results["10k"]["staged_files"]}, ensure_ascii=False))
        return 0

    report = {"harness": "adapter_copy", "mode": mode, "has_include_exhibits_flag": has_flag,
              "checks": [], "landing_current_report": landing, "scenarios": results,
              "tmp_root": tmp_root}

    def record(name: str, ok: bool, detail):
        report["checks"].append({"name": name, "ok": ok, "detail": detail})

    import hashlib as _h

    def blob(value):
        return _h.sha256(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        ).hexdigest()

    expected_8k = sorted(["d291965d8k.htm", "d291965dex991.htm"])
    record(
        "A1_8k_stages_primary_and_exhibit_only",
        results["8k_on"]["staged_files"] == expected_8k,
        {"staged": results["8k_on"]["staged_files"], "expected": expected_8k},
    )
    record(
        "A2_8k_exhibit_bytes_match_meta_sha",
        results["8k_on"]["staged_hashes"].get("d291965dex991.htm")
        == hashlib.sha256(b"<html><body>Exhibit 99.1 FY27 segments</body></html>").hexdigest(),
        {"hashes": results["8k_on"]["staged_hashes"]},
    )
    record(
        "A3_8k_receipt_points_at_primary",
        results["8k_on"]["receipt"] is not None
        and results["8k_on"]["receipt"]["staged_name"] == "d291965d8k.htm"
        and results["8k_on"]["receipt"]["staged_hash_matches_receipt"] is True,
        {"receipt": results["8k_on"]["receipt"]},
    )

    frozen = json.loads((out_dir / "adapter_frozen_before.json").read_text(encoding="utf-8"))
    record(
        "A4_6k_result_byte_identical_to_before",
        blob(results["6k"]) == blob(frozen["6k"]),
        {
            "before_sha256": blob(frozen["6k"]),
            "after_sha256": blob(results["6k"]),
            "staged_before": frozen["6k"]["staged_files"],
            "staged_after": results["6k"]["staged_files"],
            "payload_before": (frozen["6k"]["candidate"] or {}).get("adapter_payload_json"),
            "payload_after": (results["6k"]["candidate"] or {}).get("adapter_payload_json"),
        },
    )
    record(
        "A5_10k_result_byte_identical_to_before",
        blob(results["10k"]) == blob(frozen["10k"]),
        {
            "before_sha256": blob(frozen["10k"]),
            "after_sha256": blob(results["10k"]),
            "staged_before": frozen["10k"]["staged_files"],
            "staged_after": results["10k"]["staged_files"],
            "payload_before": (frozen["10k"]["candidate"] or {}).get("adapter_payload_json"),
            "payload_after": (results["10k"]["candidate"] or {}).get("adapter_payload_json"),
        },
    )
    record(
        "A6_include_exhibits_flag_gates_8k",
        has_flag
        and flag_on is True
        and results["8k_off"]["staged_files"] == ["d291965d8k.htm"],
        {"has_flag": has_flag, "flag_default": flag_on,
         "staged_when_flag_off": results.get("8k_off", {}).get("staged_files")},
    )
    record(
        "A7_landing_current_report_is_other",
        landing in {"other", "raw/other"},
        {"_destination_subdirectory(current_report)": landing},
    )

    failed = [c for c in report["checks"] if not c["ok"]]
    report["passed"] = len(report["checks"]) - len(failed)
    report["failed"] = len(failed)
    (out_dir / f"adapter_copy_{mode}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"mode": mode, "passed": report["passed"], "failed": report["failed"],
                      "failed_names": [c["name"] for c in failed]}, ensure_ascii=False))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
