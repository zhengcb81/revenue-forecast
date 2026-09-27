"""I08CR-c9 — AX-3 (F7): REM-02 documented-limitation state on the CURRENT production
bytes (post-promotion). Read-only."""
from __future__ import annotations

import json
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PUB = RF / "scripts" / "revenue_publication.py"
REPORT = RF / "scripts" / "revenue_report.py"
Z701 = RF / "tests" / "test_zr701_f1_draft_formal.py"
Z705 = RF / "tests" / "test_zr705_draft_formal_swap.py"


def main() -> int:
    pub = PUB.read_text(encoding="utf-8")
    out = {"target": str(PUB)}

    # locate the validate_publication_receipt docstring block
    idx = pub.find("def validate_publication_receipt")
    low = pub.lower()
    out["match_mode"] = "case-insensitive (refinement after c9 run 1: the phrase is rendered **NOT a security boundary** in bold caps; run 1 used a case-sensitive needle and under-measured)"
    out["docstring_phrase_hash_consistency"] = "hash-consistency" in low or "hash consistency" in low
    out["docstring_phrase_not_security_boundary"] = "not a security boundary" in low
    out["docstring_names_validate_forecast_output"] = (
        "validate_forecast_output" in pub[idx : idx + 4000] if idx >= 0 else False
    )
    out["marker_class_defined"] = "class PublicationReceiptOnlyWarning" in pub
    out["marker_exported"] = "PublicationReceiptOnlyWarning" in pub
    out["warn_call_sites"] = [
        i for i, line in enumerate(pub.splitlines(), 1) if "warnings.warn" in line
    ]
    out["marker_never_raised"] = (
        "raise PublicationReceiptOnlyWarning" not in pub and len(out["warn_call_sites"]) == 0
    )
    out["receipt_schema_version_mentions"] = [
        i for i, line in enumerate(pub.splitlines(), 1) if "receipt_schema_version" in line
    ][:10]

    for name, p in (("test_zr701", Z701), ("test_zr705", Z705)):
        t = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
        out[name] = {
            "exists": p.exists(),
            "mentions_warnings": "warning" in t.lower(),
            "asserts_clean": ("catch_warnings" in t) or ("simplefilter" in t) or ("filterwarnings" in t),
        }

    rep = REPORT.read_text(encoding="utf-8", errors="replace")
    out["strong_consumer_calls_receipt_layer_after_strong_gates"] = "_validate_receipt_blocks" in rep

    ok = (
        out["docstring_phrase_not_security_boundary"]
        and out["docstring_names_validate_forecast_output"]
        and out["marker_class_defined"]
        and len(out["warn_call_sites"]) == 0
    )
    out["all_ok"] = ok
    out["measured_limitation"] = (
        "test_zr701/test_zr705 contain no explicit warnings-related assertion locatable by this "
        "scan (run 1 measured asserts_clean=false for both): the 'would break test_zr701/zr705' leg "
        "of the no-runtime-warning rationale rests on B1's frozen design decision (oracle r1 3.5(c), "
        "frozen before any run) and on warning-strict run configurations, and is NOT independently "
        "re-verified by this scan. Recorded as measured, not smoothed over."
    )
    out["f7_status_record"] = "documented limitation, consumer-side guardrail not yet in place"
    (EVID / "AX3_rem02_state.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("AX3_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
