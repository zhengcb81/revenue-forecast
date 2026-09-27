"""Classify the failures of the CI-equivalent AFTER-B run by likely cause.

Read-only parser over evidence/34-cov-AFTER-B-CI-equiv-full.log:
splits the FAILURES section into per-test traceback blocks and tags each
FAILED line from the short summary as
  ISO-MISSING-FILE   traceback contains FileNotFoundError (file not present in the targeted iso copy)
  ASSERTION          plain assertion failure
  OTHER/ERROR
so the CI prediction table can separate iso-copy artifacts from real failures.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LOG = Path(__file__).with_name("34-cov-AFTER-B-CI-equiv-full.log")


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):  # this run log was tee'd as UTF-16
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8", errors="replace")


def main() -> None:
    text = read_text(LOG)
    head, _, tail = text.partition("short test summary info")
    failed = [ln[7:].strip() for ln in tail.splitlines() if ln.startswith("FAILED ")]
    # traceback blocks: lines of ____<nodeid>____  (CRLF-tolerant)
    blocks: dict[str, str] = {}
    parts = re.split(r"^_+ (.+?) _+\r?$", head, flags=re.M)
    # parts: [pre, name1, body1, name2, body2, ...]
    for i in range(1, len(parts) - 1, 2):
        blocks[parts[i].strip()] = parts[i + 1]
    print(f"FAILED lines in short summary: {len(failed)}")
    print(f"traceback blocks parsed: {len(blocks)}")

    def terminal_error(body: str) -> str:
        elines = [ln for ln in body.splitlines() if ln.startswith("E   ")]
        if not elines:
            return ""
        return elines[-1].strip()

    buckets: dict[str, list[tuple[str, str]]] = {
        "ISO-MISSING-FILE": [], "ASSERTION": [], "OTHER": [],
    }
    unmatched: list[str] = []
    for fid in failed:
        name = fid.split("::")[-1]
        body = ""
        for key, val in blocks.items():
            if key.endswith(name) or name.endswith(key):
                body = val
                break
        if not body:
            unmatched.append(fid)
            buckets["OTHER"].append((fid, "NO TRACEBACK BLOCK MATCHED"))
            continue
        err = terminal_error(body)
        if "FileNotFoundError" in err:
            buckets["ISO-MISSING-FILE"].append((fid, err[:200]))
        elif "AssertionError" in err or err.startswith("E   assert"):
            buckets["ASSERTION"].append((fid, err[:200]))
        else:
            buckets["OTHER"].append((fid, err[:200]))
    print(f"unmatched FAILED ids (no block): {len(unmatched)}")
    for name, items in buckets.items():
        print(f"\n=== {name}: {len(items)} ===")
        for fid, err in items:
            print(f"  {fid}\n      -> {err}")
    # which of the card's own test files (9 faces + 1 new coverage vehicle) fail?
    card = [
        "test_archive_retired_evidence_fail_closed",
        "test_fc905_receipt_envelope",
        "test_fc906a_producer_binding_metadata",
        "test_gp003_llm_exit_receipt_privacy_gate",
        "test_r4b05_metadata_provenance",
        "test_source_catalog_archive_retired",
        "test_source_catalog_focus_admission",
        "test_source_catalog_prune_retired",
        "test_source_catalog_worker",
        "test_zr1003_shadow_assertions",
    ]
    hits = [f for f in failed if any(c in f for c in card)]
    print(f"\n=== FAILED lines that belong to this card's own 10 test files: {len(hits)} ===")
    for h in hits:
        print("  " + h)


if __name__ == "__main__":
    sys.exit(main())
