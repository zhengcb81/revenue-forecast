"""Reviewer-side independent probe of the B1 fixes.

Runs ONLY against a reviewer-owned copy of the fixed tree.  Never imports from
the production repo or from iso/fixed/rf.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
REPO = ATTEMPT / "reviewer" / "scratch" / "fixed_rf"
SCRIPTS = REPO / "scripts"
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(
    ATTEMPT / "reviewer" / "scratch" / "probe_registry.jsonl"
)
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

import revenue_core  # noqa: E402
import revenue_publication  # noqa: E402
import revenue_report  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

print("EXECUTED revenue_core      :", revenue_core.__file__)
print("EXECUTED revenue_report    :", revenue_report.__file__)
print("EXECUTED revenue_publication:", revenue_publication.__file__)


def rehash(pkg):
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")}
    )
    record = receipt.get("publication_attestation")
    if isinstance(record, dict):
        record["payload_sha256"] = receipt["validated_payload_sha256"]
    receipt["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )
    pkg["result_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k != "result_sha256"}
    )
    return pkg


def verdict(label, fn):
    try:
        fn()
    except ForecastInputError as exc:
        print(f"{label}: REJECTED  <{exc}>")
        return "REJECTED"
    except Exception as exc:  # noqa: BLE001
        print(f"{label}: ERROR {type(exc).__name__} <{exc}>")
        return "ERROR"
    print(f"{label}: ACCEPTED")
    return "ACCEPTED"


honest = revenue_core.run_forecast(forecast_document())
print("\n--- honest artifact shape ---")
print("base_revenue                 :", honest["base_revenue"])
print("segments count               :", len(honest["segments"]))
for i, seg in enumerate(honest["segments"]):
    print(
        f"  segments[{i}].name={seg['name']!r} base_revenue={seg['base_revenue']!r} "
        f"base_revenue_parameter_id={seg.get('base_revenue_parameter_id')!r}"
    )
print("reconciliation_tolerance     :", honest.get("reconciliation_tolerance", "<absent>"))
print("base_adjustment_parameter_ids:", honest.get("base_adjustment_parameter_ids", "<absent>"))
print("attestation_status           :", honest["publication_receipt"]["attestation_status"])
print("keys(publication_receipt)    :", sorted(honest["publication_receipt"]))
print("ATTESTATION_FIELDS           :", sorted(revenue_publication.PUBLICATION_ATTESTATION_FIELDS))
print("len(ATTESTATION_FIELDS)      :", len(revenue_publication.PUBLICATION_ATTESTATION_FIELDS))

print("\n--- baseline ---")
verdict("V0 honest package, validate_publication_receipt", lambda: revenue_publication.validate_publication_receipt(honest))
verdict("V0 honest package, validate_forecast_output   ", lambda: revenue_report.validate_forecast_output(honest))
verdict("V0 honest package, validate_published_forecast", lambda: revenue_report.validate_published_forecast(honest, honest["input_document"]))
verdict("V0 honest package, render_markdown            ", lambda: revenue_report.render_markdown(honest))

print("\n--- REM-03: original reviewer exploit (+1000 on segments[0]) ---")
f1000 = copy.deepcopy(honest)
f1000["segments"][0]["base_revenue"] = float(f1000["segments"][0]["base_revenue"]) + 1000.0
rehash(f1000)
verdict("E1 receipt layer (documented non-security)   ", lambda: revenue_publication.validate_publication_receipt(f1000))
verdict("E1 validate_forecast_output                  ", lambda: revenue_report.validate_forecast_output(f1000))
verdict("E1 validate_published_forecast               ", lambda: revenue_report.validate_published_forecast(f1000, f1000["input_document"]))
verdict("E1 render_markdown                           ", lambda: revenue_report.render_markdown(f1000))

print("\n--- REM-03: SMALL inflation (+0.5 on segments[0]), G-A must still catch ---")
f_small = copy.deepcopy(honest)
f_small["segments"][0]["base_revenue"] = float(f_small["segments"][0]["base_revenue"]) + 0.5
rehash(f_small)
verdict("E2 validate_forecast_output (+0.5)           ", lambda: revenue_report.validate_forecast_output(f_small))

print("\n--- REM-03: G-B only survivable forgery: ALL segments + base move together ---")
f_all = copy.deepcopy(honest)
for seg in f_all["segments"]:
    seg["base_revenue"] = float(seg["base_revenue"]) + 1.0
f_all["base_revenue"] = float(f_all["base_revenue"]) + 1.0 * len(f_all["segments"])
rehash(f_all)
verdict("E3 all-segment + total inflation             ", lambda: revenue_report.validate_forecast_output(f_all))

print("\n--- REM-03: company base moved ONLY (segments untouched) ---")
f_base = copy.deepcopy(honest)
f_base["base_revenue"] = float(f_base["base_revenue"]) + 1000.0
rehash(f_base)
verdict("E4 base_revenue only (+1000)                 ", lambda: revenue_report.validate_forecast_output(f_base))

print("\n--- REM-03: name-preserving swap of two segment bases ---")
if len(honest["segments"]) >= 2:
    f_swap = copy.deepcopy(honest)
    a = float(f_swap["segments"][0]["base_revenue"])
    b = float(f_swap["segments"][1]["base_revenue"])
    f_swap["segments"][0]["base_revenue"] = b
    f_swap["segments"][1]["base_revenue"] = a
    rehash(f_swap)
    verdict("E5 swap two segment bases (names kept)       ", lambda: revenue_report.validate_forecast_output(f_swap))
else:
    print("E5 skipped: single segment")
