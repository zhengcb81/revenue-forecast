"""Milestone: real RF -> FF -> CWP CLIs with a bounded offline provider.

Only fixture construction imports test support. Runtime consumers use the public
CLI and SourceRef; no production catalog/config/raw or supplier is accessed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RF_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ff-root", type=Path, required=True)
    parser.add_argument("--cwp-root", type=Path, required=True)
    args = parser.parse_args()
    ff = args.ff_root.resolve(strict=True)
    cwp = args.cwp_root.resolve(strict=True)
    helper = ff / "docs/implementation/cmrf-provider-diagnostics-20261008/run_isolated_cause_e2e.py"
    spec = importlib.util.spec_from_file_location("joint_failure_fixture", helper)
    fixture = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(fixture)
    environment = dict(os.environ, PYTHONPATH=str(cwp / "src"),
                       PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    proof = {"schema_version": "three-repo-failure/1", "paid_calls": 0,
             "production_writes": 0, "checks": [], "cases": {}}

    def check(name, actual, expected):
        proof["checks"].append({"check": name, "status": "PASS" if actual == expected else "FAIL",
                                "actual": actual, "expected": expected})

    with tempfile.TemporaryDirectory(prefix="rfcause-") as temporary:
        base = Path(temporary).resolve()
        assert base.parent == Path(tempfile.gettempdir()).resolve()
        adapter = base / "p.py"
        code = fixture._FAKE_PROVIDER.replace(
            '"acquisition_usage": {"response_bytes": 0, "cost_usd": "0.00"}',
            '"acquisition_usage": {"schema_version": "1.0", "response_bytes": 0, "cost_usd": "0.00"}')
        adapter.write_text(code, encoding="utf-8", newline="\n")
        provider_log = base / "events.jsonl"

        def case_root(name, behavior):
            wrapper = base / (name + ".py")
            expression = "'typed_error' if 'fetch' in sys.argv else 'ok'" if behavior == "fetch_error" else repr(behavior)
            wrapper.write_text("import runpy,sys\nbehavior=" + expression + "\n"
                               + f"sys.argv=[sys.argv[0],behavior,{str(provider_log)!r}]+sys.argv[1:]\n"
                               + f"runpy.run_path({str(adapter)!r},run_name='__main__')\n",
                               encoding="utf-8", newline="\n")
            wiki = fixture._build_wiki(base / name, wrapper, broken=False)
            return base / name, wiki

        def prepare(case, wiki, request):
            request_path = case / "request.json"
            request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-B", str(RF_ROOT / "scripts/source_preparation.py"),
                 "--request-file", str(request_path), "--filing-fetch-root", str(ff),
                 "--company-wiki-config", str(case / "ff-config.json"),
                 "--company-wiki-catalog-config", str(wiki / "config/source_catalog.yaml"),
                 "--timeout-seconds", "60"],
                cwd=case, env=environment, capture_output=True, text=True, encoding="utf-8",
                timeout=75, check=False)
            return result, json.loads(result.stdout if result.returncode == 0 else result.stderr)

        expected = {"schema_version": "filing-upstream-cause/1", "operation": "ensure",
                    "code": "upstream_unavailable", "provider_started": True,
                    "usage_complete": True, "retry_scope": "none"}
        for name, behavior, latest, provider_starts in [
            ("f", "fetch_error", False, 4), ("g", "typed_error", True, 1)]:
            case, wiki = case_root(name, behavior)
            request = fixture._request("fetch_if_missing")
            if latest:
                request["mode"] = "latest_as_of"
                request.pop("fiscal_year", None)
            result, payload = prepare(case, wiki, request)
            proof["cases"][name] = payload
            check(name + "_preparation_exit", result.returncode, 3)
            check(name + "_safe_cause_survives_entire_chain", payload.get("upstream_cause"), expected)
            check(name + "_legacy_error_class", payload.get("error_code"), "upstream")
            check(name + "_no_error_on_success_stream", result.stdout, "")
            check(name + "_provider_calls_no_RF_or_FF_retry",
                  len(fixture._events(fixture._provider_log(provider_log), "provider_started")), provider_starts)
            check(name + "_raw_not_created", len(list((wiki / "companies").rglob("*.pdf"))), 0)
            check(name + "_no_secret_or_root_leak",
                  any(token in json.dumps(payload) for token in (str(base), "api_key=", "simulated upstream 503")), False)
            provider_log.unlink(missing_ok=True)

        case, wiki = case_root("s", "ok")
        first, record = prepare(case, wiki, fixture._request("fetch_if_missing"))
        proof["cases"]["success"] = {"returncode": first.returncode,
                                         "snapshot_sha256": record.get("capture", {}).get("snapshot_sha256"),
                                         "reuse_receipt": record.get("reuse_receipt")}
        check("success_exit", first.returncode, 0)
        check("source_ref_verified_actual_bytes", record.get("capture", {}).get("snapshot_sha256"), fixture.PDF_SHA)
        check("success_no_failure_metadata", "upstream_cause" in record, False)
        before = fixture._provider_log(provider_log)
        reused, again = prepare(case, wiki, fixture._request("reuse_only"))
        check("reuse_exit", reused.returncode, 0)
        check("reuse_zero_download", again.get("reuse_receipt", {}).get("download_calls"), 0)
        check("reuse_no_provider_call", fixture._provider_log(provider_log), before)
        check("reuse_exact_same_bytes", again.get("capture", {}).get("snapshot_sha256"), fixture.PDF_SHA)
        originals = list((wiki / "companies").rglob("*.pdf"))
        check("one_original", len(originals), 1)
        check("original_preserved", hashlib.sha256(originals[0].read_bytes()).hexdigest() if originals else None,
              fixture.PDF_SHA)
        proof["cases"]["reuse"] = {"returncode": reused.returncode,
                                       "snapshot_sha256": again.get("capture", {}).get("snapshot_sha256"),
                                       "download_calls": again.get("reuse_receipt", {}).get("download_calls")}
    proof["temporary_root_restored"] = not base.exists()
    proof["failures"] = [item["check"] for item in proof["checks"] if item["status"] != "PASS"]
    proof["result"] = "PASS" if not proof["failures"] and proof["temporary_root_restored"] else "FAIL"
    proof["runtime_sha256"] = {str(root / path): hashlib.sha256((root / path).read_bytes()).hexdigest()
        for root, paths in [
            (RF_ROOT, ["scripts/filing_upstream_cause.py", "scripts/filing_fetch_client.py", "scripts/source_preparation.py"]),
            (ff, ["scripts/ff_provider_cause.py", "scripts/fetch_filing.py", "scripts/ff_process_transport.py", "scripts/ff_v2_envelope.py"]),
            (cwp, ["src/company_wiki/source_catalog/acquisition_failure.py", "src/company_wiki/source_catalog/cli.py"])]
        for path in paths}
    output = Path(__file__).with_name("three_repo_e2e_report.json")
    output.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"result": proof["result"], "checks": len(proof["checks"]),
                      "failures": proof["failures"], "restored": proof["temporary_root_restored"],
                      "report": str(output)}, ensure_ascii=True))
    return 0 if proof["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
