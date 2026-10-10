"""P7-RF M3 isolated public E2E: real CLI positive/negative controls in owned TEMP.

Recipe mirrors tests/test_research_evidence_roles.py::test_actual_case_assembly_cli_then_native_validate_compute_snapshot:
build_revenue_source_record_from_verified_read -> tools/build_auditable_case.py (real argv)
-> tools/run_target_measurement_e2e.py (validate -> compute/render -> strong -> snapshot).
Every subprocess that can run_forecast/snapshot gets REVENUE_PUBLICATION_REGISTRY inside this owned TEMP root.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:/Users/郑曾波/.codex/worktrees/m3-acceptance-20261010/revenue-forecast")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

M3 = Path(r"C:/Users/郑曾波/AppData/Local/Temp/p7-rf-scoped-calibration/m3")
REGISTRY = M3 / "registry" / "publications.jsonl"

from test_research_evidence_roles import calibrated_document  # noqa: E402
from company_wiki_source_v2 import build_revenue_source_record_from_verified_read  # noqa: E402
from test_company_wiki_source_reader_v2 import BODY, _ref, _receipt  # noqa: E402

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" :: {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(label)


def owned(path: Path) -> bool:
    return str(path.resolve()).startswith(str(M3.resolve()))


def native_case(tag: str, mutate_research=None):
    case = M3 / tag
    case.mkdir(parents=True, exist_ok=False)
    d = calibrated_document()
    raw_receipt = _receipt()
    manifest = raw_receipt.pop("manifest")
    candidate = {"status": "source_candidate", "source_ref": _ref(), "byte_verification": "pending_verified_open",
                 "document_kind": manifest["document_kind"], "fiscal_year": manifest["fiscal_year"],
                 "fiscal_period": manifest["fiscal_period"], "resolution_outcome": "reused_existing",
                 "download_events": 0}
    source = build_revenue_source_record_from_verified_read(source_ref=_ref(), read_receipt=raw_receipt,
        source_bytes=BODY, source_manifest=manifest, source_candidate=candidate, as_of_date=d["as_of_date"],
        source_type="regulatory_filing", publisher="synthetic producer fixture", page_or_section="1")
    sid = source["source_id"]

    def rekey(value):
        if isinstance(value, dict):
            return {k: rekey(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rekey(v) for v in value]
        return sid if value == "filing" else value

    d = rekey(d)
    d["sources"][0] = source
    for c in d["evidence_claims"]:
        if c["source_id"] == sid:
            c["content_sha256"] = source["capture"]["snapshot_sha256"]
            c["capture_receipt_sha256"] = source["capture"]["receipt_sha256"]
    prep = {"schema_version": "source-preparation-result/1", "source": source, "filing_fetch": None, "narrative": None}
    research = d.pop("operating_research")
    if mutate_research is not None:
        mutate_research(research)
    for name, value in (("input", d), ("research", research), ("preparation", prep),
                        ("discovery", {"schema_version": "synthetic-discovery-receipt/1", "items": [], "coverage_complete": False})):
        (case / (name + ".json")).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    assembled = case / "assembled"
    native = case / "native"
    env = dict(os.environ)
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", REVENUE_PUBLICATION_REGISTRY=str(REGISTRY))
    build_cmd = [sys.executable, "-X", "utf8", "-B", str(REPO / "tools/build_auditable_case.py"), "--company", "synthetic",
                 "--input", str(case / "input.json"), "--research", str(case / "research.json"),
                 "--preparation", str(case / "preparation.json"), "--discovery", str(case / "discovery.json"),
                 "--as-of", d["as_of_date"], "--output-root", str(assembled)]
    e2e_cmd = [sys.executable, "-X", "utf8", "-B", str(REPO / "tools/run_target_measurement_e2e.py"),
               "--input", str(assembled / "linked-input.json"), "--output-root", str(native)]
    for command in (build_cmd, e2e_cmd):
        for token in command:
            if token.endswith(".json") or token.endswith(".py"):
                pass
        for path in (assembled, native):
            assert owned(path), f"output root escapes owned TEMP: {path}"
    runs = []
    for command in (build_cmd, e2e_cmd):
        done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=180, env=env)
        runs.append(done)
        if done.returncode:
            print(done.stdout[-2000:], done.stderr[-2000:])
            check(f"{tag}: CLI exit 0 ({Path(command[-1]).name})", False)
            return case, None, None
    check(f"{tag}: build+e2e exit 0", True)
    result = json.loads((native / "forecast.json").read_text(encoding="utf-8"))
    return case, result, (native, assembled)


def main():
    M3.mkdir(parents=True, exist_ok=True)
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    # ---- positive control: correct conversion/output stays referenced_range
    case_pos, result_pos, paths_pos = native_case("positive")
    if result_pos is not None:
        native, assembled = paths_pos
        cal = result_pos["confidence"]["research_adequacy"]["calibrations"][0]
        check("positive: adequacy_status referenced_range", cal["adequacy_status"] == "referenced_range")
        check("positive: no reasons", cal["reasons"] == [], str(cal["reasons"]))
        values = [cal["scenario_conversion"][s]["formula_value"] for s in ("low", "base", "high")]
        check("positive: formula values 100/110/120", values == [100.0, 110.00000000000001, 120.00000000000001] or
              all(abs(a - b) < 1e-9 for a, b in zip(values, (100, 110, 120))), str(values))
        check("positive: engine 4.2.1", result_pos["engine_version"] == "4.2.1", result_pos.get("engine_version"))
        check("positive: confidence stable-fsum/1", result_pos["confidence"]["calculation_version"] == "stable-fsum/1")
        check("positive: snapshot exists", (native / "snapshot.json").exists())
        registries = sorted(str(p) for p in M3.glob("*/native/publications.jsonl"))
        check("positive: all publication registries inside owned TEMP",
              len(registries) >= 1 and all(owned(Path(r)) for r in registries), str(registries))
        magnitude = result_pos["confidence"]["research_adequacy"]["magnitude_adequacy"]["supported_parameter_ids"]
        check("positive: magnitude 3 outputs", sorted(magnitude) == ["0_base_2026", "0_high_2026", "0_low_2026"], str(magnitude))
        markdown = (native / "forecast.md").read_text(encoding="utf-8")
        check("positive: markdown renders calibration", "reference_bridge" in markdown and "referenced_range" in markdown)
        # diagnostics CLI consistency
        diag = subprocess.run([sys.executable, "-X", "utf8", "-B", str(REPO / "scripts/research_support_diagnostics.py"),
                               "--input", str(assembled / "linked-input.json")], capture_output=True, text=True,
                              encoding="utf-8", timeout=120)
        check("positive: diagnostics CLI exit 0", diag.returncode == 0, diag.stderr[-500:])
        if diag.returncode == 0:
            data = json.loads(diag.stdout)
            seg_a = next(s for s in data["segments"] if s["segment"] == "Segment A")
            cell = {(e["scenario"], e["year"]): e["status"] for e in seg_a["entries"]}
            check("positive: diag SegmentA FY2026 supported x3",
                  all(cell[(s, "2026")] == "supported" for s in ("low", "base", "high")), str(cell))
            check("positive: diag SegmentA FY2027 unsupported", cell[("low", "2027")] == "unsupported")
            check("positive: diag sha matches linked input",
                  data["input_sha256"] == hashlib.sha256((assembled / "linked-input.json").read_bytes()).hexdigest())

    # ---- negative control: unrelated conversion scope cannot promote (CE1)
    def swap_conversion_scopes(research):
        for o in research["observations"]:
            if o["observation_kind"] == "conversion":
                o["scope"] = "Unrelated Business Line"
    case_neg, result_neg, paths_neg = native_case("negative", swap_conversion_scopes)
    if result_neg is not None:
        native_neg, assembled_neg = paths_neg
        cal = result_neg["confidence"]["research_adequacy"]["calibrations"][0]
        check("negative: adequacy_status unverified", cal["adequacy_status"] == "unverified")
        joined = " | ".join(cal["reasons"])
        check("negative: conversion scope reasons with IDs",
              "conversion_observation_unverified_scope:conversion_low:claim_parameter_conversion_low" in joined, joined)
        magnitude = result_neg["confidence"]["research_adequacy"]["magnitude_adequacy"]["supported_parameter_ids"]
        check("negative: magnitude empty", magnitude == [], str(magnitude))
        if result_pos is not None:
            check("negative: revenue arithmetic unchanged",
                  result_neg["consolidated_forecast"] == result_pos["consolidated_forecast"])
            check("negative: confidence score unchanged",
                  result_neg["confidence"]["score"] == result_pos["confidence"]["score"])
        diag = subprocess.run([sys.executable, "-X", "utf8", "-B", str(REPO / "scripts/research_support_diagnostics.py"),
                               "--input", str(assembled_neg / "linked-input.json")], capture_output=True, text=True,
                              encoding="utf-8", timeout=120)
        check("negative: diagnostics CLI exit 0", diag.returncode == 0, diag.stderr[-500:])
        if diag.returncode == 0:
            data = json.loads(diag.stdout)
            seg_a = next(s for s in data["segments"] if s["segment"] == "Segment A")
            entry = next(e for e in seg_a["entries"] if e["scenario"] == "low" and e["year"] == "2026")
            reasons = " | ".join(entry["reasons"])
            check("negative: diag unsupported with ID reasons",
                  entry["status"] == "unsupported" and "conversion_low" in reasons and
                  "claim_parameter_conversion_low" in reasons, reasons)

    # ---- evidence SHAs
    print("\n-- SHA256 evidence --")
    for tag in ("positive", "negative"):
        for name in ("input.json", "research.json", "linked-input.json"):
            candidates = list((M3 / tag).glob("**/" + name))
            for path in candidates:
                print(tag, path.relative_to(M3), hashlib.sha256(path.read_bytes()).hexdigest())
    print("\nRESULT:", "ALL_PASS" if not failures else f"{len(failures)} FAILURES: {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
