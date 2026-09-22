"""INVEST-CORE-ATTEST-GATE — REM-01 consumer-side guard (cross-repo card).

The defect (this card's DECISIVE site): ``invest_contracts.adapt_revenue``
gates publication acceptance on ``attestation_status == "host_signed"``
WITHOUT verifying a binding record, so a forged label is consumed as
host-signed.  Expectations are frozen in this attempt's ``oracle.md`` (sha256
recorded in ``before/frozen_artifacts.json``) BEFORE any run.

Tree selection (B1 pattern): the consumer under test is ``INVEST_CORE_DIR``
(default ``iso/invest-core`` = pristine/UNFIXED for RED; ``iso/invest-core-
fixed`` for GREEN; ``iso/invest-core-mutant`` for the mutation arm).  The
revenue runtime is always the attempt-local ``iso/revenue-forecast`` copy.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Tree selection — must happen BEFORE any invest_contracts import
# ---------------------------------------------------------------------------
ATTEMPT = Path(__file__).resolve().parent
CONSUMER_DIR = Path(
    os.environ.get("INVEST_CORE_DIR", str(ATTEMPT / "iso" / "invest-core"))
).resolve()
RF_DIR = Path(
    os.environ.get("REVENUE_FORECAST_DIR", str(ATTEMPT / "iso" / "revenue-forecast"))
).resolve()
# Pin the runtime explicitly: the machine's global REVENUE_FORECAST_DIR points
# at the Projects repo and must never be what these runs import.
os.environ["REVENUE_FORECAST_DIR"] = str(RF_DIR)

for _name in [m for m in list(sys.modules) if m.startswith("invest_contracts")]:
    del sys.modules[_name]
_CONSUMER_SCRIPTS = str(CONSUMER_DIR / "scripts")
while _CONSUMER_SCRIPTS in sys.path:
    sys.path.remove(_CONSUMER_SCRIPTS)
sys.path.insert(0, str(RF_DIR / "tests"))
sys.path.insert(0, str(RF_DIR / "scripts"))
sys.path.insert(0, _CONSUMER_SCRIPTS)

import invest_contracts  # noqa: E402
from invest_contracts import (  # noqa: E402
    InvestmentArtifactError,
    adapt_revenue,
    canonical_sha256,
)

# Fail-closed tree check: the executed bytes must be the selected arm's bytes.
_expected = CONSUMER_DIR / "scripts" / "invest_contracts.py"
_actual = Path(invest_contracts.__file__).resolve()
assert _actual == _expected, f"wrong consumer tree: imported {_actual}, wanted {_expected}"

from revenue_core import run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

# ---------------------------------------------------------------------------
# Constants mirroring the I-08-A E27/G4 record shape (oracle §2)
# ---------------------------------------------------------------------------
DOMAIN = "revenue-forecast/publication-attestation/v1"
ISSUER = "invest-core-attest-gate-fixture"
KEY_ID = "ic-gate-fixture-key"
REQUEST_SCHEMA_VERSION = "1.0"
SENTINEL = "0" * 64
ATTESTATION_FIELDS = {
    "attestation_payload_schema_version",
    "domain_separator",
    "issuer",
    "key_id",
    "algorithm",
    "fingerprint",
    "request_id",
    "payload_sha256",
    "signed_at",
    "signature",
}
# Fixture-only throwaway key. It exists ONLY inside this test process (in
# memory); its public part is written to a pytest tmp trust file. Nothing in
# any repository, config, or install surface ever receives it. This card
# never signs anything outside its own test run.
_FIXTURE_KEY_BYTES = b"\x23" * 32


# ---------------------------------------------------------------------------
# Environment isolation (function-scoped save/restore)
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def isolated_attestation_env():
    saved = {
        name: os.environ.get(name)
        for name in ("REVENUE_ATTESTATION_PROVIDER", "REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS")
    }
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
    yield
    for name, value in saved.items():
        os.environ.pop(name, None)
        if value is not None:
            os.environ[name] = value


@pytest.fixture(scope="module")
def work(tmp_path_factory):
    return tmp_path_factory.mktemp("ic_gate")


# ---------------------------------------------------------------------------
# Signing helpers (fixture key, in-memory only)
# ---------------------------------------------------------------------------
def _attestation_request(payload_sha256: str, request_id: str) -> dict:
    return {
        "attestation_request_schema_version": REQUEST_SCHEMA_VERSION,
        "domain_separator": DOMAIN,
        "request_id": request_id,
        "payload_sha256": payload_sha256,
        "result_sha256": SENTINEL,
        "canonical_payload_sha256": payload_sha256,
    }


def _fixture_sign(request: dict) -> tuple[str, str]:
    """Sign the canonical request with the fixture key; return (signature, fingerprint)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private = Ed25519PrivateKey.from_private_bytes(_FIXTURE_KEY_BYTES)
    public = private.public_key().public_bytes_raw()
    signature = private.sign(canonical_sha256(request).encode("ascii")).hex()
    fingerprint = hashlib.sha256(public).hexdigest()[:32]
    return signature, fingerprint


@pytest.fixture(scope="module")
def trust_file(work):
    """Isolated trust anchor under the pytest tmp dir ONLY (oracle §4)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import base64

    private = Ed25519PrivateKey.from_private_bytes(_FIXTURE_KEY_BYTES)
    public = private.public_key().public_bytes_raw()
    fingerprint = hashlib.sha256(public).hexdigest()[:32]
    path = work / "trusted_signer_public_keys.json"
    path.write_text(
        json.dumps(
            {
                "public_keys": [
                    {
                        "name": "ic-gate-fixture-signer",
                        "key_id": KEY_ID,
                        "issuer": ISSUER,
                        "public_key": base64.b64encode(public).decode("ascii"),
                        "fingerprint": fingerprint,
                    }
                ]
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _use_trust(path) -> None:
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(path)


# ---------------------------------------------------------------------------
# Package fixtures — every mutation recomputes every non-secret self-hash
# (the strongest hash-recomputing attacker, B1's `_rehash` move)
# ---------------------------------------------------------------------------
def _rehash(pkg: dict) -> dict:
    """Recompute every non-secret self-hash after a mutation.

    ``validated_payload_sha256`` is a digest of the payload EXCLUDING the
    receipt, so attaching/changing a record never changes it; recomputing it
    is a no-op there and keeps the honest case honest.  ``receipt_sha256`` and
    ``result_sha256`` then cover the mutated receipt (and the record inside
    it).  A node that wants a payload BINDING mismatch stamps the record's
    own ``payload_sha256`` copy separately (R2) — the receipt digest stays
    correct, the record copy does not, which is exactly E16's question.
    """
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")}
    )
    receipt["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )
    pkg["result_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k != "result_sha256"}
    )
    return pkg


def _forge_label(pkg: dict) -> dict:
    """R1a: ONLY the label moves to host_signed; no record exists."""
    pkg["publication_receipt"]["attestation_status"] = "host_signed"
    return _rehash(pkg)


def _attach_record(pkg: dict, *, payload: str | None = None,
                   signature: str | None = None, fingerprint: str | None = None,
                   extra_field: bool = False) -> dict:
    """R2..R5/P1: attach a publication_attestation record to an honest package.

    ``payload`` overrides the stamped ``payload_sha256`` (R2); ``signature``
    overrides the signature bytes (R3); ``fingerprint`` overrides the signer
    identity (R3b); ``extra_field`` adds a key outside the closed set (R4).
    The signature always covers exactly what is stamped, so each negative node
    is decided ONLY by the check it targets.
    """
    receipt = pkg["publication_receipt"]
    receipt["attestation_status"] = "host_signed"
    payload_value = payload if payload is not None else receipt["validated_payload_sha256"]
    request_id = hashlib.sha256(b"invest-core-attest-gate-request").hexdigest()
    request = _attestation_request(payload_value, request_id)
    sig, fp = _fixture_sign(request)
    record = {
        "attestation_payload_schema_version": REQUEST_SCHEMA_VERSION,
        "domain_separator": DOMAIN,
        "issuer": ISSUER,
        "key_id": KEY_ID,
        "algorithm": "ed25519",
        "fingerprint": fingerprint if fingerprint is not None else fp,
        "request_id": request_id,
        "payload_sha256": payload_value,
        "signed_at": "2026-09-22T00:00:00Z",
        "signature": signature if signature is not None else sig,
    }
    if extra_field:
        record["extra_note"] = "outside the closed set"
    receipt["publication_attestation"] = record
    return _rehash(pkg)


@pytest.fixture(scope="module")
def honest():
    """An honest formal publication: label unattested, no record (oracle §4)."""
    provider_saved = os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    try:
        pkg = run_forecast(forecast_document())
    finally:
        if provider_saved is not None:
            os.environ["REVENUE_ATTESTATION_PROVIDER"] = provider_saved
    receipt = pkg["publication_receipt"]
    assert receipt["attestation_status"] == "unattested"
    assert "publication_attestation" not in receipt
    return pkg


@pytest.fixture(scope="module")
def issuance_minted(work):
    """R1b fixture FROM B1'S EVIDENCE: production issuance mints `host_signed`
    from a 5-byte `.txt` provider, carrying NO binding record (issuance fix
    not promoted — handoff discloses this)."""
    target = work / "provider_is_just_text.txt"
    target.write_text("hello", encoding="utf-8")
    assert target.stat().st_size == 5
    saved = os.environ.get("REVENUE_ATTESTATION_PROVIDER")
    os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(target)
    try:
        pkg = run_forecast(forecast_document())
    finally:
        if saved is None:
            os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
        else:
            os.environ["REVENUE_ATTESTATION_PROVIDER"] = saved
    receipt = pkg["publication_receipt"]
    # Issuance fingerprint (pre-assertion): label minted, record absent.
    assert receipt["attestation_status"] == "host_signed"
    assert "publication_attestation" not in receipt
    return pkg


# ---------------------------------------------------------------------------
# R-nodes — the 7 declared RED on the unfixed consumer (oracle §4)
# ---------------------------------------------------------------------------
def test_r1a_label_flip_without_record_is_rejected(honest):
    """R1a: label-only forgery on a content-valid package must be rejected."""
    pkg = _forge_label(copy.deepcopy(honest))
    with pytest.raises(InvestmentArtifactError, match="attestation_missing_record"):
        adapt_revenue(pkg)


def test_r1b_issuance_minted_host_signed_without_record_is_rejected(issuance_minted):
    """R1b: the label minted by production issuance (5-byte .txt, B1 evidence)
    with no record must be rejected at consumption."""
    with pytest.raises(InvestmentArtifactError, match="attestation_missing_record"):
        adapt_revenue(copy.deepcopy(issuance_minted))


def test_r2_record_payload_hash_mismatch_is_rejected(honest, trust_file):
    """R2: record present but its payload digest does not bind this receipt
    (E16); the signature is valid for the STAMPED value, so only the binding
    check can catch it."""
    _use_trust(trust_file)
    pkg = _attach_record(copy.deepcopy(honest), payload="0" * 64)
    with pytest.raises(
        InvestmentArtifactError, match="attestation_payload_hash_mismatch"
    ):
        adapt_revenue(pkg)


def test_r3_record_signature_invalid_is_rejected(honest, trust_file):
    """R3: shape + binding correct, trusted fingerprint, corrupt signature
    (E14)."""
    _use_trust(trust_file)
    pkg = _attach_record(copy.deepcopy(honest), signature="0" * 128)
    with pytest.raises(InvestmentArtifactError, match="attestation_signature_invalid"):
        adapt_revenue(pkg)


def test_r3b_untrusted_fingerprint_is_rejected(honest, trust_file):
    """R3b: self-consistent record signed by a key outside the trust domain
    (E20), with the anchor configured."""
    _use_trust(trust_file)
    pkg = _attach_record(copy.deepcopy(honest), fingerprint="ab" * 16)
    with pytest.raises(InvestmentArtifactError, match="provider_key_untrusted"):
        adapt_revenue(pkg)


def test_r4_record_extra_field_is_rejected(honest, trust_file):
    """R4: the field set is closed — one extra key rejects (fields)."""
    _use_trust(trust_file)
    pkg = _attach_record(copy.deepcopy(honest), extra_field=True)
    with pytest.raises(InvestmentArtifactError, match="attestation_payload_fields"):
        adapt_revenue(pkg)


def test_r5_valid_record_without_trust_anchor_is_rejected(honest):
    """R5: no trust anchor (today's production state — the anchor file is
    absent everywhere) ⇒ a host_signed claim cannot be verified ⇒ fail closed."""
    pkg = _attach_record(copy.deepcopy(honest))
    with pytest.raises(InvestmentArtifactError, match="provider_key_untrusted"):
        adapt_revenue(pkg)


# ---------------------------------------------------------------------------
# P/B nodes — positive control + frozen existing behavior (oracle §4)
# ---------------------------------------------------------------------------
def test_p1_valid_record_is_accepted_positive_control(honest, trust_file):
    """P1: a record that is shaped, payload-bound and signature-verified
    against the isolated trust anchor is accepted as host_signed."""
    _use_trust(trust_file)
    pkg = _attach_record(copy.deepcopy(honest))
    adapter = adapt_revenue(pkg)
    assert adapter["attestation_verification"] == "host_signed"
    assert "annual_revenue" in adapter


def test_b1_unattested_default_rejected_unchanged(honest):
    """B1: label != host_signed keeps existing behavior — default policy
    still rejects an unattested formal artifact."""
    with pytest.raises(InvestmentArtifactError, match="unattested"):
        adapt_revenue(copy.deepcopy(honest))


def test_b2_unattested_bypass_traced_unchanged(honest):
    """B2: label != host_signed keeps existing behavior — the explicit
    downgrade is still recorded, not silently upgraded or blocked."""
    adapter = adapt_revenue(
        copy.deepcopy(honest), require_attestation=False
    )
    assert adapter["attestation_verification"] == "unattested_bypassed"
