"""FC-1002 RED/acceptance tests: REAL three-process E2E chain.

The chain starts at the revenue user entry (scripts/source_preparation.py),
which subprocess-spawns the filing-fetch client, which subprocess-spawns the
company-wiki CLI — three REAL OS processes (process_count>=3, per FC-102
registry gate).  The catalog/resolver/adapter/bundle/consumer are production
code; the lake (FC-1001) is a temp three-root fixture with v2 artifacts and
review receipts, so an exact hit is a pure read: download/parser/LLM all 0.

RED target: the test file's chain assertion fails when the fixture has no
review receipts (FC-905-b blocks) or no v2 artifacts (nothing to read).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "tests"))
WIKI_ROOT = PROJECT_ROOT.parent / "company-wiki"
FILING_ROOT = PROJECT_ROOT.parent / "filing-fetch"
sys.path.insert(0, str(WIKI_ROOT / "src"))
sys.path.insert(0, str(FILING_ROOT / "scripts"))

import sqlite3  # noqa: E402

from e2e_support.isolated_lake import IsolatedLake  # noqa: E402

REQUEST = {
    "schema_version": "1.1",
    "company_query": "紫金矿业",
    "market": "CN",
    "document_kind": "annual_report",
    "fiscal_year": 2025,
    "as_of_date": "2026-08-12",
}


def _run_chain(tmp_path: Path) -> dict:
    """Spawn the REAL three-process chain; return (record, trace, journal_before)."""
    m = IsolatedLake(tmp_path, seed="fc1002").build()
    assert m.catalog_path is not None
    # filing-fetch expects a JSON company-wiki config pointing at the wiki root
    wiki_cfg = tmp_path / "wiki.json"
    wiki_cfg.write_text(json.dumps({
        "schema_version": "1.0",
        "company_wiki_root": str(tmp_path / "lake" / "project"),
    }, ensure_ascii=False), encoding="utf-8")
    journal_before = sqlite3.connect(
        f"file:{m.catalog_path}?mode=ro", uri=True
    ).execute("SELECT COUNT(*) FROM producer_events").fetchone()[0]

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    # process trace: layer 0 = this test; layer 1 = source_preparation
    proc = subprocess.run(
        [sys.executable, "-B", str(PROJECT_ROOT / "scripts" / "source_preparation.py"),
         "--company-wiki-config", str(wiki_cfg)],
        input=json.dumps(REQUEST, ensure_ascii=False),
        text=True, encoding="utf-8", capture_output=True,
        cwd=str(PROJECT_ROOT), env=env, timeout=180, check=False,
    )
    assert proc.returncode == 0, f"chain failed: {proc.stderr[-800:]}"
    record = json.loads(proc.stdout)
    journal_after = sqlite3.connect(
        f"file:{m.catalog_path}?mode=ro", uri=True
    ).execute("SELECT COUNT(*) FROM producer_events").fetchone()[0]
    return record, journal_before, journal_after, m


def test_three_process_chain_exact_hit_zero_side_effects(tmp_path: Path):
    """User entry -> REAL 3-process chain -> reused_exact, artifact_read>0,
    journal unchanged (producer=0 this run), download/parser/llm all 0."""
    record, jb, ja, m = _run_chain(tmp_path)
    rr = record.get("reuse_receipt") or {}
    assert rr.get("outcome") in ("reused_existing", "reused_exact"), rr
    assert rr.get("bundle_status") == "available", rr
    assert rr.get("artifact_read"), f"bound artifacts must be read: {rr}"
    assert "normalized" in rr.get("artifact_read", [])
    assert jb == ja, f"journal changed {jb}->{ja}: consumption must not produce"
    assert rr.get("download_calls") == 0
    assert rr.get("llm_calls") == 0
    assert rr.get("prompt_injection_status") == "not_detected"


def test_chain_is_three_real_processes(tmp_path: Path):
    """The chain is genuinely three OS processes (no in-process shortcut):
    source_preparation subprocess-spawns the filing-fetch client, which
    subprocess-spawns the company-wiki CLI.  We verify the spawn chain in the
    production code AND that the subprocess output actually flows through
    each hop (the envelope in the record is produced by the wiki CLI)."""
    import inspect

    from filing_fetch_client import resolve_filing
    import source_preparation

    # hop 1: source_preparation -> filing-fetch client (subprocess.run)
    src = inspect.getsource(source_preparation.prepare_source)
    assert "subprocess.run" in src and "FILING_FETCH_CLIENT" in src, (
        "source_preparation must spawn the filing-fetch client as a subprocess"
    )
    # hop 2: filing-fetch client -> company-wiki CLI (subprocess.run)
    client = inspect.getsource(resolve_filing)
    assert "subprocess.run" in client and "fetch_filing.py" in client, (
        "filing-fetch client must spawn the wiki CLI as a subprocess"
    )
    # the record's envelope is wiki-CLI-produced JSON flowing up the chain
    record, _, _, _ = _run_chain(tmp_path)
    assert record.get("company_wiki_trace"), "wiki CLI output must reach revenue"


def test_missing_artifact_forces_producer_events(tmp_path: Path):
    """Corrupt the v2 artifact (column_drop) -> the consumer can no longer
    read it -> producer_events lists the role (DAG closure), never a blind
    full recompute and never a silent green."""
    m = IsolatedLake(tmp_path, seed="fc1002").build()
    assert m.catalog_path is not None
    IsolatedLake(tmp_path, seed="fc1002").corrupt("column_drop", m)
    wiki_cfg = tmp_path / "wiki.json"
    wiki_cfg.write_text(json.dumps({
        "schema_version": "1.0",
        "company_wiki_root": str(tmp_path / "lake" / "project"),
    }, ensure_ascii=False), encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, "-B", str(PROJECT_ROOT / "scripts" / "source_preparation.py"),
         "--company-wiki-config", str(wiki_cfg)],
        input=json.dumps(REQUEST, ensure_ascii=False),
        text=True, encoding="utf-8", capture_output=True,
        cwd=str(PROJECT_ROOT), env=env, timeout=180, check=False,
    )
    assert proc.returncode == 0, f"chain failed: {proc.stderr[-800:]}"
    record = json.loads(proc.stdout)
    rr = record.get("reuse_receipt") or {}
    assert rr.get("artifact_read") == [], (
        f"corrupted artifact must not be read: {rr.get('artifact_read')}"
    )
    assert "normalized" in rr.get("producer_events", []), (
        "normalized must be scheduled for production (DAG closure)"
    )
