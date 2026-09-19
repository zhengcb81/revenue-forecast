"""I-03-D verification harness (offline; fake provider INSIDE attempt
A only; frozen expectations from oracle.md — independent, never
generated from the modules under test).

Usage:
  <iso venv python> -X utf8 -B scripts/w03d_cases.py <out_dir> <scratch_dir>

All writes stay inside <scratch_dir>; zero network; URLs are strings.
Fake provider comes from A/samples/fake_provider.py.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from dataclasses import replace
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE.parent
SAMPLES = A / "samples"
sys.path.insert(0, str(SAMPLES))

POLICY_HASH_P = "7b94b34cbb0596ed87c97f06ff1a337ea55d56fce839a19ee805f91cd58f3ea0"
POLICY_HASH_Q = hashlib.sha256(b"policy-epoch:Q").hexdigest()
NOW0 = "2026-07-01T00:00:00Z"
EXPIRES = "2027-07-01T00:00:00Z"
P0_SHA = "b9c1847975c88dd226ef061d72630bb498be5374f80ac9c4553120583c84ba24"

import fake_provider as fp  # noqa: E402 (attempt-A-internal fake)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gp = _load(A / "iso" / "override" / "gap_plan.py", "w03d_gap_plan")
auth = _load(A / "iso" / "override" / "authorization.py", "w03d_auth")
cg = _load(A / "iso" / "override" / "close_gap.py", "w03d_close_gap")


@dataclass(frozen=True)
class Request:
    request_id: str
    entity: str
    market: str
    document_kind: str
    as_of_date: str
    provider: str
    provider_document_id: str | None


REQUEST = Request(
    request_id="req-p0",
    entity="ACME",
    market="US",
    document_kind="annual_report",
    as_of_date="2026-07-31",
    provider="test",
    provider_document_id="a-new",
)


def remote_cand(pid, **kw) -> fp.Candidate:
    kw.setdefault("provider", "test")
    kw.setdefault("url", f"https://fixture.invalid/{pid}")
    kw.setdefault("filed", "2026-04-01")
    kw.setdefault("period_start", "2024-07-01")
    kw.setdefault("period_end", "2025-06-30")
    kw.setdefault("fiscal_year", 2025)
    return fp.Candidate(pid=pid, **kw)


class LocalHandle:
    def __init__(self, *, pid, filed):
        self.document_kind = "annual_report"
        self.period_start = "2024-07-01"
        self.period_end = "2025-06-30"
        self.fiscal_year = 2025
        self.filed_at = filed
        self.filing_date = filed
        self.provider = "test"
        self.provider_document_id = pid
        self.source_url = "https://fixture.invalid/local"
        self.amended = False
        self.capture_ready = True


def _record(checks: list, case: str, want, got):
    checks.append(
        {
            "case": case,
            "independent_expected": want,
            "actual_observed": got,
            "status": "pass" if want == got else "fail",
        }
    )


def make_workdir(case: str, scratch: Path) -> Path:
    base = scratch / case
    (base / "raw_root").mkdir(parents=True, exist_ok=True)
    return base


def _registrar(case_dir: Path) -> cg.MinimalRegistrar:
    return cg.MinimalRegistrar(
        raw_root=case_dir / "raw_root",
        root_policy={"reusable_for_filing": True},
        store_path=case_dir / "catalog.sqlite3",
    )


def _catalog_rows(case_dir: Path) -> list[dict]:
    p = case_dir / "catalog.sqlite3"
    if not p.exists():
        return []
    conn = sqlite3.connect(p)
    try:
        rows = conn.execute("SELECT content_sha256, status FROM documents").fetchall()
    finally:
        conn.close()
    return [{"content_sha256": sha, "status": st} for sha, st in rows]


def build_plan(cands, locals_=(), *, policy_hash=POLICY_HASH_P, provider_error=None):
    return gp.build_gap_plan(
        request_id=REQUEST.request_id,
        as_of_date=REQUEST.as_of_date,
        document_kind=REQUEST.document_kind,
        entity=REQUEST.entity,
        market=REQUEST.market,
        local_handles=list(locals_),
        remote_candidates=list(cands),
        provider_error=provider_error,
        policy_hash=policy_hash,
    )


def make_binding(plan_hash: str, *, pids, max_items, max_bytes):
    return cg.CloseGapBinding(
        request_id="req-p0",
        gap_plan_hash=plan_hash,
        policy_hash=POLICY_HASH_P,
        provider="test",
        allowed_accessions=tuple(pids),
        max_items=max_items,
        max_bytes=max_bytes,
        expires_at=EXPIRES,
        hash_schema_version=1,
    )


def _authorization(binding):
    return auth.build_download_authorization(
        request_id=binding.request_id,
        gap_plan_hash=binding.gap_plan_hash,
        policy_hash=binding.policy_hash,
        provider=binding.provider,
        allowed_accessions=tuple(binding.allowed_accessions),
        max_items=binding.max_items,
        max_bytes=binding.max_bytes,
        expires_at=binding.expires_at,
    )


def _count_types(events):
    base = {
        "provider_fetch_attempt": 0,
        "bytes_received": 0,
        "raw_saved": 0,
        "registration_succeeded": 0,
    }
    for e in events:
        base[e["outcome"]] = base.get(e["outcome"], 0) + 1
    return base


class Rediscover:
    """Mutable world between the pre-lock (first) rediscover and the
    in-lock (second) rediscover. The BARRIER hook mutates the world."""

    def __init__(
        self, cands, locals_=(), *, policy_hash=POLICY_HASH_P, provider_error=None
    ):
        self.snap = None
        self.set_world(
            cands, locals_, policy_hash=policy_hash, provider_error=provider_error
        )
        self.calls = 0

    def set_world(
        self, cands, locals_=(), *, policy_hash=POLICY_HASH_P, provider_error=None
    ):
        self.snap = {
            "remote_candidates": list(cands),
            "local_handles": list(locals_),
            "provider_error": provider_error,
            "policy_hash": policy_hash,
        }

    def __call__(self):
        self.calls += 1
        return dict(self.snap)


def run_txn(
    world: Rediscover,
    registrar,
    *,
    plan_hash,
    pids,
    max_items,
    max_bytes,
    ledger=None,
    stream_fn=None,
    now=NOW0,
):
    """One isolated close-gap call; returns (txn, ledger)."""
    ledger = ledger or cg.EventLedger()
    binding = make_binding(
        plan_hash, pids=pids, max_items=max_items, max_bytes=max_bytes
    )
    authorization = _authorization(binding)
    txn = cg.run_close_gap_transaction(
        binding=binding,
        authorization=authorization,
        planner=gp,
        request=REQUEST,
        rediscover=world,
        stream=stream_fn or [],  # never streamed when not mapped
        registrar=registrar,
        auth_module=auth,
        ledger=ledger,
        now=now,
    )
    txn["authorization_receipt_hash"] = authorization.receipt_hash
    txn["binding_gap_plan_hash"] = binding.gap_plan_hash
    txn["binding_hash"] = hashlib.sha256(
        json.dumps(binding.to_dict(), sort_keys=True, ensure_ascii=False).encode(
            "utf-8"
        )
    ).hexdigest()
    return txn, ledger


# ---------------------------------------------------------------------------
# cases
# ---------------------------------------------------------------------------


def case_canonical(checks: list):
    """The override planner reproduces the I-03-C frozen P0 SHA
    (inherited, independent; not computed by running the executor)."""
    plan = build_plan(
        [remote_cand("a-new", url="https://fixture.invalid/a", remote_size=10)]
    )
    _record(checks, "CANON-P0-sha", P0_SHA, plan.gap_hash)


def case_gd5(scratch: Path, checks: list, events_by_case: dict):
    """G-D5: pre-lock world = P0; the mutation happens ONLY inside the
    deterministic BARRIER seam (before the in-lock rediscover)."""

    def mutant(name):
        if name == "url":
            world_c = [
                remote_cand("a-new", url="https://fixture.invalid/b", remote_size=10)
            ]
            return world_c, POLICY_HASH_P
        if name == "filed":
            world_c = [
                remote_cand(
                    "a-new",
                    url="https://fixture.invalid/a",
                    filed="2026-04-02",
                    remote_size=10,
                )
            ]
            return world_c, POLICY_HASH_P
        w_p = [remote_cand("a-new", url="https://fixture.invalid/a", remote_size=10)]
        return w_p, POLICY_HASH_Q

    for name in ("url", "filed", "policy"):
        case = f"gd5_{name}"
        cdir = make_workdir(case, scratch)
        reg = _registrar(cdir)
        before = _catalog_rows(cdir)
        pre_plan = build_plan(
            [remote_cand("a-new", url="https://fixture.invalid/a", remote_size=10)],
            policy_hash=POLICY_HASH_P,
        )
        _record(checks, f"{case}:plan_before_hash==P0", P0_SHA, pre_plan.gap_hash)
        world = Rediscover(
            [remote_cand("a-new", url="https://fixture.invalid/a", remote_size=10)],
            policy_hash=POLICY_HASH_P,
        )
        mut_cands, mut_policy = mutant(name)

        def barrier(txn, _w=world, _c=mut_cands, _policy=mut_policy):
            _w.set_world(_c, policy_hash=_policy)

        cg._BARRIER_HOOK = barrier
        ledger = cg.EventLedger()
        txn, ledger2 = run_txn(
            world,
            reg,
            plan_hash=P0_SHA,
            pids=("a-new",),
            max_items=1,
            max_bytes=1000,
            ledger=ledger,
            stream_fn=fail_on_call_stream,
        )
        cg._BARRIER_HOOK = None
        after = _catalog_rows(cdir)
        counts = _count_types(ledger2.events)
        got = (
            txn["status"],
            txn["reason"],
            counts["provider_fetch_attempt"],
            counts["bytes_received"],
            counts["raw_saved"],
            counts["registration_succeeded"],
            txn["plan_before_lock_hash"] != txn["plan_in_lock_hash"],
            before == after,
        )
        want = ("rejected", "stale_gap_hash", 0, 0, 0, 0, True, True)
        _record(checks, f"{case}:stale", want, got)
        probe = bool(txn.get("authorization_probe"))
        _record(checks, f"{case}:auth_probe_true", True, probe)
        events_by_case[case] = {
            "events": ledger2.events,
            "event_counts": counts,
            "txn_status": txn["status"],
            "reason": txn["reason"],
            "plan_before_lock_hash": txn.get("plan_before_lock_hash"),
            "plan_in_lock_hash": txn.get("plan_in_lock_hash"),
            "binding_hash": txn.get("binding_hash"),
            "authorization_probe": txn.get("authorization_probe"),
            "catalog_before": before,
            "catalog_after": after,
        }


def fail_on_call_stream(_cand):
    raise AssertionError("stream must never be reached in G-D5/G-D9 paths")


def case_gd6(scratch: Path, checks: list, events_by_case: dict):
    case = "gd6_two_gaps_max_items_1"
    cdir = make_workdir(case, scratch)
    reg = _registrar(cdir)
    candA = remote_cand(
        "a-pA", filed="2026-04-01", period_start="2024-07-01", period_end="2025-06-30"
    )
    candB = remote_cand(
        "a-pB", filed="2025-04-01", period_start="2023-07-01", period_end="2024-06-30"
    )
    plan = build_plan([candA, candB])
    _record(
        checks,
        f"{case}:plan_hash(short64)",
        ("a-pA", "a-pB"),
        tuple(c.provider_document_id for c in plan.missing),
    )
    provider = fp.FakeProvider(
        catalog_candidates=[candA, candB], policy_hash=POLICY_HASH_P
    )
    provider.script("a-pA", ("chunks", [b"FAKE-A0", b"FAKE-A1"]))
    ledger = cg.EventLedger()
    txn, ledger2 = run_txn(
        _holder(provider),
        reg,
        plan_hash=plan.gap_hash,
        pids=("a-pA", "a-pB"),
        max_items=1,
        max_bytes=1000,
        ledger=ledger,
        stream_fn=provider.stream,
    )
    counts = _count_types(ledger2.events)
    _record(checks, f"{case}:MAX_BATCH_SIZE_constant", 8, cg.MAX_BATCH_SIZE)
    _record(checks, f"{case}:scenario_cap_is_min(1,8)=1", 1, min(1, cg.MAX_BATCH_SIZE))
    expected = (
        "completed_partial",
        1,
        1,
        ["a-pB"],
        {"a-pA": "completed", "a-pB": "pending_next_batch"},
        {
            "provider_fetch_attempt": 1,
            "bytes_received": 2,
            "raw_saved": 1,
            "registration_succeeded": 1,
        },
    )
    state_map = {k: v["state"] for k, v in txn["gap_items"].items()}
    got = (
        txn["status"],
        txn["processed_count"],
        txn["remaining_count"],
        txn["pending_accessions"],
        state_map,
        counts,
    )
    _record(checks, f"{case}:bounded_batch", expected, got)
    events_by_case[case] = {
        "events": ledger2.events,
        "event_counts": counts,
        "txn_status": txn["status"],
        "plan_missing_period_keys": [pr["period_key"] for pr in plan.period_reports],
        "gap_items": txn["gap_items"],
        "processed": txn["processed_count"],
        "remaining": txn["remaining_count"],
        "catalog_before": [],
        "catalog_after": _catalog_rows(cdir),
    }


def _holder(provider: fp.FakeProvider):
    return provider.discover_snapshot


def case_gd7(scratch: Path, checks: list, events_by_case: dict):
    variants = [("remote_size_null", None), ("remote_size_lies_80", 80)]
    for name, declared in variants:
        case = f"gd7_{name}"
        cdir = make_workdir(case, scratch)
        reg = _registrar(cdir)
        cand = remote_cand(
            "a-cap", url="https://fixture.invalid/cap", remote_size=declared
        )
        plan = build_plan([cand])
        binding = make_binding(
            plan.gap_hash, pids=("a-cap",), max_items=2, max_bytes=100
        )
        authorization = _authorization(binding)
        # independent expectation: the real validation exit passes at
        # plan level (unknown size counts as 0; 80 ≤ 100)
        probe = auth.validate_download_authorization(
            authorization,
            cand,
            plan_hash=plan.gap_hash,
            now=NOW0,
            items_already_fetched=0,
            bytes_already_fetched=0,
        )
        _record(checks, f"{case}:plan_level_validate_allows_mutation", None, probe)
        provider = fp.FakeProvider(catalog_candidates=[cand], policy_hash=POLICY_HASH_P)
        provider.script(
            "a-cap",
            ("chunks", [b"FAKE-CH1-".ljust(60, b"X"), b"FAKE-CH2-".ljust(60, b"Y")]),
        )
        ledger = cg.EventLedger()
        txn, ledger2 = run_txn(
            _holder(provider),
            reg,
            plan_hash=plan.gap_hash,
            pids=("a-cap",),
            max_items=2,
            max_bytes=100,
            ledger=ledger,
            stream_fn=provider.stream,
        )
        br = [e for e in ledger2.events if e["outcome"] == "bytes_received"]
        cumulative = [e["cumulative_bytes"] for e in br]
        counts = _count_types(ledger2.events)
        _record(checks, f"{case}:bytes_received_events_2", 2, len(br))
        _record(checks, f"{case}:cumulative_progression", [60, 120], cumulative)
        _record(
            checks,
            f"{case}:last_chunk_over_cap_true",
            True,
            bool(br[-1]["over_cap"]) if br else None,
        )
        _record(
            checks,
            f"{case}:stream_stopped_on_over_chunk",
            True,
            bool(br[-1]["stream_stopped"]) if br else None,
        )
        _record(
            checks,
            f"{case}:provider_yielded_exactly_2",
            2,
            provider.consumed.get("a-cap"),
        )
        _record(
            checks,
            f"{case}:no_qualified_handle_or_commit",
            (0, 0, "failed", "byte_cap_exceeded_in_stream", ["a-cap"]),
            (
                counts["raw_saved"],
                counts["registration_succeeded"],
                txn["status"],
                txn["reason"],
                txn["pending_accessions"],
            ),
        )
        events_by_case[case] = {
            "events": ledger2.events,
            "event_counts": counts,
            "txn_status": txn["status"],
            "reason": txn["reason"],
            "declared_remote_size": declared,
            "physically_received_bytes": sum(e["chunk_bytes"] for e in br),
            "over_cap_chunks": [e for e in br if e["over_cap"]],
            "catalog_before": [],
            "catalog_after": _catalog_rows(cdir),
        }


def case_gd8(scratch: Path, checks: list, events_by_case: dict):
    case = "gd8_raw_saved_then_retry_registration"
    cdir = make_workdir(case, scratch)
    cand = remote_cand("a-reg", url="https://fixture.invalid/reg")
    plan = build_plan([cand])
    provider = fp.FakeProvider(catalog_candidates=[cand], policy_hash=POLICY_HASH_P)
    provider.script("a-reg", ("chunks", [b"FAKE-REG".ljust(40, b"Z")]))
    ledger = cg.EventLedger()
    # injected: registration fails ONCE at R5 (bytes recompute) — an
    # explicitly injected gate failure, NOT a genuine one.
    good = _registrar(cdir)

    class FailingOnceRegistrar:
        raw_root = good.raw_root

        def __init__(self):
            self.calls = 0

        def register(self, **kw):
            self.calls += 1
            if self.calls == 1:
                return {
                    "ok": False,
                    "reason": "registration: INJECTED Gate-F5 failure",
                    "gates": {
                        "R1_root_policy_reusable": True,
                        "R2_root_containment": True,
                        "R3_sidecar_adjacent": True,
                        "R4_provenance_complete": True,
                        "R5_bytes_recompute": False,
                    },
                }
            return good.register(**kw)

    fail_reg = FailingOnceRegistrar()

    txn1, ledger1 = run_txn(
        _holder(provider),
        fail_reg,
        plan_hash=plan.gap_hash,
        pids=("a-reg",),
        max_items=1,
        max_bytes=1000,
        ledger=ledger,
        stream_fn=provider.stream,
    )
    counts1 = _count_types(ledger1.events)
    raw_rows = sorted((cdir / "raw_root").glob("a-reg_*.pdf"))
    side_rows = sorted((cdir / "raw_root").glob("a-reg_*.pdf.source.json"))
    _record(
        checks,
        f"{case}:run1",
        (1, 1, 1, 0, "failed", 1, 1),
        (
            counts1["provider_fetch_attempt"],
            counts1["bytes_received"],
            counts1["raw_saved"],
            counts1["registration_succeeded"],
            txn1["status"],
            len(raw_rows),
            len(side_rows),
        ),
    )
    _record(
        checks,
        f"{case}:run1_state",
        "raw_saved_registration_pending",
        txn1["gap_items"]["a-reg"]["state"],
    )
    # run 2: retry ONLY the registration; stream must never be called.
    recover = list(raw_rows)[0]
    recover_side = recover.with_name(recover.name + ".source.json")
    guard = cg.EventLedger()  # spy: any NEW fetch inside resume → fail
    fetch_spy = {"n": 0}

    def spying_stream(_cand):
        fetch_spy["n"] += 1
        raise AssertionError("G-D8 run2 must not fetch")

    txn2 = cg.resume_registration(
        binding=make_binding(
            plan.gap_hash, pids=("a-reg",), max_items=1, max_bytes=1000
        ),
        authorization=_authorization(
            make_binding(plan.gap_hash, pids=("a-pB",), max_items=1, max_bytes=1)
        )
        if False
        else _authorization(
            make_binding(plan.gap_hash, pids=("a-reg",), max_items=1, max_bytes=1000)
        ),
        registrar=good,
        request=replace(REQUEST, provider_document_id="a-reg"),
        auth_module=auth,
        ledger=ledger1,
        recovery_raw_path=str(recover),
        recovery_sidecar_path=str(recover_side),
        now=NOW0,
    )
    counts2 = _count_types(
        [
            e
            for e in ledger1.events
            if e["outcome"] != "raw_saved" and e["txn_id"] != txn1["txn_id"]
        ]
        if False
        else ledger1.events
    )
    reg2 = [e for e in ledger1.events if e["outcome"] == "registration_succeeded"]
    _record(
        checks,
        f"{case}:run2",
        ("completed", 0, 1),
        (txn2["status"], txn2["fetch_events"], counts2["registration_succeeded"]),
    )
    events_by_case[case] = {
        "run1_events": ledger1.events,
        "run1_counts": counts1,
        "run1_status": txn1["status"],
        "run1_reason": txn1["reason"],
        "run2_status": txn2["status"],
        "run2_reason": txn2["reason"],
        "run2_fetch_events": txn2["fetch_events"],
        "run2_registration_succeeded": counts2["registration_succeeded"],
        "run1_registrar_injected": "Gate-F5 at R5",
        "run1_raw_retained": [str(p) for p in raw_rows],
        "run1_sidecar_retained": [str(p) for p in side_rows],
        "run2_gates": ledger1.events[-1].get("gates"),
        "catalog_before": [],
        "catalog_after": _catalog_rows(cdir),
    }


def case_gd9(scratch: Path, checks: list, events_by_case: dict):
    # var1: provider exception + reusable local, all fetch=0
    case = "gd9_provider_error_local_reuse"
    cdir = make_workdir(case, scratch)
    reg = _registrar(cdir)
    plan = build_plan(
        [],
        [LocalHandle(pid="z-old", filed="2026-03-01")],
        provider_error="discover boom",
    )
    world = Rediscover(
        [],
        [LocalHandle(pid="z-old", filed="2026-03-01")],
        provider_error="discover boom",
    )
    ledger = cg.EventLedger()
    txn, ledger2 = run_txn(
        world,
        reg,
        plan_hash=plan.gap_hash,
        pids=("z-old",),
        max_items=1,
        max_bytes=1000,
        ledger=ledger,
        stream_fn=fail_on_call_stream,
    )
    counts = _count_types(ledger2.events)
    reuse = [
        st["state"]
        for st in txn["gap_items"].values()
        if st["state"] == "completed_reused"
    ]
    _record(
        checks,
        f"{case}:completions",
        ("completed", 0, [1], "unknown_provider_failed", False),
        (
            txn["status"],
            counts["provider_fetch_attempt"],
            [len(reuse)],
            txn.get("latest_status"),
            txn.get("not_published_plan"),
        ),
    )
    events_by_case[case] = {
        "events": ledger2.events,
        "event_counts": counts,
        "txn": txn,
    }

    # var2: empty success world, no locals
    case = "gd9_empty_success"
    cdir2 = make_workdir(case, scratch)
    reg2 = _registrar(cdir2)
    plan2 = build_plan([])
    _record(
        checks,
        f"{case}:empty_latest_status",
        "unknown_empty_success",
        plan2.latest_status,
    )
    world2 = Rediscover([], policy_hash=POLICY_HASH_P)
    ledger = cg.EventLedger()
    txn2, ledger2 = run_txn(
        world2,
        reg2,
        plan_hash=plan2.gap_hash,
        pids=("none-actionable",),
        max_items=1,
        max_bytes=1000,
        ledger=ledger,
        stream_fn=fail_on_call_stream,
    )
    counts2 = _count_types(ledger2.events)
    _record(
        checks,
        f"{case}:no_fetch_no_notpublished",
        ("completed", 0, False),
        (txn2["status"], counts2["provider_fetch_attempt"], plan2.not_published),
    )
    events_by_case[case] = {
        "events": ledger2.events,
        "event_counts": counts2,
        "txn": txn2,
    }

    # var3: local reusable older-style; remote file older → no download
    case = "gd9_local_reusable_no_unauthorized_download"
    cdir3 = make_workdir(case, scratch)
    reg3 = _registrar(cdir3)
    precision_local = LocalHandle(pid="z-old", filed="2026-03-01")
    remote_older = remote_cand(
        "a-older", filed="2026-02-01", url="https://fixture.invalid/older"
    )
    plan3 = build_plan([remote_older], [precision_local])
    _record(
        checks,
        f"{case}:local_not_demoted_reuse_only_actions",
        (
            [],
            [],
        ),
        (
            [c.provider_document_id for c in plan3.missing],
            [c.provider_document_id for c in plan3.newer_revision],
        ),
    )
    world3 = Rediscover([remote_older], [precision_local])
    ledger = cg.EventLedger()
    txn3, ledger3 = run_txn(
        world3,
        reg3,
        plan_hash=plan3.gap_hash,
        pids=("z-old",),
        max_items=1,
        max_bytes=1000,
        ledger=ledger,
        stream_fn=fail_on_call_stream,
    )
    counts3 = _count_types(ledger3.events)
    _record(
        checks,
        f"{case}:reuse_no_unauthorized_fetch",
        ("completed", 0, 0, 0, 0, 0),
        (
            txn3["status"],
            counts3["provider_fetch_attempt"],
            counts3["bytes_received"],
            counts3["raw_saved"],
            counts3["registration_succeeded"],
            txn3["fetch_events"],
        ),
    )
    events_by_case[case] = {
        "events": ledger3.events,
        "event_counts": counts3,
        "txn": txn3,
    }


def main() -> None:
    out_dir = Path(sys.argv[1])
    scratch = Path(sys.argv[2])
    scratch.mkdir(parents=True, exist_ok=True)
    checks: list = []
    events_by_case: dict = {}
    case_canonical(checks)
    case_gd5(scratch, checks, events_by_case)
    case_gd6(scratch, checks, events_by_case)
    case_gd7(scratch, checks, events_by_case)
    case_gd8(scratch, checks, events_by_case)
    case_gd9(scratch, checks, events_by_case)
    passed = sum(1 for c in checks if c.get("status") == "pass")
    failed = sum(1 for c in checks if c.get("status") == "fail")
    (out_dir / "close-gap-matrix.json").write_text(
        json.dumps(
            {"all_checks": checks, "pass": passed, "fail": failed},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "provider-events-ledger.json").write_text(
        json.dumps({"cases": events_by_case}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # remaining-gap semantics from the observable G-D6 case
    gd6 = events_by_case.get("gd6_two_gaps_max_items_1", {})
    table = gd6.get("gap_items", {})
    periods = {}
    for pid, st in table.items():
        per = plan_period(pid)
        periods[per] = {
            "state": st["state"],
            "covered": st["state"] in ("completed", "completed_reused"),
            "pending": st["state"]
            in (
                "pending_next_batch",
                "pending_authorized_not_fetched",
                "raw_saved_registration_pending",
            ),
        }
    remaining_gap = sum(1 for v in periods.values() if v["pending"])
    (out_dir / "remaining-gap-semantic.json").write_text(
        json.dumps(
            {
                "by_period": periods,
                "total_periods": len(periods),
                "remaining_gap": remaining_gap,
                "claim_allowed": remaining_gap == 0,
                "txn_status": gd6.get("txn_status"),
                "MAX_BATCH_SIZE": cg.MAX_BATCH_SIZE,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "catalog-before-after.json").write_text(
        json.dumps(
            {
                c: {
                    "catalog_after": d.get("catalog_after"),
                    "catalog_before": d.get("catalog_before"),
                }
                for c, d in events_by_case.items()
                if "catalog_after" in d
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"pass": passed, "fail": failed}, ensure_ascii=False))


def plan_period(pid: str) -> str:
    return {
        "a-pA": "annual_report|2024-07-01|2025-06-30",
        "a-pB": "annual_report|2023-07-01|2024-06-30",
        "a-new": "annual_report|2024-07-01|2025-06-30",
        "a-reg": "annual_report|2024-07-01|2025-06-30",
        "a-cap": "annual_report|2024-07-01|2025-06-30",
        "z-old": "annual_report|2024-07-01|2025-06-30",
        "": "",
    }.get(pid, pid)


if __name__ == "__main__":
    main()
