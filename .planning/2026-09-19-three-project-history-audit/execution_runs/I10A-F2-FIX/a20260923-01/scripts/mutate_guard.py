#!/usr/bin/env python
"""I10A-F2-FIX MUTATION arm — re-arm / restore the blanket-fill guard (oracle section 4).

`apply`  : replace the entry-layer raise with ``return [0.0] * len(years)``
           (the pre-fix silent behaviour) — exactly one occurrence, asserted.
`restore`: put the frozen raise back — exactly one mutated occurrence, asserted,
           and the resulting sha256 must equal the pre-mutation sha.

The mutation exists ONLY to prove the new judgement can be driven red; it is
always restored before any other evidence run, and the restore is verified by
byte hash against the value recorded in evidence/mut_arm.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CALC = ATT / "iso" / "rf" / "scripts" / "forecast" / "calc.py"
RECORD = ATT / "evidence" / "mut_arm.json"

FIXED = """        if default is None:
            raise ForecastInputError(
                f"missing driver for {model}: {driver} has no explicit default"
            )
        return [float(default)] * len(years)
"""
MUTANT = """        if default is None:
            return [0.0] * len(years)
        return [float(default)] * len(years)
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def append(record: dict) -> None:
    if RECORD.exists():
        doc = json.loads(RECORD.read_text(encoding="utf-8"))
    else:
        doc = {"artifact": "mut_arm", "events": []}
    doc["events"].append(record)
    RECORD.write_text(
        json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


def main() -> int:
    action = sys.argv[1]
    # BYTE-exact IO on purpose: text-mode write_text() would translate LF -> CRLF
    # on Windows and silently change the delivered file's bytes (an incident this
    # attempt already hit and corrected; see evidence/mut_arm_superseded_r1.json).
    raw = CALC.read_bytes()
    text = raw.decode("utf-8")
    before_sha = sha(raw)
    if action == "apply":
        if text.count(FIXED) != 1:
            print(f"ABORT: fixed guard occurrences = {text.count(FIXED)} (want 1)")
            return 1
        new = text.replace(FIXED, MUTANT, 1)
        new_bytes = new.encode("utf-8")
        CALC.write_bytes(new_bytes)
        after_sha = sha(new_bytes)
        append(
            {
                "action": "apply",
                "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "sha_before": before_sha,
                "sha_after": after_sha,
                "bytes_before": len(raw),
                "bytes_after": len(new_bytes),
            }
        )
        print(json.dumps({"action": "apply", "sha_before": before_sha, "sha_after": after_sha}))
        return 0
    if action == "restore":
        if text.count(MUTANT) != 1:
            print(f"ABORT: mutant guard occurrences = {text.count(MUTANT)} (want 1)")
            return 1
        new = text.replace(MUTANT, FIXED, 1)
        new_bytes = new.encode("utf-8")
        CALC.write_bytes(new_bytes)
        after_sha = sha(new_bytes)
        expected = None
        if RECORD.exists():
            events = json.loads(RECORD.read_text(encoding="utf-8"))["events"]
            for ev in events:
                if ev["action"] == "apply":
                    # sha_before of the apply event == sha of the frozen fixed file
                    expected = ev["sha_before"]
        ok = expected is None or after_sha == expected
        append(
            {
                "action": "restore",
                "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "sha_before": before_sha,
                "sha_after": after_sha,
                "expected_sha": expected,
                "restored_byte_identical": ok,
            }
        )
        print(json.dumps({"action": "restore", "sha_after": after_sha, "expected": expected, "ok": ok}))
        return 0 if ok else 1
    print("usage: mutate_guard.py <apply|restore>")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
