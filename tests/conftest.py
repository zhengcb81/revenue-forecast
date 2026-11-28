"""Keep forecast publication tests from sharing or writing a checkout registry."""
from hashlib import sha256

import pytest


@pytest.fixture(autouse=True)
def isolated_publication_registry(request, tmp_path_factory, monkeypatch):
    # Resolve a private registry name without creating a temporary tree for
    # tests that never publish. Individual tests may supply a different
    # explicit registry to exercise multiple operations against one index.
    case = sha256(request.node.nodeid.encode("utf-8")).hexdigest()[:24]
    path = tmp_path_factory.getbasetemp() / f"publication-{case}.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(path))
