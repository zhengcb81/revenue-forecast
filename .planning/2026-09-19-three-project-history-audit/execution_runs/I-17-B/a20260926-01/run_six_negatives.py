"""I-17-B action 2: rerun the I-00-C six negative examples against the
CURRENT effective combination (repo `assurance/unified_completion/uc`).

Read-only with respect to production: imports the production package in place,
uses synthetic fixtures only, and writes nothing outside the directory this
script lives in (TEMP/TMP are redirected by the caller).

Frozen expectation (oracle.md §4): every one of N1..N6 must be REJECTED by the
current combination.  Any negative that is NOT rejected is a real defect and is
reported as rc=3 (never re-labelled green).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RF_ROOT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
UC_ROOT = RF_ROOT / "assurance" / "unified_completion"

sys.path.insert(0, str(UC_ROOT))  # production `uc` package = current combination

from uc import closure as uc_closure  # noqa: E402
from uc import receipt as uc_receipt  # noqa: E402
from uc import revision as uc_revision  # noqa: E402
from uc import scenarios as uc_scenarios  # noqa: E402
from uc.receipt import canonical_hash, sign  # noqa: E402

RESULTS = []


def record(name: str, rejected: bool, detail: str) -> None:
    RESULTS.append(
        {"case": name, "rejected": bool(rejected), "detail": str(detail)}
    )


# ---------------------------------------------------------------- N1
# "全部 passed 但无证据" — a bare passed status must NOT satisfy completion.
n1_payload = {
    "counts": {"unique_total": 1},
    "scenarios": {
        "AR-01": {
            "status": "passed",
            "tier": "T1",
            "evidence_path": None,
            "fixture_hash": None,
            "oracle": None,
        }
    },
}
rep1 = uc_scenarios.closure_report(n1_payload)
record(
    "N1_all_passed_but_no_evidence",
    not rep1.get("closure_ready"),
    f"closure_ready={rep1.get('closure_ready')} unsatisfied={rep1.get('unsatisfied')}",
)

# ---------------------------------------------------------------- N2
# "READ10 引用不测 deadline 的测试" — wrong-capability evidence must be rejected.
n2_payload = {
    "counts": {"unique_total": 1},
    "scenarios": {
        "READ-10": {
            "status": "passed",
            "tier": "T1",
            "evidence_path": "evidence/READ_10.json",
            "fixture_hash": "ab" * 32,
            "required_capability": "deadline",
            "covered_capabilities": ["artifact"],
        }
    },
}
rep2 = uc_scenarios.closure_report(n2_payload)
record(
    "N2_read10_wrong_capability_evidence",
    not rep2.get("closure_ready")
    and "deadline" in str(rep2.get("unsatisfied_ids", [])),
    f"closure_ready={rep2.get('closure_ready')} "
    f"unsatisfied_ids={rep2.get('unsatisfied_ids')}",
)

# control: covering capability must be accepted (positive guard, not a negative)
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
record(
    "CTRL_read10_covering_capability_accepted",
    bool(rep2b.get("closure_ready")),
    f"closure_ready={rep2b.get('closure_ready')} (control, must be True)",
)

# ---------------------------------------------------------------- N3
# "同一有效组合旧 PASS 后新 FAIL" — stale accepted must not win.
tmp = Path(tempfile.mkdtemp(prefix="i17b_n3_"))
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
for fname, payload in (
    ("11_implementer.json", r1),
    ("12_implementer.json", r2),
    ("13_reviewer_old.json", review_on_rev1),
    ("14_reviewer_new.json", review_on_rev2),
):
    (tmp / fname).write_text(json.dumps(payload), encoding="utf-8")
selection, problems = uc_revision.select(tmp)
record(
    "N3_stale_accepted_after_newer_fail",
    selection.get("verdict") != "accepted" and bool(problems),
    f"verdict={selection.get('verdict')} problems={problems}",
)

# ---------------------------------------------------------------- N4 / N5
# "空 commands" 和 "空 invariants" 各自必须使场景不满足。
def _oracle_case(case: str, oracle: dict) -> None:
    payload = {
        "counts": {"unique_total": 1},
        "scenarios": {
            "S-1": {
                "status": "passed",
                "tier": "T1",
                "evidence_path": "evidence/S_1.json",
                "fixture_hash": "cd" * 32,
                "oracle": oracle,
            }
        },
    }
    rep = uc_scenarios.closure_report(payload)
    record(
        case,
        not rep.get("closure_ready"),
        f"closure_ready={rep.get('closure_ready')} "
        f"unsatisfied_ids={rep.get('unsatisfied_ids')}",
    )


_oracle_case("N4_empty_commands", {"validated_commands": [], "invariants": ["i1"]})
_oracle_case("N5_empty_invariants", {"validated_commands": ["c1"], "invariants": []})
_oracle_case(
    "N45_both_empty", {"validated_commands": [], "invariants": []}
)

# receipt layer: an implementer receipt without `commands` must be refused
record(
    "N4b_receipt_layer_requires_commands",
    "commands" in uc_receipt.REQUIRED_BY_KIND["implementer"],
    f"required={uc_receipt.REQUIRED_BY_KIND['implementer']}",
)

# ---------------------------------------------------------------- N6
# "删除 CA206/301/302 原义务仅保留缩小卡" — originals must stay pending and
# the narrowing must be flagged; it must not unlock completion.
legacy = {
    "fc_entries": [
        {"fc_id": "CA-206", "class": "P", "obligation_target": "full-triplet-journey"},
        {"fc_id": "CA-206-narrow", "class": "D", "note": "narrowed helper-only"},
        {"fc_id": "CA-301", "class": "P", "obligation_target": "full-triplet-journey"},
        {"fc_id": "CA-301-narrow", "class": "D", "note": "narrowed helper-only"},
        {"fc_id": "CA-302", "class": "P", "obligation_target": "full-triplet-journey"},
        {"fc_id": "CA-302-narrow", "class": "D", "note": "narrowed helper-only"},
    ]
}
tmp6 = Path(tempfile.mkdtemp(prefix="i17b_n6_"))
legacy_path = tmp6 / "legacy.json"
legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
repo_roots = {
    k: Path(tempfile.mkdtemp(prefix=f"i17b_root_{k}_"))
    for k in ("revenue", "filing", "wiki")
}
reg_path = UC_ROOT / "scenarios" / "scenario_registry.json"
rep6 = uc_closure.closure_report(repo_roots, legacy_path, reg_path)
reasons = rep6.get("reasons", [])
pending = rep6.get("legacy_summary", {}).get("pending", 0)
narrow_flagged = any("narrow" in str(r).lower() for r in reasons)
originals_named = all(
    any(fc in str(r) for r in reasons) for fc in ("CA-206", "CA-301", "CA-302")
)
record(
    "N6_original_obligations_still_pending",
    pending >= 3 and originals_named,
    f"pending={pending} reasons={reasons}",
)
record(
    "N6b_narrowed_successor_flagged",
    narrow_flagged,
    f"narrowed_flagged={narrow_flagged} reasons={reasons}",
)

# ---------------------------------------------------------------- verdict
negatives = [r for r in RESULTS if r["case"].startswith("N")]
all_rejected = all(r["rejected"] for r in negatives)
controls_ok = all(
    r["rejected"] for r in RESULTS if r["case"].startswith("CTRL")
) or all(
    r["rejected"] for r in RESULTS if r["case"] == "CTRL_read10_covering_capability_accepted"
)

out = {
    "combination": {
        "uc_root": str(UC_ROOT),
        "scenarios_py_sha256": __import__("hashlib")
        .sha256((UC_ROOT / "uc" / "scenarios.py").read_bytes())
        .hexdigest(),
        "closure_py_sha256": __import__("hashlib")
        .sha256((UC_ROOT / "uc" / "closure.py").read_bytes())
        .hexdigest(),
        "registry_sha256": __import__("hashlib")
        .sha256(reg_path.read_bytes())
        .hexdigest(),
        "patch_gate_present": hasattr(uc_scenarios, "scenario_gate"),
        "python": sys.version.split()[0],
    },
    "negative_count": len(negatives),
    "negatives_rejected": sum(1 for r in negatives if r["rejected"]),
    "all_six_rejected": all_rejected,
    "results": RESULTS,
}
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
sys.exit(0 if all_rejected else 3)
