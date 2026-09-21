"""REM-22 append-only proof for execution_v2/START_HERE.md -- TWO-append chain.

Chain (every step must be a pure suffix append):
    PRE  sha256 1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835  9895 B
      + append 1 (measured rc registry)
    POST1 sha256 e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557 16314 B
      + append 2 (missing-expected classification erratum)
    POST2 (current)

Decisive check for append 2: sha256(current[:16314]) must still equal POST1's hash -- i.e. the second
append did not alter one byte of what the first append produced. Likewise current[:9895] must still
be the pre-image prefix.
"""
import difflib
import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
TARGET = os.path.join(PLAN, "execution_v2", "START_HERE.md")

PRE_SHA, PRE_BYTES = "1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835", 9895
POST1_SHA, POST1_BYTES = "e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557", 16314


def sha(b):
    return hashlib.sha256(b).hexdigest()


post = open(TARGET, "rb").read()
post_txt = post.decode("utf-8")

proof = {
    "target": os.path.relpath(TARGET, PLAN).replace("\\", "/"),
    "chain": [
        {"step": "PRE", "sha256": PRE_SHA, "bytes": PRE_BYTES,
         "source": "T1-19 handoff.json artifact_under_verification.pre_sha256 (verified before this card)"},
        {"step": "POST1", "sha256": POST1_SHA, "bytes": POST1_BYTES,
         "source": "this card's append 1: measured per-batch rc registry"},
        {"step": "POST2", "sha256": sha(post), "bytes": len(post),
         "source": "this card's append 2: missing-expected classification erratum"},
    ],
}


def append_check(pre_bytes, label):
    """Verify that the current file is exactly pre_bytes + a pure suffix append."""
    prefix = post[:pre_bytes]
    pre_lines = prefix.decode("utf-8").splitlines(keepends=True)
    post_lines = post_txt.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(None, pre_lines, post_lines, autojunk=False)
    ops = [{"op": t, "i1": i1, "i2": i2, "j1": j1, "j2": j2} for t, i1, i2, j1, j2 in sm.get_opcodes()]
    non_equal = [o for o in ops if o["op"] != "equal"]
    return {
        "prefix_ends_at_line_boundary": prefix.endswith(b"\n"),
        "prefix_sha256_matches_recorded": sha(prefix) == (PRE_SHA if label == "PRE" else POST1_SHA),
        "opcodes": [o["op"] for o in ops],
        "non_equal_opcode_count": len(non_equal),
        "only_opcode_is_single_insert": len(non_equal) == 1 and non_equal[0]["op"] == "insert",
        "deleted_lines": sum(o["i2"] - o["i1"] for o in ops if o["op"] in ("delete", "replace")),
        "inserted_lines": sum(o["j2"] - o["j1"] for o in ops if o["op"] in ("insert", "replace")),
        "appended_region_head": post[pre_bytes:pre_bytes + 26].decode("utf-8", "replace"),
    }


proof["append_1_check_vs_PRE"] = append_check(PRE_BYTES, "PRE")
proof["append_2_check_vs_POST1"] = append_check(POST1_BYTES, "POST1")
proof["read_this_correctly"] = (
    "Both checks compare the CURRENT (POST2) file against a recorded prefix, so each reports the "
    "CUMULATIVE suffix from that prefix onward. 'append_1_check_vs_PRE' therefore inserts 108 lines "
    "= append 1 (74) + append 2 (34); 'append_2_check_vs_POST1' isolates append 2 (34). The two "
    "numbers are consistent; do not read 108 as append 1's size. The decisive per-step facts are "
    "`prefix_sha256_matches_recorded` in each check and `deleted_lines == 0` in both.")

orig_table = [
    "## rc 码表（冻结；owner 裁定 T1-19 / §13）",
    "**冻结码表（本包唯一规范值）**",
    "| `0` | 通过 |",
    "| `1` | harness 失败 |",
    "| `2` | 无裁决 / 预期拒绝 |",
    "| `3` | 未达预期 |",
    "- M05–M08 用 `2 = harness`。",
    "- M09–M16 等用 `1 = harness / 2 = no-verdict / 3 = negative`。",
    "（现为 `rc=3`，而登记口径写 `rc=2`）须先按本表**统一到 `rc=2`**，再推广 runner。",
]
additive_1 = [
    "## rc 码表·实测各批码位登记（REM-22 / B5+B6 追加节；owner 裁定 T1-19）",
    "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "5307d2cc",
    "一律不回改",
]
additive_2 = [
    "## rc 码表·追加节 2：`expected` 缺失的实测归类更正（B5+B6；owner 裁定 T1-19）",
    "跨批聚合方不得假设「缺 `expected` = rc=3」",
]
proof["content_checks"] = {
    "frozen_original_lines_all_intact": all(s in post_txt for s in orig_table),
    "append_1_content_present": all(s in post_txt for s in additive_1),
    "append_2_content_present": all(s in post_txt for s in additive_2),
}

proof["APPEND_ONLY"] = (
    proof["append_1_check_vs_PRE"]["only_opcode_is_single_insert"]
    and proof["append_1_check_vs_PRE"]["prefix_sha256_matches_recorded"]
    and proof["append_1_check_vs_PRE"]["prefix_ends_at_line_boundary"]
    and proof["append_2_check_vs_POST1"]["only_opcode_is_single_insert"]
    and proof["append_2_check_vs_POST1"]["prefix_sha256_matches_recorded"]
    and proof["append_2_check_vs_POST1"]["prefix_ends_at_line_boundary"]
    and all(proof["content_checks"].values())
)

dest = os.path.join(ATT, "evidence", "start_here_append_proof.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(proof, fh, indent=1, ensure_ascii=False)

c1, c2 = proof["append_1_check_vs_PRE"], proof["append_2_check_vs_POST1"]
print("PRE  %s %d" % (PRE_SHA[:16], PRE_BYTES))
print("POST1 %s %d" % (POST1_SHA[:16], POST1_BYTES))
print("POST2 %s %d" % (sha(post)[:16], len(post)))
print("append1 vs PRE  : opcodes=%s +%d/-%d prefix_ok=%s" %
      (c1["opcodes"], c1["inserted_lines"], c1["deleted_lines"], c1["prefix_sha256_matches_recorded"]))
print("append2 vs POST1: opcodes=%s +%d/-%d prefix_ok=%s" %
      (c2["opcodes"], c2["inserted_lines"], c2["deleted_lines"], c2["prefix_sha256_matches_recorded"]))
print("content checks:", json.dumps(proof["content_checks"], ensure_ascii=False))
print("APPEND_ONLY =", proof["APPEND_ONLY"])
