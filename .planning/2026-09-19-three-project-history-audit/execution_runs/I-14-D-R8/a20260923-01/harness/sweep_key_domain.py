"""WC-1 / I-14-D-R8: BIDIRECTIONAL key-domain sweep (oracle.md 5a).

old = r8_base observability (unfixed r6 copy), new = r8_fixed observability.
Domain: {8 single atoms} u {12 pair composites} u {15 near-miss words}
        x suffix {"", "2", "3", "12", "_2"} x {lower, UPPER}.

Frozen criteria:
  old \\ new == []            (the predicate loses nothing)
  new \\ old <= digit-suffixed forms of the 20-entry credential vocabulary
               (near-miss words must never enter)

Run:  python -B harness/sweep_key_domain.py   -> evidence/key_domain_sweep.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
OBS_REL = Path("company_wiki") / "source_catalog" / "observability.py"

ATOMS = ["token", "secret", "password", "passwd", "pwd", "apikey",
         "credential", "passphrase"]
PAIRS = ["api_key", "api_token", "access_key", "access_token", "secret_key",
         "private_key", "auth_token", "session_token", "bot_token",
         "refresh_token", "id_token", "client_secret"]
NEARMISS = ["monkey", "oauth", "secretary", "tokenizer", "keyboard", "key",
            "url", "digest", "flag", "doc", "stage", "code", "document",
            "request", "next"]
SUFFIXES = ["", "2", "3", "12", "_2"]
VOCAB = ATOMS + PAIRS                      # the 20-entry credential vocabulary


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclass _is_type resolves cls.__module__ here
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old = load(ATT / "iso" / "r8_base" / OBS_REL, "obs_old_sweep")
    new = load(ATT / "iso" / "r8_fixed" / OBS_REL, "obs_new_sweep")

    domain = []
    for word in ATOMS + PAIRS + NEARMISS:
        for suffix in SUFFIXES:
            for variant in (word + suffix, (word + suffix).upper()):
                domain.append(variant)
    domain = sorted(set(domain))

    rows = []
    old_new, new_old = [], []
    for key in domain:
        o = old.key_is_credential(key)
        n = new.key_is_credential(key)
        rows.append({"key": key, "old": o, "new": n})
        if o and not n:
            old_new.append(key)
        if n and not o:
            new_old.append(key)

    def is_digit_vocab(key: str) -> bool:
        low = key.lower()
        return any(low == v + s for v in VOCAB for s in ("2", "3", "12"))

    criteria = {
        "old_minus_new_empty": old_new == [],
        "new_minus_old_subset_of_digit_vocab": all(is_digit_vocab(k) for k in new_old),
        "nearmiss_never_credential": all(
            not new.key_is_credential(w + s)
            for w in NEARMISS for s in SUFFIXES),
    }
    report = {
        "criterion": "REM-79 bidirectional difference: old\\new and new\\old, "
                     "frozen domain oracle.md 5a",
        "domain_size": len(domain),
        "old_true": sum(1 for r in rows if r["old"]),
        "new_true": sum(1 for r in rows if r["new"]),
        "old_minus_new": old_new,
        "new_minus_old": new_old,
        "new_minus_old_count": len(new_old),
        # informational (NOT a boolean criterion): the naive count 20 vocab x 3 digit
        # suffixes x 2 cases = 120 over-counts -- digit-suffixed forms whose OLD
        # predicate was ALREADY true are correctly absent from new-minus-old.
        # harness/diag_key_sweep.py accounts for every such key in
        # evidence/key_sweep_count_diag.json.
        "naive_digit_vocab_count": 120,
        "criteria": criteria,
        "verdict": "pass" if all(criteria.values()) else "FAIL",
        "rows": rows,
    }
    out = ATT / "evidence" / "key_domain_sweep.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("domain_size", "old_true", "new_true", "old_minus_new",
                       "new_minus_old_count", "criteria", "verdict")},
                     indent=2))
    return 0 if report["verdict"] == "pass" else 3


if __name__ == "__main__":
    sys.exit(main())
