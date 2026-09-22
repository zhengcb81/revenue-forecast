"""P5 — fake-receipt forgery face of the PRODUCT record_prompt_injection_review.

Target: company-wiki/src/company_wiki/source_catalog/prompt_injection.py
        (product bytes, copied into %TEMP% and imported there; isolated sqlite).
Freeze (oracle-lite):
  P5-a fabricated-but-format-valid evidence_sha256 + status=not_detected:
      ACCEPTED => forgery face CONFIRMED (I-06-B N3 "only blocks format-illegal"
      stands, not narrowed); REJECTED => N3 conclusion NARROWED (report as-is).
  P5-b reviewer="zr302-test-FAKE" free string: record spoofability.
  P5-c status=detected_and_ignored WITHOUT source_sha256/policy_hash:
      ACCEPTED => write-side dual-binding gap CONFIRMED (OPEN-6 C2 face).
  P5-d format-illegal evidence MUST raise
      PromptInjectionReviewError("evidence_sha256 must be a lowercase SHA-256").
Raw output -> evidence/05_fake_receipt.txt.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path

CW_SRC = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\prompt_injection.py"
)
OUT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\OPEN5-DOUBT-PROBE\a20260922-01\evidence\05_fake_receipt.txt"
)
TMP = Path(os.environ["TEMP"]) / "open5-doubt-probe" / "p5"

LOG: list[str] = []
results: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


def step(name: str, fn):
    try:
        value = fn()
        log(f"[{name}] rc=0 (ACCEPTED) -> {json.dumps(value, ensure_ascii=False, default=str)}")
        return 0, value
    except Exception as exc:  # noqa: BLE001
        detail = f"{type(exc).__name__}: {exc}"
        log(f"[{name}] rc=1 (REJECTED) EXC={detail}")
        return 1, detail


class StoreShim:
    """CatalogStore-compatible fetchone for read_prompt_injection_review."""

    def __init__(self, db: Path):
        self.db = db

    def fetchone(self, sql, params=()):
        con = sqlite3.connect(str(self.db))
        try:
            return con.execute(sql, params).fetchone()
        finally:
            con.close()


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    mod_copy = TMP / "prompt_injection.py"
    shutil.copy2(CW_SRC, mod_copy)
    sha = hashlib.sha256(CW_SRC.read_bytes()).hexdigest()
    log(f"target product module: {CW_SRC}")
    log(f"sha256: {sha}")
    spec = importlib.util.spec_from_file_location("pi_p5", mod_copy)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pi_p5"] = mod
    spec.loader.exec_module(mod)
    record = mod.record_prompt_injection_review
    read = mod.read_prompt_injection_review

    db = TMP / "catalog.sqlite3"
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE documents (document_id TEXT PRIMARY KEY, metadata_json TEXT)"
    )
    for i in range(1, 5):
        con.execute(
            "INSERT INTO documents VALUES(?,?)",
            (f"doc-{i}", json.dumps({"title": f"fixture {i}"})),
        )
    con.commit()
    con.close()

    NOW = "2026-09-22T00:00:00Z"
    FAKE_EVIDENCE = hashlib.sha256(b"fabricated-no-real-scan-backed-this").hexdigest()
    log(f"fabricated evidence_sha256 (format-valid, no scan backing): {FAKE_EVIDENCE}")
    log()

    # ---- P5-a: fabricated evidence + status=not_detected + plausible reviewer ----
    def _a():
        c = sqlite3.connect(str(db))
        try:
            return record(
                c, "doc-1",
                status="not_detected", reviewer="scanner-bot-v1",
                evidence_sha256=FAKE_EVIDENCE, now=NOW,
            )
        finally:
            c.commit()
            c.close()

    rc_a, val_a = step("P5-a fabricated evidence_sha256 (status=not_detected)", _a)
    back_a = read(StoreShim(db), "doc-1")
    log(f"    read-back receipt: {json.dumps(back_a, ensure_ascii=False)}")
    results["P5-a"] = {
        "rc": rc_a,
        "result": val_a if isinstance(val_a, str) else "ACCEPTED",
        "read_back": back_a,
        "interpretation": (
            "ACCEPTED => forgery face CONFIRMED; I-06-B N3 'only blocks "
            "format-illegal' stands (NOT narrowed)"
            if rc_a == 0 else
            "REJECTED => I-06-B N3 conclusion is NARROWED (format-valid fakes "
            "are also blocked)"
        ),
    }
    log()

    # ---- P5-b: reviewer free string (identity spoofing) ----
    def _b():
        c = sqlite3.connect(str(db))
        try:
            return record(
                c, "doc-2",
                status="not_detected", reviewer="zr302-test-FAKE",
                evidence_sha256=hashlib.sha256(b"another-fake").hexdigest(),
                now=NOW,
            )
        finally:
            c.commit()
            c.close()

    rc_b, val_b = step("P5-b reviewer='zr302-test-FAKE' free string", _b)
    results["P5-b"] = {
        "rc": rc_b,
        "result": val_b if isinstance(val_b, str) else "ACCEPTED",
        "interpretation": (
            "ACCEPTED => reviewer identity is a spoofable free string"
            if rc_b == 0 else "REJECTED => reviewer identity is constrained"
        ),
    }
    log()

    # ---- P5-c: detected_and_ignored WITHOUT dual binding ----
    def _c():
        c = sqlite3.connect(str(db))
        try:
            return record(
                c, "doc-3",
                status="detected_and_ignored", reviewer="zr302-test-FAKE",
                evidence_sha256=hashlib.sha256(b"fake-3").hexdigest(),
                now=NOW,
            )
        finally:
            c.commit()
            c.close()

    rc_c, val_c = step("P5-c detected_and_ignored WITHOUT source_sha256/policy_hash", _c)
    results["P5-c"] = {
        "rc": rc_c,
        "result": val_c if isinstance(val_c, str) else "ACCEPTED",
        "interpretation": (
            "ACCEPTED => dual binding optional at write time = write-side gap "
            "CONFIRMED (matches OPEN-6 C2-described face)"
            if rc_c == 0 else "REJECTED => dual binding enforced for "
            "detected_and_ignored"
        ),
    }
    log()

    # ---- P5-d control: format-illegal evidence MUST be rejected with exact text ----
    def _d():
        c = sqlite3.connect(str(db))
        try:
            return record(
                c, "doc-4",
                status="not_detected", reviewer="scanner-bot-v1",
                evidence_sha256="ABC", now=NOW,
            )
        finally:
            c.commit()
            c.close()

    rc_d, val_d = step("P5-d format-illegal evidence_sha256='ABC' (control)", _d)
    expected_text = "evidence_sha256 must be a lowercase SHA-256"
    results["P5-d"] = {
        "rc": rc_d,
        "result": val_d,
        "expected_rejection_text": expected_text,
        "exact_text_match": expected_text in str(val_d),
        "ok": rc_d == 1 and expected_text in str(val_d),
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    log()
    log(f"P5-a verdict: {'FORGERY-FACE-CONFIRMED' if rc_a == 0 else 'N3-NARROWED'}")
    log(f"P5-b verdict: {'SPOOFABLE' if rc_b == 0 else 'CONSTRAINED'}")
    log(f"P5-c verdict: {'WRITE-SIDE-GAP-CONFIRMED' if rc_c == 0 else 'BINDING-ENFORCED'}")
    log(f"P5-d verdict: {'PASS' if results['P5-d']['ok'] else 'FAIL'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(LOG) + "\n" + traceback.format_exc(), encoding="utf-8")
        sys.exit(1)
