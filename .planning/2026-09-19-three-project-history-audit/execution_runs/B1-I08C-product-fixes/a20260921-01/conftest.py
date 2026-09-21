"""Attempt-root pytest bootstrap.

Redirects the publication registry BEFORE any production import so a formal
``run_forecast`` can never append to a repository registry from this attempt, no
matter which test file is selected.  The repo under test is chosen by
``B1_REPO_ROOT``.
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
