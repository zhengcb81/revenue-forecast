"""Diagnostic for the key-domain sweep count: expected 120 vs measured 114.

Explains which digit-suffixed vocabulary keys were ALREADY credential-true on the
OLD predicate (hence correctly absent from new\\old), so the 114 count is audited
rather than hand-waved.  Run: python -B harness/diag_key_sweep.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
VOCAB = ["token", "secret", "password", "passwd", "pwd", "apikey",
         "credential", "passphrase",
         "api_key", "api_token", "access_key", "access_token", "secret_key",
         "private_key", "auth_token", "session_token", "bot_token",
         "refresh_token", "id_token", "client_secret"]


def main() -> int:
    report = json.loads((ATT / "evidence" / "key_domain_sweep.json")
                        .read_text(encoding="utf-8"))
    expected = set()
    for v in VOCAB:
        for s in ("2", "3", "12"):
            expected.add(v + s)
            expected.add((v + s).upper())
    actual = set(report["new_minus_old"])
    rows = {r["key"]: r for r in report["rows"]}
    old_true_digit = sorted(
        k for k, r in rows.items()
        if r["old"] and k in expected)
    out = {
        "expected_digit_vocab_keys": len(expected),
        "actual_new_minus_old": len(actual),
        "missing_from_new_minus_old": sorted(expected - actual),
        "missing_were_old_true": {k: rows[k]["old"] for k in sorted(expected - actual)},
        "old_true_digit_keys_explained": old_true_digit,
        "extra_in_new_minus_old": sorted(actual - expected),
        "verdict": ("all missing keys were ALREADY true on the old predicate "
                    "(correctly excluded from new-minus-old)"
                    if all(rows[k]["old"] for k in (expected - actual))
                    else "UNEXPLAINED"),
    }
    (ATT / "evidence" / "key_sweep_count_diag.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["verdict"].startswith("all missing") else 3


if __name__ == "__main__":
    sys.exit(main())
