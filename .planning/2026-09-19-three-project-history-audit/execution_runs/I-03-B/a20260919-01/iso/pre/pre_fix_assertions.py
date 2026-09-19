"""I-03-B pre-fix assertions (independent expectations, frozen before any run).

Rules:
- Expected values are FIXED LITERALS derived from I-03-A D1-D6 / oracle C-cells.
  They are NEVER computed from the planner under test.
- The harness imports a gap_plan module given by a path on sys.path (iso harness
  prepends override or baseline dir). We do NOT import company_wiki.
- Each assertion records: fixed expected, actual, status (pass/fail/not_applicable).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_gap_plan_module(module_path: Path):
    spec = importlib.util.spec_from_file_location("gap_plan_under_test", module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gap_plan_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


class _Local:
    def __init__(
        self,
        period_start,
        period_end,
        kind,
        filed_at,
        accession,
        amended=False,
        capture_ready=True,
        fiscal_year=2025,
        accepted_at=None,
        root="r1",
    ):
        self.kind = kind
        self.period_start = period_start
        self.period_end = period_end
        self.filed_at = filed_at
        self.accepted_at = accepted_at
        self.filing_date = filed_at
        self.provider_document_id = accession
        self.amended = amended
        self.capture_ready = capture_ready
        self.fiscal_year = fiscal_year
        self.root = root

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in (
                "kind",
                "period_start",
                "period_end",
                "filed_at",
                "accepted_at",
                "provider_document_id",
                "amended",
                "capture_ready",
                "fiscal_year",
                "root",
            )
        }


class _Remote:
    def __init__(
        self,
        period_start,
        period_end,
        kind,
        filed_at,
        accession,
        amended=False,
        fiscal_year=2025,
        accepted_at=None,
        url="https://example.org/x.pdf",
        provider="fake-provider",
    ):
        self.kind = kind
        self.period_start = period_start
        self.period_end = period_end
        self.filed_at = filed_at
        self.accepted_at = accepted_at
        self.filing_date = filed_at
        self.provider_document_id = accession
        self.amended = amended
        self.fiscal_year = fiscal_year
        self.source_url = url
        self.provider = provider

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in (
                "kind",
                "period_start",
                "period_end",
                "filed_at",
                "accepted_at",
                "provider_document_id",
                "amended",
                "fiscal_year",
                "source_url",
                "provider",
            )
        }


def _call(gap_plan_mod, locals_, remotes, provider_error=None):
    return gap_plan_mod.build_gap_plan(
        request_id="req-gb",
        as_of_date="2026-07-31",
        document_kind="annual_report",
        entity="ACME",
        market="US",
        local_handles=list(locals_),
        remote_candidates=list(remotes),
        provider_error=provider_error,
    )


def _ids(seq):
    return [getattr(x, "provider_document_id", None) for x in seq]


# ---- fixed inputs -------------------------------------------------------

P_START, P_END = "2024-07-01", "2025-06-30"
KIND = "annual_report"
FY = 2025

L_ZOLD = dict(
    period_start=P_START,
    period_end=P_END,
    kind=KIND,
    filed_at="2026-03-01",
    accession="z-old",
    fiscal_year=FY,
    accepted_at="2026-03-01",
)
L_ANEW = dict(
    L_ZOLD, accession="a-new", filed_at="2026-04-01", accepted_at="2026-04-01"
)
R_ZOLD = dict(L_ZOLD)
R_ANEW = dict(L_ANEW)
R_BASE = dict(L_ANEW, accession="a-base", amended=False)
R_AMEND = dict(L_ANEW, accession="a-2026-04-01-amend", amended=True)
R_BREV = dict(L_ANEW, accession="b-rev", amended=False)
R_FUTURE = dict(
    L_ANEW, accession="a-future", filed_at="2026-08-01", accepted_at="2026-08-01"
)


def _cases():
    cases = {}

    # G-B1 (C01 forward): L=z-old, R=[z-old, a-new]; a-new filed later but ID sorts first
    cases["G-B1"] = dict(
        locals_=[_Local(**L_ZOLD)],
        remotes=[_Remote(**R_ZOLD), _Remote(**R_ANEW)],
        expect={
            "newer_revision_ids": ["a-new"],
            "reuse_ids": ["z-old"],
            "missing_ids": [],
            "latest_status": "newer_remote_available",
            "not_published": False,
        },
        rationale="I-03-A C01: filed_at 2026-04-01 > 2026-03-01 decides; ID order has no say. "
        "Old code max(accession lexicographic) picks z-old -> false gap closure.",
    )

    # G-B2 (C02 reverse): L=a-new, R=[z-old]
    cases["G-B2"] = dict(
        locals_=[_Local(**L_ANEW)],
        remotes=[_Remote(**R_ZOLD)],
        expect={
            "newer_revision_ids": [],
            "reuse_ids": ["a-new"],
            "missing_ids": [],
            "latest_status": "unknown_if_remote_confirmed_newer",
            "not_published": False,
        },
        rationale="I-03-A C02: remote shows nothing >= local; local must not be demoted; "
        "z-old (earlier filed) can never be a newer revision.",
    )

    # G-B3 (C01 family, empty local, two revisions same period, order-invariance)
    cases["G-B3"] = dict(
        locals_=[],
        remotes=[_Remote(**R_ZOLD), _Remote(**R_ANEW)],
        remotes_reversed=[_Remote(**R_ANEW), _Remote(**R_ZOLD)],
        expect={
            "missing_ids": ["a-new"],
            "newer_revision_ids": [],
            "latest_status": "newer_remote_available",
        },
        order_invariance=True,
        rationale="Only the newest revision enters missing (single gap); reversed remote "
        "input order must produce identical output (date decides, not order/ID).",
    )

    # G-B4 (C13 future)
    cases["G-B4"] = dict(
        locals_=[],
        remotes=[_Remote(**R_FUTURE)],
        expect={
            "future_ids": ["a-future"],
            "missing_ids": [],
            "newer_revision_ids": [],
            "not_published": False,
            "latest_status": "unknown_empty_success",
        },
        rationale="I-03-A C13: filed_at > as_of goes to explicit future bucket; never "
        "downloadable/current; not_published stays false (no exhaustiveness claim).",
    )

    # G-B5a: capture_ready=False local + provider_error
    cases["G-B5a"] = dict(
        locals_=[_Local(**dict(L_ZOLD, capture_ready=False))],
        remotes=[],
        provider_error="provider_unreachable",
        expect={
            "reuse_ids": [],
            "provider_unavailable": True,
            "latest_status": "unknown_provider_failed",
            "not_published": False,
        },
        rationale="ZR-406: capture-incomplete handle is never reusable evidence; "
        "provider failure => unknown_provider_failed, never up-to-date.",
    )

    # G-B5b: two local roots same accession, capture_ready, remote same accession
    cases["G-B5b"] = dict(
        locals_=[_Local(**dict(L_ZOLD, root="r1")), _Local(**dict(L_ZOLD, root="r2"))],
        remotes=[_Remote(**R_ZOLD)],
        expect={
            "reuse_ids": ["z-old", "z-old"],
            "reuse_dedup_accessions": ["z-old"],
            "latest_status": "local_is_latest_confirmed",
        },
        rationale="Multi-root same-bytes reuse: no duplicate download plan; accession hit "
        "confirms local is latest (C12).",
    )

    # G-B5c: same FY2025, two different period keys -> never merged (C05 structure)
    cases["G-B5c"] = dict(
        locals_=[],
        remotes=[
            _Remote(**dict(L_ZOLD, kind="annual_report", accession="r-annual")),
            _Remote(
                **dict(
                    L_ZOLD,
                    kind="interim_report",
                    period_end="2024-12-31",
                    accession="r-interim",
                    filed_at="2025-02-15",
                    accepted_at="2025-02-15",
                )
            ),
        ],
        remotes_reversed=[
            _Remote(
                **dict(
                    L_ZOLD,
                    kind="interim_report",
                    period_end="2024-12-31",
                    accession="r-interim",
                    filed_at="2025-02-15",
                    accepted_at="2025-02-15",
                )
            ),
            _Remote(**dict(L_ZOLD, kind="annual_report", accession="r-annual")),
        ],
        order_invariance=True,
        expect={
            "missing_ids": ["r-annual", "r-interim"],
            "missing_period_keys": [
                "annual_report|2024-07-01|2025-06-30",
                "interim_report|2024-07-01|2024-12-31",
            ],
            "merged_single_bucket": False,
        },
        rationale="I-03-A C05/D1: (kind, period_start, period_end) triple key; same FY "
        "different periods are independent gaps; D5 deterministic ordering, "
        "reversed remote input order must not change output.",
    )

    return cases


def main():
    module_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    mod = load_gap_plan_module(module_path)

    results = {}
    for case_id, case in _cases().items():
        checks = []
        try:
            remotes = case.get("remotes", [])
            plan = _call(
                mod, case.get("locals_", []), remotes, case.get("provider_error")
            )
            actual = {
                "newer_revision_ids": _ids(getattr(plan, "newer_revision", ()) or []),
                "reuse_ids": _ids(getattr(plan, "reuse", ()) or []),
                "missing_ids": _ids(getattr(plan, "missing", ()) or []),
                "future_ids": _ids(getattr(plan, "future", ()) or []),
                "latest_status": getattr(plan, "latest_status", None),
                "not_published": getattr(plan, "not_published", None),
                "provider_unavailable": getattr(plan, "provider_unavailable", None),
                "period_keys_missing": [
                    f"{getattr(c, 'kind', '')}|{getattr(c, 'period_start', '')}|{getattr(c, 'period_end', '')}"
                    for c in getattr(plan, "missing", ()) or []
                ],
                "gap_hash": getattr(plan, "gap_hash", None),
            }
            expect = case["expect"]
            for key, want in expect.items():
                if key == "reuse_dedup_accessions":
                    got = sorted(set(actual["reuse_ids"]))
                elif key == "missing_period_keys":
                    got = actual["period_keys_missing"]
                elif key == "merged_single_bucket":
                    got = len(set(actual["period_keys_missing"])) <= 1
                else:
                    got = actual.get(key)
                checks.append(
                    {
                        "field": key,
                        "expected": want,
                        "actual": got,
                        "status": "pass" if got == want else "fail",
                    }
                )
            if case.get("order_invariance"):
                plan2 = _call(mod, case["locals_"], case["remotes_reversed"])
                inv_ok = (
                    _ids(plan2.missing) == actual["missing_ids"]
                    and _ids(plan2.reuse) == actual["reuse_ids"]
                    and _ids(plan2.newer_revision) == actual["newer_revision_ids"]
                    and getattr(plan2, "gap_hash", None) == actual["gap_hash"]
                )
                checks.append(
                    {
                        "field": "order_invariance",
                        "expected": True,
                        "actual": inv_ok,
                        "status": "pass" if inv_ok else "fail",
                    }
                )
        except Exception as exc:  # structural difference counts as fail with evidence
            checks.append(
                {
                    "field": "execution",
                    "expected": "plan produced",
                    "actual": f"exception: {type(exc).__name__}: {exc}",
                    "status": "fail",
                }
            )
        overall = (
            "pass"
            if all(c["status"] == "pass" for c in checks)
            else ("not_applicable" if not checks else "fail")
        )
        results[case_id] = {
            "overall": overall,
            "checks": checks,
            "rationale": case["rationale"],
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: v["overall"] for k, v in results.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
