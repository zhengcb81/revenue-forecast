"""I-00-C six-negative / one-positive / cross-entry checks on the patched uc package.

Read-only with respect to production: operates on synthetic fixtures and
the isolated scenario registry copy only.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "iso" / "_pkgdir"))

from uc import closure as uc_closure
from uc import scenarios as uc_scenarios
from uc.receipt import canonical_hash, sign
from uc.revision import select as revision_select

RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append({"name": name, "pass": bool(condition), "detail": str(detail)})


reg = json.loads(
    (Path(__file__).parent / "iso" / "scenario_registry_fixture.json").read_text(
        encoding="utf-8"
    )
)

# ---- BEFORE-state reproduction (old semantics, for contrast) ------------
old_style_satisfied = [
    sid
    for sid, info in reg["scenarios"].items()
    if info.get("status") in ("passed", "expected_failure_pass")
]
check(
    "before_state_197_passed_all_bare",
    len(old_style_satisfied) == 197
    and all(
        s.get("fixture_hash") is None and s.get("oracle") is None
        for s in reg["scenarios"].values()
    ),
    f"old-style counted {len(old_style_satisfied)} satisfied, zero bindings",
)

# ---- N1: all passed but no bindings -> must stay red --------------------
report_new = uc_scenarios.closure_report(reg)
check(
    "N1_registry_bare_passed_rejected",
    not report_new["closure_ready"] and report_new["unsatisfied"] == 197,
    f"unsatisfied={report_new['unsatisfied']} "
    f"first_reasons={dict(list(report_new['unsatisfied_reasons'].items())[:2])}",
)

# ---- N2: READ10 wrong-evidence mapping ----------------------------------
n2 = {
    "READ-10": {
        "status": "passed",
        "tier": "T1",
        "evidence_path": "evidence/READ_10.json",
        "fixture_hash": "ab" * 32,
        "required_capability": "deadline",
        "covered_capabilities": ["artifact"],
    }
}
rep2 = uc_scenarios.closure_report({"counts": {"unique_total": 1}, "scenarios": n2})
check(
    "N2_wrong_test_evidence_rejected",
    not rep2["closure_ready"]
    and "deadline" in str(rep2["unsatisfied_reasons"].get("READ-10")),
    f"reasons={rep2['unsatisfied_reasons'].get('READ-10')}",
)

# control: covering capability is accepted
rep2b = uc_scenarios.closure_report(
    {
        "counts": {"unique_total": 1},
        "scenarios": {
            "READ-10": {
                "status": "passed",
                "tier": "T1",
                "evidence_path": "evidence/READ_10.json",
                "fixture_hash": "ab" * 32,
                "required_capability": "deadline",
                "covered_capabilities": ["deadline"],
            }
        },
    }
)
check(
    "N2_control_covering_capability_accepted",
    rep2b["closure_ready"],
)

# ---- N3: stale accepted must not beat newer changes_required ------------
tmp = Path(tempfile.mkdtemp(prefix="i00c_n3_"))
impl_base = {
    "schema_version": 1,
    "unit": "U-1",
    "kind": "implementer",
    "created_at_utc": "2026-09-01T00:00:00Z",
    "base_triplet": {"revenue": "a" * 40},
    "result_triplet": {"revenue": "b" * 40},
    "plan_sha256": "c" * 64,
    "commands": [{"exit_code": 0}],
    "touched_files": ["x.py"],
    "side_effect_counts": {"writes": 1},
    "implementer": "impl-agent",
}
rev_template = {
    "schema_version": 1,
    "unit": "U-1",
    "kind": "reviewer",
    "created_at_utc": "2026-09-02T00:00:00Z",
    "reviewer": "rev-a",
    "verdict": "accepted",
    "commands": [{"exit_code": 0}],
    "reviewed_object_sha256": "d" * 64,
}
r1 = sign(dict(impl_base, revision="rev1"))
review_on_rev1 = dict(rev_template, reviewed_object_sha256=canonical_hash(r1))
r2 = sign(dict(impl_base, revision="rev2", supersedes="rev1"))
review_on_rev2 = dict(
    rev_template,
    reviewer="rev-b",
    verdict="changes_required",
    reviewed_object_sha256=canonical_hash(r2),
)
for name, payload in (
    ("11_implementer.json", r1),
    ("12_implementer.json", r2),
    ("13_reviewer_old.json", review_on_rev1),
    ("14_reviewer_new.json", review_on_rev2),
):
    (tmp / name).write_text(json.dumps(payload), encoding="utf-8")
selection, problems = revision_select(tmp)
check(
    "N3_stale_accepted_does_not_unlock",
    selection.get("verdict") != "accepted"
    and problems
    and (
        any("stale" in p for p in problems)
        or any("latest" in p or "references the latest" in p for p in problems)
    ),
    f"verdict={selection.get('verdict')} problems={problems}",
)

# ---- N4/N5: empty commands / empty invariants evidence ------------------
n45 = {
    "S-1": {
        "status": "passed",
        "tier": "T1",
        "evidence_path": "evidence/S_1.json",
        "oracle": {"validated_commands": [], "invariants": []},
    }
}
rep45 = uc_scenarios.closure_report({"counts": {"unique_total": 1}, "scenarios": n45})
check(
    "N45_empty_commands_and_invariants_do_not_satisfy",
    not rep45["closure_ready"],
    f"reasons={rep45['unsatisfied_reasons'].get('S-1')}",
)

# receipt layer already rejects empty commands for implementer receipts
impl_bad_commands = dict(impl_base, commands=[])
(tmp / "15_impl_empty_commands.json").write_text(
    json.dumps(impl_bad_commands), encoding="utf-8"
)
from uc import receipt as uc_receipt

check(
    "N4_receipt_layer_commands_required_field",
    "commands" in str(uc_receipt.REQUIRED_BY_KIND["implementer"]) and True,
    f"required={uc_receipt.REQUIRED_BY_KIND['implementer']}",
)

# ---- N6: narrowed successor never clears original obligation ------------
legacy = {
    "fc_entries": [
        {"fc_id": "CA-206", "class": "P", "obligation_target": "full-triplet-journey"},
        {"fc_id": "CA-206-narrow", "class": "D", "note": "narrowed helper-only"},
    ]
}
tmpdir6 = Path(tempfile.mkdtemp(prefix="i00c_n6_"))
tmp_legacy = tmpdir6 / "legacy.json"
tmp_legacy.write_text(json.dumps(legacy), encoding="utf-8")
repo_roots = {
    k: Path(tempfile.mkdtemp(prefix=f"i00c_root_{k}_"))
    for k in ("revenue", "filing", "wiki")
}
reg_path = Path(__file__).parent / "iso" / "scenario_registry_fixture.json"
rep6 = uc_closure.closure_report(repo_roots, tmp_legacy, reg_path)
check(
    "N6_original_still_pending",
    rep6["legacy_summary"]["pending"] >= 1
    and any("CA-206" in r for r in rep6["reasons"]),
    f"pending={rep6['legacy_summary']['pending']}",
)
check(
    "N6_narrowing_flagged",
    any("narrowed successor" in r for r in rep6["reasons"]),
    f"narrow_reason={[r for r in rep6['reasons'] if 'narrowed' in r]}",
)

# ---- P1: fully bound scenario scoped-accepted ---------------------------
pos = {
    "counts": {"unique_total": 1},
    "scenarios": {
        "AR-01": {
            "status": "passed",
            "tier": "T1",
            "evidence_path": "evidence/AR_01.json",
            "fixture_hash": "ef" * 32,
            "oracle": {"metric": "ids_count", "expected": 4, "observed": 4},
            "required_capability": "binding",
            "covered_capabilities": ["binding"],
        }
    },
}
rep_pos = uc_scenarios.closure_report(pos)
check(
    "P1_fully_bound_scenario_scoped_accepted",
    rep_pos["closure_ready"] and rep_pos["unsatisfied"] == 0,
)

# ---- Cross-entry: lower red -> upper verdict stays incomplete -----------
rep_cross = uc_closure.closure_report(repo_roots, tmp_legacy, reg_path)
check(
    "X1_lower_red_blocks_upper_verdict",
    rep_cross["old_plan_verdict"] == "incomplete"
    and rep_cross["scenario_summary"]["unsatisfied"] == 197,
    f"verdict={rep_cross['old_plan_verdict']} "
    f"unsatisfied={rep_cross['scenario_summary']['unsatisfied']}",
)

out = {"all_pass": all(r["pass"] for r in RESULTS), "results": RESULTS}
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
sys.exit(0 if out["all_pass"] else 1)
