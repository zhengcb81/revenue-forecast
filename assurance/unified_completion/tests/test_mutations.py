"""CA-108: the mutation suite must kill 100% of its critical mutations."""

from __future__ import annotations

from uc.mutations import run_suite


def test_all_mutations_killed(tmp_path):
    report = run_suite(tmp_path)
    assert report["alive"] == [], (
        f"{report['killed']}/{report['total']} killed; alive={report['alive']}"
    )
    assert report["total"] >= 30
