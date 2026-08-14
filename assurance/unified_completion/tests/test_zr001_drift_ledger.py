"""ZR-001 drift ledger structure and binding guards.

The ledger is the mandatory exit artifact of ZR-001.  These tests pin:

- schema/enum discipline (classification vocabulary, successor references
  resolve in the frozen CA/ZR DAG);
- frozen-triplet binding (the ledger must name the exact three HEADs the
  replays ran against, and every replay evidence file must bind its own
  repo head to the same triplet — replaying against a floating sibling is
  rejected);
- evidence integrity (every bound evidence file must exist with the exact
  recorded sha256);
- the canonical ledger hash (recomputed from the ledger content);
- coverage of the four mandated counterexample families and a real-catalog
  fingerprint that proves the read-only queries left the catalog unchanged.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from conftest import REPO_ROOT

from uc.dag import load_dag

EVIDENCE_DIR = REPO_ROOT / "assurance" / "unified_completion" / "replays" / "evidence"
LEDGER_PATH = (
    REPO_ROOT
    / "assurance"
    / "unified_completion"
    / "receipts"
    / "ZR-001"
    / "drift_ledger.json"
)

FROZEN_TRIPLET = {
    "revenue": "dc41ef335b0c71fc22610201b235a33528d3e950",
    "filing": "83c638e76e40890262746cdf02b6df495dcb4031",
    "wiki": "ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875",
}

CLASSIFICATIONS = {"still-failing", "already-satisfied", "superseded", "blocked"}
MANDATORY_FAMILIES = {
    "zijin_exact_reuse",
    "old_artifact",
    "dropbox",
    "draft_renderer",
}
EVIDENCE_HEAD_FIELDS = {
    "r1_generator_schema_drift.json": ("revenue_head", "revenue"),
    "r2_validate_only_writes_registry.json": ("revenue_head", "revenue"),
    "r3_draft_renderer_gate_mismatch.json": ("revenue_head", "revenue"),
    "r4_publication_non_transactional.json": ("revenue_head", "revenue"),
    "w1_catalog_read_path_writes.json": ("wiki_head", "wiki"),
    "f1_external_root_default_rejected.json": ("filing_head", "filing"),
    "f2_lock_error_misclassified.json": ("filing_head", "filing"),
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def test_ledger_exists_and_hashes() -> None:
    assert LEDGER_PATH.exists(), "drift_ledger.json is the mandatory ZR-001 artifact"
    payload = _ledger()
    assert payload["schema_version"] == 1
    assert payload["unit"] == "ZR-001"
    recomputed = _canonical_sha256(
        {key: value for key, value in payload.items() if key != "ledger_sha256"}
    )
    assert payload["ledger_sha256"] == recomputed


def test_ledger_freezes_the_exact_triplet() -> None:
    payload = _ledger()
    assert payload["triplet"] == {
        "revenue": FROZEN_TRIPLET["revenue"],
        "filing": FROZEN_TRIPLET["filing"],
        "wiki": FROZEN_TRIPLET["wiki"],
        "branches": {"revenue": "fcap", "filing": "fcap", "wiki": "fcap"},
    }


def test_evidence_heads_bind_to_the_frozen_triplet() -> None:
    payload = _ledger()
    for name in payload["evidence_binding"]:
        if name not in EVIDENCE_HEAD_FIELDS:
            continue
        field, repo = EVIDENCE_HEAD_FIELDS[name]
        data = json.loads((EVIDENCE_DIR / name).read_text(encoding="utf-8"))
        assert data[field] == FROZEN_TRIPLET[repo], (
            f"{name} was replayed against {data[field]!r}, not the frozen "
            f"{repo} HEAD {FROZEN_TRIPLET[repo]!r}"
        )


def test_every_bound_evidence_file_exists_with_matching_sha() -> None:
    payload = _ledger()
    assert payload["evidence_binding"], "ledger must bind its evidence files"
    for name, expected in payload["evidence_binding"].items():
        path = EVIDENCE_DIR / name
        assert path.exists(), f"bound evidence missing: {name}"
        assert _sha256_file(path) == expected, f"evidence changed after binding: {name}"


def test_every_bound_replay_script_exists_with_matching_sha() -> None:
    payload = _ledger()
    assert payload["replay_binding"], "ledger must bind its replay scripts"
    replay_dir = EVIDENCE_DIR.parent
    for name, expected in payload["replay_binding"].items():
        path = replay_dir / name
        assert path.exists(), f"bound replay script missing: {name}"
        assert _sha256_file(path) == expected, (
            f"replay script changed after binding: {name}"
        )


def test_item_classification_vocabulary() -> None:
    payload = _ledger()
    items = payload["items"]
    assert len(items) >= 12, "the counterexample families must all be itemized"
    for item in items:
        assert item["classification"] in CLASSIFICATIONS, item["id"]
        assert item["successors"], f"{item['id']} must name successor work units"
        assert item["evidence"], f"{item['id']} must name its evidence file"


def test_successors_resolve_in_the_frozen_dag() -> None:
    payload = _ledger()
    dag = load_dag(REPO_ROOT)
    for item in payload["items"]:
        unknown = [unit for unit in item["successors"] if unit not in dag]
        assert not unknown, f"{item['id']} references unknown units {unknown}"


def test_mandatory_counterexample_families_are_covered() -> None:
    payload = _ledger()
    families = {item["family"] for item in payload["items"]}
    assert MANDATORY_FAMILIES <= families, (
        f"missing mandatory families: {MANDATORY_FAMILIES - families}"
    )


def test_no_item_claims_the_fix() -> None:
    payload = _ledger()
    assert all(
        item["classification"] != "already-satisfied" for item in payload["items"]
    ), (
        "ZR-001 replays at the frozen triplet: if any counterexample became "
        "already-satisfied this assertion must be revisited with fresh evidence"
    )


def test_summary_counts_match_items() -> None:
    payload = _ledger()
    assert sum(payload["summary"].values()) == len(payload["items"])
    for classification, count in payload["summary"].items():
        actual = sum(
            1 for item in payload["items"] if item["classification"] == classification
        )
        assert count == actual, classification


def test_real_catalog_fingerprint_proves_zero_write() -> None:
    payload = _ledger()
    fingerprint = payload["catalog_fingerprint"]
    assert fingerprint.get("unchanged_by_this_script") is True, (
        "read-only catalog queries must leave size+mtime unchanged"
    )


def test_ledger_rebuild_is_deterministic() -> None:
    import os
    import subprocess
    import sys

    builder = EVIDENCE_DIR.parent / "zr001_build_ledger.py"
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(REPO_ROOT / "assurance" / "unified_completion")
    completed = subprocess.run(
        [sys.executable, "-B", str(builder), "--verify"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
        timeout=120,
    )
    assert completed.returncode == 0, (
        f"ledger --verify failed: rc={completed.returncode}\n"
        f"stdout={completed.stdout}\nstderr={completed.stderr[-1200:]}"
    )
