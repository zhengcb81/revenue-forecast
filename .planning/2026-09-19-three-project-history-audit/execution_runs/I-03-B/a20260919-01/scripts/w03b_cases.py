"""I-03-B verification harness (pure, offline).

Usage:
  python w03b_cases.py <impl_gap_plan.py> <out.json> [--only-after]

Loads a gap_plan implementation by path (baseline = production frozen
anchor copy, override = patched copy), runs the frozen independent
expectations (I-03-A oracle C01-C15 pure-selection subset + this card's
G-B1..G-B5 + CN/HK/US metadata templates + hash/D6 assertions) and
writes a per-case result JSON. Expected values are fixed literals; they
are never computed from the module under test.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PRE = Path(__file__).resolve().parents[1] / "iso" / "pre"
sys.path.insert(0, str(PRE))

from pre_fix_assertions import (  # noqa: E402
    KIND,
    L_ANEW,
    L_ZOLD,
    P_END,
    P_START,
    R_AMEND,
    R_ANEW,
    R_BASE,
    R_BREV,
    R_FUTURE,
    R_ZOLD,
    FY,
    KIND,
    _Local,
    _Remote,
    load_gap_plan_module,
)

AS_OF = "2026-07-31"


def _ids(seq):
    return [getattr(x, "provider_document_id", None) for x in seq]


def _call(mod, locals_, remotes, provider_error=None, as_of=AS_OF):
    return mod.build_gap_plan(
        request_id="req-w03b",
        as_of_date=as_of,
        document_kind=KIND,
        entity="ACME",
        market="US",
        local_handles=list(locals_),
        remote_candidates=list(remotes),
        provider_error=provider_error,
    )


def _snap(plan):
    return {
        "reuse_ids": _ids(getattr(plan, "reuse", ()) or []),
        "missing_ids": _ids(getattr(plan, "missing", ()) or []),
        "newer_revision_ids": _ids(getattr(plan, "newer_revision", ()) or []),
        "future_ids": _ids(getattr(plan, "future", ()) or []),
        "ambiguous_ids": [
            n.get("id") for n in getattr(plan, "ambiguous_candidates", ()) or ()
        ],
        "conflicting_ids": [
            n.get("id") for n in getattr(plan, "conflicting_candidates", ()) or ()
        ],
        "unknown_note_ids": [
            n.get("id") for n in getattr(plan, "unknown_candidates", ()) or ()
        ],
        "superseded_ids": _ids(getattr(plan, "superseded_remote", ()) or []),
        "latest_status": getattr(plan, "latest_status", None),
        "already_covered": getattr(plan, "already_covered", None),
        "not_published": getattr(plan, "not_published", None),
        "no_gap": getattr(plan, "no_gap", None),
        "provider_unavailable": getattr(plan, "provider_unavailable", None),
        "gap_hash": getattr(plan, "gap_hash", None),
        "period_keys_missing": sorted(
            {
                f"{getattr(c, 'kind', '') or getattr(c, 'document_kind', '')}|"
                f"{getattr(c, 'period_start', '')}|{getattr(c, 'period_end', '')}"
                for c in getattr(plan, "missing", ()) or ()
            }
        ),
        "unknown_period_reasons": sorted(
            {
                f"{n.get('id')}:{n.get('kind')}|{n.get('period_start')}|{n.get('period_end')}"
                for n in getattr(plan, "unknown_candidates", ()) or ()
                if str(n.get("reason", "")).startswith("period_missing")
            }
        ),
    }


def _check(checks, field, want, got, note=""):
    checks.append(
        {
            "field": field,
            "expected": want,
            "actual": got,
            "status": "pass" if want == got else "fail",
            "note": note,
        }
    )


def _case_C01(mod):
    plan = _call(mod, [_Local(**L_ZOLD)], [_Remote(**R_ZOLD), _Remote(**R_ANEW)])
    plan_rev = _call(mod, [_Local(**L_ZOLD)], [_Remote(**R_ANEW), _Remote(**R_ZOLD)])
    checks = []
    s = _snap(plan)
    _check(checks, "newer_revision_ids", ["a-new"], s["newer_revision_ids"])
    _check(checks, "reuse_ids", ["z-old"], s["reuse_ids"])
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "latest_status", "newer_remote_available", s["latest_status"])
    _check(checks, "not_published", False, s["not_published"])
    _check(checks, "reverse_order_equivalent", True, _snap(plan_rev) == s)
    return "C01", checks


def _case_C02(mod):
    plan = _call(mod, [_Local(**L_ANEW)], [_Remote(**R_ZOLD)])
    s = _snap(plan)
    checks = []
    _check(checks, "newer_revision_ids", [], s["newer_revision_ids"])
    _check(checks, "reuse_ids", ["a-new"], s["reuse_ids"])
    _check(
        checks, "latest_status", "unknown_if_remote_confirmed_newer", s["latest_status"]
    )
    _check(checks, "already_covered", True, s["already_covered"])
    return "C02", checks


def _case_C03(mod):
    plan = _call(mod, [], [_Remote(**R_BASE), _Remote(**R_AMEND)])
    plan_rev = _call(mod, [], [_Remote(**R_AMEND), _Remote(**R_BASE)])
    s = _snap(plan)
    checks = []
    _check(checks, "missing_ids", ["a-2026-04-01-amend"], s["missing_ids"])
    _check(checks, "latest_status", "newer_remote_available", s["latest_status"])
    _check(checks, "reverse_order_equivalent", True, _snap(plan_rev) == s)
    return "C03", checks


def _case_C04(mod):
    plan = _call(mod, [], [_Remote(**R_BASE), _Remote(**R_BREV)])
    plan_rev = _call(mod, [], [_Remote(**R_BREV), _Remote(**R_BASE)])
    s = _snap(plan)
    checks = []
    _check(checks, "ambiguous_ids", ["a-base", "b-rev"], sorted(s["ambiguous_ids"]))
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "newer_revision_ids", [], s["newer_revision_ids"])
    _check(checks, "already_covered", False, s["already_covered"])
    _check(checks, "reverse_order_equivalent", True, _snap(plan_rev) == s)
    return "C04", checks


def _case_C05(mod):
    plan = _call(
        mod,
        [],
        [
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
            _Remote(
                **dict(
                    L_ZOLD,
                    kind="quarterly_report",
                    period_start="2025-01-01",
                    period_end="2025-03-31",
                    accession="r-quarter",
                    filed_at="2025-05-10",
                    accepted_at="2025-05-10",
                )
            ),
        ],
    )
    s = _snap(plan)
    checks = []
    _check(
        checks,
        "missing_period_keys",
        sorted(
            [
                "annual_report|2024-07-01|2025-06-30",
                "interim_report|2024-07-01|2024-12-31",
                "quarterly_report|2025-01-01|2025-03-31",
            ]
        ),
        s["period_keys_missing"],
    )
    _check(
        checks,
        "missing_ids",
        ["r-annual", "r-interim", "r-quarter"],
        sorted(s["missing_ids"]),
    )
    return "C05", checks


def _case_C06(mod):
    c = _Remote(**dict(L_ZOLD, fiscal_year=None, accession="fy25-key"))
    plan = _call(mod, [], [c])
    s = _snap(plan)
    checks = []
    _check(checks, "missing_ids", ["fy25-key"], s["missing_ids"])
    report_fy = [
        r.get("fiscal_year_label") for r in getattr(plan, "period_reports", ()) or ()
    ]
    _check(checks, "derived_fiscal_year_label", [2025], report_fy)
    _check(checks, "latest_status", "newer_remote_available", s["latest_status"])
    return "C06", checks


def _case_C07(mod):
    c = _Remote(
        **dict(L_ZOLD, period_start=None, period_end=None, accession="no-period")
    )
    plan = _call(mod, [], [c])
    s = _snap(plan)
    checks = []
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "unknown_period_ids", ["no-period"], s["unknown_note_ids"])
    reports = getattr(plan, "period_reports", ()) or ()
    _check(
        checks,
        "unknown_period_confidence",
        ["annual_report|unknown|unknown"],
        sorted(r["period_key"] for r in reports if r["state"] != "ordered" or True)
        if False
        else [r["period_key"] for r in reports],
    )
    return "C07", checks


def _case_C08(mod):
    c = _Remote(**dict(L_ZOLD, filed_at=None, accepted_at=None, accession="no-dates"))
    plan = _call(mod, [], [c])
    s = _snap(plan)
    checks = []
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "unknown_date_ids", ["no-dates"], s["unknown_note_ids"])
    reasons = [n.get("reason") for n in getattr(plan, "unknown_candidates", ()) or ()]
    _check(
        checks,
        "date_state_unknown_missing_date",
        ["unknown_missing_date"],
        sorted(set(reasons)),
    )
    return "C08", checks


def _case_C09(mod):
    c = _Remote(
        **dict(
            L_ZOLD, accession="bad-acc", filed_at="2026-04-01", accepted_at="2026-03-01"
        )
    )
    plan = _call(mod, [], [c])
    s = _snap(plan)
    checks = []
    _check(checks, "conflicting_ids", ["bad-acc"], s["conflicting_ids"])
    _check(checks, "missing_ids", [], s["missing_ids"])
    return "C09", checks


def _case_C10(mod):
    plan = _call(mod, [], [])
    s = _snap(plan)
    checks = []
    _check(checks, "latest_status", "unknown_empty_success", s["latest_status"])
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "not_published", False, s["not_published"])
    _check(checks, "no_gap", True, s["no_gap"])
    return "C10", checks


def _case_C11(mod):
    plan = _call(mod, [_Local(**L_ZOLD)], [], provider_error="rate_limit_exceeded")
    s = _snap(plan)
    checks = []
    _check(checks, "latest_status", "unknown_provider_failed", s["latest_status"])
    _check(checks, "reuse_ids", ["z-old"], s["reuse_ids"])
    _check(checks, "already_covered", True, s["already_covered"])
    _check(checks, "not_published", False, s["not_published"])
    _check(checks, "provider_unavailable", True, s["provider_unavailable"])
    return "C11", checks


def _case_C12(mod):
    plan = _call(mod, [_Local(**L_ZOLD)], [_Remote(**R_ZOLD)])
    s = _snap(plan)
    checks = []
    _check(checks, "reuse_ids", ["z-old"], s["reuse_ids"])
    _check(checks, "latest_status", "local_is_latest_confirmed", s["latest_status"])
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "newer_revision_ids", [], s["newer_revision_ids"])
    _check(checks, "already_covered", True, s["already_covered"])
    _check(checks, "no_gap", True, s["no_gap"])
    return "C12", checks


def _case_C13(mod):
    plan = _call(mod, [], [_Remote(**R_FUTURE)])
    s = _snap(plan)
    checks = []
    _check(checks, "future_ids", ["a-future"], s["future_ids"])
    _check(checks, "missing_ids", [], s["missing_ids"])
    _check(checks, "not_published", False, s["not_published"])
    _check(checks, "latest_status", "unknown_empty_success", s["latest_status"])
    return "C13", checks


def _case_C14(mod):
    """Planner-facing part of C14: three distinct periods, missing sorted
    period_start DESC (new period first). Batch execution stays I-03-C."""
    plan = _call(
        mod,
        [],
        [
            _Remote(
                **dict(
                    L_ZOLD,
                    period_start="2021-07-01",
                    period_end="2022-06-30",
                    accession="miss-p3",
                )
            ),
            _Remote(
                **dict(
                    L_ZOLD,
                    period_start="2023-07-01",
                    period_end="2024-06-30",
                    accession="miss-p1",
                )
            ),
            _Remote(
                **dict(
                    L_ZOLD,
                    period_start="2022-07-01",
                    period_end="2023-06-30",
                    accession="miss-p2",
                )
            ),
        ],
    )
    s = _snap(plan)
    checks = []
    _check(
        checks,
        "missing_ids_in_d5_order",
        ["miss-p1", "miss-p2", "miss-p3"],
        s["missing_ids"],
    )
    return "C14", checks


def _case_hash(mod):
    """D6 planner side: url/date/period/accepted_at enter the hash; remote
    order does not; identical selection after metadata change => different
    hash (authorization consequently fails closed at I-03-C)."""
    base = _call(mod, [_Local(**L_ZOLD)], [_Remote(**R_ZOLD), _Remote(**R_ANEW)])
    same = _call(mod, [_Local(**L_ZOLD)], [_Remote(**R_ANEW), _Remote(**R_ZOLD)])
    checks = []
    _check(
        checks,
        "hash_order_independent",
        True,
        base.gap_hash
        == _call(
            mod, [_Local(**L_ZOLD)], [_Remote(**R_ANEW), _Remote(**R_ZOLD)]
        ).gap_hash,
    )
    changed = _call(
        mod,
        [_Local(**L_ZOLD)],
        [_Remote(**dict(R_ANEW, url="https://example.org/other.pdf"))],
    )
    _check(checks, "url_change_changes_hash", False, base.gap_hash == changed.gap_hash)
    changed_date = _call(
        mod,
        [_Local(**L_ZOLD)],
        [_Remote(**dict(R_ANEW, filed_at="2026-05-01", accepted_at="2026-05-01"))],
    )
    _check(
        checks,
        "filed_at_change_changes_hash",
        False,
        base.gap_hash == changed_date.gap_hash,
    )
    changed_period = _call(
        mod,
        [_Local(**dict(L_ZOLD, period_end="2025-12-31"))],
        [
            _Remote(**dict(R_ZOLD, period_end="2025-12-31")),
            _Remote(**dict(R_ANEW, period_end="2025-12-31")),
        ],
    )
    _check(
        checks,
        "period_change_changes_hash",
        False,
        base.gap_hash == changed_period.gap_hash,
    )
    _check(checks, "hash_schema_version", 1, getattr(base, "hash_schema_version", None))
    return "HASH-D6", checks


def _market_samples(mod):
    """Three manual metadata samples (card step 5): CN annual/interim,
    HK annual, US non-calendar FY. Field-source simulation declarations
    live in scripts/samples/*.json; all run through the SAME rule engine.
    NOT real-provider acceptance."""
    out = []
    samples = sorted((Path(__file__).parent / "samples").glob("sample_*.json"))
    for path in samples:
        spec = json.loads(path.read_text(encoding="utf-8"))
        for scen in spec["scenarios"]:
            remotes = [
                _Remote(
                    period_start=m["period_start"],
                    period_end=m["period_end"],
                    kind=m["kind"],
                    filed_at=m["filed_at"],
                    accepted_at=m.get("accepted_at"),
                    accession=m["accession"],
                    amended=m.get("amended", False),
                    fiscal_year=m.get("fiscal_year"),
                    url=m["url"],
                    provider=m.get("provider", spec["provider"]),
                )
                for m in scen["remote"]
            ]
            locals_ = [
                _Local(
                    period_start=m["period_start"],
                    period_end=m["period_end"],
                    kind=m["kind"],
                    filed_at=m["filed_at"],
                    accession=m["accession"],
                    capture_ready=True,
                    fiscal_year=m.get("fiscal_year"),
                    accepted_at=m.get("accepted_at"),
                    root="L",
                )
                for m in scen["local"]
            ]
            plan = _call(mod, locals_, remotes)
            s = _snap(plan)
            checks = []
            for field, want in scen["expect"].items():
                got = (
                    sorted(s.get(field, []))
                    if isinstance(want, list) and field != "latest_status"
                    else s.get(field)
                )
                if isinstance(want, list):
                    want = sorted(want)
                _check(checks, field, want, got)
            out.append(
                (
                    f"MARKET:{spec['template']}:{scen['name']}",
                    checks,
                    spec["field_source_simulation"],
                )
            )
    return out


def run(mod):
    results = {}
    for fn in (
        _case_C01,
        _case_C02,
        _case_C03,
        _case_C04,
        _case_C05,
        _case_C06,
        _case_C07,
        _case_C08,
        _case_C09,
        _case_C10,
        _case_C11,
        _case_C12,
        _case_C13,
        _case_C14,
        _case_hash,
    ):
        try:
            case_id, checks = fn(mod)
            results[case_id] = {
                "overall": "pass"
                if all(c["status"] == "pass" for c in checks)
                else "fail",
                "checks": checks,
            }
        except Exception as exc:
            results[fn.__name__.replace("_case_", "C-").upper()] = {
                "overall": "fail",
                "checks": [
                    {
                        "field": "execution",
                        "expected": "ok",
                        "actual": f"exception: {type(exc).__name__}: {exc}",
                        "status": "fail",
                    }
                ],
            }
    for case_id, checks, declaration in _market_samples(mod):
        results[case_id] = {
            "overall": "pass" if all(c["status"] == "pass" for c in checks) else "fail",
            "checks": checks,
            "field_source_declaration": declaration,
        }
    return results


def main():
    impl_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    mod = load_gap_plan_module(impl_path)
    results = run(mod)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "impl": str(impl_path),
                "impl_sha256": None,
                "results": results,
                "summary": {k: v["overall"] for k, v in sorted(results.items())},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    import hashlib

    out = json.loads(out_path.read_text(encoding="utf-8"))
    out["impl_sha256"] = hashlib.sha256(impl_path.read_bytes()).hexdigest()
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
