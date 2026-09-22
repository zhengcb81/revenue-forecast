"""Build freeze.json — the hash-pin chain that freezes this attempt BEFORE any run.

Ordering evidence is the CHAIN (each entry commits to the previous entry's
canonical JSON), never filesystem mtimes (finding F5 / REM-44). Timestamps, if
present, are non-normative data.

Usage: python build_freeze.py <attempt_root>
Also snapshots two byte-copies at freeze time and pins them:
  * scratch/oracle_pre_r5.md        (copy of SRC oracle.md before this card's append)
  * scratch/frozen12/test_b1_rem.py (copy of B1's frozen 12-node test file)
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MY = Path(sys.argv[1]).resolve()
PLAN = MY.parents[2]  # a20260922-01 -> B1-PREREQ -> execution_runs -> plan root
SRC = PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01"
PROD = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

PIN = {
    "src_oracle_pre": "fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae",
    "src_reviewer_report": "6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b",
    "src_test_b1_rem": "636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16",
    "fixed_revenue_publication": "bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0",
    "fixed_revenue_core": "8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883",
    "fixed_revenue_report": "212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b",
    "fixed_evidence": "054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561",
    "before_r1_stdout_overwritten_artifact": "58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335",
    "before_frozen_artifacts": "4721d1fbcb620346fe19c93ef793d527e644bd3e096bd5a014f576caab82b1f4",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    # --- freeze-time snapshots (byte copies; pinned below) ---
    # SRC oracle may already carry this card's sanctioned r5/r6 suffix appends:
    # the snapshot must be the PRE-APPEND prefix (append-only property), never a
    # fresh full-file copy.
    PRE_R5_BYTES = 39287
    pre_r5 = MY / "scratch" / "oracle_pre_r5.md"
    frozen12 = MY / "scratch" / "frozen12" / "test_b1_rem.py"
    live_oracle = (SRC / "oracle.md").read_bytes()
    live_prefix = hashlib.sha256(live_oracle[:PRE_R5_BYTES]).hexdigest()
    if live_prefix != PIN["src_oracle_pre"]:
        raise SystemExit(f"SRC oracle PREFIX changed (append-only broken?): {live_prefix}")
    if not pre_r5.exists() or sha256_file(pre_r5) != PIN["src_oracle_pre"]:
        pre_r5.write_bytes(live_oracle[:PRE_R5_BYTES])
    if sha256_file(pre_r5) != PIN["src_oracle_pre"]:
        raise SystemExit("pre_r5 snapshot does not match the pinned pre-append bytes")
    if not frozen12.exists():
        frozen12.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SRC / "test_b1_rem.py", frozen12)
    if sha256_file(frozen12) != PIN["src_test_b1_rem"]:
        raise SystemExit("SRC test_b1_rem.py changed since verification — freeze aborted")

    specs = [
        # --- SRC inputs (read-mostly) ---
        ("src_oracle_pre_r5", SRC / "oracle.md", "SRC frozen oracle BEFORE this card's append (r1-r4)"),
        ("src_reviewer_report", SRC / "reviewer_report.md", "the accepted_with_conditions review whose F1-F5 this card closes"),
        ("src_frozen_test_12node", SRC / "test_b1_rem.py", "B1's frozen 12-node proof file (NOT edited by this card)"),
        ("src_iso_fixed_revenue_publication", SRC / "iso/fixed/rf/scripts/revenue_publication.py", "fixed tree / M6 patch target (READ-ONLY)"),
        ("src_iso_fixed_revenue_core", SRC / "iso/fixed/rf/scripts/revenue_core.py", "fixed tree (READ-ONLY)"),
        ("src_iso_fixed_revenue_report", SRC / "iso/fixed/rf/scripts/revenue_report.py", "fixed tree (READ-ONLY)"),
        ("src_iso_fixed_evidence", SRC / "iso/fixed/rf/scripts/contracts/evidence.py", "trust loader under F3 investigation (READ-ONLY)"),
        ("src_before_b1_unfixed_stdout", SRC / "before/b1_unfixed.stdout.txt", "F4: the OVERWRITTEN-r1 artifact (final 11/1 output) — pinned as the disclosed gap object"),
        ("src_before_frozen_artifacts", SRC / "before/frozen_artifacts.json", "B1's r1 freeze record (mtime-ordered era; pinned for contrast with this chain)"),
        # --- freeze-time snapshots ---
        ("snap_oracle_pre_r5_copy", pre_r5, "byte copy of the SRC pre-append oracle (used for changes.diff)"),
        ("snap_frozen12_copy", frozen12, "byte copy of B1's frozen 12-node file (used by arm 3)"),
        # --- this attempt's frozen carriers + executable expectations ---
        ("my_oracle_md", MY / "oracle.md", "THIS CARD'S FROZEN ORACLE — five fixes + expected outcomes, frozen before any run (incl. F2 node expectations)"),
        ("my_node_r13_equiv_rem41", MY / "test_r13_equiv_rem41.py", "the R13-equivalent node (F2), frozen before any run"),
        ("my_conftest", MY / "conftest.py", "registry redirect"),
        ("my_runner_run_arm", MY / "runner/run_arm.ps1", "write-once evidence runner (F4 protocol)"),
        ("my_commands_json", MY / "commands.json", "argv + EXPECTED outcomes, byte-frozen so expectations cannot be edited post-run"),
        ("my_apply_m6", MY / "scratch/apply_m6.py", "M6 patch script (mutation bytes + pre-hash assertion frozen)"),
        ("my_verify_m6_delta", MY / "scratch/verify_m6_delta.py", "single-file-delta prover for the mutant"),
        ("my_append_revision", MY / "scratch/append_revision.py", "append-only proof tool for the SRC oracle appends"),
        ("my_probe_e21", MY / "scratch/probe_e21_binding.py", "F3 read-only probe, expectations in oracle §3.3"),
        ("my_final_integrity_check", MY / "scratch/final_integrity_check.py", "boundary verifier run after all arms"),
        ("my_oracle_revision_r5", MY / "scratch/oracle_revision_r5.md", "F1 correction text to be appended to SRC oracle"),
        ("my_oracle_revision_r6", MY / "scratch/oracle_revision_r6.md", "F2 mutation-table + node text to be appended to SRC oracle"),
        ("my_evidence_readme", MY / "evidence/README.md", "F4 evidence protocol"),
    ]

    entries = []
    prev_canon = b'{"prev":"genesis"}'
    prev_sha = "0" * 64
    for seq, (eid, path, role) in enumerate(specs, start=1):
        path = Path(path)
        if not path.is_file():
            raise SystemExit(f"freeze input missing: {path}")
        entry = {
            "seq": seq,
            "id": eid,
            "path": str(path),
            "rel": str(path.relative_to(MY)) if str(path).startswith(str(MY)) else str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "role": role,
            "prev_entry_sha256": prev_sha,
        }
        # pin against known expectations where we have them
        expect = None
        if eid == "src_oracle_pre_r5":
            expect = PIN["src_oracle_pre"]
        elif eid == "src_reviewer_report":
            expect = PIN["src_reviewer_report"]
        elif eid == "src_frozen_test_12node":
            expect = PIN["src_test_b1_rem"]
        elif eid == "snap_frozen12_copy":
            expect = PIN["src_test_b1_rem"]
        elif eid == "snap_oracle_pre_r5_copy":
            expect = PIN["src_oracle_pre"]
        elif eid == "src_iso_fixed_revenue_publication":
            expect = PIN["fixed_revenue_publication"]
        elif eid == "src_iso_fixed_revenue_core":
            expect = PIN["fixed_revenue_core"]
        elif eid == "src_iso_fixed_revenue_report":
            expect = PIN["fixed_revenue_report"]
        elif eid == "src_iso_fixed_evidence":
            expect = PIN["fixed_evidence"]
        elif eid == "src_before_b1_unfixed_stdout":
            expect = PIN["before_r1_stdout_overwritten_artifact"]
        elif eid == "src_before_frozen_artifacts":
            expect = PIN["before_frozen_artifacts"]
        if expect is not None:
            if eid == "src_oracle_pre_r5":
                # the live file may carry the sanctioned r5/r6 suffix appends;
                # the PIN applies to its frozen prefix.
                live = path.read_bytes()
                entry["prefix_bytes"] = PRE_R5_BYTES
                entry["prefix_sha256"] = hashlib.sha256(live[:PRE_R5_BYTES]).hexdigest()
                entry["expected_prefix_sha256"] = expect
                entry["pin_match"] = entry["prefix_sha256"] == expect
                entry["post_append_bytes"] = len(live)
            else:
                entry["expected_sha256"] = expect
                entry["pin_match"] = entry["sha256"] == expect
            if not entry["pin_match"]:
                raise SystemExit(f"PIN MISMATCH for {eid}: {entry}")
        entry["entry_sha256"] = hashlib.sha256(canon(entry)).hexdigest()
        entries.append(entry)
        prev_sha = entry["entry_sha256"]

    freeze = {
        "schema": "b1-freeze-hash-chain/1",
        "card": "B1-PREREQ",
        "attempt": str(MY),
        "frozen_before_any_run": True,
        "ordering_rule": "ORDERING IS THE HASH CHAIN ONLY: entry N commits to entry N-1 via prev_entry_sha256 = sha256(canonical JSON of previous entry); genesis prev = 64 zeros. Filesystem mtimes are explicitly NON-NORMATIVE for order (finding F5 / REM-44). Future freezes in the B1 line must use this scheme.",
        "created_utc_non_normative": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "created_by": "delegated prereq session — does NOT self-sign accepted",
        "entry_count": len(entries),
        "chain_head": entries[-1]["entry_sha256"],
        "entries": entries,
        "verify": "re-hash every entry's file; recompute entry_sha256 = sha256(json.dumps(entry_without_entry_sha256, sort_keys=True, separators=(',',':'))); check each prev_entry_sha256 equals the previous entry's entry_sha256.",
    }
    out = MY / "freeze.json"
    out.write_text(json.dumps(freeze, indent=2), encoding="utf-8")
    print(json.dumps({"freeze": str(out), "entries": len(entries), "chain_head": freeze["chain_head"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
