"""Reviewer-authored node R13 — NOT part of the frozen oracle.

The frozen 12-node set never exercises the clause "a record that IS present is
verified even when the label says `unattested`" with a *broken* record: R2/R3/R4
carry no record at all, and R1/R7 carry the `host_signed` label.  R13 closes that
gap: an `unattested`-labelled package whose record has an invalid Ed25519
signature must still be rejected, so a present record can never become
present-but-ignored.

Fixtures (fake_provider / trusted_domain / workdir) are imported from the frozen
test module so the setup is identical and nothing here re-implements the
provider.
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import pytest

_ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
_REPO = Path(os.environ["B1_REPO_ROOT"]).resolve()
for _p in (str(_REPO / "tests"), str(_REPO / "scripts"), str(_ATTEMPT)):
    if _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(_REPO / "tests"))
sys.path.insert(0, str(_REPO / "scripts"))
sys.path.insert(0, str(_ATTEMPT))

from contracts.evidence import ForecastInputError  # noqa: E402
from test_b1_rem import (  # noqa: E402
    _rehash,
    _receipt_of,
    _record_of,
    _with_provider,
    _clear_provider,
    fake_provider,  # noqa: F401 - pytest fixture
    trusted_domain,  # noqa: F401 - pytest fixture
    workdir,  # noqa: F401 - pytest fixture (dependency of fake_provider)
    public_key_bytes,  # noqa: F401 - pytest fixture (dependency of trusted_domain)
    isolated_env,  # noqa: F401 - pytest fixture (autouse registry redirect)
)
from revenue_core import run_forecast  # noqa: E402
from revenue_publication import validate_publication_receipt  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def test_r13_present_record_is_verified_even_when_label_is_unattested(
    fake_provider, trusted_domain
):
    """A record that does not verify must never be present-but-ignored."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        signed = run_forecast(forecast_document())
        status = _receipt_of(signed)["attestation_status"]
        assert status == "host_signed", (
            f"setup failed: label={status!r} provider={os.environ.get('REVENUE_ATTESTATION_PROVIDER')!r} "
            f"trust={os.environ.get('REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS')!r} "
            f"last_failure={getattr(__import__('revenue_core'), 'attestation_last_failure', lambda: None)()!r}"
        )
        assert isinstance(_record_of(signed), dict)

        forged = copy.deepcopy(signed)
        forged["publication_receipt"]["attestation_status"] = "unattested"
        forged["publication_receipt"]["publication_attestation"]["signature"] = "0" * 128
        _rehash(forged)

        with pytest.raises(ForecastInputError) as excinfo:
            validate_publication_receipt(forged)
        assert "attestation" in str(excinfo.value)
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)


def test_r13b_structurally_valid_record_with_unattested_label_is_accepted(
    fake_provider, trusted_domain
):
    """Positive control: the SAME shape with a valid signature+correct hashes is
    accepted, so R13 measures verification and not the label."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        signed = run_forecast(forecast_document())
        ok = copy.deepcopy(signed)
        ok["publication_receipt"]["attestation_status"] = "unattested"
        _rehash(ok)
        validate_publication_receipt(ok)
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
