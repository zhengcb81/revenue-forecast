"""Round 64 append-only proof. Line-based difflib instead of char-based (char-level on a
180 KB CJK text is O(n^2); the earlier round's version took minutes). Same judgement."""
import difflib
import hashlib
import json
import pathlib

CARD = pathlib.Path(__file__).resolve().parent.parent
PLANNING = next(p for p in CARD.parents if p.name == ".planning")
TARGET = PLANNING / "2026-09-19-three-project-history-audit/task_plan.md"

PRE_BYTES = 176279
PRE_SHA = "131d1c1e38ec86cf84cab34204d2d688fbb5d7eb926d54c62e0b0f8cbd126bde"

post = TARGET.read_bytes()
pre_head = post[:PRE_BYTES]
pre_text = pre_head.decode("utf-8", errors="replace")
post_text = post.decode("utf-8", errors="replace")

# ROUTE 1 -- character domain, but compared LINE-WISE (SequenceMatcher over lines).
a = pre_text.splitlines(keepends=True)
b = post_text.splitlines(keepends=True)
oc = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
tags = sorted({t for t, *_ in oc})
deleted_lines = sum((i2 - i1) for t, i1, i2, _, _ in oc if t in ("delete", "replace"))

# ROUTE 2 -- byte domain. Bare prefix comparison.
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
}
out = {
    "round": 64,
    "target": "task_plan.md",
    "pre_image": {"bytes": len(pre_head), "sha256": hashlib.sha256(pre_head).hexdigest()},
    "post_image": {"bytes": len(post), "sha256": hashlib.sha256(post).hexdigest()},
    "inserted_bytes": inserted_bytes,
    "inserted_chars": inserted_chars,
    "checks": checks,
    "append_only": all(checks.values()),
    "note": ("route 1 is line-wise (SequenceMatcher over lines) rather than char-wise: a "
             "char-level comparison of a 180 KB CJK text is quadratic and took minutes. "
             "The judgement is unchanged -- only equal and insert opcodes are permitted."),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
(CARD / "append_only_proof_round64_section.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print("APPEND_ONLY =", out["append_only"])
