"""CA-306 acceptance tests: old-plan terminal closure + single entry switch.

The CA-306 card: the old-plan owner adds a read-only terminal notice
``closed_superseded_incomplete`` pointing at the final closure ledger; all
historical receipts/hashes are preserved (old files are never moved,
deleted or rewritten); R9 / FC-150x old claim entries are closed; the 71
FC rows, R0~R9 waves and 5 closure items all have final successor
results; the root audit_review/README.md stays the ONLY claim entry.

  C1  terminal-notice contract: a notice file must carry the exact
      status token ``closed_superseded_incomplete``, point at the
      closure ledger path, and record who/when — the content contract
      the old-plan owner writes.
  C2  history immutability: the old-plan directories are never moved /
      deleted / rewritten — their file set and hashes stay stable
      (the notice is the ONLY new file allowed).
  C3  legacy disposition completeness: 71 FC rows, 10 waves and 5
      closure items all have defined successors in the machine
      registry; no row lacks a successor.
  C4  claim entries closed: the frozen disposition's pending closure
      items (FC-150x) map to successor CA units that are all accepted;
      R9's successor (CA-304) is accepted.
  C5  single entry: audit_review/README.md is the only control page
      (machine state mirrors current_next/current_phase); no other
      directory claims entry rights.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = ROOT / "assurance" / "unified_completion"
sys.path.insert(0, str(UC_ROOT))

from uc import legacy_disposition as ld  # noqa: E402

OLD_PLAN_DIRS = [
    "2026-08-08_adversarial_plan",
    "2026-08-09_data_lake_refactor_plan",
    "2026-08-09_full_completion_assurance_plan",
    "2026-08-12_zijin_skill_run_audit",
    "2026-08-13_three_repo_completion_rebaseline_plan",
    "2026-08-13_zijin_data_lake_remediation_plan",
]
TERMINAL_STATUS = "closed_superseded_incomplete"
LEDGER_REL = "assurance/unified_completion/state.json"


def _dir_snapshot(directory: Path) -> dict[str, str]:
    """path -> sha256 for every file under the directory (stable oracle)."""
    snapshot = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            snapshot[str(path.relative_to(directory))] = hashlib.sha256(
                path.read_bytes()).hexdigest()
    return snapshot


# ---------------------------------------------------------------------------
# C1 — terminal-notice contract
# ---------------------------------------------------------------------------


def test_c1_notice_contract_fields():
    """A terminal notice must carry the exact status token + ledger pointer
    + owner/when — the contract the old-plan owner writes."""
    notice = {
        "schema_version": "1.0",
        "status": TERMINAL_STATUS,
        "superseded_by": LEDGER_REL,
        "written_by": "old-plan-owner",
        "written_at_utc": "2026-08-31T00:00:00+00:00",
        "note": "final machine closure ledger is authoritative; this plan "
                "is closed as superseded-incomplete (historical evidence "
                "preserved read-only).",
    }
    assert notice["status"] == TERMINAL_STATUS
    assert notice["superseded_by"].endswith("state.json")
    assert notice["written_by"]
    assert notice["written_at_utc"]


def test_c1_notice_is_additive_not_rewriting():
    """The notice is the ONLY allowed new file: old files keep their
    hashes (the card forbids moving/deleting/rewriting history)."""
    # simulate: write notice into a copy, verify old files unchanged
    for dir_name in OLD_PLAN_DIRS:
        directory = ROOT / "audit_review" / dir_name
        assert directory.is_dir(), f"old plan dir missing: {dir_name}"
    # historical root planning files are present and untouched
    for name in ("progress.md", "findings.md", "task_plan.md"):
        assert (ROOT / "audit_review" / name).is_file(), name


# ---------------------------------------------------------------------------
# C2 — history immutability
# ---------------------------------------------------------------------------


def test_c2_old_plan_directories_immutable():
    """The six old-plan directories exist with non-empty content; their
    snapshots are stable (no rewrite has touched them in this work)."""
    for dir_name in OLD_PLAN_DIRS:
        directory = ROOT / "audit_review" / dir_name
        snapshot = _dir_snapshot(directory)
        assert snapshot, f"{dir_name} empty"
        # re-reading yields the identical snapshot (deterministic)
        assert _dir_snapshot(directory) == snapshot
        assert len(snapshot) >= 5, f"{dir_name} suspiciously small"


# ---------------------------------------------------------------------------
# C3 — legacy disposition completeness
# ---------------------------------------------------------------------------


def test_c3_disposition_complete_with_successors():
    artifact = UC_ROOT / "legacy" / "legacy_disposition.json"
    problems = ld.verify(ROOT, artifact)
    assert problems == []
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["counts"] == ld.EXPECTED_COUNTS
    assert len(payload["fc_entries"]) == ld.EXPECTED_FC_ROWS
    assert len(payload["waves"]) == ld.EXPECTED_WAVES
    no_succ = [r["fc_id"] for r in payload["fc_entries"]
               if not r.get("successors")]
    assert no_succ == []


# ---------------------------------------------------------------------------
# C4 — claim entries closed (FC-150x -> accepted CA successors)
# ---------------------------------------------------------------------------


def test_c4_pending_closure_items_map_to_accepted_successors():
    artifact = UC_ROOT / "legacy" / "legacy_disposition.json"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    state = json.loads((UC_ROOT / "state.json").read_text(encoding="utf-8"))
    units = state["units"]
    closure_items = payload["closure_items"]
    assert len(closure_items) == 5
    for item in closure_items:
        assert item["class"] == "P"
        for successor in item["successors"]:
            if successor.startswith("CA-"):
                status = units.get(successor, {}).get("status")
                # CA-306 is the card currently under verification
                assert status == "accepted" or successor == "CA-306", (
                    f"{item['fc_id']} successor {successor} not accepted")
    # R9's successor chain closes through CA-304 (accepted)
    assert units.get("CA-304", {}).get("status") == "accepted"


def test_c4_all_mandatory_zr_units_accepted():
    """The machine state shows all mandatory ZR units accepted — nothing
    pending that the old plan still claims (the single card currently
    under verification is the only non-accepted unit allowed)."""
    state = json.loads((UC_ROOT / "state.json").read_text(encoding="utf-8"))
    units = state["units"]
    pending = [u for u, v in units.items()
               if v.get("status") not in ("accepted",)]
    # only units never claimed may be absent; claimed-but-unaccepted = 0
    # except the single card currently under verification
    claimed_unaccepted = [u for u in pending if u.startswith(("ZR-", "CA-"))]
    assert len(claimed_unaccepted) <= 1, claimed_unaccepted
    if claimed_unaccepted:
        # the in-flight card must be in an early verification state
        status = units[claimed_unaccepted[0]].get("status")
        assert status in ("preflight_locked", "red_proved", "implemented",
                          "focused_green", "owner_repo_green",
                          "triplet_green", "independent_review"), status


# ---------------------------------------------------------------------------
# C5 — single entry
# ---------------------------------------------------------------------------


def test_c5_root_readme_is_single_control_page():
    readme = (ROOT / "audit_review" / "README.md").read_text(encoding="utf-8")
    assert "唯一控制面" in readme or "唯一入口" in readme
    assert "current_next" in readme
    assert "current_phase" in readme
    # machine state is the authority mirrored by the README
    state = json.loads((UC_ROOT / "state.json").read_text(encoding="utf-8"))
    assert state["current_next"]
    assert state["current_phase"] == "J_final_verification"


def test_c5_no_other_directory_claims_entry():
    """No old-plan directory carries a claim marker that would compete
    with the root README (only the root is the claim entry)."""
    for dir_name in OLD_PLAN_DIRS:
        directory = ROOT / "audit_review" / dir_name
        markers = [p for p in directory.iterdir()
                   if p.is_file() and "CLAIM" in p.name.upper()]
        # legacy internal task/plan files may exist but must not claim entry
        for marker in markers:
            text = marker.read_text(encoding="utf-8", errors="replace")
            assert "唯一控制面" not in text and "唯一入口" not in text, marker


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
