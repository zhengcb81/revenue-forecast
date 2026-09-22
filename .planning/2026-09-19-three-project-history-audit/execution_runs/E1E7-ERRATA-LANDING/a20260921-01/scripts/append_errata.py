#!/usr/bin/env python3
"""E1E7-ERRATA-LANDING / a20260921-01 — append-only errata landing with proofs.

Rules enforced here (see ../oracle.md):
  * pin re-check right before append (frozen-body prefix / whole-file hash)
  * byte-prefix proof: sha256(after[:len(before)]) == sha256(before)
  * difflib opcodes must be a subset of {equal, insert}  (insertion-only)
  * any failure => that card is RESTORED to its original bytes and reported as STOPPED
No product file, no pytest, no git write.
"""
import difflib
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
RUNS = os.path.join(PLAN, "execution_runs")
MINE = os.path.join(RUNS, "E1E7-ERRATA-LANDING", "a20260921-01")
EVID = os.path.join(MINE, "evidence")

TARGETS = {
    "M05": {
        "pin_prefix_bytes": 8774,
        "pin_prefix_sha": "ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a",
        "pin_kind": "frozen_body_prefix (handoff oracle_md_hash_ledger.v1_frozen_body_prefix_bytes)",
        "e_items": ["E-1 M05 oracle.json defaults"],
    },
    "M14": {
        "pin_prefix_bytes": 9367,
        "pin_prefix_sha": "8d74e94fb4771123b5de49fde34d0501d9cfe41e3f6fdf7b824754ca4809bf8f",
        "pin_kind": "frozen_body_prefix (handoff input_hashes['oracle.md:frozen_body_sha256'] = before/oracle_md_v1.json, 9367 B)",
        "e_items": [
            "E-2 M14 oracle.json defaults",
            "E-5 M14 cases.json OBS-SUPPLY-BOUND",
            "E-6 M14 oq_rulings.json OQ-03",
            "E-7 M14 recovery/probes/signed_driver_probe.json",
        ],
    },
    "M20": {
        "pin_prefix_bytes": 13074,
        "pin_prefix_sha": "b43abd8dafe0f5812cfdbd6847fbf332384840982960874f29967657c776672a",
        "pin_kind": "whole-file (handoff input_hashes['oracle.md'], revision r1)",
        "e_items": ["E-3 M20 oracle.json defaults"],
    },
    "M24": {
        "pin_prefix_bytes": 13382,
        "pin_prefix_sha": "9c8f6b238d38841704acd7de305038190b18b93062eaff55fe74bb6bf41b3e9f",
        "pin_kind": "frozen_body_prefix (handoff input_hashes['oracle.md_frozen_body'] = 13382 B)",
        "e_items": ["E-4 M24 oracle.json defaults + hand_notes.defaults"],
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jdump(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> int:
    results = {}
    for card, spec in TARGETS.items():
        target = os.path.join(RUNS, card, "a20260919-01", "oracle.md")
        payload_path = os.path.join(EVID, "landed_text", f"{card}.md")
        rec = {"card": card, "file": target, "e_items": spec["e_items"]}

        if not os.path.exists(target):
            rec.update(status="SKIPPED", reason="oracle.md does not exist")
            results[card] = rec
            continue

        with open(target, "rb") as fh:
            before = fh.read()
        with open(payload_path, "rb") as fh:
            payload = fh.read()
        addition = b"\n" + payload

        before_sha = sha(before)
        before_bytes = len(before)
        rec["sha256_before"] = before_sha
        rec["bytes_before"] = before_bytes

        # ---- pin re-check right before append -------------------------------
        n = spec["pin_prefix_bytes"]
        pin_actual = sha(before[:n])
        pin_ok = pin_actual == spec["pin_prefix_sha"]
        rec["pin_check"] = {
            "kind": spec["pin_kind"],
            "prefix_bytes": n,
            "expected": spec["pin_prefix_sha"],
            "actual": pin_actual,
            "match": pin_ok,
        }
        if not pin_ok:
            rec.update(status="SKIPPED", reason="pin check failed before append — not the pinned oracle")
            results[card] = rec
            continue

        # ---- append ---------------------------------------------------------
        after = before + addition
        with open(target, "wb") as fh:
            fh.write(after)

        after_sha = sha(after)
        after_bytes = len(after)

        # ---- proof 1: byte-prefix -------------------------------------------
        reread = open(target, "rb").read()
        prefix_hash_now = sha(reread[:before_bytes])
        prefix_ok = reread[:before_bytes] == before and prefix_hash_now == before_sha

        # ---- proof 3: difflib insertion-only --------------------------------
        a_lines = before.decode("utf-8").splitlines(keepends=True)
        b_lines = after.decode("utf-8").splitlines(keepends=True)
        sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
        opcodes = [list(op) for op in sm.get_opcodes()]
        tags = sorted({op[0] for op in opcodes})
        insertion_only = set(tags) <= {"equal", "insert"}

        if not (prefix_ok and insertion_only and reread == after):
            # hard rule: leave the card untouched
            with open(target, "wb") as fh:
                fh.write(before)
            rec.update(
                status="STOPPED",
                reason="post-append proof failed; original bytes restored (card left untouched)",
                prefix_proof_ok=prefix_ok,
                insertion_only=insertion_only,
            )
            results[card] = rec
            continue

        # ---- evidence files --------------------------------------------------
        jdump(os.path.join(EVID, "prefix_proof", f"{card}.json"), {
            "card": card,
            "file": target,
            "claim": "sha256(oracle_old_prefix) unchanged after append (byte-prefix proof)",
            "prefix_definition": "the ENTIRE pre-append file is the prefix: bytes[0:bytes_before]",
            "sha256_before": before_sha,
            "bytes_before": before_bytes,
            "sha256_of_prefix_after_append": prefix_hash_now,
            "bytewise_prefix_identical": reread[:before_bytes] == before,
            "match": prefix_ok,
            "pin_check": rec["pin_check"],
        })
        jdump(os.path.join(EVID, "after_hash", f"{card}.json"), {
            "card": card,
            "file": target,
            "sha256_after": after_sha,
            "bytes_after": after_bytes,
            "sha256_before": before_sha,
            "bytes_before": before_bytes,
            "appended_bytes": len(addition),
            "appended_sha256": sha(addition),
            "append_payload_source": os.path.relpath(payload_path, MINE).replace("\\", "/"),
            "append_payload_sha256": sha(payload),
            "line_endings": "LF (matches the file's on-disk state; .gitattributes: *.md text eol=lf)",
        })
        jdump(os.path.join(EVID, "diff_summary", f"{card}.json"), {
            "card": card,
            "file": target,
            "method": "difflib.SequenceMatcher(None, before_lines, after_lines, autojunk=False).get_opcodes()",
            "allowed_tags": ["equal", "insert"],
            "observed_tags": tags,
            "insertion_only": insertion_only,
            "opcodes": opcodes,
            "lines_before": len(a_lines),
            "lines_after": len(b_lines),
            "lines_inserted": len(b_lines) - len(a_lines),
        })

        rec.update(
            status="APPENDED",
            sha256_after=after_sha,
            bytes_after=after_bytes,
            appended_bytes=len(addition),
            prefix_proof_ok=prefix_ok,
            insertion_only=insertion_only,
            observed_diff_tags=tags,
        )
        results[card] = rec

    summary = {
        "attempt": "E1E7-ERRATA-LANDING/a20260921-01",
        "rule": "append-only; prefix proof + insertion-only diff; zero expectation change",
        "results": results,
        "appended": [c for c, r in results.items() if r.get("status") == "APPENDED"],
        "stopped_or_skipped": {c: r.get("reason") for c, r in results.items()
                               if r.get("status") != "APPENDED"},
    }
    jdump(os.path.join(EVID, "proof_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if len(summary["appended"]) == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
