"""Short, exclusive synthetic roots; boundary-checked cleanup only."""

from pathlib import Path
import shutil
import tempfile
import uuid
import pytest
from .fixtures import build


@pytest.fixture
def case_factory(monkeypatch):
    roots = []

    def factory(**options):
        root = Path(tempfile.gettempdir()) / ("rfp-" + uuid.uuid4().hex[:10])
        root.mkdir()
        roots.append(root)
        return build(root, monkeypatch, **options)

    try:
        yield factory
    finally:
        for root in roots:
            resolved = root.resolve()
            base = Path(tempfile.gettempdir()).resolve()
            assert resolved.is_relative_to(base) and resolved.name.startswith("rfp-")
            assert not any(
                p.is_symlink() or getattr(p, "is_junction", lambda: False)()
                for p in [resolved, *resolved.rglob("*")]
            )
            for p in resolved.rglob("*"):
                if p.is_file():
                    p.chmod(0o600)
            shutil.rmtree(resolved)


@pytest.fixture
def case(case_factory):
    return case_factory()
