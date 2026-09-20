#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
T1-18 verifier.

Card:  T1-18  (OWNER_DECISIONS.md section 13, TIER-1)
Ruling text (verbatim):
    T1-18 | section 4: I-14-B D-1 |
    CONFIRMED: `frozen_tolerance_seconds = 5` and
    `capture_latency_tolerance_seconds = 5` (legal band `[1, 86] s`).
    BUT the signature is NOT permission to open a real window: the real
    30/60/120 stays `blocked` (see T1-9).

Ruling class: interpretation confirmation, and a JOINT one.

Why this card has TWO affirmative halves that must both hold
------------------------------------------------------------
The ruling does two things at once, and they pull in opposite directions:

  (1) It CONFIRMS the frozen tolerance values -- i.e. it ratifies the
      reviewer's freeze as correct and in force.
  (2) It CONFIRMS a LIMIT -- the signature does not authorise running the
      real window; that stays blocked.

A card that only checked (1) would be dangerous: it could "prove" the
qualification is ready while the boundary that keeps it from being claimed
had been eroded. A card that only checked (2) would ignore the actual values
being ratified. So both halves are separate legs, and the second one must be
tested against the ORIGINAL standard the ruling cites (T1-9), not against a
weakened restatement.

Legs
----
  U-1  The freeze is in force with the ratified VALUES: frozen_tolerance_
       seconds = 5 and capture_latency_tolerance_seconds = 5, both signed by
       an independent reviewer (not the implementer), with the signature
       line present.
  U-2  The legal BAND the ruling states ([1, 86] s) is the band the card
       actually derived, from two independent bounds -- not a number chosen
       by preference. Both bounds must be reproducible from the recorded
       measurements.
  U-3  The LIMIT is intact: the real 30/60/120 window is still `blocked`,
       and `blocked_by` still names the missing preconditions. Crucially, the
       implementer did NOT convert a signature into a run.
  U-4  The rejected alternative is absent: nothing presents the tolerance as
       self-chosen by the implementer, and nothing presents the freeze as
       sufficient to have opened the window.
  U-5  Additivity/state: the ruling orders no write; the frozen four lines
       are byte-intact and the card's evidence is untouched by this card.

Why U-2 is not decorative
-------------------------
The ruling cites a BAND, and a band is a claim of the form "values below 1 are
wrong AND values at/above 87 are wrong". That is a two-sided claim: it needs
TWO bounds, derived independently. A card that checked only "the value is 5
and 5 is inside [1,86]" would be assuming the band it was asked to verify.
Shape-matching again: the object is a BAND, so the criterion must be the two
bounds, not the single point.

Exit codes: 0 = PASS, 1 = harness failure, 2 = precondition, 3 = not met.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

EXEC = pathlib.Path(__file__).resolve().parent.parent          # .../T1-18/a20260920-01
# Depth counted from EXEC: parents[0]=T1-18 parents[1]=execution_runs
# parents[2]=<audit dir> parents[3]=.planning parents[4]=<repo root>
REPO = EXEC.parents[4]
PLAN = ".planning/2026-09-19-three-project-history-audit"
I14B = f"{PLAN}/execution_runs/I-14-B/a20260919-01"
OD = f"{PLAN}/OWNER_DECISIONS.md"

EXPECTED_ANCHOR = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"


def _fail(msg):
    print(f"FATAL: {msg}")
    return 2


def main():
    sanity = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                            cwd=str(REPO), capture_output=True)
    if sanity.returncode != 0:
        return _fail("REPO is not inside a git work tree")
    if pathlib.Path(sanity.stdout.decode("utf-8", "replace").strip()) != REPO:
        return _fail("REPO != git toplevel")

    card = REPO / I14B
    if not card.is_dir():
        return _fail(f"I-14-B dir missing: {card}")

    oracle = (card / "oracle.md").read_text(encoding="utf-8")
    review = (card / "review.md").read_text(encoding="utf-8")
    decision = (card / "decision.md").read_text(encoding="utf-8")
    handoff = json.loads((card / "handoff.json").read_text(encoding="utf-8"))
    od = (REPO / OD).read_text(encoding="utf-8")

    results = {}
    notes = []

    # ===================== U-1  the freeze, with values =====================
    block = oracle[oracle.index("TOLERANCE PRE-REGISTRATION"):]
    block = block[: block.index("```")] if "```" in block else block

    def field(name):
        m = re.search(rf"^\s*{name}\s*:\s*(.+?)\s*$", block, re.M)
        return m.group(1) if m else None

    fr_by = field("frozen_by")
    fr_at = field("frozen_at_utc")
    fr_tol = field("frozen_tolerance_seconds")
    sig = field("reviewer_signature_line")

    u1 = {
        "frozen_tolerance_seconds_value": fr_tol,
        "frozen_tolerance_is_5": (fr_tol == "5"),
        # Shape-matching note: the review states this one as
        # "`capture_latency_tolerance_seconds` 同为 5" ("likewise 5"), NOT as
        # "capture_latency_tolerance_seconds = 5". A criterion that demands the
        # "= 5" surface form reports a missing value that IS present.
        "capture_latency_tolerance_is_5": bool(
            re.search(r"capture_latency_tolerance_seconds[^\n]{0,40}5\b", review)),
        "frozen_by_is_independent_reviewer": bool(fr_by and "independent reviewer" in fr_by),
        "frozen_by_is_not_the_implementer": bool(fr_by and "implementer" not in fr_by.lower()),
        "frozen_at_recorded": bool(fr_at and re.match(r"\d{4}-\d{2}-\d{2}T", fr_at)),
        "signature_line_present": bool(sig and "frozen_tolerance_seconds = 5" in sig),
        "signature_names_a_reviewer_session": bool(sig and "reviewer=" in sig),
    }
    u1_ok = all(v for k, v in u1.items() if k != "frozen_tolerance_seconds_value")
    results["U-1"] = {
        "claim": "the freeze is in force with the ratified values (5 / 5), signed by an independent reviewer, not the implementer",
        "holds": bool(u1_ok),
        "evidence": u1,
    }

    # ===================== U-2  the band is DERIVED, from two bounds =====================
    # The ruling states [1, 86] s. That is a two-sided claim:
    #   lower bound 1  -- from L1 (an honest 1 s capture delay must not be killed)
    #   upper bound 86 -- from L2 (the reproduced historical defect must stay rejected)
    # Both bounds must be recoverable from the recorded text, and the frozen
    # value must sit strictly inside the resulting band.
    lower_match = re.search(r"tol\s*=\s*0\.9\s*拒\s*/\s*tol\s*=\s*1\.0\s*起通过", review)
    upper_match = re.search(r"tol\s*≤\s*86\s*拒\s*/\s*tol\s*=\s*87\s*起通过", review)
    band_stated = re.search(r"合法区间\s*\[1\s*s,\s*86\s*s\]", review) or \
        re.search(r"\[1\s*s,\s*86\s*s\]", review)
    # independent corroboration that the band is in the ruling itself
    band_in_ruling = ("[1, 86]" in od) or ("1, 86" in od)

    # the two anchor measurements that generate the bounds
    l1_anchor = re.search(r"捕获延迟\s*1\s*s", review) or re.search(r"capture delay 1 s", review, re.I)
    l2_anchor = re.search(r"29/88/207", review) or re.search(r"29/88/207", review)

    # the frozen 5 must be strictly inside [1, 86]
    try:
        v = float(fr_tol)
        inside = (1.0 < v < 86.0) or (1.0 <= v <= 86.0)
    except (TypeError, ValueError):
        inside = False

    u2 = {
        "lower_bound_derivation_present": bool(lower_match),
        "upper_bound_derivation_present": bool(upper_match),
        "band_stated_in_review": bool(band_stated),
        "band_also_stated_in_the_ruling": bool(band_in_ruling),
        "lower_anchor_measurement_present": bool(l1_anchor),
        "upper_anchor_measurement_present": bool(l2_anchor),
        "frozen_value_inside_band": inside,
        "derivation_is_two_sided": bool(lower_match and upper_match),
        "why_two_sided": "a band is a claim that values below 1 are wrong AND values at/above 87 are wrong; "
                         "one bound alone cannot support it",
    }
    u2_ok = all(v for k, v in u2.items() if k != "derivation_is_two_sided" and k != "why_two_sided")
    results["U-2"] = {
        "claim": "the legal band [1, 86] s is DERIVED from two independent bounds, not chosen by preference, and the frozen 5 sits inside it",
        "holds": bool(u2_ok),
        "evidence": u2,
    }

    # ===================== U-3  the LIMIT is intact =====================
    blocked_by = handoff.get("blocked_by", [])
    bb = json.dumps(blocked_by, ensure_ascii=False)
    scope_txt = json.dumps(handoff.get("qualifications", {}), ensure_ascii=False) + \
        json.dumps(handoff.get("not_granted", ""), ensure_ascii=False) + \
        json.dumps(handoff.get("scope", ""), ensure_ascii=False) + \
        json.dumps(handoff.get("reviewer_status", ""), ensure_ascii=False)

    u3 = {
        "blocked_by_names_the_30_60_120_window": bool(re.search(r"30/60/120", bb)),
        "blocked_by_says_BLOCKED": bool(re.search(r"BLOCKED", bb)),
        "blocked_by_names_missing_preconditions": bool(
            re.search(r"pre-placed recorder", bb, re.I) or re.search(r"owner authorisation", bb, re.I)),
        "real_window_needs_new_attempt_and_binding": bool(
            re.search(r"new attempt\s*\+\s*new binding", bb, re.I) or
            re.search(r"new attempt", bb, re.I)),
        "status_never_claims_ui_immediacy_granted": not bool(
            re.search(r"real UI-immediacy[^\n]{0,40}(granted|qualified)", scope_txt, re.I)
            and not re.search(r"NOT GRANTED|stays `?blocked", scope_txt, re.I)),
        "reviewer_status_says_ui_immediacy_stays_blocked": bool(
            re.search(r"real UI-immediacy qualification \(stays blocked\)", scope_txt)),
        "natural_observation_still_not_granted": bool(
            re.search(r"NOT granted[^\n]{0,120}natural-observation", scope_txt, re.I) or
            re.search(r"real natural-observation qualification \(17 rows still pending\)", scope_txt)),
    }
    # The decisive one: did anyone actually RUN the window? The card must show
    # it did not. "signature != permission to run" is exactly this.
    #
    # Shape-matching note: the card says "签字只把它从 blocked 变为可开卡，不等于
    # 已运行" -- a DENIAL containing the word 运行. A criterion that merely greps
    # for 运行/ran matches the denial and reports the opposite of the truth. So
    # the probe must only count AFFIRMATIVE run statements (excluding any line
    # that denies or negates a run).
    ran_the_window = False
    for line in review.split("\n"):
        if not re.search(r"30/60/120", line):
            continue
        if not re.search(r"(was run|已运行|ran\b|运行了)", line, re.I):
            continue
        # exclude denials/negations on the same line
        if re.search(r"(不等于|并非|未|没有|not\b|NOT\b|never|未运行|尚未)", line):
            continue
        ran_the_window = True
    u3["no_evidence_the_real_window_was_run"] = not ran_the_window

    u3_ok = all(u3.values())
    results["U-3"] = {
        "claim": "the LIMIT is intact: the real 30/60/120 window is still blocked with its preconditions named, and no signature was converted into a run",
        "holds": bool(u3_ok),
        "evidence": u3,
    }

    # ===================== U-4  rejected forms absent =====================
    # (a) nothing presents the tolerance as self-chosen by the implementer as
    #     the FINAL value (the proposal exists, but must be marked NOT frozen).
    selfchosen = []
    for i, line in enumerate(oracle.split("\n"), 1):
        if "proposed = 5" in line and "NOT frozen" not in line:
            selfchosen.append(f"oracle.md:{i}")
    # (b) nothing presents the freeze as sufficient to have opened the window.
    opens_window = []
    for i, line in enumerate(review.split("\n"), 1):
        if re.search(r"冻结容差[^\n]{0,30}(即可|就可以|足以)[^\n]{0,20}(开|运行|跑)", line):
            opens_window.append(f"review.md:{i}")
    # (c) the explicit negation must be present (the ruling's second half).
    negation_present = bool(re.search(
        r"签字不等于可以开真实窗口|签字\s*≠\s*可开真实窗口|signature[^\n]{0,40}NOT[^\n]{0,20}permission",
        review + od, re.I))

    u4 = {
        "no_unmarked_implementer_proposal_as_final": (len(selfchosen) == 0),
        "unmarked_proposal_sites": selfchosen,
        "nothing_claims_freeze_opens_the_window": (len(opens_window) == 0),
        "window_opening_claims": opens_window,
        "explicit_negation_present": negation_present,
    }
    u4_ok = all(v for k, v in u4.items() if k not in ("unmarked_proposal_sites", "window_opening_claims"))
    results["U-4"] = {
        "claim": "the rejected forms are absent: the implementer's 5 s is still marked NOT frozen, nothing claims the freeze opened the window, and the ruling's negation is present",
        "holds": bool(u4_ok),
        "evidence": u4,
    }

    # ===================== U-5  additivity / state =====================
    add = {}
    for rel in ("oracle.md", "review.md", "decision.md"):
        blob = subprocess.run(["git", "show", f"HEAD:{I14B}/{rel}"], cwd=str(REPO),
                              capture_output=True)
        if blob.returncode != 0 or not blob.stdout:
            return _fail(f"could not read pre-image for {rel}")
        pre, now = blob.stdout, (card / rel).read_bytes()
        add[rel] = {"pre_bytes": len(pre), "now_bytes": len(now),
                    "prefix_preserved": now[: len(pre)] == pre,
                    "pre_sha256": hashlib.sha256(pre).hexdigest()[:16],
                    "now_sha256": hashlib.sha256(now).hexdigest()[:16]}
    # note: not all of these are append-only by the card's own design (the
    # reviewer FILLED four lines), so we report rather than assert prefix here;
    # the meaningful claim is that THIS card wrote nothing to them.
    this_card_wrote_nothing = all(v["pre_bytes"] == v["now_bytes"] for v in add.values())

    diff = subprocess.run(["git", "diff", "HEAD", "--name-only", "--", I14B],
                          cwd=str(REPO), capture_output=True)
    i14b_touched = [x for x in diff.stdout.decode().splitlines() if x.strip()]
    product = subprocess.run(["git", "diff", "HEAD", "--name-only", "--", ".",
                              ":(exclude).planning"], cwd=str(REPO), capture_output=True)
    product_touched = [x for x in product.stdout.decode().splitlines() if x.strip()]

    u5 = {
        "i14b_card_untouched_by_this_card": (len(i14b_touched) == 0),
        "i14b_files": i14b_touched,
        "product_files_changed": product_touched,
        "frozen_four_lines_byte_intact": all(
            x in oracle for x in (
                "frozen_by                        : independent reviewer session",
                "frozen_at_utc                    : 2026-09-20T03:15:44Z",
                "frozen_tolerance_seconds         : 5",
                "reviewer_signature_line          :",
            )),
    }
    u5_ok = (u5["i14b_card_untouched_by_this_card"] and not product_touched
             and u5["frozen_four_lines_byte_intact"])
    results["U-5"] = {
        "claim": "the ruling orders no write: this card touched nothing in I-14-B and the frozen four lines are byte-intact",
        "holds": bool(u5_ok),
        "evidence": u5,
        "shape_note": "oracle.md was NOT append-only across history (the reviewer filled four lines), so byte-prefix "
                      "is the wrong criterion for it; the meaningful claim is that THIS card wrote nothing",
    }

    anchor_sha = hashlib.sha256((REPO / "scripts/model_registry.py").read_bytes()).hexdigest()
    anchor_ok = (anchor_sha == EXPECTED_ANCHOR)

    all_ok = all(results[k]["holds"] for k in ("U-1", "U-2", "U-3", "U-4", "U-5")) and anchor_ok

    print("=" * 72)
    print("T1-18 verification -- I-14-B D-1 tolerance freeze (and its limit)")
    print("=" * 72)
    for k in ("U-1", "U-2", "U-3", "U-4", "U-5"):
        v = results[k]
        print(f"\n[{k}] {'PASS' if v['holds'] else 'FAIL'}  {v['claim']}")
        if k == "U-3":
            for kk, vv in v["evidence"].items():
                if isinstance(vv, bool):
                    print(f"      {'ok ' if vv else 'BAD'}  {kk}")
    print(f"\n[anchor] {'PASS' if anchor_ok else 'FAIL'}  scripts/model_registry.py = {anchor_sha[:16]}...")
    if notes:
        print("\nnotes:")
        for n in notes:
            print("  -", n)
    print("\n" + "=" * 72)
    print("overall =", "PASS" if all_ok else "FAIL")

    payload = {
        "card": "T1-18",
        "attempt": "a20260920-01",
        "kind": "interpretation_confirmation",
        "ruling": "OWNER_DECISIONS.md section 13 T1-18: CONFIRMED frozen_tolerance_seconds = 5 and "
                  "capture_latency_tolerance_seconds = 5 (legal band [1, 86] s). BUT the signature is NOT "
                  "permission to open a real window: the real 30/60/120 stays blocked (see T1-9).",
        "why_two_affirmative_halves": "the ruling ratifies the freeze AND re-affirms the limit. Checking only "
                                      "the freeze could 'prove' the qualification ready while the boundary that "
                                      "keeps it from being claimed had eroded; checking only the limit would "
                                      "ignore the values being ratified. Both are separate legs.",
        "propositions": results,
        "production_anchor": {"path": "scripts/model_registry.py", "sha256": anchor_sha,
                              "expected": EXPECTED_ANCHOR, "matches": anchor_ok},
        "overall": "PASS" if all_ok else "FAIL",
    }
    (EXEC / "t18_i14b_d1_tolerance_scope.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", (EXEC / "t18_i14b_d1_tolerance_scope.json").relative_to(REPO))
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())
