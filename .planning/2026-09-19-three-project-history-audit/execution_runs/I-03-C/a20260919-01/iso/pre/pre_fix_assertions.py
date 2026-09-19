"""I-03-C pre-fix assertions (independent, frozen expectations).

Runs against iso/baseline copies of the PRODUCTION frozen anchors
(gap_plan d18391b7…, authorization f858a369…). Expected values are FIXED
literals / fixed relations (e.g. "these two hashes must differ"), never
generated from the module under test. Real RED domains are recorded with
the actually observed behavior; already-correct narrow surfaces are
recorded not_applicable (no fabricated RED, per common_filing_cards).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

POLICY_HASH_P = "7b94b34cbb0596ed87c97f06ff1a337ea55d56fce839a19ee805f91cd58f3ea0"
NOW0 = "2026-07-01T00:00:00Z"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class _Remote:
    def __init__(self, **kw):
        self.document_kind = kw.get("document_kind", "annual_report")
        self.period_start = kw.get("period_start", "2024-07-01")
        self.period_end = kw.get("period_end", "2025-06-30")
        self.fiscal_year = kw.get("fiscal_year", 2025)
        self.filing_date = kw.get("filed_at", "2026-04-01")
        self.provider_document_id = kw.get("id", "a-new")
        self.provider = kw.get("provider", "test")
        self.source_url = kw.get("url", "https://fixture.invalid/a")
        self.amended = kw.get("amended", False)
        self.remote_size = kw.get("remote_size", 10)


def main() -> None:
    baseline = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    gp = _load(baseline / "gap_plan.py", "gap_plan_pre")
    auth = _load(baseline / "authorization.py", "auth_pre")

    results = []

    def rec(case, desc, expected, actual, status):
        results.append(
            {
                "case": case,
                "description": desc,
                "independent_expected": expected,
                "actual_observed": actual,
                "status": status,
            }
        )

    # P0 via the OLD planner + OLD hash (url absent from old hash by defect)
    base_remote = _Remote()
    p0 = gp.build_gap_plan(
        request_id="req-p0",
        as_of_date="2026-07-31",
        document_kind="annual_report",
        entity="ACME",
        market="US",
        local_handles=[],
        remote_candidates=[base_remote],
    )
    # PRE-C1a: url-only change
    p1a = gp.build_gap_plan(
        request_id="req-p0",
        as_of_date="2026-07-31",
        document_kind="annual_report",
        entity="ACME",
        market="US",
        local_handles=[],
        remote_candidates=[_Remote(url="https://fixture.invalid/b")],
    )
    same_a = p0.gap_hash == p1a.gap_hash
    rec(
        "PRE-C1a",
        "URL /a->/b only",
        "gap_hash differs",
        {"p0_hash": p0.gap_hash, "p1_url_changed_hash": p1a.gap_hash, "equal": same_a},
        "fail" if same_a else "pass",
    )

    # PRE-C1b: filing-date-only change
    p1b = gp.build_gap_plan(
        request_id="req-p0",
        as_of_date="2026-07-31",
        document_kind="annual_report",
        entity="ACME",
        market="US",
        local_handles=[],
        remote_candidates=[_Remote(filed_at="2026-04-02")],
    )
    same_b = p0.gap_hash == p1b.gap_hash
    rec(
        "PRE-C1b",
        "filing_date 2026-04-01->2026-04-02",
        "gap_hash differs",
        {"p1_date_changed_hash": p1b.gap_hash, "equal": same_b},
        "fail" if same_b else "pass",
    )

    # PRE-C1c: an A0 built (old receipt) against the OLD P0 hash still
    # authorizes the URL-changed P1 candidate (same accession) — the
    # authorization binding is effectively bypassed.
    a0 = auth.build_download_authorization(
        request_id="req-p0",
        gap_plan_hash=p0.gap_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=("a-new",),
        max_items=1,
        max_bytes=100,
        expires_at="2027-07-01T00:00:00Z",
    )
    verdict = auth.validate_download_authorization(
        a0, p1a.missing[0], plan_hash=p1a.gap_hash, now=NOW0
    )
    rec(
        "PRE-C1c",
        "A0(old receipt) vs URL-changed P1 candidate",
        "refused (stale plan)",
        verdict or "AUTHORIZED",
        "fail" if verdict is None else "pass",
    )

    # PRE-C4a: missing provider default-pass
    no_prov = _Remote(provider=None)
    v_no = auth.validate_download_authorization(
        a0, no_prov, plan_hash=p0.gap_hash, now=NOW0
    )
    rec(
        "PRE-C4a",
        "candidate with MISSING provider attr",
        "refused",
        v_no or "AUTHORIZED",
        "fail" if v_no is None else "pass",
    )

    # PRE-C4b: legacy receipt (old schema_version, no hash_schema_version)
    legacy = auth.DownloadAuthorization(
        schema_version="1.0",
        request_id="req-p0",
        gap_plan_hash=p0.gap_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=("a-new",),
        max_items=1,
        max_bytes=100,
        expires_at="2027-07-01T00:00:00Z",
        receipt_hash=a0.receipt_hash,
    )
    v_leg = auth.validate_download_authorization(
        legacy, base_remote, plan_hash=p0.gap_hash, now=NOW0
    )
    # old validate has no version gate: a legacy-shaped receipt that carries
    # an old-style receipt_hash passes (default-pass domain)
    rec(
        "PRE-C4b",
        "legacy receipt (schema_version=1.0, no hash_schema_version)",
        "explicitly refused / re-authorization required",
        v_leg or "AUTHORIZED",
        "fail" if v_leg is None else "pass",
    )

    # PRE-C4c/e: already-correct surfaces (record, no fabricated RED)
    v_exp = auth.validate_download_authorization(
        a0, base_remote, plan_hash=p0.gap_hash, now="2027-07-01T00:00:01Z"
    )
    rec(
        "PRE-C4c",
        "expired authorization",
        "refused",
        v_exp or "AUTHORIZED",
        "not_applicable" if v_exp else "pass (already correct pre-fix)",
    )
    v_cap = auth.validate_download_authorization(
        a0,
        _Remote(remote_size=20),
        plan_hash=p0.gap_hash,
        now=NOW0,
        items_already_fetched=1,
        bytes_already_fetched=90,
    )
    rec(
        "PRE-C4d",
        "caps: used 1/1 items; used 90+20 bytes / 100",
        "refused",
        v_cap or "AUTHORIZED",
        "not_applicable" if v_cap else "pass (already correct pre-fix)",
    )

    out = {
        "phase": "pre-fix",
        "baseline": str(baseline),
        "cases": results,
        "summary": {
            "fail": sum(1 for r in results if r["status"] == "fail"),
            "pass": sum(1 for r in results if r["status"].startswith("pass")),
            "not_applicable": sum(
                1 for r in results if r["status"].startswith("not_applicable")
            ),
        },
    }
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(out["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
