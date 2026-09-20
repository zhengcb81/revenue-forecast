"""Re-derive the oracle.md r2 boundary from the file itself (standard library only).

Independent re-check of the single-baseline rule:
  * exactly one boundary marker and exactly one "修订 r2" heading exist in oracle.md;
  * sha256(oracle.md bytes before the marker line) equals the frozen-body hash recorded in
    ``before/oracle_md_v1.json`` at freeze time - i.e. the pre-append hash is reproducible at a
    real line boundary;
  * the frozen evidence files still hash to the freeze-time values.

Writes ``evidence/<CARD>/r2_boundary_check.json`` and prints an ASCII summary.
Exit codes: 0 ok, 6 mismatch, 1 harness error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

MARKER = "<!-- R2-APPEND-BOUNDARY: everything above this line is the frozen oracle body (v1) -->"
R2_HEADING = "## 修订 r2"


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    try:
        with open(os.path.join(attempt, "oracle.md"), "rb") as handle:
            payload = handle.read()
        text = payload.decode("utf-8")
        v1 = load_json(os.path.join(attempt, "before", "oracle_md_v1.json"))
        revision = load_json(os.path.join(evidence, "revision_r2.json"))
        freeze = load_json(os.path.join(evidence, "oracle_selfcheck.json"))[
            "frozen_file_sha256_at_freeze_time"]

        marker_bytes = MARKER.encode("utf-8")
        offset = payload.find(marker_bytes)
        prefix_hash = sha256_bytes(payload[:offset]) if offset >= 0 else None
        marker_occurrences = text.count(MARKER)
        heading_occurrences = text.count(R2_HEADING)
        frozen_now = {"evidence/%s/%s" % (card, name): sha256_bytes(open(
            os.path.join(evidence, name), "rb").read())
            for name in ("input.json", "cases.json", "oracle.json")}

        checks = {
            "marker_present": offset >= 0,
            "exactly_one_marker": marker_occurrences == 1,
            "exactly_one_r2_heading": heading_occurrences == 1,
            "prefix_hash_reproduces_recorded_frozen_body": prefix_hash == v1["sha256"],
            "boundary_offset_matches_revision_record": offset == revision["boundary"]["byte_offset"],
            "single_revision_node": revision.get("single_revision_node") is True
                                    and revision.get("competing_baselines_present") is False,
            "frozen_files_still_equal_freeze_time_hashes": frozen_now == freeze,
        }
        report = {
            "card_id": card,
            "attempt": attempt,
            "oracle_md_sha256": sha256_bytes(payload),
            "oracle_md_bytes": len(payload),
            "boundary_byte_offset": offset,
            "sha256_of_bytes_before_the_marker": prefix_hash,
            "frozen_body_sha256_recorded_at_freeze_time": v1["sha256"],
            "marker_occurrences": marker_occurrences,
            "r2_heading_occurrences": heading_occurrences,
            "frozen_hashes_now": frozen_now,
            "frozen_hashes_at_freeze_time": freeze,
            "checks": checks,
            "all_checks_passed": all(checks.values()),
            "checked_at_unix": time.time(),
            "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(os.path.join(evidence, "r2_boundary_check.json"), "w",
                  encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, ensure_ascii=True, indent=1)
            handle.write("\n")
        for name, ok in checks.items():
            print("r2 boundary check %-52s ok=%s" % (name, ok))
        print("all_checks_passed: %s" % report["all_checks_passed"])
        return 0 if report["all_checks_passed"] else 6
    except Exception as exc:  # noqa: BLE001
        print("r2 boundary verifier harness error: %s: %s" % (
            type(exc).__name__, str(exc).encode("ascii", "backslashreplace").decode("ascii")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
