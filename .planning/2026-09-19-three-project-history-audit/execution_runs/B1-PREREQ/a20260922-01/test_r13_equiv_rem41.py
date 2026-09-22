"""B1-PREREQ node R13-equivalent (REM-41 / B1 review F2).

Closes the frozen 12-node set's measured blind spot: every node in B1's frozen
``test_b1_rem.py`` that carries a ``publication_attestation`` record also
carries the ``host_signed`` label, so mutation **M6** (short-circuit
``validate_publication_attestation`` after the closed-set checks whenever the
label is not ``host_signed``) leaves that file 12/12 GREEN while making any
present record ignorable under an ``unattested`` label — the clause frozen in
B1's oracle r1 §3.1 ("a record that does not verify must never be
present-but-ignored") was unmeasured.

This node is frozen in THIS attempt's ``oracle.md`` §3.2 BEFORE any run
(sha256 pinned in ``freeze.json``). The tree under test is selected by
``B1_REPO_ROOT``:

* ``SRC/iso/fixed/rf``        -> expect 2 passed (GREEN arm)
* ``.../scratch/mutations/M6/rf`` -> expect node (a) RED, control GREEN
* ``SRC/iso/rf`` (unfixed)    -> expect node (a) RED (no record exists at all),
                                 control GREEN

Fixtures and helpers are IMPORTED from B1's frozen test module (byte-pinned
``636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16``), so the
setup is identical and nothing is re-implemented. B1's frozen test file itself
is NOT edited.
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import pytest

# B1's attempt (read-only): source of the frozen fixtures + test module.
_SRC_ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
_REPO = Path(os.environ["B1_REPO_ROOT"]).resolve()
for _p in (str(_REPO / "tests"), str(_REPO / "scripts"), str(_SRC_ATTEMPT)):
    if _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(_REPO / "tests"))
sys.path.insert(0, str(_REPO / "scripts"))
sys.path.insert(0, str(_SRC_ATTEMPT))

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


def test_rem41_a_present_record_is_verified_even_when_label_is_unattested(
    fake_provider, trusted_domain
):
    """REM-41: a record that does NOT verify must be rejected even when the
    label says `unattested` — present-but-ignored is forbidden (B1 oracle r1
    §3.1). RED under mutation M6, GREEN on the fixed tree."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        signed = run_forecast(forecast_document())
        status = _receipt_of(signed)["attestation_status"]
        assert status == "host_signed", (
            f"setup failed: label={status!r} "
            f"provider={os.environ.get('REVENUE_ATTESTATION_PROVIDER')!r} "
            f"trust={os.environ.get('REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS')!r} "
            f"last_failure={getattr(__import__('revenue_core'), 'attestation_last_failure', lambda: None)()!r}"
        )
        assert isinstance(_record_of(signed), dict), (
            "a host_signed package must carry a record before this node can "
            "measure record VERIFICATION (absence means the tree under test "
            "is the unfixed one, or issuance failed)"
        )

        # The attacker move: keep the (present) record, flip the label DOWN to
        # `unattested`, break the signature, rehash every self-hash.
        forged = copy.deepcopy(signed)
        forged["publication_receipt"]["attestation_status"] = "unattested"
        forged["publication_receipt"]["publication_attestation"]["signature"] = "0" * 128
        _rehash(forged)

        with pytest.raises(ForecastInputError) as excinfo:
            validate_publication_receipt(forged)
        assert "attestation" in str(excinfo.value), (
            f"rejected for the wrong reason: {excinfo.value}"
        )
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)


def test_rem41b_positive_control_valid_record_unattested_is_accepted(
    fake_provider, trusted_domain
):
    """Positive control: the SAME shape with a valid signature and consistent
    hashes is accepted with label `unattested`, so node (a) measures record
    verification and not the label itself. Stays GREEN under M6 by design
    (M6 only SKIPS verification; the honest path never depended on it)."""
    _with_provider(fake_provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trusted_domain)
    try:
        signed = run_forecast(forecast_document())
        ok = copy.deepcopy(signed)
        ok["publication_receipt"]["attestation_status"] = "unattested"
        _rehash(ok)
        validate_publication_receipt(ok)  # must not raise
        assert _receipt_of(ok)["attestation_status"] == "unattested"
        assert isinstance(_record_of(ok), dict)
    finally:
        _clear_provider()
        os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
