"""TTL-30D-POLICY oracle probe — every expectation is FROZEN in oracle.md.

Usage: python ttl30d_probe.py <mirror_src_dir> <out_json>

The probe never derives `expect` from the implementation under test; expects
are literals transcribed from oracle.md §2 (+ errata §5).  Emits one JSON
result file binding the run to the exact SHA-256 of the guard module loaded.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MIRROR_SRC = Path(sys.argv[1])
OUT_PATH = Path(sys.argv[2])
sys.path.insert(0, str(MIRROR_SRC))

from company_wiki.source_catalog import prompt_injection_guard as pig  # noqa: E402
from company_wiki.source_catalog.prompt_injection import (  # noqa: E402
    record_prompt_injection_review,
)
from company_wiki.source_catalog.prompt_injection_guard import (  # noqa: E402
    RULESET_HASH,
    PromptInjectionGuardError,
    evaluate_review,
)
from company_wiki.source_catalog.readiness_graph import evaluate_readiness  # noqa: E402
from company_wiki.source_catalog.reader import ReadOnlyCatalogReader  # noqa: E402

# --- frozen literals (oracle.md) -------------------------------------------
CAP = 86400 * 30  # 2592000, owner §十九 option A
CAP_MSG = "ttl_seconds exceeds policy cap of 2592000s"
NEG_MSG = "must be >= 0"
REVIEWED = "2026-08-01T00:00:00Z"
NOW = "2026-08-02T00:00:00Z"
SRC = "a" * 64
results: dict[str, dict] = {}


class _Store:
    def __init__(self, con):
        self._con = con

    def fetchone(self, sql, params=()):
        return self._con.execute(sql, tuple(params)).fetchone()


def make_store(reviewed_at=REVIEWED, source=SRC, policy=RULESET_HASH, doc="d1"):
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE documents (document_id TEXT PRIMARY KEY, "
        "metadata_json TEXT NOT NULL)"
    )
    con.execute("INSERT INTO documents VALUES (?, '{}')", (doc,))
    if reviewed_at is not None:
        # GUARD-MERGE fixture adaptation ONLY (rule 1-3: prompt_injection.py =
        # FIX face, P5-a payload binding mandatory).  Every frozen expectation
        # (check(...) calls) is byte-identical to TTL's probe; only this data
        # producer is brought up to the merged receipt contract.
        _payload = ""  # clean text => scan_text => not_detected (matches status)
        record_prompt_injection_review(
            con, doc, status="not_detected", reviewer="ttl30d-probe",
            evidence_sha256=hashlib.sha256(_payload.encode("utf-8")).hexdigest(),
            now=reviewed_at,
            source_sha256=source, policy_hash=policy,
            evidence_payload=_payload,
        )
        con.commit()
    return _Store(con)


def observe(store, *, ttl, now=NOW, source=SRC, policy=RULESET_HASH, doc="d1"):
    try:
        r = evaluate_review(
            store, doc, source_sha256=source, policy_hash=policy,
            now=now, ttl_seconds=ttl,
        )
        return {"raised": None, "status": r.status,
                "cache_state": r.cache_state, "reason": r.reason}
    except PromptInjectionGuardError as exc:
        return {"raised": "PromptInjectionGuardError", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001 — any other type is an observation
        return {"raised": type(exc).__name__, "message": str(exc)}


def check(cid, observed, predicate, expect_desc, gating=True):
    results[cid] = {
        "expect": expect_desc,
        "observed": observed,
        "ok": bool(predicate(observed)),
        "gating": gating,
    }


def is_cap_reject(obs):
    return (obs.get("raised") == "PromptInjectionGuardError"
            and obs.get("message") == CAP_MSG)


def is_tampered_clock(obs):
    return (obs.get("raised") is None
            and obs.get("status") == "not_reviewed"
            and obs.get("cache_state") == "tampered"
            and "reviewed_at" in (obs.get("reason") or ""))


def is_hit(obs):
    return (obs.get("raised") is None
            and obs.get("cache_state") == "hit"
            and obs.get("status") == "not_detected")


# --- C0: policy constant -----------------------------------------------------
_const = getattr(pig, "POLICY_RECEIPT_TTL_CAP_SECONDS", None)
check(
    "TTL-C0",
    {"has_const": _const is not None, "value": _const,
     "in_all": "POLICY_RECEIPT_TTL_CAP_SECONDS" in getattr(pig, "__all__", [])},
    lambda o: o["has_const"] and o["value"] == CAP and o["in_all"],
    "POLICY_RECEIPT_TTL_CAP_SECONDS present, == 86400*30 == 2592000, in __all__",
)

# --- N1/N2/N3: cap rejection (exact message) ---------------------------------
check("TTL-N1", observe(make_store(), ttl=86400 * 365), is_cap_reject,
      f"raise PromptInjectionGuardError, message == {CAP_MSG!r} (ttl=86400*365)")
check("TTL-N2", observe(make_store(), ttl=2592001), is_cap_reject,
      f"raise PromptInjectionGuardError, message == {CAP_MSG!r} (ttl=2592001)")
check("TTL-N3", observe(make_store(), ttl=86400 * 31), is_cap_reject,
      f"raise PromptInjectionGuardError, message == {CAP_MSG!r} (ttl=86400*31)")

# --- N9/N8: inf / NaN fail closed --------------------------------------------
check("TTL-N9", observe(make_store(), ttl=float("inf")),
      lambda o: o.get("raised") == "PromptInjectionGuardError",
      "raise PromptInjectionGuardError (ttl=inf)")
check("TTL-N8", observe(make_store(), ttl=float("nan")),
      lambda o: o.get("raised") == "PromptInjectionGuardError",
      "raise PromptInjectionGuardError (ttl=NaN)")

# --- P1/P2: legal boundary + tightening --------------------------------------
check("TTL-P1", observe(make_store(), ttl=CAP), is_hit,
      "ttl==cap is legal: fresh bound receipt => hit/not_detected, no raise")
check("TTL-P2",
      observe(make_store(reviewed_at="2026-07-30T00:00:00Z"), ttl=86400),
      lambda o: o.get("raised") is None and o.get("cache_state") == "expired",
      "tightening works: age(3d) > ttl(1d) => expired, no raise")

# --- N4: negative ttl (pre-existing behavior) --------------------------------
check("TTL-N4", observe(make_store(), ttl=-1),
      lambda o: o.get("raised") == "PromptInjectionGuardError"
      and NEG_MSG in (o.get("message") or ""),
      f"raise PromptInjectionGuardError, message contains {NEG_MSG!r}")

# --- N5/N6: past now must not count as fresh (clock anomaly) -----------------
check("TTL-N5",
      observe(make_store(reviewed_at=REVIEWED), ttl=CAP, now="2026-07-30T00:00:00Z"),
      is_tampered_clock,
      "now < reviewed_at on an otherwise-expired receipt => not_reviewed/tampered "
      "(reason contains reviewed_at); NEVER hit")
check("TTL-N6",
      observe(make_store(reviewed_at=REVIEWED), ttl=CAP, now="2026-07-01T00:00:00Z"),
      is_tampered_clock,
      "now < reviewed_at on a fresh receipt => not_reviewed/tampered, never hit")

# --- N7: in-window past now — STRUCTURAL LIMITATION, non-gating --------------
check(
    "TTL-N7",
    observe(make_store(reviewed_at="2026-01-01T00:00:00Z"), ttl=CAP,
            now="2026-01-10T00:00:00Z"),
    lambda o: True,  # observed + reported either way; not a gate (oracle §5-3)
    "LIMITATION (non-gating): past now >= reviewed_at within ttl window — pure "
    "guard has no trusted clock; record observed and report, do not claim pass",
    gating=False,
)

# --- P3/P4/P5: boundary/regression -------------------------------------------
check("TTL-P3",
      observe(make_store(reviewed_at=NOW), ttl=CAP, now=NOW), is_hit,
      "now == reviewed_at (age 0) => hit (strict < boundary)")
check("TTL-P4", observe(make_store(reviewed_at=REVIEWED), ttl=CAP, now=NOW),
      is_hit, "normal forward now within ttl => hit (regression)")
check("TTL-P5",
      observe(make_store(), ttl=CAP, policy="c" * 64),
      lambda o: o.get("raised") is None and o.get("cache_state") == "ignored"
      and o.get("status") == "not_reviewed",
      "policy_hash change => ignored/not_reviewed (OPEN-4 4c regression)")

# --- G1/G2: readiness passthrough --------------------------------------------
_test_mod_path = MIRROR_SRC.parent / "tests" / "unit" / "test_readiness_graph.py"
_spec = importlib.util.spec_from_file_location("ttl30d_trg", _test_mod_path)
trg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trg)


def observe_readiness(**overrides):
    tmp = tempfile.mkdtemp(prefix="ttl30d-seed-")
    db = trg._seed(Path(tmp))
    reader = ReadOnlyCatalogReader(db)
    try:
        evaluate_readiness(reader, "s1", **trg._args(**overrides))
        return {"raised": None}
    except PromptInjectionGuardError as exc:
        return {"raised": "PromptInjectionGuardError", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"raised": type(exc).__name__, "message": str(exc)}
    finally:
        reader.close()


def observe_readiness_decision(**overrides):
    tmp = tempfile.mkdtemp(prefix="ttl30d-seed-")
    db = trg._seed(Path(tmp))
    reader = ReadOnlyCatalogReader(db)
    try:
        d = evaluate_readiness(reader, "s1", **trg._args(**overrides))
        return {"raised": None, "type": type(d).__name__,
                "safety_cache_state": d.safety_cache_state, "ready": d.ready}
    except PromptInjectionGuardError as exc:
        return {"raised": "PromptInjectionGuardError", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"raised": type(exc).__name__, "message": str(exc)}
    finally:
        reader.close()


check("TTL-G1", observe_readiness(ttl_seconds=86400 * 365), is_cap_reject,
      "evaluate_readiness passthrough inherits cap: raise with exact cap message")
check("TTL-G2", observe_readiness_decision(ttl_seconds=CAP),
      lambda o: o.get("raised") is None
      and o.get("type") == "ReadinessDecision"
      and o.get("safety_cache_state") == "hit",
      "evaluate_readiness with ttl==cap returns ReadinessDecision, "
      "safety_cache_state=hit (regression)")

# --- emit ---------------------------------------------------------------------
guard_sha = hashlib.sha256(Path(pig.__file__).read_bytes()).hexdigest()
failed = sorted(cid for cid, r in results.items() if not r["ok"])
gating_failed = sorted(cid for cid, r in results.items()
                       if r["gating"] and not r["ok"])
payload = {
    "card": "TTL-30D-POLICY",
    "attempt": "a20260922-01",
    "run_utc": datetime.now(timezone.utc).isoformat(),
    "guard_module": str(Path(pig.__file__)),
    "guard_sha256": guard_sha,
    "python": sys.version,
    "cap_frozen": CAP,
    "results": results,
    "failed": failed,
    "gating_failed": gating_failed,
    "gating_total": sum(1 for r in results.values() if r["gating"]),
    "gating_passed": sum(1 for r in results.values()
                         if r["gating"] and r["ok"]),
}
OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8")
print(json.dumps({"out": str(OUT_PATH), "guard_sha256": guard_sha,
                  "gating_failed": gating_failed, "failed": failed,
                  "gating_passed": payload["gating_passed"],
                  "gating_total": payload["gating_total"]},
                 ensure_ascii=False))
sys.exit(0)
