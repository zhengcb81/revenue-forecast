"""B1 — I-08-C product defects REM-01/02/03.

Consumer-level proof for the three product defects found by the I-08-C
independent review (`execution_runs/I-08-C/a20260919-01/review.md`, F1/F2/F3).

The tree under test is selected by ``B1_REPO_ROOT`` (an isolated copy, never the
production repo).  Expectations are frozen in this attempt's ``oracle.md``
(sha256 recorded in ``binding.json``) BEFORE any run.

REM-01 (HIGH)   attestation_status="host_signed" is a plain label:
                (a) it is not bound to any signature/issuer record;
                (b) attestation_capability() treats file existence as signing
                    capability, so a 5-byte .txt can mint "host_signed".
REM-02 (MEDIUM) validate_publication_receipt is hash-consistency only, not a
                security boundary -> must be documented/deprecated as such.
REM-03 (MEDIUM) segments[i].base_revenue is bound by NO output gate and renders
                into the official 分部表 -> must be bound.

REM-03 scope note (the reviewer's narrowing is adopted, not re-widened): company
totals were never forgeable through this path; the defect is a presentation-field
coverage gap in the per-segment opening base.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Tree selection + import order (the iso tree must win sys.path)
# ---------------------------------------------------------------------------
REPO = Path(os.environ["B1_REPO_ROOT"]).resolve()
SCRIPTS = REPO / "scripts"
TESTS = REPO / "tests"
for _p in (str(TESTS), str(SCRIPTS)):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
import revenue_core  # noqa: E402
from revenue_core import attestation_capability, run_forecast  # noqa: E402
import revenue_publication  # noqa: E402


def _last_failure():
    """Diagnostic accessor; absent on the unfixed tree (returns {} there, which
    makes the corresponding assertions fail loudly instead of at import time)."""
    getter = getattr(revenue_core, "attestation_last_failure", None)
    return getter() if callable(getter) else {}

from revenue_publication import validate_publication_receipt  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

DOMAIN = "revenue-forecast/publication-attestation/v1"
ISSUER = "revenue-forecast/host-b1"
KEY_ID = "rf-b1-test-key"
ATTESTATION_FIELDS = {
    "attestation_payload_schema_version",
    "domain_separator",
    "issuer",
    "key_id",
    "algorithm",
    "fingerprint",
    "request_id",
    "payload_sha256",
    "result_sha256",
    "receipt_sha256",
    "signed_at",
    "signature",
}

FAKE_PROVIDER_SOURCE = '''\
"""Bounded fake attestation provider for the B1-I08C card (isolated fixture)."""
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main() -> int:
    raw = sys.stdin.read()
    request = json.loads(raw)
    if os.environ.get("B1_FAKE_PROVIDER_MODE") == "refuse":
        sys.stderr.write("no private key available\\n")
        return 11
    private = Ed25519PrivateKey.from_private_bytes(b"\\x07" * 32)
    public = private.public_key().public_bytes_raw()
    payload = {k: v for k, v in request.items() if k != "canonical_payload_sha256"}
    signature = private.sign(canonical(payload).encode("ascii")).hex()
    response = {
        "attestation_response_schema_version": "1.0",
        "request_id": request["request_id"],
        "payload_sha256": request["payload_sha256"],
        "domain_separator": request["domain_separator"],
        "issuer": os.environ.get("B1_FAKE_PROVIDER_ISSUER", ""),
        "key_id": os.environ.get("B1_FAKE_PROVIDER_KEY_ID", ""),
        "fingerprint": hashlib.sha256(public).hexdigest()[:32],
        "algorithm": "ed25519",
        "signature": signature,
        "signed_at": "2026-07-12T00:00:00Z",
    }
    sys.stdout.write(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module", autouse=True)
def isolated_env(tmp_path_factory):
    """Never let a formal run_forecast touch a real registry."""
    saved = {
        name: os.environ.get(name)
        for name in (
            "REVENUE_PUBLICATION_REGISTRY",
            "REVENUE_ATTESTATION_PROVIDER",
            "REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS",
            "B1_FAKE_PROVIDER_ISSUER",
            "B1_FAKE_PROVIDER_KEY_ID",
            "B1_FAKE_PROVIDER_MODE",
        )
    }
    root = tmp_path_factory.mktemp("b1")
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(root / "publications.jsonl")
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
    os.environ.pop("B1_FAKE_PROVIDER_MODE", None)
    os.environ["B1_FAKE_PROVIDER_ISSUER"] = ISSUER
    os.environ["B1_FAKE_PROVIDER_KEY_ID"] = KEY_ID
    yield root
    for name, value in saved.items():
        os.environ.pop(name, None)
        if value is not None:
            os.environ[name] = value


@pytest.fixture(scope="module")
def workdir(tmp_path_factory):
    return tmp_path_factory.mktemp("b1_work")


@pytest.fixture(scope="module")
def fake_provider(workdir):
    """A real one-shot provider process; its private key never leaves the fixture."""
    path = workdir / "fake_attestation_provider.py"
    path.write_text(FAKE_PROVIDER_SOURCE, encoding="utf-8")
    return path


@pytest.fixture(scope="module")
def public_key_bytes():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private = Ed25519PrivateKey.from_private_bytes(b"\x07" * 32)
    return private.public_key().public_bytes_raw()


@pytest.fixture(scope="module")
def trusted_domain(workdir, public_key_bytes):
    """Trust file lives ONLY in the isolated attempt tmp dir (I-08-A R-PROV-2)."""
    path = workdir / "trusted_signer_public_keys.json"
    path.write_text(
        json.dumps(
            {
                "public_keys": [
                    {
                        "name": "b1-isolated-test-signer",
                        "key_id": KEY_ID,
                        "issuer": ISSUER,
                        "public_key": base64.b64encode(public_key_bytes).decode("ascii"),
                        "fingerprint": hashlib.sha256(public_key_bytes).hexdigest()[:32],
                    }
                ]
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _rehash(pkg):
    """Attacker move: recompute every NON-SECRET self-hash, keep the signed domain."""
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")}
    )
    record = receipt.get("publication_attestation")
    if isinstance(record, dict):
        # the attacker cannot forge the signature; updating the record's own
        # payload copies is exactly the "recompute what you can" move.
        record["payload_sha256"] = receipt["validated_payload_sha256"]
        record["result_sha256"] = "pending"
    receipt["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )
    if isinstance(record, dict):
        record["receipt_sha256"] = receipt["receipt_sha256"]
    pkg["result_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k != "result_sha256"}
    )
    if isinstance(record, dict):
        record["result_sha256"] = pkg["result_sha256"]
    return pkg


def _unattested_package():
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    return run_forecast(forecast_document())


def _with_provider(path):
    os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(path)


def _clear_provider():
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)


def _receipt_of(pkg):
    return pkg["publication_receipt"]


def _record_of(pkg):
    return _receipt_of(pkg).get("publication_attestation")


# ---------------------------------------------------------------------------
# REM-01
# ---------------------------------------------------------------------------
def test_rem01_a_label_only_flip_is_rejected():
    """Card case A-C2 on the product: the label must not be accepted on set
    membership.  Honest `unattested` package, ONLY the label flipped, every
    non-secret self-hash recomputed."""
    honest = _unattested_package()
    assert _receipt_of(honest)["attestation_status"] == "unattested"
    assert "publication_attestation" not in _receipt_of(honest)

    flipped = _rehash(copy.deepcopy(honest))
    flipped["publication_receipt"]["attestation_status"] = "host_signed"
    _rehash(flipped)

    with pytest.raises(ForecastInputError, match="attestation_missing_record"):
        validate_publication_receipt(flipped)
    with pytest.raises(ForecastInputError):
        validate_forecast_output(flipped)


@pytest.mark.parametrize(
    "kind",
    ["plain_txt", "bare_py", "sys_executable"],
)
def test_rem01_b_to_d_file_existence_is_not_signing_capability(
    kind, workdir, tmp_path_factory
):
    """REM-01(b): a path that EXISTS but has no proven signing capability must
    grant no capability and must not yield a `host_signed` label."""
    if kind == "plain_txt":
        target = workdir / "provider_is_just_text.txt"
        target.write_text("hello", encoding="utf-8")  # 5 bytes, exactly the reviewer's proof
        assert target.stat().st_size == 5
    elif kind == "bare_py":
        target = workdir / "provider_is_bare_script.py"
        target.write_text("print('not a provider')\n", encoding="utf-8")
    else:
        target = Path(sys.executable)
        assert target.is_file()

    _with_provider(target)
    try:
        assert attestation_capability() is False
        failure = _last_failure()
        assert isinstance(failure, dict) and failure.get("code")
        package = run_forecast(forecast_document())
        receipt = _receipt_of(package)
        assert receipt["attestation_status"] == "unattested"
        assert "publication_attestation" not in receipt
        # consumption side: an honest unattested publication stays consumable
        validate_publication_receipt(package)
        validate_forecast_output(package)
    finally:
        _clear_provider()


def test_rem01_e_trusted_provider_yields_verifiable_record(
    fake_provider, trusted_domain
):
    """Positive case: a provider that completes a bounded handshake with a key
    from the (isolated) trust domain produces a real, verifiable record."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        assert attestation_capability() is True
        package = run_forecast(forecast_document())
        receipt = _receipt_of(package)
        assert receipt["attestation_status"] == "host_signed"
        record = _record_of(package)
        assert isinstance(record, dict), "host_signed must carry a binding record"
        assert set(record) == ATTESTATION_FIELDS
        assert record["algorithm"] == "ed25519"
        assert record["domain_separator"] == DOMAIN
        assert record["issuer"] == ISSUER
        assert record["key_id"] == KEY_ID
        assert re.fullmatch(r"[0-9a-f]{32}", record["fingerprint"])
        assert re.fullmatch(r"[0-9a-f]{128}", record["signature"])
        assert record["payload_sha256"] == receipt["validated_payload_sha256"]
        assert record["result_sha256"] == package["result_sha256"]
        assert record["receipt_sha256"] == receipt["receipt_sha256"]
        validate_publication_receipt(package)
        validate_forecast_output(package)
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)


def test_rem01_f_untrusted_provider_is_not_host_signed(fake_provider, workdir):
    """A provider that answers correctly but whose key is NOT in the trust
    domain must not yield `host_signed` (or must yield a record that the
    consumer rejects)."""
    _with_provider(fake_provider)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)  # zero trusted keys
    try:
        assert attestation_capability() is False
        package = run_forecast(forecast_document())
        receipt = _receipt_of(package)
        assert receipt["attestation_status"] == "unattested"
        assert "publication_attestation" not in receipt
        failure = _last_failure()
        assert failure and failure.get("code") == "provider_key_untrusted"
        validate_publication_receipt(package)
        validate_forecast_output(package)
    finally:
        _clear_provider()


def test_rem01_g_replayed_record_is_rejected(fake_provider, trusted_domain):
    """A record that does not match the live payload/result/receipt must be
    rejected even when every self-hash the attacker can recompute is repaired."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        package = run_forecast(forecast_document())
        assert _receipt_of(package)["attestation_status"] == "host_signed"
        forged = copy.deepcopy(package)
        forged["confidence"]["score"] = float(forged["confidence"]["score"]) + 0.5
        _rehash(forged)
        with pytest.raises(ForecastInputError) as excinfo:
            validate_publication_receipt(forged)
        assert "attestation" in str(excinfo.value)
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)


def test_rem01_h_signed_record_is_repeatable_and_stable(fake_provider, trusted_domain):
    """R-REPLAY-1 (I-08-A): a previously issued signature is not a one-shot
    token — the same immutable artifact must keep verifying.  On the unfixed
    tree this node is RED for a structural reason: a `host_signed` label exists
    with no binding record at all."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        package = run_forecast(forecast_document())
        assert _receipt_of(package)["attestation_status"] == "host_signed"
        record = _record_of(package)
        assert isinstance(record, dict), "host_signed must carry a binding record"
        assert set(record) == ATTESTATION_FIELDS
        before = copy.deepcopy(package)
        validate_publication_receipt(package)
        validate_forecast_output(package)
        validate_publication_receipt(package)
        validate_forecast_output(package)
        assert package == before
        assert _receipt_of(package)["attestation_status"] == "host_signed"
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)


# ---------------------------------------------------------------------------
# REM-02
# ---------------------------------------------------------------------------
def test_rem02_receipt_layer_is_documented_as_non_security():
    """REM-02: `validate_publication_receipt` is hash-consistency only.  It must
    say so, name the function consumers must call instead, and export an
    explicit marker so a caller cannot mistake it for a gate."""
    doc = revenue_publication.validate_publication_receipt.__doc__ or ""
    assert "NOT a security boundary" in doc
    assert "validate_forecast_output" in doc
    marker = getattr(revenue_publication, "PublicationReceiptOnlyWarning", None)
    assert isinstance(marker, type) and issubclass(marker, Warning)
    assert marker.__name__ in doc
    # the module-level contract must say it too, so an API reader sees it
    module_doc = revenue_publication.__doc__ or ""
    assert "validate_forecast_output" in module_doc


# ---------------------------------------------------------------------------
# REM-03
# ---------------------------------------------------------------------------
def _forge_segment_base(package, delta=1000.0, index=0):
    """The reviewer's F3 construction: input_document, input_sha256 and
    parameter_trace stay COMPLETELY unchanged; only the presentation field moves."""
    forged = copy.deepcopy(package)
    forged["segments"][index]["base_revenue"] = (
        float(forged["segments"][index]["base_revenue"]) + delta
    )
    return _rehash(forged)


def test_rem03_forged_segment_base_revenue_is_rejected():
    """segments[i].base_revenue must be bound: a self-consistent forgery that
    renders into the official 分部表 must be rejected by the consumer."""
    honest = _unattested_package()
    validate_forecast_output(honest)
    forged = _forge_segment_base(honest)
    # the forgery is fully self-consistent at the hash layer (that is the point)
    validate_publication_receipt(forged)
    with pytest.raises(ForecastInputError, match="segment base revenue mismatch"):
        validate_forecast_output(forged)


def test_rem03_honest_package_still_accepted():
    """No regression: the honest package passes the new gates."""
    honest = _unattested_package()
    validate_publication_receipt(honest)
    validate_forecast_output(honest)


def test_rem03_moving_base_and_total_together_is_still_rejected():
    """A forgery that also moves `result["base_revenue"]` by the same amount
    (so a naive sum-vs-total check would pass) must still be caught by the
    per-segment parameter binding."""
    honest = _unattested_package()
    forged = copy.deepcopy(honest)
    forged["segments"][0]["base_revenue"] = (
        float(forged["segments"][0]["base_revenue"]) + 1000.0
    )
    forged["base_revenue"] = float(forged["base_revenue"]) + 1000.0
    _rehash(forged)
    with pytest.raises(ForecastInputError, match="segment base revenue mismatch"):
        validate_forecast_output(forged)
