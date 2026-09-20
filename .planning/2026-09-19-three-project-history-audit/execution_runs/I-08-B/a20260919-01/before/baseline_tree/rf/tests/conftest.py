"""Test isolation: the publication registry (R1.2) must never write to the
canonical repo's artifacts/registry from a test run."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolate_publication_registry(tmp_path_factory) -> None:
    directory = tmp_path_factory.mktemp("publication-registry")
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(directory)
    yield
    os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
