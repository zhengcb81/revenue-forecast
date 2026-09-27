"""WU-101 RED/audit tests: BASE-01..04 for the immutable-baseline gate."""
import hashlib
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from baseline_gate import (  # noqa: E402
    verify_head,
    verify_dirty_allowlist,
    verify_collection,
    verify_plan_hash,
    verify_config_hashes,
)


def _baseline(heads=None, node_ids=None, dirty=None, configs=None, plan_hash="ph") -> dict:
    heads = heads or {"revenue": "AAA", "filing": "BBB", "wiki": "CCC"}
    return {
        "plan_hash": plan_hash,
        "repos": {
            "revenue": {"path": "C:/repos/revenue", "head": heads["revenue"], "branch": "main", "dirty": []},
            "filing": {"path": "C:/repos/filing", "head": heads["filing"], "branch": "main", "dirty": []},
            "wiki": {"path": "C:/repos/wiki", "head": heads["wiki"], "branch": "master", "dirty": []},
        },
        "collection": node_ids or {
            "revenue": {"node_ids": ["a::t1", "a::t2"], "skipped": 0, "xfailed": 0},
            "filing": {"node_ids": [], "skipped": 0, "xfailed": 0},
            "wiki": {"node_ids": [], "skipped": 0, "xfailed": 0},
        },
        "user_dirty": dirty or ["llm_cost_log.csv", "source_manifests/archive"],
        "config_hashes": configs or {},
    }


def test_base01_head_mismatch_fails():
    b = _baseline()
    problems = verify_head(b, {"revenue": "DDD"})  # current HEAD differs
    assert any("revenue" in p and "DDD" in p for p in problems)


def test_base01_head_match_passes():
    b = _baseline()
    assert verify_head(b, {"revenue": "AAA", "filing": "BBB", "wiki": "CCC"}) == []


def test_base02_user_dirty_in_allowlist_fails():
    b = _baseline()
    # WU-101 must never let baseline dirty files into an implementation allowlist
    problems = verify_dirty_allowlist(
        b, ["llm_cost_log.csv", "source_manifests/archive/2026-08-07/retired-evidence.jsonl.gz"]
    )
    assert any("llm_cost_log.csv" in p for p in problems)


def test_base02_clean_allowlist_passes():
    b = _baseline()
    assert verify_dirty_allowlist(b, ["src/company_wiki/source_catalog/scanner.py"]) == []


def test_base03_node_removed_fails():
    b = _baseline()
    current = {
        "revenue": {"node_ids": ["a::t1"], "skipped": 0, "xfailed": 0},
        "filing": {"node_ids": [], "skipped": 0, "xfailed": 0},
        "wiki": {"node_ids": [], "skipped": 0, "xfailed": 0},
    }
    problems = verify_collection(b, current)
    assert any("a::t2" in p for p in problems)


def test_base03_skip_added_fails():
    b = _baseline()
    current = {
        "revenue": {"node_ids": ["a::t1", "a::t2"], "skipped": 3, "xfailed": 0},
        "filing": {"node_ids": [], "skipped": 0, "xfailed": 0},
        "wiki": {"node_ids": [], "skipped": 0, "xfailed": 0},
    }
    assert verify_collection(b, current)


def test_base04_plan_hash_mismatch_fails(tmp_path):
    plan = tmp_path / "task_plan.md"
    plan.write_text("new plan content", encoding="utf-8")
    assert verify_plan_hash(plan, "stale-hash")


def test_base04_plan_hash_match_passes(tmp_path):
    plan = tmp_path / "task_plan.md"
    plan.write_text("content", encoding="utf-8")
    expected = hashlib.sha256(b"content").hexdigest()
    assert verify_plan_hash(plan, expected) == []


def test_config_hash_mismatch_fails(tmp_path):
    cfg = tmp_path / "source_catalog.yaml"
    cfg.write_text("roots: []", encoding="utf-8")
    problems = verify_config_hashes({str(cfg): "deadbeef"}, {str(cfg): "cafebabe"})
    assert problems


def test_config_hash_match_passes(tmp_path):
    cfg = tmp_path / "source_catalog.yaml"
    cfg.write_text("roots: []", encoding="utf-8")
    h = hashlib.sha256(b"roots: []").hexdigest()
    assert verify_config_hashes({str(cfg): h}, {str(cfg): h}) == []


def test_capture_output_is_stable_json(tmp_path):
    """The capture manifest must be deterministic JSON (no timestamps inside)."""
    from baseline_gate import capture_manifest

    manifest = capture_manifest(
        repos={},  # injected; real capture fills these
        collection={},
        config_hashes={},
        plan_hash="ph",
        user_dirty=[],
    )
    first = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    second = json.dumps(capture_manifest({}, {}, {}, "ph", []), sort_keys=True, ensure_ascii=False)
    assert first == second
