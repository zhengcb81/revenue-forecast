"""Exclusive synthetic owner roots; no publication or business data are touched."""
from pathlib import Path
import shutil
import tempfile
import uuid
import pytest
from b34_release.test_research_identity import anchored


@pytest.fixture
def case():
    root = Path(tempfile.gettempdir()) / ("rfms-" + uuid.uuid4().hex[:10])
    root.mkdir()
    try:
        run, anchor = anchored(root)
        yield {"root": root, "run": run, "data": {"as_of_date": "2026-11-01",
               "sources": [anchor["source"], {
                   "source_id": "controlled_release", "source_type": "company_release",
                   "title": "Synthetic company release", "publisher": "Synthetic issuer",
                   "url": "https://example.org/official-release", "published_date": "2026-10-26",
                   "accessed_date": "2026-11-01", "page_or_section": "Synthetic section",
                   "capture": {"capture_schema_version": "1.0", "capture_method": "api_response",
                       "tool_name": "tavily_extract", "tool_call_id": "synthetic-request",
                       "captured_date": "2026-11-01", "snapshot_sha256": "",
                       "content_treatment": "untrusted_data_only",
                       "prompt_injection_status": "not_detected"},
               }], "parameters": [{"source_ids": ["controlled_release"]}]}}
    finally:
        resolved = root.resolve()
        assert resolved.is_relative_to(Path(tempfile.gettempdir()).resolve())
        assert resolved.name.startswith("rfms-")
        assert not any(p.is_symlink() or getattr(p, "is_junction", lambda: False)()
                       for p in [resolved, *resolved.rglob("*")])
        for path in resolved.rglob("*"):
            if path.is_file():
                path.chmod(0o600)
        shutil.rmtree(resolved)
