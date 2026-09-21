"""Reviewer probe #3: (a) the strongest consistent re-basing attack, where the
attacker ALSO republishes a self-consistent input_document; (b) what the
attestation record does and does not bind after the receipt exists."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
REPO = ATTEMPT / "reviewer" / "scratch" / "fixed_rf"
SCRATCH = ATTEMPT / "reviewer" / "scratch"
sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO / "scripts"))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(SCRATCH / "probe_registry3.jsonl")
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

import revenue_core  # noqa: E402
import revenue_publication  # noqa: E402
import revenue_report  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_core import calculate_cagr, calculate_model_path  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

DELTA = 1000.0


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


def rebuild_segment(segment, parameter_index, years):
    base = float(segment["base_revenue"])
    for scenario in ("low", "base", "high"):
        output = segment["scenarios"][scenario]
        recalculated = calculate_model_path(
            output["model"], base, output["driver_parameter_ids"],
            parameter_index, list(map(int, years)), scenario,
        )
        output["modeled_activity"] = recalculated["annual_revenue"]
        modeled = list(output["modeled_activity"].values())
        recognition = segment["recognition"]
        if recognition["timing"] == "over_time":
            progress = list(output["progress_values"].values())
            recognized = {y: v * f for y, v, f in zip(years, modeled, progress)}
        elif recognition["mode"] == "lagged_activity":
            lag = recognition["lag_years"]
            recognized = dict(zip(years, list(output["carry_in_revenue"]) + modeled[:-lag]))
        else:
            recognized = dict(zip(years, modeled))
        output["recognized_revenue"] = recognized
        if "effective_revenue" in output:
            output["effective_revenue"] = dict(recognized)


def rebuild_consolidated(result, years):
    for scenario in ("low", "base", "high"):
        annual = {}
        for year in years:
            total = 0.0
            for segment in result["segments"]:
                output = segment["scenarios"][scenario]
                eff = output.get("effective_revenue", output["recognized_revenue"])
                total += float(eff[year])
            for adjustment in result.get("adjustment_bridge", []):
                total += float(adjustment["annual_adjustment"][year])
            annual[year] = total
        consolidated = result["consolidated_forecast"][scenario]
        consolidated["annual_revenue"] = annual
        values = [float(annual[y]) for y in years]
        consolidated["terminal_revenue"] = values[-1]
        consolidated["cagr"] = calculate_cagr(
            float(result["base_revenue"]), values[-1], len(years)
        )
        consolidated["annual_growth"] = {
            y: (None if (float(result["base_revenue"]) if i == 0 else float(annual[years[i - 1]])) == 0
                else float(annual[y]) / (float(result["base_revenue"]) if i == 0 else float(annual[years[i - 1]])) - 1)
            for i, y in enumerate(years)
        }
        consolidated["incremental_revenue"] = values[-1] - float(result["base_revenue"])
        if isinstance(consolidated.get("incremental_contribution"), dict):
            consolidated["incremental_contribution"]["total"] = consolidated["incremental_revenue"]
        for bridge in consolidated["segment_bridge"]:
            segment = next(s for s in result["segments"] if s["name"] == bridge["name"])
            output = segment["scenarios"][scenario]
            bridge["annual_revenue"] = dict(
                output.get("effective_revenue", output["recognized_revenue"])
            )


def check(label, fn):
    try:
        fn()
    except ForecastInputError as exc:
        print(f"{label}: REJECTED <{exc}>")
        return "REJECTED"
    except Exception as exc:  # noqa: BLE001
        print(f"{label}: ERROR {type(exc).__name__} <{exc}>")
        return "ERROR"
    print(f"{label}: ACCEPTED")
    return "ACCEPTED"


honest = revenue_core.run_forecast(forecast_document())
years = list(map(str, honest["forecast_years"]))

print("=" * 72)
print("(a) STRONGEST consistent re-basing: attacker republishes a matching")
print("    input_document too (base parameter 100 -> 1100) and re-anchors it.")
print("=" * 72)
forged = copy.deepcopy(honest)
forged["hard_label"] = forged.get("hard_label")  # no-op touch
index = {p["parameter_id"]: p for p in forged["parameter_trace"]}
forged["segments"][0]["base_revenue"] = float(forged["segments"][0]["base_revenue"]) + DELTA
pid = forged["segments"][0]["base_revenue_parameter_id"]
index[pid]["value"] = float(index[pid]["value"]) + DELTA
# also forge the embedded input document's copy of that parameter, and re-anchor
for param in forged["input_document"]["parameters"]:
    if param["parameter_id"] == pid:
        param["value"] = float(param["value"]) + DELTA
forged["input_sha256"] = canonical_sha256(forged["input_document"])
rebuild_segment(forged["segments"][0], index, years)
rebuild_consolidated(forged, years)
rehash(forged)
print("input_sha256 re-anchored to:", forged["input_sha256"][:16], "...")
check("(a) validate_forecast_output", lambda: revenue_report.validate_forecast_output(forged))
try:
    md = revenue_report.render_markdown(forged)
    print("(a) render rows:", [ln for ln in md.splitlines() if "Segment" in ln][:3])
except ForecastInputError as exc:
    print("(a) render REJECTED <", exc, ">")

print()
print("=" * 72)
print("(b) what the attestation record binds AFTER the receipt exists")
print("=" * 72)

# --- build an isolated trusted provider, exactly as the frozen test does -------
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

PROVIDER_SRC = '''\
import hashlib, json, os, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()

raw = sys.stdin.read()
request = json.loads(raw)
private = Ed25519PrivateKey.from_private_bytes(b"\\x09" * 32)
public = private.public_key().public_bytes_raw()
signature = private.sign(canonical(request).encode("ascii")).hex()
response = {
    "attestation_response_schema_version": "1.0",
    "request_id": request["request_id"],
    "payload_sha256": request["payload_sha256"],
    "domain_separator": request["domain_separator"],
    "issuer": "revenue-forecast/reviewer-b1",
    "key_id": "rf-reviewer-key",
    "fingerprint": hashlib.sha256(public).hexdigest()[:32],
    "algorithm": "ed25519",
    "signature": signature,
    "signed_at": "2026-07-12T00:00:00Z",
}
sys.stdout.write(json.dumps(response, sort_keys=True))
'''
script = SCRATCH / "reviewer_provider.py"
script.write_text(PROVIDER_SRC, encoding="utf-8")
launcher = SCRATCH / "reviewer_provider.cmd"
launcher.write_text(
    "@echo off\r\n" f'"{sys.executable}" -B -X utf8 "{script}" %*\r\n', encoding="utf-8"
)
private = Ed25519PrivateKey.from_private_bytes(b"\x09" * 32)
public = private.public_key().public_bytes_raw()
trust = SCRATCH / "reviewer_trust.json"
trust.write_text(
    json.dumps({
        "public_keys": [{
            "name": "reviewer-isolated-signer",
            "key_id": "rf-reviewer-key",
            "issuer": "revenue-forecast/reviewer-b1",
            "public_key": base64.b64encode(public).decode("ascii"),
            "fingerprint": hashlib.sha256(public).hexdigest()[:32],
        }]
    }, sort_keys=True),
    encoding="utf-8",
)

os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(launcher)
os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trust)
signed = revenue_core.run_forecast(forecast_document())
receipt = signed["publication_receipt"]
record = receipt.get("publication_attestation")
print("attestation_status :", receipt["attestation_status"])
print("record field set   :", sorted(record) if record else None)
print("record payload_sha256 == validated_payload_sha256:",
      bool(record) and record["payload_sha256"] == receipt["validated_payload_sha256"])
check("signed package accepted", lambda: revenue_report.validate_forecast_output(signed))

print("\n-- (b1) tamper result_sha256 and rehash every self-hash --")
b1 = copy.deepcopy(signed)
b1["result_sha256"] = hashlib.sha256(b"totally-different-artifact").hexdigest()
# a fully-informed attacker recomputes it, so emulate the strongest real move:
b1["result_sha256"] = canonical_sha256({k: v for k, v in b1.items() if k != "result_sha256"})
check("(b1) validate_forecast_output after result_sha256 rewrite",
      lambda: revenue_report.validate_forecast_output(b1))

print("\n-- (b2) mutate an attestation-record field (issuer) and rehash --")
b2 = copy.deepcopy(signed)
b2["publication_receipt"]["publication_attestation"]["issuer"] = "revenue-forecast/evil"
rehash(b2)
check("(b2) validate_publication_receipt", lambda: revenue_publication.validate_publication_receipt(b2))

print("\n-- (b3) drop the record, keep the host_signed label, rehash --")
b3 = copy.deepcopy(signed)
del b3["publication_receipt"]["publication_attestation"]
rehash(b3)
check("(b3) validate_publication_receipt", lambda: revenue_publication.validate_publication_receipt(b3))

print("\n-- (b4) move a signature onto a different payload (request_id swap) --")
b4 = copy.deepcopy(signed)
b4["publication_receipt"]["publication_attestation"]["request_id"] = "a" * 64
rehash(b4)
check("(b4) validate_publication_receipt", lambda: revenue_publication.validate_publication_receipt(b4))

print("\n-- (b5) extra key added to the record (closed-set check) --")
b5 = copy.deepcopy(signed)
b5["publication_receipt"]["publication_attestation"]["extra_note"] = "hello"
rehash(b5)
check("(b5) validate_publication_receipt", lambda: revenue_publication.validate_publication_receipt(b5))

print("\n-- (b6) flip label host_signed -> unattested but KEEP the record --")
b6 = copy.deepcopy(signed)
b6["publication_receipt"]["attestation_status"] = "unattested"
rehash(b6)
check("(b6) validate_publication_receipt (record still verified)",
      lambda: revenue_publication.validate_publication_receipt(b6))
