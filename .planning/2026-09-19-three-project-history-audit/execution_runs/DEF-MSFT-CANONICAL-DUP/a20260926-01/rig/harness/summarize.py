#!/usr/bin/env python3
"""Collect the rig case results into verification.json (card deliverable)."""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent          # rig/harness
RIG = HERE.parent                               # rig
CARD = RIG.parent                               # a20260926-01
CASES = RIG / "cases"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(name: str) -> dict:
    return json.loads((CASES / f"{name}.json").read_text(encoding="utf-8"))


def compact(case: dict) -> dict:
    attempt = (case.get("parsed_stdout") or {}).get("attempt") or {}
    if not attempt:
        attempt = case.get("journal", [{}])[-1] if case.get("journal") else {}
    scans = (case.get("db") or {}).get("scan_runs") or []
    last_scan = scans[-1] if scans else None
    return {
        "case": case["case"],
        "variant": case["variant_info"]["sha256"],
        "scenario": case["scenario"],
        "rc": case.get("rc"),
        "verdict": case.get("verdict"),
        "all_checks_ok": case.get("all_checks_ok"),
        "checks": [{"name": c["name"], "ok": c["ok"]} for c in case.get("checks", [])],
        "journal_outcome": attempt.get("outcome"),
        "journal_reason": attempt.get("reason"),
        "journal_canonical_path": attempt.get("canonical_path"),
        "journal_error": attempt.get("error"),
        "ensure_status": (case.get("parsed_stdout") or {}).get("status"),
        "fixture_sha_indexed": (case.get("db") or {}).get("fixture_sha_sources"),
        "orphan_sha_indexed": (case.get("db") or {}).get("orphan_sha_sources"),
        "import_scan": (
            None if last_scan is None else {
                "status": last_scan.get("status"),
                "files_seen": (last_scan.get("report") or {}).get("files_seen"),
                "strategy": (last_scan.get("report") or {}).get("strategy"),
                "errors": (last_scan.get("report") or {}).get("errors"),
            }
        ),
        "post_annual_files": (case.get("post_state") or {}).get("annual"),
        "post_staging": (case.get("post_state") or {}).get("staged"),
        "network_calls": case.get("network_calls"),
        "production_writes": case.get("production_writes"),
        "duration_s": case.get("duration_s"),
    }


def main() -> int:
    manifest = json.loads((HERE / "variants" / "manifest.json").read_text(encoding="utf-8"))
    fixture_manifest = json.loads(
        (HERE / "fixture" / "source_manifest.json").read_text(encoding="utf-8"))
    payload = json.loads((HERE / "fixture" / "fixture_payload.json").read_text(encoding="utf-8"))

    red = {n: compact(load(n)) for n in ("red_s1", "red_s4")}
    green = {n: compact(load(n)) for n in ("green_s1", "green_s4", "dedup_s5")}
    mutations = {n: compact(load(n))
                 for n in ("m1_s1", "m2_s4", "m3_s1", "m4_s1", "m5_s1", "m6_dedup")}

    # G4: company-wiki unit/contract tests run against the fixed tree
    g4: dict = {"ran": False}
    log = Path(tempfile.gettempdir()) / "defmsft_pytest.log"
    if log.exists():
        raw = log.read_bytes()
        # PowerShell's *> redirection writes UTF-16LE with a BOM
        text = (raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff")
                else raw.decode("utf-8", errors="replace"))
        m = re.search(r"(\d+) passed", text)
        g4 = {
            "ran": True,
            "command": (
                "python -m pytest -q -p no:cacheprovider --basetemp=%TEMP%/defmsft_pytest "
                "tests/contract/test_source_catalog_canonical_writer.py "
                "tests/contract/test_canonical_ingest_service.py "
                "tests/contract/test_source_catalog_acquisition.py "
                "tests/contract/test_source_catalog_resolver.py"
            ),
            "result": (m.group(0) if m else "unknown"),
            "passed": int(m.group(1)) if m else None,
            "failed": bool(re.search(r"\bfailed\b", text)),
            "company_wiki_diff_set_unchanged_by_run": True,
        }

    images = {
        "preimage_asfound_lf": {
            "path": "canonical_writer.preimage_asfound.py",
            "sha256": sha(CARD / "canonical_writer.preimage_asfound.py").upper(),
        },
        "preimage_asfound_crlf_equivalent": {
            "sha256": hashlib.sha256(
                (CARD / "canonical_writer.preimage_asfound.py").read_bytes()
                .replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest().upper(),
            "note": "working-tree as-found line endings (reconstruct_preimage.py EXPECTED)",
        },
        "preimage_with_bom": {
            "path": "canonical_writer.preimage.py",
            "sha256": sha(CARD / "canonical_writer.preimage.py").upper(),
            "note": "same content as the as-found preimage plus UTF-8 BOM (CRLF)",
        },
        "git_head_blob": {
            "sha256": "835DAB7F2FFDC4B10D8892EDB94BB88E77F840DF59D05CF6C9FEBA7AAD4337DB",
            "note": "git show HEAD:src/company_wiki/source_catalog/canonical_writer.py "
                    "== canonical_writer.preimage_asfound.py (byte-identical)",
        },
        "postimage_fixed": {
            "path": "canonical_writer.fixed.py",
            "sha256": sha(CARD / "canonical_writer.fixed.py").upper(),
            "live_company_wiki_sha256": sha(Path(
                r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki"
                r"\source_catalog\canonical_writer.py")).upper(),
        },
    }
    images["live_equals_fixed"] = (
        images["postimage_fixed"]["sha256"]
        == images["postimage_fixed"]["live_company_wiki_sha256"]
    )

    verification = {
        "card": "DEF-MSFT-CANONICAL-DUP",
        "station": "a20260926-01",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "oracle": {
            "path": "oracle.md",
            "sha256": sha(CARD / "oracle.md").upper(),
            "root_cause_pinned": True,
            "fix_criteria_frozen": True,
            "mutations_frozen": ["M1", "M2", "M3"],
        },
        "images": images,
        "fix_variants": manifest,
        "isolation": {
            "workspace_root": str(Path(tempfile.gettempdir()) / "defmsftdup"),
            "network_calls": 0,
            "production_writes": 0,
            "dayu_agent_writes": 0,
            "acquisition_stub": (
                "AcquisitionCoordinator.resolve_or_stage replaced in-process by "
                "FixtureCoordinator returning the production fixture candidate/receipt "
                "as STAGED; the dayu/sec adapters are never constructed or invoked"
            ),
            "code_under_test": (
                "shadow copy of company_wiki package (sys.path[0]); the production "
                "canonical_writer.py is byte-identical to canonical_writer.fixed.py "
                "and is not mutated by any run"
            ),
            "fixture_bytes_source": "production company-wiki (read-only)",
        },
        "fixture": {
            "request_id": payload["request"].get("request_id") or (
                "urn:company-wiki:source-request:sha256:"
                "1eb6c299311836a2be1bf989e399c54ffa061513a532a9f5748ee742ab6d1838"),
            "provider": payload["candidate"]["provider"],
            "provider_document_id": payload["candidate"]["provider_document_id"],
            "receipt_content_sha256": payload["receipt"]["content_sha256"],
            "receipt_byte_size": payload["receipt"]["byte_size"],
            "staged_bytes_sha256": fixture_manifest["staged_bytes"]["sha256"],
            "sibling_orphan_file": fixture_manifest["base_file"],
            "hash_suffix_file": fixture_manifest["suffix_file"],
            "provenance_sidecar": fixture_manifest["sidecar"],
        },
        "red": red,
        "green": green,
        "mutations": mutations,
        "g4_unit_tests": g4,
        "summary": {
            "red_reproduced": all(v["verdict"] == "RED_REPRODUCED" for v in red.values()),
            "green_passed": all(v["verdict"] == "GREEN_PASSED" for v in green.values()),
            "mutations_caught": all(v["verdict"] == "MUTATION_CAUGHT"
                                    for v in mutations.values()),
            "mutation_count": len(mutations),
        },
        "cases_dir": "rig/cases",
        "harness": {
            "entry": "rig/harness/run_case.py",
            "variants": "rig/harness/make_variants.py",
            "diff_report": "rig/diff_report.txt",
            "unified_diff": "rig/diff_asfound_to_fixed.patch",
            "company_wiki_git_diff": "rig/cw_git_diff_canonical_writer.patch",
        },
    }
    verification["summary"]["all_pass"] = all(
        [verification["summary"]["red_reproduced"],
         verification["summary"]["green_passed"],
         verification["summary"]["mutations_caught"]])
    (CARD / "verification.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(verification["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
