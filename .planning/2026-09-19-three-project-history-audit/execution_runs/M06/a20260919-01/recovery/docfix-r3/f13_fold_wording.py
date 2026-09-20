"""F-R3-01 fix: re-render the r3 block inside oracle.md with the fold/insert wording.

The r3 block used to say "deleted the duplicate section + appended an r3 note", which
mismatches the bytes: the live file has pre's complete r2 body as a byte prefix and the
r3 block was INSERTED at the duplicate's former position (which is also EOF). Only the
r3 block text changes here; the kept prefix is taken from the preserved pre image and is
verified byte-identical before and after.

For every card:
  1. read oracle_pre_<card>.md (byte-exact pre image) and recompute the kept prefix
  2. render the new r3 block (self-consistent {inserted_bytes} via r3_render)
  3. rebuild = pre_bytes[:K] + new_block ; assert oracle.md[:K] is unchanged
  4. verify live = pre[:K] + old_block (so the ONLY change is inside the r3 block)
  5. write oracle.md, the oracle_merged_<card>.md image, and refresh
     f06_dedupe.json's after-hashes with the previous value kept

Usage: <iso venv python> -X utf8 -B f13_fold_wording.py [--apply] > f13_fold_wording.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_render  # noqa: E402

BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
APPLY = "--apply" in sys.argv


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    print("== F-R3-01: re-render the oracle.md r3 block (fold + insert wording) ==")
    print(f"apply={APPLY}")
    tpl = open(os.path.join(HERE, "r3_block_template.txt"), encoding="utf-8").read()
    dpath = os.path.join(HERE, "f06_dedupe.json")
    dedupe = json.load(open(dpath, encoding="utf-8"))
    report = {}
    for card in CARDS:
        at = os.path.join(BASE, card, "a20260919-01")
        live_p = os.path.join(at, "oracle.md")
        pre_p = os.path.join(HERE, f"oracle_pre_{card}.md")
        pre = open(pre_p, "rb").read()
        live = open(live_p, "rb").read()
        d = dedupe[card]
        pre_txt = pre.decode("utf-8")
        K = len(pre_txt[: d["r2_heading_offsets_before"][1]].encode("utf-8"))

        print("")
        print(f"-- {card} --")
        print(f"   pre_bytes={len(pre)} live_bytes={len(live)} kept_prefix_bytes={K}")

        values = {
            "card": card,
            "before_sha": d["oracle_md_sha256_before"],
            "before_bytes": d["oracle_md_bytes_before"],
            "kept_end": d["r2_heading_offsets_before"][1],
            "prefix_bytes": K,
            "removed_bytes": len(pre) - K,
            "v1_claim": d["authoritative_v1_claim"],
            "v1_offset": d["authoritative_v1_cut"]["char_offset"],
            "v1_bytes": d["authoritative_v1_cut"]["payload_bytes"],
            "gap_claim": d["provenance_gap_claim"],
            "gap_offset": d["provenance_gap_cut"]["char_offset"],
            "gap_bytes": d["provenance_gap_cut"]["payload_bytes"],
        }
        text, size = r3_render.render_block(
            tpl, values, size_dependent=lambda s: {"after_bytes": K + s})
        total = K + size
        new_block = text.encode("utf-8")
        rebuilt = pre[:K] + new_block

        prefix_same = live[:K] == pre[:K]
        live_is_prefix_plus_old = live[:K] == pre[:K] and len(live) > K
        only_block_changed = live[:K] == rebuilt[:K]
        print(f"   r3_block_bytes {len(live) - K} -> {len(new_block)}")
        print(f"   pre[:K] == live[:K]  (byte-identical prefix) = {prefix_same}")
        print(f"   rebuilt[:K] == live[:K] (only the block changed) = {only_block_changed}")
        print(f"   byte accounting: {len(pre)} - {len(pre) - K} + {len(new_block)} = "
              f"{len(pre) - (len(pre) - K) + len(new_block)} == rebuilt={len(rebuilt)} "
              f"= {len(pre) - (len(pre) - K) + len(new_block) == len(rebuilt)}")
        print(f"   live sha256 {sha(live)} -> {sha(rebuilt)}")
        print(f"   old_block_sha256={sha(live[K:])} new_block_sha256={sha(new_block)}")

        if APPLY:
            open(live_p, "wb").write(rebuilt)
            open(os.path.join(HERE, f"oracle_merged_{card}.md"), "wb").write(rebuilt)
            assert sha(open(live_p, "rb").read()) == sha(rebuilt)
            print("   APPLIED")

        report[card] = {
            "oracle_md_sha256_before_wording_fix": sha(live),
            "oracle_md_sha256_after_wording_fix": sha(rebuilt),
            "oracle_md_bytes": len(rebuilt),
            "kept_prefix_bytes": K,
            "r3_block_bytes_before": len(live) - K,
            "r3_block_bytes_after": len(new_block),
            "r3_block_sha256_before": sha(live[K:]),
            "r3_block_sha256_after": sha(new_block),
            "kept_prefix_byte_identical": prefix_same,
            "only_r3_block_changed": only_block_changed,
            "note": "live = pre[:K] + r3_block; the r3 block was INSERTED at the folded "
                    "duplicate's former position, which is also EOF",
        }
        # refresh the after-hashes so every downstream ledger reads one consistent value
        prev_after = d["oracle_md_sha256_after"]
        dedupe[card]["oracle_md_sha256_after"] = sha(rebuilt)
        dedupe[card]["oracle_md_bytes_after"] = len(rebuilt)
        if prev_after != sha(rebuilt):
            dedupe[card]["oracle_md_sha256_after_pre_wording_fix"] = prev_after

    if APPLY:
        with open(dpath, "w", encoding="utf-8") as fh:
            json.dump(dedupe, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("")
        print("refreshed f06_dedupe.json after-hashes "
              "(previous values kept as oracle_md_sha256_after_pre_wording_fix)")
    with open(os.path.join(HERE, "f13_fold_wording.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f13_fold_wording.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
