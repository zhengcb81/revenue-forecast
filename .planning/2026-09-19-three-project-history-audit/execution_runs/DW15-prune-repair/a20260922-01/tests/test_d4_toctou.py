"""D4 — TOCTOU: the state a delete acts on is re-verified with the delete.

Frozen expectations: oracle.md §2 rows t_d4_1, t_d4_2.
"""
from __future__ import annotations

import sqlite3

from dw15_fixtures import (
    NOW_PRUNE,
    RETENTION_DAYS,
    call_prune,
    live_span_ids,
    pre_to_post_case,
)


def _freeze_plan(case):
    dry = call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                     apply=False, retention_days=RETENTION_DAYS)
    return getattr(dry, "plan", None), dry


def test_d4_row_mutation_after_plan_freeze_refuses_the_whole_apply(tmp_path):
    """t_d4_1: a2's content changes after the plan is frozen."""
    case = pre_to_post_case(tmp_path)
    plan, dry = _freeze_plan(case)

    conn = sqlite3.connect(case["db"])
    conn.execute("UPDATE evidence_spans SET raw_text=? WHERE span_id=?",
                 ("MUTATED AFTER PLAN", "a2"))
    conn.commit()
    conn.close()

    before = live_span_ids(case["db"])
    refused = None
    try:
        call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                   apply=True, retention_days=RETENTION_DAYS, plan=plan)
    except Exception as exc:                     # any refusal counts
        refused = exc
    after = live_span_ids(case["db"])

    assert refused is not None, (
        "apply must refuse the whole plan when a frozen row digest no "
        f"longer matches; it deleted {sorted(set(before) - set(after))}")
    assert sorted(set(before) - set(after)) == [], (
        "a refused apply must delete nothing (no silent narrowing, no partial run)")
    assert plan is not None, "dry run must hand back a frozen plan object"


def test_d4_status_flip_after_plan_freeze_refuses_the_whole_apply(tmp_path):
    """t_d4_2: doc-A becomes active again after the plan is frozen."""
    case = pre_to_post_case(tmp_path)
    plan, dry = _freeze_plan(case)

    conn = sqlite3.connect(case["db"])
    conn.execute("UPDATE documents SET source_status='active' "
                 "WHERE document_id='doc-A'")
    conn.commit()
    conn.close()

    before = live_span_ids(case["db"])
    refused = None
    try:
        call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                   apply=True, retention_days=RETENTION_DAYS, plan=plan)
    except Exception as exc:
        refused = exc
    after = live_span_ids(case["db"])

    assert refused is not None, (
        "apply must refuse when a planned row's document is no longer "
        f"retired; it deleted {sorted(set(before) - set(after))}")
    assert sorted(set(before) - set(after)) == []
    assert plan is not None
