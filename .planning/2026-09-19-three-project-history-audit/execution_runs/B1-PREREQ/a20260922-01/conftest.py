"""Attempt-root pytest bootstrap (B1-PREREQ).

Redirects the publication registry into THIS attempt BEFORE any production
import, so a formal ``run_forecast`` can never append to a repository registry
no matter which tree ``B1_REPO_ROOT`` selects (production, B1's iso trees, or
this attempt's mutation copy). Mirrors B1's attempt-root conftest.
"""
from __future__ import annotations

import os
from pathlib import Path

_attempt = Path(__file__).resolve().parent


def pytest_configure(config):  # noqa: ARG001 - pytest hook signature
    target = _attempt / "runner" / "registry"
    target.mkdir(parents=True, exist_ok=True)
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(target / "publications.jsonl")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
