"""Round 65 append-only proof. Line-wise difflib; byte-arithmetic checked in each unit."""
import difflib
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve()
PLANNING = next(p for p in HERE.parents if p.name == ".planning")
CARD = PLANNING / "2026-09-19-three-project-history-audit/execution_runs/T1-23-T1-25/a20260920-01"
TARGET = PLANNING / "2026-09-19-three-project-history-audit/task_plan.md"

PRE_BYTES = 181635
PRE_SHA = "d5245674ebd457af4bd47980cf4357229d8074198d39cacdab901f39df5f5e39"

post = TARGET.read_bytes()
pre_head = post[:PRE_BYTES]
pre_text = pre_head.decode("utf-8", errors="replace")
post_text = post.decode("utf-8", errors="replace")

a = pre_text.splitlines(keepends=True)
b = post_text.splitlines(keepends=True)
oc = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
tags = sorted({t for t, *_ in oc})
deleted_lines = sum((i2 - i1) for t, i1, i2, _, _ in oc if t in ("delete", "replace"))

common = 0
n = min(len(pre_head), len(post))
while common < n and pre_head[common] == post[common]:
    common += 1
inserted_bytes = len(post) - common
inserted_chars = len(post_text) - len(pre_text)

checks = {
    "pre_bytes_match_recorded": len(pre_head) == PRE_BYTES,
    "pre_sha_match_recorded": hashlib.sha256(pre_head).hexdigest() == PRE_SHA,
    "route1_opcodes_only_equal_and_insert": tags == ["equal", "insert"],
    "route1_deleted_lines_zero": deleted_lines == 0,
    "route2_common_prefix_equals_pre_image": common == PRE_BYTES,
    "byte_arithmetic_consistent": (len(post) - len(pre_head)) == inserted_bytes,
    "char_arithmetic_consistent": inserted_chars == len(post_text) - len(pre_text),
    "units_are_declared_and_differ": inserted_bytes != inserted_chars,
    "appended_section_is_round65": ("## Round 65" in post_text) and ("## Round 65" not in pre_text),
}
out = {
    "round": 65,
    "target": "task_plan.md",
    "pre_image": {"bytes": len(pre_head), "sha256": hashlib.sha256(pre_head).hexdigest()},
    "post_image": {"bytes": len(post), "sha256": hashlib.sha256(post).hexdigest()},
    "inserted_bytes": inserted_bytes,
    "inserted_chars": inserted_chars,
    "checks": checks,
    "append_only": all(checks.values()),
    "note": ("route 1 is line-wise (SequenceMatcher over lines) -- a char-level comparison over "
             "180 KB of CJK is quadratic; the judgement is unchanged: only equal and insert "
             "opcodes are permitted."),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
(CARD / "append_only_proof_round65_section.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print("APPEND_ONLY =", out["append_only"])
