"""Control-page §0 patch function: precise, byte-conservative, rejective."""

from __future__ import annotations

import pytest

from conftest import REPO_ROOT
from uc.control import patch_section0, plan_advance_fields, plan_release_fields

YAML_BLOCK = """```yaml
plan_id: X
plan_status: ready
implementation_status: not_started
current_phase: A0
current_next: CA-001
active_owner: unassigned
lease: none
blocked_reason: none
last_control_update: 2026-08-13
```
"""


def test_patch_replaces_only_requested_fields():
    out = patch_section0(YAML_BLOCK, {"current_next": "CA-002"})
    assert "current_next: CA-002" in out
    assert "plan_id: X" in out
    assert "implementation_status: not_started" in out


def test_patch_preserves_all_other_lines_byte_identical():
    source = "preamble\nnot yaml\n" + YAML_BLOCK + "epilogue\n"
    out = patch_section0(source, {"lease": "none"})
    assert out.count("\n") == source.count("\n")
    assert "preamble" in out and "epilogue" in out and "not yaml" in out


def test_patch_rejects_unknown_field():
    with pytest.raises(ValueError, match="unknown"):
        patch_section0(YAML_BLOCK, {"current_next": "CA-002", "bogus_field": "x"})


def test_patch_rejects_missing_yaml_block():
    with pytest.raises(ValueError, match="yaml"):
        patch_section0("no yaml here\n", {"current_next": "CA-002"})


def test_patch_rejects_missing_field_in_block():
    source = "```yaml\nplan_id: X\n```\n"
    with pytest.raises(ValueError, match="not found"):
        patch_section0(source, {"current_next": "CA-002"})


def test_real_readme_section0_patch_is_minimal():
    """The closure patch path works on the real README and changes only the
    three mirrored fields."""
    readme = (REPO_ROOT / "audit_review" / "README.md").read_text(encoding="utf-8")
    before = readme.splitlines()
    out = patch_section0(
        readme,
        plan_advance_fields(
            current_next="CA-002",
            current_phase="A0_bootstrap_and_rebaseline",
            now_iso="2026-08-13T21:00:00+00:00",
        ),
    )
    after = out.splitlines()
    assert len(before) == len(after)
    changed = [(b, a) for b, a in zip(before, after) if b != a]
    assert len(changed) == 2
    assert {line.strip().split(":")[0] for _, line in changed} == {
        "implementation_status",
        "current_next",
    }


def test_release_fields_clear_owner_and_lease():
    fields = plan_release_fields("2026-08-13T21:00:00+00:00")
    assert fields["active_owner"] == "unassigned"
    assert fields["lease"] == "none"
    assert fields["last_control_update"] == "2026-08-13"
