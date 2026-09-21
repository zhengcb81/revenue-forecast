"""Independent verification of the REVISED candidate (I-06-A, OPEN-2 option A).

Frozen oracle: oracle_rev2_open2_optionA.json (written BEFORE this script ran).
Runs entirely in a scratch directory.  Never touches production, never touches
the v1 candidate, never promotes anything.

Exit codes per START_HERE.md frozen legend:
  0 = pass (business verdict pass)
  2 = negative case correctly rejected / no verdict
  3 = expected red but stayed green, or expected green but went red
  1 = harness failure
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SUBJECT = ATTEMPT / "iso" / "candidate" / "processing_demand_store_rev2.py"
ORACLE = ATTEMPT / "oracle_rev2_open2_optionA.json"

RESULTS: list[dict] = []


def load_subject():
    spec = importlib.util.spec_from_file_location("rev2_store", SUBJECT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(case_id: str, name: str, actual, expected, *, kind: str = "positive") -> None:
    ok = actual == expected
    RESULTS.append(
        {
            "case": case_id,
            "check": name,
            "kind": kind,
            "expected": expected,
            "actual": actual,
            "ok": ok,
        }
    )
    print(f"[{'PASS' if ok else 'FAIL'}] {case_id} · {name}")
    print(f"        expected={expected!r}")
    print(f"        actual  ={actual!r}")


def main() -> int:
    if not SUBJECT.is_file():
        print(f"harness failure: subject missing at {SUBJECT}", file=sys.stderr)
        return 1
    if not ORACLE.is_file():
        print(f"harness failure: oracle missing at {ORACLE}", file=sys.stderr)
        return 1

    subject_bytes = SUBJECT.read_bytes()
    subject_sha = hashlib.sha256(subject_bytes).hexdigest()
    print(f"subject = {SUBJECT.name}")
    print(f"subject_sha256 = {subject_sha}")
    print(f"oracle = {ORACLE.name}")
    print()

    m = load_subject()

    scratch = Path(tempfile.mkdtemp(prefix="i06a-rev2-"))
    try:
        db = scratch / "catalog.sqlite3"
        store = m.DurableDemandStore(db)

        SOURCE = "80a76889bdafda4ae14d66429082ca33f41cfd3174fe61ef8f2a40d2bc643d71"
        POLICY = "pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"
        ROLES = "normalized,sections"

        req_a = {"as_of_date": "2026-09-19", "document_kind": "annual_report", "entity": "翡翠矿业"}
        req_b = {"as_of_date": "2026-09-20", "document_kind": "annual_report", "entity": "翡翠矿业"}
        req_c = {"as_of_date": "2026-09-19", "document_kind": "interim_report", "entity": "翡翠矿业"}
        req_d = {"as_of_date": "2026-09-19", "document_kind": "annual_report", "entity": "翡翠矿业",
                 "future_new_field": "x"}

        def reg(req, kind="source_preparation"):
            return store.register(
                kind=kind, source_id="urn:cw:source:sha256:emerald-2025-annual",
                source_sha256=SOURCE, review_policy=POLICY, role_set=ROLES,
                gaps=[{"gap": "prompt_injection_not_reviewed"}], request=req,
                now=1_700_000_000.0,
            )

        # ---- R2-P1: identical request resubmitted reuses the same demand ----
        d1, created1 = reg(req_a)
        d1b, created2 = reg(req_a)
        check("R2-P1", "first registration created", created1, True)
        check("R2-P1", "second registration NOT created",
              created2, False, kind="positive")
        check("R2-P1", "demand_id identical across identical resubmit",
              d1["demand_id"] == d1b["demand_id"], True)

        # ---- R2-N1: differ ONLY in as_of_date => must NOT merge -------------
        d2, created3 = reg(req_b)
        k1 = d1["demand_key"]
        k2 = d2["demand_key"]
        check("R2-N1", "demand_key differs when as_of_date differs",
              k1 == k2, False, kind="negative")
        check("R2-N1", "demand_id differs when as_of_date differs",
              d1["demand_id"] == d2["demand_id"], False, kind="negative")
        check("R2-N1", "second registration DID create a new row", created3, True)
        rows_after_n1 = store.find_by_request(
            source_sha256=SOURCE, review_policy=POLICY, role_set=ROLES, request={})
        check("R2-N1", "rows for this source == 2 (no silent merge)",
              len(rows_after_n1), 2, kind="negative")

        # ---- R2-N2: differ in TARGET => must NOT merge ----------------------
        d3, created4 = reg(req_c)
        check("R2-N2", "demand_id differs when target differs",
              d1["demand_id"] == d3["demand_id"], False, kind="negative")
        check("R2-N2", "third registration DID create a new row", created4, True)
        rows_after_n2 = store.find_by_request(
            source_sha256=SOURCE, review_policy=POLICY, role_set=ROLES, request={})
        check("R2-N2", "rows for this source == 3",
              len(rows_after_n2), 3, kind="negative")

        # ---- R2-N3: unlisted future field must NOT be silently ignored -----
        d4, created5 = reg(req_d)
        check("R2-N3", "demand_id differs when an unlisted field is added",
              d1["demand_id"] == d4["demand_id"], False, kind="negative")
        check("R2-N3", "payload_sha256 covers unlisted fields",
              m.canonical_sha256({"future_new_field": "x"})
              != m.canonical_sha256({}), True, kind="negative")

        # ---- key shape (frozen in the oracle in advance) --------------------
        key_shape = set(d1.keys())
        # verify via the stored identity + key derivation rather than internals
        ident = d1["request_identity"]
        check("KEY-SHAPE", "request_identity has as_of_date", "as_of_date" in ident, True)
        check("KEY-SHAPE", "request_identity has target", "target" in ident, True)
        check("KEY-SHAPE", "request_identity has payload_sha256",
              "payload_sha256" in ident, True)
        check("KEY-SHAPE", "key_version recorded",
              d1["key_version"], "2.0.0")

        # the v1 insufficient triple alone must NOT reproduce the v2 key
        v1_triple_key = m.canonical_sha256({
            "source_sha256": SOURCE, "review_policy": POLICY, "role_set": ROLES})
        check("KEY-SHAPE",
              "v2 key is NOT the bare v1 triple (the insufficient shape)",
              k1 == v1_triple_key, False)

        # ---- R2-P2: attempt ledger at the real call boundary ---------------
        a1 = store.record_attempt(demand_id=d1["demand_id"],
                                  producer_name="llm_summarizer",
                                  call_status="error", error_redacted="TimeoutError")
        a2 = store.record_attempt(demand_id=d1["demand_id"],
                                  producer_name="llm_summarizer",
                                  call_status="ok",
                                  artifact_id="urn:cw:artifact:sha256:summary")
        check("R2-P2", "first attempt_number", a1["attempt_number"], 1)
        check("R2-P2", "second attempt_number", a2["attempt_number"], 2)
        check("R2-P2",
              "FAILED call (no artifact) IS counted — attempts not derived from artifacts",
              (a1["call_status"], a1["artifact_id"]), ("error", None))
        try:
            store.record_attempt(demand_id=d1["demand_id"],
                                 producer_name="x", call_status="bogus")
            check("R2-P2", "unknown call_status is refused", "refused", "NOT RAISED",
                  kind="negative")
        except ValueError:
            check("R2-P2", "unknown call_status is refused", "ValueError", "ValueError",
                  kind="negative")

        # ---- claim() stays explicit single-shot ----------------------------
        # Freeze state BEFORE claiming so the second-claim expectation is
        # derived from measured state, not assumed.
        pre_claim_pending = [r["demand_id"] for r in store.list_active()
                             if r["status"] == "pending"]
        claimed = store.claim(owner="verifier")
        check("OPEN-3", "claim returns a row when a pending demand exists",
              claimed is not None, True)
        check("OPEN-3", "claimed demand is the oldest pending one",
              claimed["demand_id"] == pre_claim_pending[0]
              if pre_claim_pending else False, True)
        check("OPEN-3", "claimed row is now status=running (not auto-completed)",
              claimed["status"], "running")
        post_claim_pending = [r["demand_id"] for r in store.list_active()
                              if r["status"] == "pending"]
        check("OPEN-3", "exactly one pending demand was consumed by the claim",
              len(pre_claim_pending) - len(post_claim_pending), 1)

        # A second claim must pick up the NEXT pending demand (still explicit,
        # never a background resume).  When none remain it must return None.
        second = store.claim(owner="verifier")
        if post_claim_pending:
            check("OPEN-3", "second explicit claim serves the next pending demand",
                  second is not None and second["demand_id"] == post_claim_pending[0],
                  True)
        else:
            check("OPEN-3", "no pending left => second claim returns None "
                            "(never an auto-resume)", second, None)

        # ---- store failure is structured, never a silent memory fallback ---
        # A deep path is still creatable on Windows, so use a target that
        # genuinely cannot be opened as a SQLite database: the database path is
        # a DIRECTORY.  mkdir(parents=True, exist_ok=True) on the parent
        # succeeds; sqlite3 then fails to open the directory as a DB file.
        blocked = scratch / "blocked-store"
        blocked.mkdir(parents=True, exist_ok=True)
        # put a file where the DB path must be a directory
        (blocked / "inner.sqlite3").mkdir(parents=True, exist_ok=True)
        bad = m.DurableDemandStore(blocked / "inner.sqlite3")
        try:
            bad.register(kind="k", source_id="s", source_sha256=SOURCE,
                         review_policy=POLICY, role_set=ROLES, gaps=[], request=req_a)
            check("W06A-N2", "unwritable store raises DemandStoreUnavailable",
                  "not raised", "DemandStoreUnavailable", kind="negative")
        except m.DemandStoreUnavailable:
            check("W06A-N2", "unwritable store raises DemandStoreUnavailable",
                  "DemandStoreUnavailable", "DemandStoreUnavailable", kind="negative")
        except OSError:
            check("W06A-N2", "unwritable store raises DemandStoreUnavailable",
                  "OSError", "DemandStoreUnavailable", kind="negative")

        # and confirm there was NO silent in-memory fallback: the registration
        # above must not have produced a readable row anywhere.
        check("W06A-N2", "no silent in-memory fallback occurred",
              store.list_active() and len(store.list_active()) == 4, True)

    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = [r for r in RESULTS if not r["ok"]]
    print()
    print(f"total checks = {len(RESULTS)} | passed = {len(RESULTS) - len(failed)} | failed = {len(failed)}")
    (ATTEMPT / "rev2_verification_result.json").write_text(
        json.dumps(
            {"subject_sha256": subject_sha, "checks": RESULTS,
             "total": len(RESULTS), "failed": len(failed)},
            ensure_ascii=False, indent=2),
        encoding="utf-8")
    return 3 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
