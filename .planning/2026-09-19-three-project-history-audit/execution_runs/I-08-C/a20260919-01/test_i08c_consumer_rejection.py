"""I-08-C: consumers must reject forged receipts, cross-payload replay, unsigned structures.
Under test (READ-ONLY, by path; expectations frozen in oracle.md):
revenue_publication.validate_publication_receipt, revenue_report.validate_forecast_output /
validate_published_forecast, publication_registry.is_registered.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from publication_registry import RegistryError, is_registered  # noqa: E402
from revenue_core import attestation_capability, run_forecast  # noqa: E402
from revenue_publication import validate_publication_receipt  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def readonly_env(tmp_path_factory):
    """Formal run_forecast REGISTERS — redirect registry to temp; repo stays read-only."""
    old_reg = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
    old_prov = os.environ.get("REVENUE_ATTESTATION_PROVIDER")
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(tmp_path_factory.mktemp("i08c_registry") / "publications.jsonl")
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    yield
    for name, value in (("REVENUE_PUBLICATION_REGISTRY", old_reg), ("REVENUE_ATTESTATION_PROVIDER", old_prov)):
        os.environ.pop(name, None)
        if value is not None:
            os.environ[name] = value


def _mutated_document():
    doc = forecast_document()
    pid = doc["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    next(p for p in doc["parameters"] if p["parameter_id"] == pid)["value"] *= 1.05
    return finalize_contract(doc)


def _rehash(pkg):
    """Attacker move: recompute every NON-SECRET self-hash, keep signed domain."""
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")})
    receipt["receipt_sha256"] = canonical_sha256({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    pkg["result_sha256"] = canonical_sha256({k: v for k, v in pkg.items() if k != "result_sha256"})
    return pkg


@pytest.fixture(scope="module")
def S(readonly_env):  # legit signed package: production issuer, provider present
    os.environ["REVENUE_ATTESTATION_PROVIDER"] = sys.executable
    try:
        return run_forecast(forecast_document())
    finally:
        os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)


@pytest.fixture(scope="module")
def U(readonly_env):  # explicit unattested formal package
    return run_forecast(forecast_document())


@pytest.fixture(scope="module")
def D(readonly_env):  # draft package
    return run_forecast(forecast_document(), mode="draft")


@pytest.fixture(scope="module")
def S2(readonly_env):  # different input anchor, formal
    return run_forecast(_mutated_document())


# --- A-C1: legit signed package passes, repeatably -----------------------------

def test_e1_legit_signed_package_passes_repeatably(S):
    assert S["publication_receipt"]["attestation_status"] == "host_signed"
    validate_publication_receipt(S)
    validate_forecast_output(S)
    validate_publication_receipt(S)  # repeated read still passes
    validate_forecast_output(S)


# --- A-C3 / A-C5: forged and replayed receipts ---------------------------------
def test_e2_forged_payload_with_original_receipt_rejected(S):
    forged = copy.deepcopy(S)
    forged["segments"][0]["base_revenue"] = forged["segments"][0]["base_revenue"] + 1
    with pytest.raises(ForecastInputError, match="validated_payload_sha256 mismatch"):
        validate_publication_receipt(forged)


def test_e3_forged_gate_ids_and_context_rejected(S):
    forged = copy.deepcopy(S)
    forged["publication_receipt"]["gate_ids"].append("sensitivity_shock_recomputation")
    with pytest.raises(ForecastInputError, match="gate_ids mismatch"):
        validate_publication_receipt(forged)
    forged2 = copy.deepcopy(S)
    forged2["publication_receipt"]["verification_context_sha256"] = "0" * 64
    with pytest.raises(ForecastInputError, match="verification context mismatch"):
        validate_publication_receipt(forged2)


def test_e5_whole_receipt_replayed_onto_other_payload_rejected(S, S2):
    replayed = copy.deepcopy(S2)
    replayed["publication_receipt"] = copy.deepcopy(S["publication_receipt"])
    with pytest.raises(ForecastInputError, match="publication_receipt"):
        validate_publication_receipt(replayed)


def test_e4_verification_context_mutation_rejected(S, S2):
    """E4 (oracle r1 line 54, IMPLEMENTED in r3): mutating the signed
    `verification_context_sha256` is rejected, and recomputing the non-secret
    self-hashes does not repair it.  `expected` comes from the source text
    (`revenue_publication.py:232-240`, `:85-93`); the correct value used in the
    last case is reconstructed from literals, never read from the fixture.
    """
    # E4a: mutate the verification-context digest only.
    mutated = copy.deepcopy(S)
    mutated["publication_receipt"]["verification_context_sha256"] = "0" * 64
    with pytest.raises(ForecastInputError, match="verification context mismatch"):
        validate_publication_receipt(mutated)
    with pytest.raises(ForecastInputError):
        validate_forecast_output(mutated)

    # E4b: attacker also recomputes every non-secret self-hash — still rejected.
    rehashed = copy.deepcopy(mutated)
    _rehash(rehashed)
    with pytest.raises(ForecastInputError, match="verification context mismatch"):
        validate_publication_receipt(rehashed)

    # E4c: a context digest that is valid, but belongs to a DIFFERENT input.
    foreign_context = canonical_sha256(
        {
            "validated_input_sha256": S2["input_sha256"],
            "executed_gate_ids": ["output_recomputation"],
            "validator_version": "4.1.0",
        }
    )
    assert foreign_context != S["publication_receipt"]["verification_context_sha256"]
    grafted = copy.deepcopy(S)
    grafted["publication_receipt"]["verification_context_sha256"] = foreign_context
    with pytest.raises(ForecastInputError, match="verification context mismatch"):
        validate_publication_receipt(grafted)

    # E4d: the correct digest is necessary AND sufficient for this gate, so the
    # three rejections above fail for the context binding and nothing else.
    correct_context = canonical_sha256(
        {
            "validated_input_sha256": S["input_sha256"],
            "executed_gate_ids": ["output_recomputation"],
            "validator_version": "4.1.0",
        }
    )
    assert correct_context == S["publication_receipt"]["verification_context_sha256"]
    repaired = copy.deepcopy(S)
    repaired["publication_receipt"]["verification_context_sha256"] = correct_context
    validate_publication_receipt(repaired)


def test_e6_recomputed_self_hashes_do_not_repair_value_forgery(S):
    """E6: recomputing non-secret self-hashes fixes the receipt layer alone
    (limitation); the dispatcher still rejects via bound recomputation."""
    forged = copy.deepcopy(S)
    forged["base_revenue"] = forged["base_revenue"] + 1
    _rehash(forged)
    validate_publication_receipt(forged)  # limitation, frozen in oracle E6
    with pytest.raises(ForecastInputError):
        validate_forecast_output(forged)


def test_e13_segment_base_revenue_not_bound_by_output_gates(S):
    """E13 (pinned gap, oracle): self-hash-consistent segment base forgery
    passes even the strong dispatcher (empirical, reported to reviewer)."""
    forged = copy.deepcopy(S)
    forged["segments"][0]["base_revenue"] = forged["segments"][0]["base_revenue"] + 1
    _rehash(forged)
    validate_publication_receipt(forged)
    validate_forecast_output(forged)  # pinned: accepted by current gates


def test_e7_registry_anchor_does_not_admit_forged_package(S):
    assert is_registered(S["input_sha256"]) is True
    forged = copy.deepcopy(S)
    forged["base_revenue"] = forged["base_revenue"] + 1
    _rehash(forged)
    with pytest.raises(ForecastInputError):
        validate_forecast_output(forged)  # is_registered(input)=True is not admission


def test_e8_old_verification_context_on_other_input_rejected(S, S2):
    forged = copy.deepcopy(S2)
    forged["publication_receipt"] = copy.deepcopy(S["publication_receipt"])
    _rehash(forged)  # self-consistent hashes, OLD signed context/input anchor kept
    with pytest.raises(ForecastInputError, match="validated_input_sha256 mismatch"):
        validate_publication_receipt(forged)
    with pytest.raises(ForecastInputError):
        validate_forecast_output(forged)


# --- A-C2: unsigned / draft structures -----------------------------------------

def test_e9_draft_package_rejected_by_formal_consumer(D):
    with pytest.raises(ForecastInputError, match="gate_ids mismatch"):
        validate_publication_receipt(D)
    with pytest.raises(ForecastInputError):
        validate_forecast_output(D)


def test_e10_result_without_receipt_rejected():
    bare = run_forecast(forecast_document())
    bare.pop("publication_receipt")
    with pytest.raises(ForecastInputError, match="missing field: publication_receipt"):
        validate_publication_receipt(bare)


def test_e11_host_signed_label_flip_is_not_bound_at_consumption(U):
    """KNOWN GAP (oracle E11): the label is only set-membership checked; no
    consumption-side attestation verification exists in this tree."""
    assert attestation_capability() is False  # issuance gate present
    flipped = copy.deepcopy(U)
    assert flipped["publication_receipt"]["attestation_status"] == "unattested"
    flipped["publication_receipt"]["attestation_status"] = "host_signed"
    _rehash(flipped)
    validate_publication_receipt(flipped)  # GAP: label forgery accepted at receipt layer
    validate_forecast_output(flipped)  # GAP: strong dispatcher does not bind the label


# --- registry fail-closed (A-C4 integrity precondition) ------------------------

def test_e12_registry_fail_closed_on_corruption(S):
    path = Path(os.environ["REVENUE_PUBLICATION_REGISTRY"])
    path.chmod(0o666)  # registry sets its file read-only after each append
    lines = path.read_text(encoding="utf-8").splitlines()
    entry = json.loads(lines[0])
    entry["result_sha256"] = "f" * 64
    lines[0] = json.dumps(entry, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(RegistryError):
        is_registered(S["input_sha256"])
