"""FIX-W06-GAPS C7 scenario runner: state_domain fail-closed disambiguation.

Runs against ONE pkg dir (before/cw or iso/pi_pkg).  Expected contract is
oracle C7-SCOPE (state_domain fallback adopted after the frozen-vocabulary
conflict check).  Scenarios:
  N1  cache-invalidation record cannot be read as a review conclusion
      (gate rejects; policy-changed evaluation stays status="not_reviewed")
  N2  a detected_and_ignored review record cannot be read as cache state
  N3  record MISSING state_domain => rejected at both boundaries
      (receipt read fail-closed -> None; ReviewEvaluation construction -> TypeError)
  N4  illegal value => rejected / strictest
      (bad domain tag; cross-domain tag on ReviewEvaluation; unknown cache_state
       in readiness _SAFETY_MAP -> strictest "unsatisfied", never KeyError)

Usage: python -X utf8 -B s_c7_state_domain.py --pkg-dir <dir> --out <evidence.txt>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

LOG: list[str] = []
RESULTS: dict = {}

STUB_READER = '''
from typing import Any
class CatalogReader:  # minimal import stub for readiness_graph (scenario harness)
    def fetchone(self, sql, params=()):  # pragma: no cover
        raise NotImplementedError
'''
STUB_LIFECYCLE = '''
from dataclasses import dataclass, field
from typing import Any
@dataclass(frozen=True)
class ConsumerRequirements:
    required_stages: tuple = ()
@dataclass(frozen=True)
class SourceReadiness:
    stages: tuple = ()
def evaluate_source_readiness(reader, source_id, requirements=None):  # pragma: no cover
    return SourceReadiness(stages=())
'''


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def attempt(fn):
    try:
        value = fn()
        return {"outcome": "ACCEPTED", "value": value}
    except BaseException as exc:  # noqa: BLE001
        return {"outcome": "REJECTED", "error_type": type(exc).__name__, "text": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "c7"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    pkg = TMP / "pi_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for f in args.pkg_dir.glob("*.py"):
        shutil.copy2(f, pkg / f.name)
    # import stubs for readiness_graph siblings (identical for before/ and iso/)
    if not (pkg / "reader.py").exists():
        (pkg / "reader.py").write_text(STUB_READER, encoding="utf-8")
    if not (pkg / "source_lifecycle.py").exists():
        (pkg / "source_lifecycle.py").write_text(STUB_LIFECYCLE, encoding="utf-8")
    log(f"target pkg-dir : {args.pkg_dir}")
    for f in sorted(pkg.glob("*.py")):
        log(f"    {f.name} sha256={hashlib.sha256(f.read_bytes()).hexdigest()}")
    log()
    sys.path.insert(0, str(TMP))
    import pi_pkg.prompt_injection as pi
    import pi_pkg.prompt_injection_guard as guard
    import pi_pkg.readiness_graph as rg

    def gate(value, expected):
        return attempt(lambda: (guard.require_state_domain(value, expected), "gate-passed")[1])

    def make_eval(**kwargs):
        return attempt(lambda: guard.ReviewEvaluation(**kwargs))

    # ---------- N1: cache record not readable as review conclusion ----------
    class OneRow:
        def __init__(self, raw):
            self._raw = raw

        def fetchone(self, sql, params=()):
            return (self._raw,)

    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE documents (document_id TEXT PRIMARY KEY, metadata_json TEXT)")
    con.execute("INSERT INTO documents VALUES('doc-c1', ?)", (json.dumps({
        "prompt_injection_review": {
            "schema_version": "1.0", "status": "not_detected",
            "reviewer": "r", "reviewed_at": "2026-09-22T00:00:00Z",
            "evidence_sha256": "a" * 64, "source_sha256": "b" * 64,
            "policy_hash": "c" * 64, "state_domain": "review",
        }}),))
    con.commit()

    class StoreShim:
        def fetchone(self, sql, params=()):
            return con.execute(sql, params).fetchone()

    eval_policy_changed = attempt(lambda: guard.evaluate_review(
        StoreShim(), "doc-c1", source_sha256="b" * 64, policy_hash="d" * 64,
        now="2026-09-22T00:00:00Z", ttl_seconds=3600.0))
    ev = eval_policy_changed.get("value")
    log(f"[N1 policy-changed evaluation] -> {json.dumps(eval_policy_changed, default=str)}")
    n1_gate = gate("cache", "review") if ev is None else attempt(
        lambda: (guard.require_state_domain(ev.state_domain, "review"), "gate-passed")[1])
    log(f"[N1 read cache record as review conclusion] -> {json.dumps(n1_gate, default=str)}")
    n1_ok = (
        ev is not None and getattr(ev, "status", None) == "not_reviewed"
        and getattr(ev, "cache_state", None) == "ignored"
        and getattr(ev, "state_domain", None) == "cache"
        and n1_gate["outcome"] == "REJECTED"
        and n1_gate.get("error_type") == "PromptInjectionGuardError"
        and n1_gate.get("text") == "state_domain 'cache' record cannot be read as 'review'"
    )
    RESULTS["C7_N1_cache_record_not_review_conclusion"] = {
        "maps_c7": "dual negative ①: cache-invalidation record must not be readable as a review conclusion",
        "policy_changed_evaluation": eval_policy_changed,
        "read_as_review": n1_gate,
        "ok": n1_ok,
    }
    log()

    # ---------- N2: review record not readable as cache state ----------
    review_record = {"status": "detected_and_ignored", "state_domain": "review",
                     "evidence_sha256": "a" * 64}
    n2_gate = attempt(
        lambda: (guard.require_state_domain(review_record.get("state_domain"), "cache"),
                 "gate-passed")[1])
    log(f"[N2 read review record as cache state] -> {json.dumps(n2_gate, default=str)}")
    disjoint = (
        "detected_and_ignored" not in set(guard.CACHE_STATES)
        and "ignored" not in {"not_detected", "detected_and_ignored", "not_reviewed"}
    )
    RESULTS["C7_N2_review_record_not_cache_state"] = {
        "maps_c7": "dual negative ②: detected_and_ignored must not be readable as cache state",
        "read_as_cache": n2_gate,
        "vocabularies_disjoint": disjoint,
        "ok": disjoint and n2_gate["outcome"] == "REJECTED"
        and n2_gate.get("error_type") == "PromptInjectionGuardError"
        and n2_gate.get("text") == "state_domain 'review' record cannot be read as 'cache'",
    }
    log()

    # ---------- N3: missing state_domain => rejected ----------
    con.execute("INSERT INTO documents VALUES('doc-c3', ?)", (json.dumps({
        "prompt_injection_review": {
            "schema_version": "1.0", "status": "not_detected",
            "reviewer": "r", "reviewed_at": "2026-09-22T00:00:00Z",
            "evidence_sha256": "a" * 64,  # legacy record: NO state_domain
        }}),))
    con.commit()
    n3_read = attempt(lambda: pi.read_prompt_injection_review(StoreShim(), "doc-c3"))
    log(f"[N3 read receipt MISSING state_domain] -> {json.dumps(n3_read, default=str)}")
    n3_guard_read = attempt(lambda: guard._receipt_from_store(StoreShim(), "doc-c3"))
    log(f"[N3 guard _receipt_from_store MISSING state_domain] -> {json.dumps(n3_guard_read, default=str)}")
    n3_construct = make_eval(status="not_reviewed", cache_state="absent")
    log(f"[N3 ReviewEvaluation WITHOUT state_domain] -> {json.dumps(n3_construct, default=str)}")
    n3_ok = (
        n3_read["outcome"] == "ACCEPTED" and n3_read.get("value") is None
        and n3_guard_read["outcome"] == "ACCEPTED" and n3_guard_read.get("value") is None
        and n3_construct["outcome"] == "REJECTED"
    )
    RESULTS["C7_N3_missing_state_domain_rejected"] = {
        "maps_c7": "fail-closed negative ③: record missing state_domain => reject / strictest "
                   "(receipt read -> None/not_reviewed; ReviewEvaluation construction -> TypeError)",
        "receipt_read": n3_read,
        "guard_receipt_read": n3_guard_read,
        "evaluation_construction": n3_construct,
        "ok": n3_ok,
    }
    log()

    # ---------- N4: illegal value => rejected / strictest ----------
    n4_bad_domain = gate("banana", "cache")
    log(f"[N4 gate with illegal state_domain] -> {json.dumps(n4_bad_domain, default=str)}")
    n4_cross = make_eval(status="not_reviewed", cache_state="ignored",
                         state_domain="review")
    log(f"[N4 ReviewEvaluation with cross-domain tag] -> {json.dumps(n4_cross, default=str)}")
    n4_illegal_tag = make_eval(status="not_reviewed", cache_state="ignored",
                               state_domain="banana")
    log(f"[N4 ReviewEvaluation with illegal tag] -> {json.dumps(n4_illegal_tag, default=str)}")

    real_eval = getattr(ev, "state_domain", None)
    fake_eval = SimpleNamespace(status="not_reviewed", cache_state="weird-future-state",
                                state_domain=real_eval or "cache", reason="")
    orig = rg.evaluate_review
    rg.evaluate_review = lambda *a, **k: fake_eval

    class RGReader:
        def fetchone(self, sql, params=()):
            return {"document_id": "doc-x"}

    n4_safety = attempt(lambda: rg._safety_verdict(
        RGReader(), "src-x", policy_hash="c" * 64, source_sha256="b" * 64,
        now="2026-09-22T00:00:00Z", ttl_seconds=3600.0))
    rg.evaluate_review = orig
    log(f"[N4 readiness _SAFETY_MAP with unknown cache_state] -> {json.dumps(n4_safety, default=str)}")
    n4_ok = (
        n4_bad_domain["outcome"] == "REJECTED"
        and n4_bad_domain.get("text") == (
            "state_domain 'banana' is missing or illegal — fail closed (ambiguity is never defaulted)")
        and n4_cross["outcome"] == "REJECTED"
        and n4_cross.get("text") == "ReviewEvaluation state_domain must be 'cache', got 'review'"
        and n4_illegal_tag["outcome"] == "REJECTED"
        and n4_safety["outcome"] == "ACCEPTED"
        and n4_safety.get("value") == (
            "unsatisfied",
            "weird-future-state",
            "unrecognized safety cache_state — fail closed (ambiguity is never defaulted)")
    )
    RESULTS["C7_N4_illegal_value_rejected_strictest"] = {
        "maps_c7": "fail-closed negative ④: illegal value => reject / strictest, never passed",
        "gate_illegal": n4_bad_domain,
        "evaluation_cross_domain": n4_cross,
        "evaluation_illegal_tag": n4_illegal_tag,
        "readiness_unknown_cache_state": n4_safety,
        "ok": n4_ok,
    }
    log()
    con.close()

    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    for name, res in RESULTS.items():
        log(f"    {name}: {'PASS' if res.get('ok') else 'FAIL'}")
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"C7 SCENARIOS: {'PASS' if overall else 'FAIL'}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {args.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
