#!/usr/bin/env python3
"""Create mutant trees: iso with EXACTLY ONE guard flipped per tree.

Three arms (oracle.md mutation plan + §2-再补):
  --kind key       iso-mutant            compute_demand_key drops the OPEN-2A
                                          request_identity key clause  ⇒
                                          W06A2-N1 red (+ P4/N5 collateral)
  --kind nan       iso-mutant-nan        effective_receipt_ttl loses its
                                          math.isfinite gate  ⇒ W06A2-N8b red
  --kind identity  iso-mutant-identity   _validated_request_identity degrades
                                          back to any-of  ⇒ W06A2-N11 red

Writes are BYTE-EXACT (read_bytes/write_bytes): the mutant differs from iso
by precisely the declared block — no whole-file newline rewrite (round-1
review finding 7: write_text had translated LF to CRLF).
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso"

REL_PD = Path("cw/src/company_wiki/source_catalog/processing_demand.py")
REL_GUARD = Path("cw/src/company_wiki/source_catalog/prompt_injection_guard.py")

ARMS = {
    "key": {
        "out": "iso-mutant",
        "file": REL_PD,
        "expected_red": ["W06A2-N1", "W06A2-P4", "W06A2-N5"],
        "old": b'''    payload = {
        "source_sha256": source_sha256,
        "review_policy": review_policy,
        "role_set": normalize_role_set(role_set),
        "request_identity": identity,
    }''',
        "new": b'''    payload = {
        "source_sha256": source_sha256,
        "review_policy": review_policy,
        "role_set": normalize_role_set(role_set),
    }''',
    },
    "nan": {
        "out": "iso-mutant-nan",
        "file": REL_GUARD,
        "expected_red": ["W06A2-N8b"],
        "old": b'''    if not math.isfinite(ttl_seconds):
        raise PromptInjectionGuardError("ttl_seconds must be a finite number")
''',
        "new": b'''    # MUTATION: the non-finite gate is removed
''',
    },
    "identity": {
        "out": "iso-mutant-identity",
        "file": REL_PD,
        "expected_red": ["W06A2-N11"],
        "old": b'''    covered = ("as_of_date", "target", "payload_digest")
    missing = sorted(
        field
        for field in covered
        if identity.get(field) is None or identity.get(field) == ""
    )
    if missing:
        raise DemandRegistrationError(
            "request_identity must cover as_of_date / target / payload digest"
            f" (missing: {missing})"
        )''',
        "new": b'''    if not {"as_of_date", "target", "payload_digest"} & set(identity):
        raise DemandRegistrationError(
            "request_identity must cover as_of_date / target / payload digest"
        )''',
    },
}


def build(kind: str) -> int:
    arm = ARMS[kind]
    mutant = ATTEMPT / arm["out"]
    if mutant.exists():
        shutil.rmtree(mutant)
    shutil.copytree(ISO, mutant, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    target_file = mutant / arm["file"]
    data = target_file.read_bytes()
    if data.count(arm["old"]) != 1:
        print(f"[{kind}] guard anchor not found exactly once in {target_file}",
              file=sys.stderr)
        return 2
    target_file.write_bytes(data.replace(arm["old"], arm["new"]))
    (mutant / "MUTATION.json").write_text(
        json.dumps(
            {
                "kind": kind,
                "flipped_guard": {
                    "key": "compute_demand_key: OPEN-2 option A request_identity key clause",
                    "nan": "effective_receipt_ttl: non-finite (isfinite) gate",
                    "identity": "_validated_request_identity: covers-three requirement",
                }[kind],
                "file": str(arm["file"].as_posix()),
                "before": arm["old"].decode("utf-8"),
                "after": arm["new"].decode("utf-8"),
                "expected_red": arm["expected_red"],
                "expected_still_green": "all other cases",
                "write_mode": "byte-exact (read_bytes/write_bytes; no newline translation)",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"mutant ready: {mutant}")
    return 0


def main() -> int:
    kinds = sys.argv[1:] or list(ARMS)
    rc = 0
    for kind in kinds:
        rc = max(rc, build(kind))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
