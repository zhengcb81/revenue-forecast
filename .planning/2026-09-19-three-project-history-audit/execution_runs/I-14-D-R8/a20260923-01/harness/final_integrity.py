"""WC-1 / I-14-D-R8 close-out: pin recompute + zero-write scan + deliverable hashes.

Step 9/9 (revised after the first scan taught us the attribution rules):

* INPUT PINS: every read-only input must still hash to its freeze-time value.
  The register is the one KNOWN external drift: REGISTRY-CLOSURE's card (or the
  parent) appended to REMEDIATION_REGISTER.md DURING this card's session (freeze
  pin 5348278f/218750 B) -- this card never wrote it (commands.md contains no
  register write).  It is accepted only under ROW-LEVEL verification: every
  register row this card cites must still be present verbatim; freeze + current
  pins are both recorded.
* ZERO-WRITE SCAN, mtime cutoff = THIS ATTEMPT DIR'S CREATION TIME (not
  midnight): any file under the sealed I-14-D attempt or company-wiki/src with
  LastWrite >= cutoff would be a violation (those are the roots this card's
  commands could plausibly have touched).  REGISTRY-CLOSURE hits are reported as
  external/concurrent (its own reviewer landed during our session); its
  decision.md -- our SPEC -- is content-pinned and must match.
* Deliverable hashes -> evidence/final_hashes.json.

Run: python -B harness/final_integrity.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
PLAN = ATT.parents[2]                   # a20260923-01 -> I-14-D-R8 -> execution_runs -> plan
I14D = PLAN / "execution_runs" / "I-14-D" / "a20260919-01"
RC = PLAN / "execution_runs" / "REGISTRY-CLOSURE" / "a20260923-01"
REGISTER = PLAN / "REMEDIATION_REGISTER.md"
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog"
            r"\observability.py")
PROD_ROOT = PROD.parents[1]             # company-wiki/src/company_wiki
CUTOFF = os.path.getctime(ATT)         # Windows creation time of this attempt dir
                                        # (= session start, 23:29:53; st_mtime would
                                        #  drift with this card's own writes)

PINS = {
    "wc1_spec_decision": (RC / "decision.md",
                          "a68ed77fe922f768a845a6497000de93baab922f1d2128ffe9bbc5727fe79353"),
    "r6_tree_observability": (
        I14D / "iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py",
        "2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464"),
    "r6_oracle_harness": (I14D / "harness/run_i14d_oracle_r6.py",
                          "85a1b064fa90616a04f0ae34f618576af073bccbaff02b01c5c6ebeb70813f30"),
    "r6_rule_harness": (I14D / "harness/run_rule_table_i14d_r6.py",
                        "8f5feffddb6f2931942bb76ab0aa213e82d3fa23f645d0206d063f397b162638"),
    "product_base_observability": (
        I14D / "iso/product_base/src/company_wiki/source_catalog/observability.py",
        "c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c"),
    "reviewer_report_r7": (I14D / "reviewer_report_r7.md",
                           "cc6da8d3878dbd942bc6d47bdd750913d1c0646742e22c737ffe73191f610076"),
    "production_observability": (PROD,
                                 "edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e"),
    "r8_base_observability": (
        ATT / "iso/r8_base/company_wiki/source_catalog/observability.py",
        "2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464"),
    "r8_fixed_observability": (
        ATT / "iso/r8_fixed/company_wiki/source_catalog/observability.py",
        "90b3fdc39ddc3b90395df459f298ce3bcb652bbb4f54542bb6f8060657d1cce0"),
    "changes_diff": (ATT / "changes.diff",
                     "baec3153e853ae8eb20c7683c5c508d1336559e70d2b61e061ed11cc4e0a6925"),
}

REGISTER_FREEZE_PIN = "5348278fc1c4ffdc4aff9d26067ded13f7746e12b228d376aaf920b3a82b58d6"
REGISTER_CITED_ROWS = [
    # verbatim row fragments this card's decision/oracle cite (L17 / L1665 / L1713)
    "| **REM-06** | I-14-D F-REV-D-03 | MEDIUM |",
    "`token2/secret2/password2/api_key2` 不是凭据键",
    "| **REM-06**（token2 等非凭据键） | **WORK-CARD WC-1**",
    "WC-1｜I-14-D r8 残差轮**（REM-06+REM-67③+R5-08+R3-07）",
    "iso 基=product_narrow_r6(`2f644994…`)",
]

DELIVERABLES = ["oracle.md", "oracle.sha256", "binding.json", "commands.md",
                "decision.md", "changes.diff", "handoff.md", "recovery.md"]
HARNESS = ["freeze_arithmetic.py", "build_r8.py", "build_mutants.py",
           "sweep_key_domain.py", "sweep_value_start.py", "diag_key_sweep.py",
           "make_changes_diff.py", "final_integrity.py",
           "run_i14d_oracle_r8.py", "run_rule_table_i14d_r8.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scan_since(root: Path) -> list[dict]:
    hits = []
    for p in root.rglob("*"):
        if p.is_file() and p.stat().st_mtime >= CUTOFF:
            hits.append({"path": str(p), "last_write": p.stat().st_mtime})
    return hits


def main() -> int:
    pin_res, ok = {}, True
    for name, (path, expected) in PINS.items():
        got = sha(path)
        match = got == expected
        pin_res[name] = {"path": str(path), "sha256": got, "expected": expected,
                         "match": match}
        ok = ok and match

    # register: known external append -> row-level verification instead of sha
    reg_bytes = REGISTER.read_bytes()
    reg_text = reg_bytes.decode("utf-8")
    row_checks = {frag: (frag in reg_text) for frag in REGISTER_CITED_ROWS}
    register_ok = all(row_checks.values())
    register = {
        "freeze_pin": REGISTER_FREEZE_PIN,
        "freeze_bytes": 218750,
        "current_sha256": hashlib.sha256(reg_bytes).hexdigest(),
        "current_bytes": len(reg_bytes),
        "drift": "external append during this card's session (this card's command log "
                 "contains no register write); accepted under row-level verification",
        "cited_rows_present_verbatim": row_checks,
        "row_level_ok": register_ok,
    }

    i14d_hits = scan_since(I14D)
    prod_hits = scan_since(PROD_ROOT)
    rc_hits = scan_since(RC)
    scan_ok = (not i14d_hits) and (not prod_hits)

    report = {
        "card": "WC-1 / I-14-D-R8", "date": "2026-09-23",
        "cutoff": "Windows creation time (os.path.getctime) of this attempt dir = "
                  f"session start; cutoff epoch {CUTOFF}",
        "read_only_contract": "production/sealed/plan sources READ-ONLY; writes "
                              "confined to this attempt + %TEMP% scratch",
        "pins": pin_res,
        "pins_all_match": ok,
        "register_drift": register,
        "zero_write_scan": {
            "sealed_I-14-D_attempt": i14d_hits,
            "company-wiki_src": prod_hits,
            "REGISTRY-CLOSURE_attempt_external": rc_hits,
        },
        "zero_write_ok": scan_ok,
        "external_notes": [
            "REGISTRY-CLOSURE hits (if any) are that card's own reviewer artifacts "
            "landing concurrently; our SPEC file there is content-pinned above.",
            "Files under company-wiki/src with mtime BEFORE this cutoff (earlier the "
            "same day) belong to other actors; the file this card read (observability)"
            " is content-pinned above and unchanged.",
            "The register drifted via external append; row-level check above.",
        ],
    }
    report["verdict"] = "pass" if (ok and scan_ok and register_ok) else "FAIL"
    (ATT / "evidence" / "final_integrity.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    hashes = {"deliverables": {}, "harness": {}, "evidence_files": {}}
    for n in DELIVERABLES:
        p = ATT / n
        hashes["deliverables"][n] = {"bytes": p.stat().st_size, "sha256": sha(p)}
    for n in HARNESS:
        p = ATT / "harness" / n
        if p.exists():
            hashes["harness"][n] = {"bytes": p.stat().st_size, "sha256": sha(p)}
    for p in sorted((ATT / "evidence").iterdir()):
        if p.is_file():
            hashes["evidence_files"][p.name] = {"bytes": p.stat().st_size,
                                                "sha256": sha(p)}
    hashes["targets_before_after"] = {
        "r6_generation_tree_observability": {
            "before": "2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464",
            "after": "90b3fdc39ddc3b90395df459f298ce3bcb652bbb4f54542bb6f8060657d1cce0"},
        "production_observability": {
            "before": "edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e",
            "after": "081fdf5ee002f26415050adbdf0de4e8478712e282f5a9ea80c547159afc65f0 "
                     "(in-memory target state; production file NOT written)"},
        "oracle_md": {"before": "c6cbf8691c838ddb5c0e06d803ebff364dfff8b8870e0e00202ed8bc6e50c16c"
                                " (pre-run freeze)",
                      "after": "cd8b05e07118844135dfba4349488b47f10a52479b7f0caa7af35e02e18162c4"
                               " (post CORRECTION W1)"},
        "r8_harnesses": {"run_i14d_oracle_r8": "85a1b064… -> ad7861ee… (44->61 cases)",
                         "run_rule_table_i14d_r8": "8f5feffd… -> ffe3372b… (95->113 rows)"},
        "register": {"freeze": REGISTER_FREEZE_PIN, "current": register["current_sha256"],
                     "note": "external append, not this card's write"},
    }
    (ATT / "evidence" / "final_hashes.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8")

    print(json.dumps({
        "integrity_verdict": report["verdict"],
        "pins_all_match": ok,
        "zero_write_ok": scan_ok,
        "register_row_level_ok": register_ok,
        "scan_hits": {k: len(v) for k, v in report["zero_write_scan"].items()},
    }, indent=2))
    return 0 if report["verdict"] == "pass" else 3


if __name__ == "__main__":
    sys.exit(main())
