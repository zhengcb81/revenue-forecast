"""CA-106 side-effect ledger + independent oracle: fingerprints, diffs,
declared-vs-measured verification, privacy tokens."""

from __future__ import annotations

import json

import pytest

import uc.ledger as lg


def test_fingerprint_and_diff_detect_changes(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")
    before = lg.root_fingerprint(root)
    (root / "b.txt").write_text("b", encoding="utf-8")
    after = lg.root_fingerprint(root)
    diff = lg.diff_fingerprints(before, after)
    assert diff["file_count_delta"] == 1
    assert diff["added_files"] == 1
    assert diff["unchanged"] is False


def test_fingerprint_unchanged(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("a", encoding="utf-8")
    before = lg.root_fingerprint(root)
    assert lg.diff_fingerprints(before, lg.root_fingerprint(root))["unchanged"] is True


def test_paths_are_hashed_not_stored(tmp_path):
    root = tmp_path / "private-parent" / "private-root"
    root.mkdir(parents=True)
    (root / "secret-name.txt").write_text("x", encoding="utf-8")
    fingerprint = lg.root_fingerprint(root)
    serialized = json.dumps(fingerprint)
    assert "private-parent" not in serialized  # full path never stored
    assert "secret-name" in serialized  # basename kept for diagnosis
    assert "path_sha256" in serialized


def test_ledger_append_read_roundtrip(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    lg.append_entry(ledger, "parser_call", "parser", {"input_sha256": "a" * 64})
    lg.append_entry(ledger, "llm_call", "llm", {"model": "x"})
    entries = lg.read_ledger(ledger)
    assert [e["kind"] for e in entries] == ["parser_call", "llm_call"]


def test_unknown_kind_rejected(tmp_path):
    with pytest.raises(ValueError):
        lg.append_entry(tmp_path / "l.jsonl", "not_a_kind", None, None)


def test_verify_summary_match_and_mismatch(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    for _ in range(3):
        lg.append_entry(ledger, "parser_call", "parser", {})
    entries = lg.read_ledger(ledger)
    assert lg.verify_summary(entries, {"parser_call": 3}) == []
    problems = lg.verify_summary(entries, {"parser_call": 0})
    assert any("declared parser_call=0" in p for p in problems)


def test_verify_summary_reports_unclaimed(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    lg.append_entry(ledger, "db_write", None, {})
    entries = lg.read_ledger(ledger)
    problems = lg.verify_summary(entries, {})
    assert any("unclaimed db_write" in p for p in problems)


def test_count_by_kind(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    for _ in range(2):
        lg.append_entry(ledger, "lock_wait", None, {})
    lg.append_entry(ledger, "commit", None, {})
    counts = lg.count_by_kind(lg.read_ledger(ledger))
    assert counts == {"lock_wait": 2, "commit": 1}
