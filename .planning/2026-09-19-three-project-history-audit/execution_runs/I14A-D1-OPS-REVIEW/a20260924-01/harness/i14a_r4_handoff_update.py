"""I-14-A, r4 follow-up: attribute the r3 block correctly and register the reviewer's r4 attestation.

Bookkeeping only — appends/edits fields in handoff.json. It does NOT touch review.md (the reviewer's
file) and does not modify the review's bytes. Run once; the resulting handoff.json hash is what
after/summary.json cites (and handoff.json is removed from the cited set for the same reason).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
HANDOFF = ATT / "handoff.json"
SUMMARY = ATT / "after" / "summary.json"

REVIEWER_AUTHORED = [":3", ":156", ":189", ":276-415"]
TRANSCRIBED = ":242-272"
SUPERSEDED = ":233-263"

NEW_STATUS = (
    "accepted_scoped — for the ISOLATED measurement fix only, limited to the exact card scope. The "
    "operative record is the reviewer's OWN appended attestation in review.md (:276-415, "
    "`## r4 — reviewer's own attestation`), which the reviewer wrote and appended itself; the earlier "
    "r3 text was a bookkeeping transcription and the reviewer explicitly does NOT author it. "
    "Transcribed for bookkeeping by the implementer on 2026-09-20; the implementer did not and does not "
    "sign acceptance. Promotion remains blocked (see promotion_blocked): D1/D2/D3 are unsigned, so "
    "accepted_scoped is the reviewer's qualification of the isolated measurement fix, NOT a promotion "
    "and NOT a card closure. The implementer changed no verdict word and no scope."
)

NEW_R3 = (
    "accepted_scoped CONFIRMED again by the r3 re-read; P4 and P5 CLOSED, residue N2 fixed, one reviewer "
    "error explicitly not carried forward. ATTRIBUTION: the r3 text in review.md (:242-272) is a "
    "BOOKKEEPING TRANSCRIPTION, not reviewer-authored; the reviewer disclaims its verdict sentence at "
    ":244. The same confirmation is re-registered by the reviewer in its own r4 append (:276-415)."
)

SOURCE = {
    "reviewer_authored_lines": REVIEWER_AUTHORED,
    "note": ("The sections the reviewer's r4 attestation names as its own: the PENDING preamble (:3), "
             "the r2 block (:156), the r3-confirmation sentence as re-registered in the r2 frame "
             "(:189), and the r4 attestation (:276-415)."),
    "transcribed_not_reviewer_authored": {
        "lines": TRANSCRIBED,
        "what": ("the `## r3 re-read — P4/P5 closed, N2 fixed…` block — written by a bookkeeping "
                 "transcription of the reviewer's r3 report, not by the reviewer"),
        "reviewer_position": ("The reviewer explicitly does NOT claim it and is not the author of its "
                              "verdict sentence at :244 ('The r3 re-read **confirmed accepted_scoped** "
                              "for this card…'). It preserved the text unedited (plus an attribution "
                              "marker at :234-241) and answered it in r4."),
        "superseded_citation": (f"{SUPERSEDED} — the range this field previously carried; the reviewer's "
                                "r4 attestation (:291-295) states that citation is inaccurate"),
        "consequence": ("Do NOT cite :242-272 as reviewer-authored and do not treat its assertions as "
                        "endorsed. Reviewer's §6.2: 'Any other statement inside :233-263 is someone "
                        "else's text and is not endorsed by this signature.'"),
    },
    "reviewer_self_registered_caveat": ("From the reviewer's own r4 text: if a reviewer-authored r3 "
                                        "re-read block is wanted inside review.md, THE REVIEWER MUST ADD "
                                        "IT ITSELF; the implementer authored none and signed nothing."),
    "line_number_maps": {
        "attribution_marker": ":234-241",
        "transcribed_r3_block": ":242-272",
        "r4_attestation": ":276-415",
        "reviewer_own_maps": ("The reviewer's §7 (:370-395) and §8 (:397-415) publish two successive line "
                              "maps and correct their own off-by-one errors in writing; §8's table is the "
                              "last word, and the disclaimed sentence is identified identically in every "
                              "frame."),
    },
    "coverage_of_the_signature": ("The r4 append covers ONLY the claims in its §2 (:297-311) and the "
                                  "counter-claim in its §4 (:323-334). It did not repeat the r1 re-runs "
                                  "(`--all`, pytest, changes.diff regeneration)."),
}

R4_VERDICT = {
    "verdict": ("accepted_scoped — isolated measurement fix only, limited to the exact card scope (three "
                "fixtures behave as frozen; command-total / business-latency / RSS-sampling windows "
                "reported separately; success latency and failure rate reported separately; budgets "
                "untouched)"),
    "disclosure_adaptation": "unmapped — this card never touched the log-redaction clause (that is I-14-C)",
    "accuracy": "unproven — no prediction, no accuracy claim, no basis for one",
    "card_status_effect": ("none — 'accepted_scoped here is the reviewer's qualification of the isolated "
                           "fix, not a promotion and not a card closure'"),
    "decisions": "D1/D2/D3 remain unsigned; the promotion prohibition stands",
}

P4_REOPENED = {
    "finding": ("review.md §4 (:323-334): the claim that summary.json's `values` block was recomputed in "
                "one write is NOT reproducible — 11 of 12 cited entries matched, `handoff.json` did not "
                "(cited c5ba34d716f3cd1cdb0722c8d736b86b302949d0e2c3d9db4e110d6cf012a0c3; actual at "
                "review time 6722ab34e91defae3fdcbb256eae5f6afd83d0fe5ab35f841d20dc62ca06cac0, 20445 B, "
                "mtime 2026-09-20 04:17:53, i.e. edited after the 02:51:24 capture)"),
    "why": ("the record had to be extended again AFTER the capture, so the citation went stale a second "
            "time — P4 live again in its narrowest form. The rule ('must be recomputed on use') is right "
            "but has to be applied at hand-off time, after the last write, not before it."),
    "already_verified_by_the_reviewer": ("handoff.json contains NO citation of its own hash (12 distinct "
                                         "64-hex strings, none self), so the earlier 'self-citation "
                                         "removed' statement holds; the stale value belonged to "
                                         "summary.json."),
    "implementer_disposition": ("OPTION 2 ADOPTED — `handoff.json` is REMOVED from the cited set in "
                                "after/summary.json:r2_new_hashes.values, and that block now declares the "
                                "file uncited. Rationale: option 1 (recompute after the last write) "
                                "cannot be executed by the same pass that performs the write, so it "
                                "would re-arm the same trap."),
}

REVIEWER_PORTFOLIO_CORRECTION = {
    "who_withdrew": "the independent reviewer, in its own r4 attestation (review.md §3, :313-321)",
    "their_words": ("'In my r3 report I stated that company-wiki porcelain was completely empty. That was "
                    "wrong' — root cause: a PowerShell subexpression calling a non-existent `-NoNewline` "
                    "parameter on `Out-String` failed, the failure was swallowed inside a string "
                    "interpolation, and the empty rendering was read as command output."),
    "clean_remeasure": {
        "company-wiki": [" M CLAUDE.md", " M README.md"],
        "company-wiki_count": 2,
        "filing-fetch": [],
        "revenue-forecast_tools": [],
    },
    "carried_forward_effect": ("the 'company-wiki completely empty' claim is WITHDRAWN and must not be "
                               "carried forward; the correct statement is 'exactly the two pre-existing "
                               "` M` entries'. No conclusion depends on it."),
}


def main() -> int:
    data = json.loads(HANDOFF.read_text(encoding="utf-8"))
    before_keys = set(data)

    data["reviewer_status"] = NEW_STATUS
    data["reviewer_status_r3"] = NEW_R3
    data["reviewer_status_source"] = SOURCE
    data["reviewer_r4_verdict"] = R4_VERDICT
    data["reviewer_r4_counter_claim_P4_reopened"] = P4_REOPENED

    # register the reviewer's own withdrawal of the porcelain claim in the carried-forward list
    carried = data.setdefault("reviewer_unverified_list_carried_forward", {})
    carried["reviewer_self_withdrawals_registered"] = [REVIEWER_PORTFOLIO_CORRECTION]
    carried["note"] = (
        "Reproduced from the reviews' own words. NONE of these may be cited as established. Items marked "
        "reviewer_self_withdrawals_registered were retracted by the reviewer itself and must be carried "
        "as withdrawn, not as findings."
    )
    porc = data.get("porcelain_correction")
    if isinstance(porc, dict):
        porc["reviewer_now_agrees"] = (
            "The reviewer re-measured cleanly in its r4 attestation and withdrew its own 'completely "
            "empty' claim (review.md §3 :313-321, root cause: a failed `Out-String -NoNewline` "
            "subexpression whose error was swallowed by string interpolation). Clean result: exactly two "
            "` M` entries in company-wiki, empty filing-fetch, empty `RF -- tools`."
        )

    HANDOFF.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "keys_before": len(before_keys),
        "keys_after": len(data),
        "added": sorted(set(data) - before_keys),
        "reviewer_authored_lines": REVIEWER_AUTHORED,
        "transcribed": TRANSCRIBED,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
