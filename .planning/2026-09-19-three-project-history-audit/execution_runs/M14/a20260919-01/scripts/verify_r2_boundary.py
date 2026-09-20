"""Re-derive the oracle.md append boundaries (r2 and r3) from the file itself.

Independent re-check of the single-baseline rule for BOTH revisions:
  * exactly one r2 marker and one "修订 r2" heading, exactly one r3 marker and one "修订 r3"
    heading;
  * sha256(oracle.md bytes before the r2 marker) equals the frozen-body hash recorded in
    ``before/oracle_md_v1.json`` at freeze time - i.e. the pre-r2 hash is reproducible at a real
    line boundary;
  * sha256(oracle.md bytes before the r3 marker) equals ``revision_r2.json``'s recorded
    ``oracle_md_sha256_after_append`` - i.e. the pre-r3 hash is reproducible the same way, with no
    competing value anywhere;
  * each revision file declares exactly one revision node and no competing baseline;
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

MARKER_R2 = "<!-- R2-APPEND-BOUNDARY: everything above this line is the frozen oracle body (v1) -->"
MARKER_R3 = ("<!-- R3-APPEND-BOUNDARY: everything above this line is the r2-reviewed frozen "
             "oracle body -->")
HEADING_R2 = "## 修订 r2"
HEADING_R3 = "## 修订 r3"


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
        payload = open(os.path.join(attempt, "oracle.md"), "rb").read()
        text = payload.decode("utf-8")
        v1 = load_json(os.path.join(attempt, "before", "oracle_md_v1.json"))
        revision2 = load_json(os.path.join(evidence, "revision_r2.json"))
        revision3 = load_json(os.path.join(evidence, "revision_r3.json"))
        freeze = load_json(os.path.join(evidence, "oracle_selfcheck.json"))[
            "frozen_file_sha256_at_freeze_time"]

        offset_r2 = payload.find(MARKER_R2.encode("utf-8"))
        offset_r3 = payload.find(MARKER_R3.encode("utf-8"))
        prefix_r2 = sha256_bytes(payload[:offset_r2]) if offset_r2 >= 0 else None
        prefix_r3 = sha256_bytes(payload[:offset_r3]) if offset_r3 >= 0 else None
        frozen_now = {"evidence/%s/%s" % (card, name): sha256_bytes(open(
            os.path.join(evidence, name), "rb").read())
            for name in ("input.json", "cases.json", "oracle.json")}

        checks = {
            "r2_marker_present": offset_r2 >= 0,
            "exactly_one_r2_marker": text.count(MARKER_R2) == 1,
            "exactly_one_r2_heading": text.count(HEADING_R2) == 1,
            "r2_prefix_hash_reproduces_recorded_frozen_body": prefix_r2 == v1["sha256"],
            "r2_boundary_offset_matches_revision_record":
                offset_r2 == revision2["boundary"]["byte_offset"],
            "r2_single_revision_node": revision2.get("single_revision_node") is True
                                       and revision2.get("competing_baselines_present") is False,
            "r3_marker_present": offset_r3 >= 0,
            "exactly_one_r3_marker": text.count(MARKER_R3) == 1,
            "exactly_one_r3_heading": text.count(HEADING_R3) == 1,
            "r3_prefix_hash_reproduces_r2_post_append_hash":
                prefix_r3 == revision2["boundary"]["oracle_md_sha256_after_append"],
            "r3_boundary_offset_matches_revision_record":
                offset_r3 == revision3["boundary"]["byte_offset"],
            "r3_single_revision_node": revision3.get("single_revision_node") is True
                                       and revision3.get("competing_baselines_present") is False,
            "r2_marker_precedes_r3_marker": 0 <= offset_r2 < offset_r3,
            "frozen_files_still_equal_freeze_time_hashes": frozen_now == freeze,
        }
        report = {
            "card_id": card,
            "attempt": attempt,
            "oracle_md_sha256": sha256_bytes(payload),
            "oracle_md_bytes": len(payload),
            "r2": {
                "boundary_byte_offset": offset_r2,
                "sha256_of_bytes_before_the_marker": prefix_r2,
                "frozen_body_sha256_recorded_at_freeze_time": v1["sha256"],
                "marker_occurrences": text.count(MARKER_R2),
                "heading_occurrences": text.count(HEADING_R2),
            },
            "r3": {
                "boundary_byte_offset": offset_r3,
                "sha256_of_bytes_before_the_marker": prefix_r3,
                "sha256_recorded_in_revision_r2_after_its_append":
                    revision2["boundary"]["oracle_md_sha256_after_append"],
                "marker_occurrences": text.count(MARKER_R3),
                "heading_occurrences": text.count(HEADING_R3),
            },
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
            print("boundary check %-56s ok=%s" % (name, ok))
        print("all_checks_passed: %s" % report["all_checks_passed"])
        return 0 if report["all_checks_passed"] else 6
    except Exception as exc:  # noqa: BLE001
        print("boundary verifier harness error: %s: %s" % (
            type(exc).__name__, str(exc).encode("ascii", "backslashreplace").decode("ascii")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
