"""Attempt-root pytest bootstrap for INVEST-CORE-ATTEST-GATE.

Redirects the publication registry BEFORE any production import so a formal
``run_forecast`` can never append to a repository registry from this attempt,
no matter which test file is selected (mirror of B1's attempt conftest).

The tree under test is chosen by the test module itself: ``INVEST_CORE_DIR``
(default ``<attempt>/iso/invest-core``), and the revenue runtime is pinned to
``<attempt>/iso/revenue-forecast`` via ``REVENUE_FORECAST_DIR``.
"""
from __future__ import annotations

import os
from pathlib import Path

_attempt = Path(__file__).resolve().parent


def pytest_configure(config):  # noqa: ARG001 - pytest hook signature
    target = _attempt / "runner" / "registry"
    target.mkdir(parents=True, exist_ok=True)
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(target / "publications.jsonl")
    os.environ["REVENUE_FORECAST_DIR"] = str(_attempt / "iso" / "revenue-forecast")
    # The machine's global value (if any) must never leak into a run.
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
