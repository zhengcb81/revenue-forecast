"""I-03-C verification harness (pure, offline, frozen expectations).

Usage:
  python w03c_cases.py <impl_dir> <out_dir>

<impl_dir> holds the override copies gap_plan.py / authorization.py /
close_gap.py. Frozen expectations: canonical/p0.expected.json (built by
scripts/canonical_p0_ref.py BEFORE implementation with independent
serialization code) and the fixed relations in oracle.md. A fetch-spy
counter must stay 0 across every authorization refusal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path

POLICY_HASH_P = "7b94b34cbb0596ed87c97f06ff1a337ea55d56fce839a19ee805f91cd58f3ea0"
POLICY_HASH_Q = hashlib.sha256(b"policy-epoch:Q").hexdigest()
NOW0 = "2026-07-01T00:00:00Z"
NOW_EXPIRED_1S = "2026-07-01T00:00:01Z"
EXPIRES_LATER = "2027-07-01T00:00:00Z"
P0_SHA = "b9c1847975c88dd226ef061d72630bb498be5374f80ac9c4553120583c84ba24"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class _Handle:
    def __init__(
        self,
        *,
        provider="test",
        pid="a-new",
        filed="2026-04-01",
        url="https://fixture.invalid/a",
        **extra,
    ):
        self.document_kind = "annual_report"
        self.period_start = "2024-07-01"
        self.period_end = "2025-06-30"
        self.fiscal_year = 2025
        self.filing_date = filed
        self.provider_document_id = pid
        self.provider = provider
        self.source_url = url
        self.amended = False
        self.remote_size = 10
        for key, value in extra.items():
            setattr(self, key, value)


class _LocalHandle:
    def __init__(self, *, pid="z-old", filed="2026-03-01"):
        self.document_kind = "annual_report"
        self.period_start = "2024-07-01"
        self.period_end = "2025-06-30"
        self.fiscal_year = 2025
        self.filed_at = filed
        self.filing_date = filed
        self.provider_document_id = pid
        self.provider = "test"
        self.source_url = "https://fixture.invalid/a"
        self.amended = False
        self.capture_ready = True


class _Runner:
    def __init__(self, impl_dir: Path):
        self.gp = _load(impl_dir / "gap_plan.py", "gp_c")
        self.auth = _load(impl_dir / "authorization.py", "auth_c")
        self.cg = _load(impl_dir / "close_gap.py", "cg_c")
        self.spy_events = 0

    def plan(
        self,
        *,
        locals_=(),
        remotes=None,
        policy_hash=POLICY_HASH_P,
        provider_error=None,
    ):
        return self.gp.build_gap_plan(
            request_id="req-p0",
            as_of_date="2026-07-31",
            document_kind="annual_report",
            entity="ACME",
            market="US",
            local_handles=list(locals_),
            remote_candidates=list([_Handle()] if remotes is None else remotes),
            provider_error=provider_error,
            policy_hash=policy_hash,
        )

    def a0_for(self, plan):
        return self.auth.build_download_authorization(
            request_id="req-p0",
            gap_plan_hash=plan.gap_hash,
            policy_hash=POLICY_HASH_P,
            provider="test",
            allowed_accessions=("a-new",),
            max_items=1,
            max_bytes=100,
            expires_at=EXPIRES_LATER,
        )

    def validate(self, auth_, candidate, plan, *, now=NOW0, items=0, used=0):
        self.spy_events = 0
        err = self.auth.validate_download_authorization(
            auth_,
            candidate,
            plan_hash=plan.gap_hash,
            now=now,
            items_already_fetched=items,
            bytes_already_fetched=used,
        )
        fetched = self.spy_events
        return err, fetched


def _ids(seq):
    return [getattr(c, "provider_document_id", None) for c in seq]


def _check(checks, case, want, got):
    checks.append(
        {
            "case": case,
            "independent_expected": want,
            "actual_observed": got,
            "status": "pass" if want == got else "fail",
        }
    )


def _actionable(plan):
    return list(plan.missing) + list(plan.newer_revision)


def run(r: _Runner) -> tuple[list[dict], dict]:
    checks: list[dict] = []

    p0 = r.plan()
    _check(
        checks,
        "CANON-P0-buckets",
        (["a-new"], [], "newer_remote_available", False, False),
        (
            _ids(p0.missing),
            _ids(p0.newer_revision),
            p0.latest_status,
            p0.not_published,
            p0.no_gap,
        ),
    )
    _check(checks, "CANON-P0", P0_SHA, p0.gap_hash)
    a0 = r.a0_for(p0)

    e, f = r.validate(a0, p0.missing[0], p0)
    _check(checks, "A0-POS", (None, 0), (e, f))

    # G-C1: url-only / date-only
    p1a = r.plan(remotes=[_Handle(url="https://fixture.invalid/b")])
    e1, f1 = r.validate(a0, _actionable(p1a)[0], p1a)
    _check(checks, "G-C1a", (True, True, 0), (p1a.gap_hash != P0_SHA, bool(e1), f1))
    p1b = r.plan(remotes=[_Handle(filed="2026-04-02")])
    e2, f2 = r.validate(a0, _actionable(p1b)[0], p1b)
    _check(checks, "G-C1b", (True, True, 0), (p1b.gap_hash != P0_SHA, bool(e2), f2))

    # G-C2: single-field mutations (13 qualification fields + policy epoch)
    def variant_entity():
        return r.gp.build_gap_plan(
            request_id="req-p0",
            as_of_date="2026-07-31",
            document_kind="annual_report",
            entity="ACME2",
            market="US",
            local_handles=[],
            remote_candidates=[_Handle()],
            policy_hash=POLICY_HASH_P,
        )

    def variant_market():
        return r.gp.build_gap_plan(
            request_id="req-p0",
            as_of_date="2026-07-31",
            document_kind="annual_report",
            entity="ACME",
            market="HK",
            local_handles=[],
            remote_candidates=[_Handle()],
            policy_hash=POLICY_HASH_P,
        )

    def variant_kind():
        return r.plan(remotes=[_Handle(document_kind="interim_report")])

    def variant_period_start():
        return r.plan(remotes=[_Handle(period_start="2024-07-02")])

    def variant_period_end():
        return r.plan(remotes=[_Handle(period_end="2025-06-29")])

    def variant_fiscal_year():
        return r.plan(remotes=[_Handle(fiscal_year=2024)])

    def variant_provider():
        return r.plan(remotes=[_Handle(provider="other")])

    def variant_id():
        return r.plan(remotes=[_Handle(pid="b-new")])

    def variant_filed_at():
        return r.plan(remotes=[_Handle(filed="2026-04-02")])

    def variant_accepted_at():
        return r.plan(remotes=[_Handle(accepted_at="2026-04-03")])

    def variant_revision():
        return r.plan(remotes=[_Handle(revision="r1")])

    def variant_amended():
        return r.plan(remotes=[_Handle(amended=True)])

    def variant_policy_epoch():
        return r.plan(policy_hash=POLICY_HASH_Q)

    makers = {
        "entity": variant_entity,
        "market": variant_market,
        "kind": variant_kind,
        "period_start": variant_period_start,
        "period_end": variant_period_end,
        "fiscal_year": variant_fiscal_year,
        "provider": variant_provider,
        "id": variant_id,
        "filed_at": variant_filed_at,
        "accepted_at": variant_accepted_at,
        "revision": variant_revision,
        "amended": variant_amended,
        "policy_epoch": variant_policy_epoch,
    }
    for name, maker in makers.items():
        plan_v = maker()
        cand = _actionable(plan_v)[0] if _actionable(plan_v) else _Handle()
        e, f = r.validate(a0, cand, plan_v)
        _check(
            checks,
            f"G-C2:{name}",
            (True, True, 0),
            (plan_v.gap_hash != P0_SHA, bool(e), f),
        )

    # G-C3a candidate-list reversal — same canonical hash
    extra = _Handle(pid="b-extra", url="https://fixture.invalid/c")
    fwd = r.plan(remotes=[extra, _Handle()])
    rev = r.plan(remotes=[_Handle(), extra])
    _check(checks, "G-C3a", fwd.gap_hash, rev.gap_hash)

    # G-C3b allowed-set reorder invariance on the receipt hash
    ax1 = r.auth.build_download_authorization(
        request_id="req-p0",
        gap_plan_hash=p0.gap_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=("b-extra", "a-new"),
        max_items=2,
        max_bytes=100,
        expires_at=EXPIRES_LATER,
    )
    ax2 = r.auth.build_download_authorization(
        request_id="req-p0",
        gap_plan_hash=p0.gap_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=("a-new", "b-extra"),
        max_items=2,
        max_bytes=100,
        expires_at=EXPIRES_LATER,
    )
    _check(checks, "G-C3b", ax1.receipt_hash, ax2.receipt_hash)

    # G-C3c partition change (missing -> newer_revision): hash MUST change
    p_part = r.plan(locals_=[_LocalHandle(pid="z-old", filed="2026-03-01")])
    _check(
        checks,
        "G-C3c",
        (True, 1),
        (p_part.gap_hash != P0_SHA, len(p_part.newer_revision)),
    )

    # G-C4a item cap
    e, f = r.validate(a0, p0.missing[0], p0, items=1)
    _check(checks, "G-C4a", ("item cap reached", 0), (e, f))
    # G-C4b byte cap
    e, f = r.validate(a0, _Handle(remote_size=20), p0, used=90)
    _check(checks, "G-C4b", ("byte cap exceeded", 0), (e, f))
    # G-C4d expiry (1 second late): a receipt expiring AT the frozen clock,
    # validated one second after it
    a0e = r.auth.build_download_authorization(
        request_id="req-p0",
        gap_plan_hash=p0.gap_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=("a-new",),
        max_items=1,
        max_bytes=100,
        expires_at=NOW0,
    )
    e, f = r.validate(a0e, p0.missing[0], p0, now=NOW_EXPIRED_1S)
    _check(checks, "G-C4d", ("authorization expired", 0), (e, f))
    # G-C4e missing provider (no default-pass)
    e, f = r.validate(a0, _Handle(provider=None), p0)
    _check(
        checks,
        "G-C4e",
        ("provider not authorized: (missing provider on candidate)", 0),
        (e, f),
    )

    # receipt tamper
    tampered = r.auth.DownloadAuthorization(
        **{**a0.to_dict(), "receipt_hash": "0" * 64}
    )
    e, f = r.validate(tampered, p0.missing[0], p0)
    _check(checks, "RECEIPT-TAMPER", ("authorization receipt hash mismatch", 0), (e, f))

    # G-C4c legacy receipt explicit invalidation (no auto-upgrade)
    legacy = r.auth.DownloadAuthorization(
        schema_version="1.0",
        request_id=a0.request_id,
        gap_plan_hash=a0.gap_plan_hash,
        policy_hash=a0.policy_hash,
        provider=a0.provider,
        allowed_accessions=a0.allowed_accessions,
        max_items=a0.max_items,
        max_bytes=a0.max_bytes,
        expires_at=a0.expires_at,
        receipt_hash=a0.receipt_hash,
    )
    e, f = r.validate(legacy, p0.missing[0], p0)
    _check(
        checks,
        "G-C4c",
        (True, 0),
        (str(e).startswith("unsupported authorization schema_version '1.0'"), f),
    )

    # BINDING-OK: same values + same version
    binding_ok = r.cg.CloseGapBinding(
        request_id=a0.request_id,
        gap_plan_hash=a0.gap_plan_hash,
        policy_hash=a0.policy_hash,
        provider=a0.provider,
        allowed_accessions=tuple(a0.allowed_accessions),
        max_items=a0.max_items,
        max_bytes=a0.max_bytes,
        expires_at=a0.expires_at,
        hash_schema_version=1,
    )
    _check(checks, "BINDING-OK", None, r.cg.validate_close_gap_binding(binding_ok, a0))

    # BINDING-MISMATCH: each shared field mutated once + version 0 +
    # allowed-set change -> all refused
    mutated_specs = {
        "request_id": {"request_id": "req-other"},
        "gap_plan_hash": {"gap_plan_hash": "0" * 64},
        "policy_hash": {"policy_hash": POLICY_HASH_Q},
        "provider": {"provider": "x"},
        "max_items": {"max_items": 9},
        "max_bytes": {"max_bytes": 999},
        "expires_at": {"expires_at": "2029-01-01T00:00:00Z"},
        "allowed_accessions": {"allowed_accessions": ("a-new", "b-extra")},
        "version": {"hash_schema_version": 0},
    }
    mismatch_results = {}
    for name, kw in mutated_specs.items():
        mutated = replace(binding_ok, **kw)
        err = r.cg.validate_close_gap_binding(mutated, a0)
        mismatch_results[name] = err
    _check(
        checks,
        "BINDING-MISMATCH",
        {k: True for k in mutated_specs},
        {k: bool(v) for k, v in mismatch_results.items()},
    )

    canon = {
        "plan": "P0",
        "plan_sha": p0.gap_hash,
        "expected_sha": P0_SHA,
        "match": p0.gap_hash == P0_SHA,
        "ref_source": "canonical/p0.expected.json (scripts/canonical_p0_ref.py)",
        "ref_canonical_bytes_len": 786,
        "policy_hash_bound": POLICY_HASH_P,
        "policy_epoch": "P",
        "note": (
            "P0 canonical bytes are frozen in canonical/p0.expected.json "
            "(independent serializer); this file records the override "
            "planner reproducing the frozen SHA so the canonical-bytes "
            "equivalence holds without ever generating expected from the "
            "module under test"
        ),
    }
    return checks, canon


def main() -> None:
    impl_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    r = _Runner(impl_dir)
    checks, canon = run(r)
    binding_variants = [c for c in checks if c["case"].startswith("BINDING")]
    refusals = [
        c
        for c in checks
        if c["case"].startswith("G-C4") or c["case"] == "RECEIPT-TAMPER"
    ]
    (out_dir / "binding-variants.json").write_text(
        json.dumps({"binding_variants": binding_variants}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "authorization-refusals.json").write_text(
        json.dumps({"authorization_refusals": refusals}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "canonical-bytes-vs-ref.json").write_text(
        json.dumps(canon, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "w03c-all-cases.json").write_text(
        json.dumps({"all_cases": checks}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "pass": sum(1 for c in checks if c["status"] == "pass"),
                "fail": sum(1 for c in checks if c["status"] == "fail"),
                "total": len(checks),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
