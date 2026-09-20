"""T1-7: land the owner's rulings on I-14-C r5's four open questions.

WHAT THIS CARD IS
-----------------
T1-7 is a `立卡` (card-creation) ruling.  The reviewer of I-14-C r5 explicitly DECLINED to
decide these four items ("属 owner 决策，我**不代为裁定**"), so this is an owner-authority
action and not a blocked one.  Two of the four ask for NEW CARDS; one asks for a product-side
test-convention change; one picks a form for a promotion precondition.

The deliverable is therefore a CARD-CREATION REGISTER plus a verification that each ruling's
PREMISE still holds on disk.  This card does NOT create the four product-side cards itself
(those belong to the batches/harness that own the product test tree, and creating them here
would be this card authoring work it does not own), and it does NOT edit any frozen artefact.

JUDGE DISCIPLINE APPLIED HERE
-----------------------------
Each of the four rulings names a THING (a baseline, a rate, a path limit, a dependency) as
the reason it must be handled separately.  A ruling is only actionable if the thing it names
is still the thing on disk.  So for each item we verify the NAMED PREMISE, not merely that
the ruling text exists:

  item 1 (C13)  -> the E4b baseline length (193) and that the greedy semantics is what
                   produces it, and that a narrower semantics would MOVE it
  item 2 (flake) -> the ~25% rate and the "trees flip between rounds" observation
  item 3 (206)   -> the character count at which Windows refuses (166/167)
  item 4 (C12)   -> that the dependency the owner declined to add is NOT already present,
                   and that the accepted alternative (subprocess wrap) is expressible
                   without it

Exit codes: 0 all propositions hold / 1 a premise no longer holds / 2 harness unavailable.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
PLAN = REPO / ".planning/2026-09-19-three-project-history-audit"
I14C = PLAN / "execution_runs/I-14-C/a20260919-01"
CARD = PLAN / "execution_runs/T1-7/a20260920-01"
REVIEW = I14C / "review.md"
ORACLE = I14C / "oracle.md"
DECISION = I14C / "decision.md"
HANDOFF = I14C / "handoff.json"

assert (REPO / ".git").is_dir(), "FATAL: not a git toplevel: %s" % REPO
assert REVIEW.is_file(), "FATAL: review missing: %s" % REVIEW
assert CARD.is_dir(), "FATAL: card dir missing: %s" % CARD

text = REVIEW.read_text(encoding="utf-8")
# Normalise ALL runs of whitespace, including NEWLINES.  The reviewer's prose hard-wraps
# mid-sentence, so a pattern anchored with single spaces silently fails to cross a line
# break -- lesson #17 in this project's series, which this very check then reproduced.
flat = re.sub(r"\s+", " ", text)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def find_all(pat, s=None, flags=0):
    return list(re.finditer(pat, s if s is not None else text, flags))


propositions = {}


# ---------------------------------------------------------------- P-1: C13 / E4b 193
# The ruling says carding C13 "会移动 E4b 的 193 基线与 envelope 宽度".  If either half is
# false the ruling's stated cost is wrong and the item would not need its own card.
p1 = {}

# (a) the baseline number 193 is present and attached to E4b
m = re.search(r"E4b\s*\|\s*len\s*193\s*\|\s*len\s*198\s*\|\s*\*\*len\s*193\*\*", flat)
p1["baseline_193_present_and_attached_to_E4b"] = bool(m)
if m:
    p1["baseline_row_as_written"] = m.group(0)

# (b) the 193 is DERIVED from the greedy semantics, not merely coincident with it: the
#     reviewer states the greedy value is what produces it.
m2 = re.search(r"C13[^\n]{0,400}?E4b acceptance length \(193\) is derived from it", flat)
p1["193_is_stated_to_be_derived_from_the_greedy_value"] = bool(m2)

# (c) and the ruling-level claim that narrowing MOVES the baseline appears in the review's
#     open-question section (this is the reviewer's own statement of the trade-off).
m3 = re.search(r"会移动 E4b 的 193 基线与 envelope 宽度", text)
p1["narrowing_is_stated_to_move_the_baseline"] = bool(m3)

# (d) the greedy semantics itself: the frozen fidelity expectation for the middle-value case.
m4 = re.search(r"cred-line-middle-greedy-value[^\n]{0,120}", flat)
p1["greedy_fidelity_case_is_frozen"] = bool(m4)
if m4:
    p1["greedy_fidelity_case_as_written"] = m4.group(0)[:160]

# (e) MULTI-TOKEN, not single-token: the case's expected output redacts the whole run.
#     "a=1 token=<marker> b=2" -> "a=1 token=<redacted>":  the value is the run.
m5 = re.search(r"the value is the whole space/tab\s+separated run, not one token", flat)
p1["semantics_is_multi_token_not_single_token"] = bool(m5)

p1["holds"] = all(v for k, v in p1.items() if isinstance(v, bool))
propositions["P-1_C13_moves_the_E4b_193_baseline_and_the_envelope_width"] = p1


# ------------------------------------------------------- P-2: the ~25% restart flake
# The ruling authorises its own card on the grounds the jitter is LOAD-related, not
# tree-related.  That ground is the difference between "give it a card" and "the trees differ".
p2 = {}

# (a) the rate is quantified in the review (T0 6/24, T4 6/24 -> ~1/4, so ~25%)
m = re.search(r"T0\s*6/24[^\n]{0,200}", flat)
p2["rate_is_quantified"] = bool(m)
if m:
    p2["rate_as_written"] = m.group(0)[:220]

# (b) the FLIP observation: the same tree fails more in one round and less in the next.
#     This is what makes it a timing assumption rather than a tree defect.
flake_pats = [
    r"翻转",
    r"两轮翻转",
    r"trees? flip",
]
p2["flip_between_rounds_is_observed"] = any(find_all(p) for p in flake_pats)

# (c) it is demonstrated NOT to be caused by this card: the reviewer checked that the only
#     diff's worker.py hunks are off the node's path.
m2 = re.search(r"worker\.py\s*改动不在该节点路径上|不在该节点路径上", flat)
p2["attributed_away_from_this_card"] = bool(m2)

# (d) the raw per-run evidence exists on disk (the ruling's card must be buildable from it)
fe = I14C / "r5/flake-evidence"
p2["per_run_evidence_dir_exists"] = fe.is_dir()
if fe.is_dir():
    runs = sorted(x.name for x in fe.iterdir() if x.is_dir())
    p2["per_run_evidence_run_dirs"] = runs
    p2["per_run_evidence_run_count"] = len(runs)

p2["holds"] = all(v for k, v in p2.items() if isinstance(v, bool))
propositions["P-2_the_flake_is_load_related_and_quantified"] = p2


# -------------------------------------------------- P-3: WinError 206 path limit
# The ruling authorises a product-side short-basetemp convention on the ground that
# 166/167 characters trips the Windows limit.  Verify the number is the review's number.
p3 = {}
m = re.search(r"166/167\s*字符即触 Windows 路径上限|166/167[^\n]{0,80}", flat)
p3["character_limit_is_quoted"] = bool(m)
if m:
    p3["character_limit_as_written"] = m.group(0)[:160]

m2 = re.search(r"WinError 206", text)
p3["winerror_206_is_named"] = bool(m2)

# the failure is shown to be SAME-CAUSE on both trees (that is why it is a convention issue,
# not a defect of either tree)
m3 = re.search(r"两树同因失败", flat)
p3["shown_to_be_same_cause_on_both_trees"] = bool(m3)

# and it is a real observed failure, with the secondary symptom recorded
m4 = re.search(r"FileNotFoundError: \[WinError 206\] 文件名或扩展名太长", flat)
p3["observed_failure_text_present"] = bool(m4)

p3["holds"] = all(v for k, v in p3.items() if isinstance(v, bool))
propositions["P-3_the_206_is_a_path_length_convention_issue"] = p3


# ------------------------------------------------------------- P-4: C12 / no new dep
# The owner chose the subprocess wrap AND explicitly declined to add pytest-timeout.  That
# choice is only meaningful if the dependency is genuinely absent (otherwise "not adding it"
# is a no-op) and if the wrap is expressible with the stdlib.
p4 = {}

# (a) pytest-timeout is NOT already a declared dependency.
#
# JUDGE CORRECTED (lesson #20 in this project's series).  The first version of this check
# looked at requirements.txt / pyproject.toml / setup.cfg / pytest.ini / tox.ini -- NONE of
# which exist in this repository.  It therefore iterated over zero files and reported
# `pytest_timeout_already_declared = false`, which READS as "verified absent" but is in fact
# "checked nothing".  An empty scope reporting as a negative finding is exactly the failure
# mode this project keeps recording: the judge must look WHERE THE FACT LIVES, and must be
# able to tell "searched and did not find" apart from "did not search".
#
# The fact lives in the CI install line, which is the only dependency declaration here.
WORKFLOW = REPO / ".github/workflows/quality.yml"
p4["dependency_declaration_lives_in"] = str(WORKFLOW.relative_to(REPO)).replace("\\", "/")
p4["dependency_declaration_exists"] = WORKFLOW.is_file()
install_lines = []
if WORKFLOW.is_file():
    wt = WORKFLOW.read_text(encoding="utf-8", errors="replace")
    install_lines = [ln.strip() for ln in wt.splitlines() if "pip install" in ln]
p4["ci_install_lines"] = install_lines
p4["scope_was_non_empty"] = bool(install_lines)
joined = " ".join(install_lines)
p4["pytest_timeout_already_declared"] = ("pytest-timeout" in joined
                                         or "pytest_timeout" in joined)
# A hard gate: if nothing was actually searched, the proposition FAILS rather than passing
# vacuously.  "I did not look" must never be reported as "I looked and it was not there".
p4["scope_guard_not_vacuous"] = bool(install_lines)

# (b) the ruling's premise: the assertion fires only AFTER the call returns, so a hang
#     presents as a hung session rather than a clean failure.  Judge widened to accept the
#     reviewer's ACTUAL wording (two variants appear; both say the same thing) rather than
#     one guessed spelling -- and `flat` now normalises newlines too, because the reviewer's
#     prose hard-wraps mid-sentence.
hang_pats = [
    r"the 5 s assertion fires only \*{0,2}after\*{0,2} `?redact_text`? returns, "
    r"so a (?:full hang presents as a )?hung (?:test )?session rather than a clean failure",
    r"the 5 s assertion fires only \*{0,2}after\*{0,2} `?redact_text`? returns, "
    r"so a blocking implementation hangs the session instead of failing",
]
p4["hang_mode_is_stated"] = any(re.search(p, flat) for p in hang_pats)
p4["hang_mode_quotes"] = [m.group(0) for p in hang_pats
                          for m in [re.search(p, flat)] if m]

# (c) the accepted alternative is the one the reviewer already built and used: the
#     subprocess-capped bench harness exists on disk.
bench = I14C / "harness/bench_redact.py"
p4["subprocess_capped_harness_exists"] = bench.is_file()
if bench.is_file():
    bb = bench.read_bytes()
    p4["subprocess_capped_harness_bytes"] = len(bb)
    p4["subprocess_capped_harness_sha16"] = sha16(bb)

# (d) the hang was actually OBSERVED, otherwise the precondition is theoretical.  Two
#     observations are on record: this attempt's >60 s kill and the reviewer's >90 s / >300 s.
p4["hang_was_observed"] = bool(
    re.search(r"was \*\*?still running after 60 s and had to be\s+killed\*\*?", flat)
    or re.search(r"still running after 60 s and had to be killed", flat))
p4["hang_observations"] = [m.group(0) for m in
                           re.finditer(r"[^.]{0,80}hung (?:twice )?on `?-k f07`?[^.]{0,120}", flat)][:2]
p4["hang_duration_evidence"] = [m.group(0) for m in
                                re.finditer(r">90 s[^;]{0,60}", flat)][:2]

# (e) C12 is a HARD PRECONDITION for promoting the test (C9), per the reviewer
m3 = re.search(r"C12 remains a hard precondition|C12 is now a promotion precondition", flat)
p4["c12_is_a_promotion_precondition"] = bool(m3)

# `holds` must AND only the POSITIVE claims.  Two of the fields above are deliberately
# NEGATIVE assertions -- `pytest_timeout_already_declared` is what we want to be FALSE, and
# `scope_guard_not_vacuous` exists to make sure we actually looked.  Folding every bool into
# one AND would make this proposition UNSATISFIABLE: it would demand that the dependency both
# be absent (the ruling's premise) and be counted as satisfied.  Name the gate explicitly.
p4["holds"] = all([
    p4["scope_guard_not_vacuous"],     # we looked somewhere real
    not p4["pytest_timeout_already_declared"],   # and the dep is genuinely absent
    p4["hang_mode_is_stated"],         # the hazard is the reviewer's own finding
    p4["hang_was_observed"],           # not theoretical
    p4["subprocess_capped_harness_exists"],  # the accepted alternative already exists
    p4["c12_is_a_promotion_precondition"],
])
p4["holds_basis"] = ("positive claims AND-ed; the negative assertion is wanted FALSE and is "
                     "written that way on purpose, so it must not be folded into the AND")
propositions["P-4_C12_form_is_decidable_without_a_new_dependency"] = p4


# ------------------------------------------------------------ registers
REGISTER = [
    {
        "item": 1,
        "ruling": "C13 单独立卡",
        "owner_choice": ("authorise a separate card that narrows the redaction value semantics "
                         "to a single token, accepting that E4b's 193 baseline and the envelope "
                         "width move, and requiring a NEW oracle"),
        "kind": "NEW CARD (product test tree)",
        "card_id_proposed": "I-18-A",
        "blocked": False,
        "why_not_now": ("the card must be built by whoever owns the product test tree, and it "
                        "REQUIRES a new oracle by the ruling's own terms; this card can only "
                        "register it, not author it"),
        "precondition_verified": "P-1",
        "material_for_the_card": {
            "baseline_to_be_moved": 193,
            "current_semantics": "multi-token greedy run (X+(?:\\s+X+)*)",
            "target_semantics": "single token",
            "frozen_case_that_pins_today_behaviour": "cred-line-middle-greedy-value",
            "companion_case": "cred-line-middle-trailing-punct (the `; b=2` survivor)",
        },
    },
    {
        "item": 2,
        "ruling": "~25% 重启抖动另立卡",
        "owner_choice": ("authorise a separate card to fix the PRODUCT TEST's timing assumption, "
                         "on the basis that the flake is load-related rather than a tree difference"),
        "kind": "NEW CARD (product test tree)",
        "card_id_proposed": "I-18-B",
        "blocked": False,
        "why_not_now": "same ownership boundary as item 1",
        "precondition_verified": "P-2",
        "material_for_the_card": {
            "observed_rate": "T0 6/24 and T4 6/24, i.e. about one in four",
            "discriminating_observation": "the tree that fails more flips between rounds",
            "what_must_NOT_be_concluded": ("a tree defect -- the reviewer checked the only diff's "
                                           "worker.py hunks and they are not on this node's path"),
        },
    },
    {
        "item": 3,
        "ruling": "深层 cwd 的 WinError 206 -> 产品侧改短路径 basetemp 约定",
        "owner_choice": ("authorise a product-side change to a short-path basetemp convention"),
        "kind": "PRODUCT-SIDE CONVENTION CHANGE",
        "card_id_proposed": "I-18-C",
        "blocked": False,
        "why_not_now": ("this card holds no authority over the product test tree, and the "
                        "convention must be applied where the tests run"),
        "precondition_verified": "P-3",
        "material_for_the_card": {
            "threshold": "166/167 characters trips the Windows path limit",
            "evidence_that_it_is_a_convention_not_a_defect": "both trees fail for the same cause",
            "secondary_symptom": "a downstream FileNotFoundError",
        },
    },
    {
        "item": 4,
        "ruling": "C12 形式：子进程硬超时包裹（不新增 pytest-timeout）",
        "owner_choice": ("the form is a SUBPROCESS hard-timeout wrap; do NOT add pytest-timeout, "
                         "to avoid introducing a new dependency into the product tests"),
        "kind": "FORM DECISION for a promotion precondition (C9)",
        "card_id_proposed": None,
        "blocked": False,
        "why_not_now": ("the wrap lands in the product test tree together with the promoted test; "
                        "the ORDER is: implement the wrap, demonstrate blocked=>FAIL, and only "
                        "then may the C9 test be promoted"),
        "precondition_verified": "P-4",
        "material_for_the_card": {
            "precondition_unblocked": "C12 was the hard precondition for promoting the C9 test",
            "acceptance_test": "blocked => FAIL must be DEMONSTRATED, not asserted",
            "existing_asset_to_reuse": "harness/bench_redact.py (subprocess-capped)",
        },
    },
]

result = {
    "card": "T1-7",
    "attempt": "a20260920-01",
    "kind": "ruling_landing_and_card_creation_register",
    "ruling_source": "OWNER_DECISIONS.md section 13, T1-7",
    "why_owner_authority": ("the I-14-C r5 reviewer wrote, for all four items, that they are "
                            "owner decisions the reviewer will not decide on behalf -- so these "
                            "are not blocked on another party, they are simply unexecuted"),
    "subject_under_test": {
        "review.md": {"bytes": REVIEW.stat().st_size, "sha16": sha16(REVIEW.read_bytes())},
        "oracle.md": {"bytes": ORACLE.stat().st_size, "sha16": sha16(ORACLE.read_bytes())},
        "decision.md": {"bytes": DECISION.stat().st_size, "sha16": sha16(DECISION.read_bytes())},
        "handoff.json": {"bytes": HANDOFF.stat().st_size, "sha16": sha16(HANDOFF.read_bytes())},
    },
    "propositions": propositions,
    "card_creation_register": REGISTER,
    "what_this_card_did_NOT_do": [
        "did not create any of the four product-side cards (ownership boundary)",
        "did not edit review.md, oracle.md, decision.md or handoff.json (0 bytes written)",
        "did not add pytest-timeout or any other dependency",
        "did not change any product test",
        "did not perform any status transition, and did not sign on any other party's behalf",
    ],
    "overall": "PASS" if all(p["holds"] for p in propositions.values()) else "FAIL",
}

(CARD / "t17_ruling_landing.json").write_text(
    json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

print(json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True))
print()
print("overall =", result["overall"])
for k, v in propositions.items():
    print("  %-62s %s" % (k, "HOLDS" if v["holds"] else "FAILS"))
raise SystemExit(0 if result["overall"] == "PASS" else 1)
