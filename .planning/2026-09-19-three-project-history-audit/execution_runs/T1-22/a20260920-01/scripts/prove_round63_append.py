"""Prove round 63's append to task_plan.md was append-only. Independent of the appender."""
import hashlib
import json
import pathlib

CARD = pathlib.Path(__file__).resolve().parent.parent
PLANNING = next(p for p in CARD.parents if p.name == ".planning")
TARGET = PLANNING / "2026-09-19-three-project-history-audit/task_plan.md"

PRE_BYTES = 167407
PRE_SHA = "5767fa7565ad55f69d8226d664b0c25ea788e92fc6ece1d13854d74a8298f63a"
POST_BYTES = 176279

post = TARGET.read_bytes()
pre_head = post[:PRE_BYTES]

# ROUTE 1 -- character domain. difflib over text; only equal+insert are permissible.
import difflib  # noqa: E402

pre_text = pre_head.decode("utf-8", errors="replace")
post_text = post.decode("utf-8", errors="replace")
oc = difflib.SequenceMatcher(None, pre_text, post_text, autojunk=False).get_opcodes()
tags = sorted({t for t, *_ in oc})
deleted_chars = sum((i2 - i1) for t, i1, i2, _, _ in oc if t in ("delete", "replace"))
inserted_chars = sum((j2 - j1) for t, _, _, j1, j2 in oc if t in ("insert", "replace"))

# ROUTE 2 -- byte domain. Bare prefix comparison of the pre-image against the post-image.
common = 0
n = min(len(pre_head), len(post))
while common < n and pre_head[common] == post[common]:
    common += 1
inserted_bytes = len(post) - common

checks = {
    "pre_bytes_match_recorded": PRE_BYTES == len(pre_head),
    "post_bytes_match_recorded": POST_BYTES == len(post),
    "pre_sha_match_recorded": hashlib.sha256(pre_head).hexdigest() == PRE_SHA,
    "route1_opcodes_only_equal_and_insert": tags == ["equal", "insert"],
    "route1_deleted_chars_zero": deleted_chars == 0,
    "route2_common_prefix_equals_pre_image": common == PRE_BYTES,
    "byte_arithmetic_consistent": (len(post) - len(pre_head)) == inserted_bytes,
    "char_arithmetic_consistent": (len(post_text) - len(pre_text)) == inserted_chars,
    # units are named and DIFFER -- lesson #21/#22: never compare bytes to chars
    "units_are_declared_and_differ": inserted_bytes != inserted_chars,
}
appended_section_is_round63 = ("## Round 63" in post_text) and ("## Round 63" not in pre_text)

out = {
    "round": 63,
    "target": "task_plan.md",
    "pre_image": {"bytes": len(pre_head), "sha256": hashlib.sha256(pre_head).hexdigest()},
    "post_image": {"bytes": len(post), "sha256": hashlib.sha256(post).hexdigest()},
    "inserted_bytes": inserted_bytes,
    "inserted_chars": inserted_chars,
    "appended_section_is_round63": appended_section_is_round63,
    "checks": checks,
    "append_only": all(checks.values()),
    "note": ("inserted_bytes != inserted_chars because the section is mostly non-ASCII; the two "
             "routes measure different things on purpose and both must hold."),
}
print(json.dumps(out, ensure_ascii=False, indent=1))
(CARD / "append_only_proof_round63_section.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print()
print("APPEND_ONLY =", out["append_only"])
