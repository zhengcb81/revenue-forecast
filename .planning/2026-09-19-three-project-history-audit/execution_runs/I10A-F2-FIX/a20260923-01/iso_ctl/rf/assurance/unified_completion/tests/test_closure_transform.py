"""Regression test for reviewer finding F4: the closure state transform must
mirror control_page_sha256 / machine_manifest_sha256 so no stale mirror field
survives closure."""

from __future__ import annotations

import json

from uc.cli import closure_state_transform


def _state() -> dict:
    return json.loads(
        json.dumps(
            {
                "schema_version": 1,
                "control_page_sha256": "old-readme-hash",
                "machine_manifest_sha256": "old-manifest-hash",
                "current_next": "CA-001",
                "current_phase": "A0_bootstrap_and_rebaseline",
                "active_owner": "implementer",
                "lease": "held",
                "last_control_update": "2026-08-13",
                "units": {"CA-001": {"status": "accepted"}},
            }
        )
    )


def test_closure_transform_mirrors_hashes():
    out = closure_state_transform(
        _state(),
        unit="CA-001",
        next_unit="CA-002",
        phase="A0_bootstrap_and_rebaseline",
        reviewer="reviewer-ca001-independent",
        new_manifest_hash="new-manifest-hash",
        new_readme_hash="new-readme-hash",
        now_iso="2026-08-13T21:00:00+00:00",
    )
    assert out["control_page_sha256"] == "new-readme-hash"
    assert out["machine_manifest_sha256"] == "new-manifest-hash"
    assert out["current_next"] == "CA-002"
    assert out["active_owner"] is None
    assert out["lease"] is None
    assert out["last_control_update"] == "2026-08-13"
    closure = out["units"]["CA-001"]["closure"]
    assert closure["by"] == "reviewer-ca001-independent"
    assert closure["next"] == "CA-002"


def test_closure_transform_leaves_other_fields_untouched():
    out = closure_state_transform(
        _state(),
        unit="CA-001",
        next_unit="CA-002",
        phase="A0_bootstrap_and_rebaseline",
        reviewer="r",
        new_manifest_hash="m",
        new_readme_hash="c",
        now_iso="2026-08-13T21:00:00+00:00",
    )
    assert out["schema_version"] == 1
    assert out["units"]["CA-001"]["status"] == "accepted"
