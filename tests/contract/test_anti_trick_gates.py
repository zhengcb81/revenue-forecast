"""Compare the full RF runtime tree with the independently recorded S6 baseline."""

from pathlib import Path

import json

from tools.anti_trick_gate_spec.evidence import baseline, changed_inventory, compare, renamed_waivers
from tools.anti_trick_gate_spec.static_scan import scan


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "tools/rf-runtime-baseline.json"


def test_runtime_tree_does_not_add_boundary_bypasses():
    recorded = json.loads(BASELINE.read_text(encoding="utf-8"))
    actual = scan(
        ROOT, ("scripts",),
        storage=("scripts/rf_feedback_outbox.py",),
        entry=("scripts/rf_job_cli.py", "scripts/report_catalog_cli.py", "scripts/rf_job_feedback.py"),
    )
    observed = {**baseline(actual.findings), "constant_shapes": actual.constant_shapes}
    assert changed_inventory(actual, recorded, ROOT) == ()
    assert compare(observed, recorded) + renamed_waivers(observed, recorded) == ()
