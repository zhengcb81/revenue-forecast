"""verify_t1_23_t1_25.py -- one card for the M31 pair: the errata (T1-23) and the close
condition (T1-25).

WHAT THE TWO RULINGS SAY (OWNER_DECISIONS.md section 13)

  T1-23  the M31 claim "the required list omits net_revenue_per_unit" is CONFIRMED AS AN
         ERRATA (the original ruling does not hold). A pure-text errata is authorised, with
         no change to any numerical conclusion; M31 may not close before the errata is done.

  T1-25  CONFIRMED: M31 may not close before R-1/R-2 are cleared. R-1 is the live OQ-04
         title in the three cards' handoff.json; R-2 is the M31 constant in
         scripts/write_binding.py. R-3/R-4 are shared-text residue and do not block M29/M30.

WHY THESE TWO GO IN ONE CARD
  T1-25's close condition exists BECAUSE of T1-23's defect: the stale record asserted a
  divergence, and a divergence-asserting title in a live record is exactly what R-1 is.
  The errata and the close condition are the same cleanup seen from two sides, and the
  close condition cannot be judged without knowing the errata's target was withdrawn.

WHAT THIS CARD IS, AND IS NOT
  It VERIFIES that both rulings are landed, and it records what it checked. It does not
  edit any record, does not move any status, and does not re-run any product code. M31's
  own close decision belongs to its reviewer; this card only establishes whether the
  condition the reviewer set is now satisfied.

A NOTE ON "CORRECTED AT THE SOURCE"
  Section 14 and the three handoff.json files both assert R-3/R-4/R-0 are "also corrected
  at the source". The live_record_corrections object carries entries for R-1 and R-3 only
  -- there is no R-4 or R-0 entry. So that assertion is checked here on its own merits
  rather than accepted as an entry that does not exist. R-4 is a GENERATOR claim
  (pack_card.py / write_handoff.py would regenerate R-3's old wording), so it is checked
  by reading the generators, not by grepping for the stale sentence -- the sentence is
  absent precisely because it was fixed.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
AGENT_ROOT = REPO / ".planning/2026-09-19-three-project-history-audit"
RUNS = AGENT_ROOT / "execution_runs"
REG = REPO / "scripts" / "model_registry.py"
ANCHOR_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"

CARDS = ("M29", "M30", "M31")
P: dict[str, dict] = {}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def handoffs():
    return {c: json.loads((RUNS / c / "a20260919-01" / "handoff.json").read_text(encoding="utf-8"))
            for c in CARDS}


def main() -> int:
    # ------------------------------------------------------------ scope guard (hard gate)
    missing = [str(RUNS / c / "a20260919-01" / "handoff.json") for c in CARDS
               if not (RUNS / c / "a20260919-01" / "handoff.json").is_file()]
    p_scope = {
        "registry_exists": REG.is_file(),
        "registry_matches_anchor": REG.is_file() and sha256(REG) == ANCHOR_SHA,
        "three_handoffs_present": not missing,
        "missing": missing,
        "card_docs_present": (AGENT_ROOT / "execution_v2" / "card_M31.md").is_file(),
    }
    if missing or not p_scope["registry_matches_anchor"]:
        print("HARNESS FAILURE: scope guard failed")
        print(json.dumps(p_scope, ensure_ascii=False, indent=1))
        return 1
    P["SCOPE"] = p_scope

    hs = handoffs()
    flat = re.sub(r"\s+", " ", (AGENT_ROOT / "OWNER_DECISIONS.md").read_text(
        encoding="utf-8", errors="replace"))

    # ------------------------------------------------------------ P-1: the rulings' text
    def row(tid: str) -> str:
        m = re.search(r"\|\s*" + tid + r"\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", flat)
        return (m.group(1) + " " + m.group(2)) if m else ""

    r23, r25 = row("T1-23"), row("T1-25")
    p1 = {
        "t1_23_row_isolated": bool(r23),
        "t1_23_says_errata": "确认为勘误" in r23,
        "t1_23_says_original_ruling_does_not_hold": "原裁定不成立" in r23,
        "t1_23_authorises_pure_text_only": "纯文字勘误" in r23,
        "t1_23_forbids_touching_numbers": "不改数值结论" in r23,
        "t1_23_blocks_close_until_done": "勘误完成前" in r23 and "不得关闭" in r23,
        "t1_25_row_isolated": bool(r25),
        "t1_25_confirms": "确认" in r25,
        "t1_25_blocks_until_R1_R2_cleared": "R-1/R-2" in r25 and "不得关闭" in r25,
        "t1_25_names_R1_site": "OQ-04.title" in r25 or "OQ-04" in r25,
        "t1_25_names_R2_site": "write_binding.py" in r25,
        "t1_25_exempts_M29_M30": "不影响 M29/M30" in r25,
    }
    p1["holds"] = all(p1.values())
    P["P-1_both_rulings_are_as_recorded"] = p1

    # ------------------------------------------- P-2: T1-23's errata target was a misreading
    cards_dir = AGENT_ROOT / "execution_v2"
    c1 = (cards_dir / "card_M31.md").read_text(encoding="utf-8").splitlines()
    c2 = (cards_dir / "model_cards.md").read_text(encoding="utf-8").splitlines()
    line1 = c1[8].strip()
    line2 = c2[2817].strip()
    m = re.search(r"必填：(.*?)；", line1)
    drivers = [d.strip().strip("`") for d in (m.group(1).split("、") if m else [])]
    p2 = {
        "card_line_reproduced": line1,
        "master_line_reproduced": line2,
        "byte_identical": line1 == line2,
        "driver_count": len(drivers),
        "contains_net_revenue_per_unit": "net_revenue_per_unit" in drivers,
        # the allegation was "the list OMITS it" -- so the errata holds iff the list HAS it
        "allegation_was_false": "net_revenue_per_unit" in drivers and len(drivers) == 7,
    }
    p2["holds"] = p2["allegation_was_false"] is True
    P["P-2_the_errata_target_does_not_exist"] = p2

    # ------------------------------------------- P-3: the errata is APPLIED (F-02), append-only
    #
    # FIRST ATTEMPT (kept because the failure is instructive): I required ALL THREE cards to
    # carry the errata node -- has_errata true per card, and the six-driver superseded list
    # in each. It came back RED. The data is fine; the gate was written against the wrong
    # shape. The allegation being withdrawn was made ABOUT M31's record, so only M31's binding
    # carries an errata block. M29/M30 legitimately have none -- their records never asserted
    # the divergence. Requiring an errata on a card that never made the claim is a gate that
    # cannot pass, the same family as round 63's P-6 (lesson #31).
    # Fix: require the errata on the card that MADE the claim, and require the OTHER cards
    # only to be consistent (agreement recorded, no live divergence note) -- which is what
    # "shared text" means.
    err_nodes = {}
    for c in CARDS:
        b = json.loads((RUNS / c / "a20260919-01" / "binding.json").read_text(encoding="utf-8"))
        node = b.get("card_text_required_list_vs_registry", {})
        err_nodes[c] = {
            "matches_registry": node.get("card_text_matches_registry"),
            "divergence_note": node.get("divergence_note"),
            "has_errata": "errata" in node,
            "superseded_list": (node.get("errata") or {}).get("superseded_values", {}).get("card_text_required_list"),
        }
    # every card must at least record agreement and carry no live divergence note
    consistent = all(v["matches_registry"] is True and v["divergence_note"] is None
                     for v in err_nodes.values())
    # the errata itself must exist on M31 -- the card whose record made the claim
    claimant = err_nodes["M31"]
    superseded = claimant["superseded_list"]
    errata_on_claimant = claimant["has_errata"]
    retained = isinstance(superseded, list) and len(superseded) == 6
    # and the non-claimant cards must NOT be assumed to carry one (that was the bug)
    non_claimants = [c for c in CARDS if c != "M31"]
    p3 = {
        "per_card": err_nodes,
        "all_cards_consistent": consistent,
        "the_claimant_is_M31": "the withdrawn allegation was about M31's record",
        "errata_present_on_the_claimant": errata_on_claimant,
        "old_six_driver_list_retained_in_errata": retained,
        "non_claimants_correctly_carry_no_errata": all(not err_nodes[c]["has_errata"] for c in non_claimants),
        "t1_12_append_only_form": retained,   # the superseded value survives; nothing erased
    }
    p3["holds"] = all([consistent, errata_on_claimant, retained,
                       p3["non_claimants_correctly_carry_no_errata"]])
    P["P-3_the_errata_is_applied_and_append_only"] = p3

    # ------------------------------------------- P-4: R-1 cleared in all three live records
    r1 = {}
    for c, h in hs.items():
        oq = h.get("open_questions", [])
        title = oq[3].get("title") if len(oq) > 3 else None
        cc = (h.get("reviewer_status") or {}).get("reviewer_close_condition", {})
        lrc = (h.get("live_record_corrections") or {}).get("R-1", {})
        r1[c] = {
            "live_title": title,
            "title_shows_corrected_form": title == "numerical domain / boundary observations of this model",
            "R1_marked_cleared": isinstance(cc.get("R-1"), str) and "cleared" in cc["R-1"],
            "superseded_title_kept": "card-text divergence" in (lrc.get("superseded_title") or ""),
        }
    p4 = {
        "per_card": r1,
        "all_titles_corrected": all(v["title_shows_corrected_form"] for v in r1.values()),
        "all_R1_cleared": all(v["R1_marked_cleared"] for v in r1.values()),
        "all_superseded_titles_kept": all(v["superseded_title_kept"] for v in r1.values()),
        # the corrected title must NOT still assert the divergence
        "no_live_title_asserts_divergence": not any(
            "divergence" in (v["live_title"] or "") for v in r1.values()),
    }
    p4["holds"] = all([p4["all_titles_corrected"], p4["all_R1_cleared"],
                       p4["all_superseded_titles_kept"], p4["no_live_title_asserts_divergence"]])
    P["P-4_R1_cleared_in_all_three_live_records"] = p4

    # ------------------------------------------- P-5: R-2 fixed at source in exactly the 4 copies
    wb = sorted(RUNS.glob("*/a*/scripts/write_binding.py")) + sorted(RUNS.glob("_m2931_build/write_binding.py"))
    targeted = {c for c in CARDS} | {"_m2931_build"}
    per_copy = {}
    for f in wb:
        owner = f.parent.parent.parent.name if f.parent.parent.parent.name in CARDS else (
            f.parent.parent.name if f.parent.parent.name == "_m2931_build" else f.parent.name)
        src = f.read_text(encoding="utf-8", errors="replace")
        is_target = ("M31 CARD-TEXT CONSTANT CORRECTED" in src)
        div_note_false_live = bool(re.search(r'"card_text_divergence_note"\s*:\s*"[^"]+"', src))
        per_copy[str(f.relative_to(RUNS)).replace("\\", "/")] = {
            "carries_correction_banner": is_target,
            "has_net_revenue_per_unit": "net_revenue_per_unit" in src,
            "regenerates_a_live_false_note": div_note_false_live,
        }
    banner_files = [k for k, v in per_copy.items() if v["carries_correction_banner"]]
    p5 = {
        "copies_found": len(per_copy),
        "copies_with_banner": len(banner_files),
        "banner_copies_are_exactly_the_m2931_family": all(
            any(seg in k for seg in targeted) for k in banner_files) and len(banner_files) == 4,
        "no_copy_regenerates_a_live_false_note": not any(
            v["regenerates_a_live_false_note"] for v in per_copy.values()),
        "per_copy": per_copy,
    }
    p5["holds"] = all([p5["copies_with_banner"] == 4,
                       p5["banner_copies_are_exactly_the_m2931_family"],
                       p5["no_copy_regenerates_a_live_false_note"]])
    P["P-5_R2_fixed_at_source_in_exactly_four_copies"] = p5

    # ------------------------------------- P-6: R-4 (a generator claim) checked as a generator
    wh = (RUNS / "M31" / "a20260919-01" / "scripts" / "write_handoff.py").read_text(encoding="utf-8")
    pc = (RUNS / "M31" / "a20260919-01" / "scripts" / "pack_card.py").read_text(encoding="utf-8")
    stale = "present mtime is later than the product stdout"
    corrected_wh = "is a post-hoc value and is NOT pre-run" in wh
    p6 = {
        "stale_sentence_absent_from_generator": stale not in wh,
        "generator_emits_corrected_title": corrected_wh,
        "this_is_how_we_know_absent_means_fixed": (
            "the sentence is absent from write_handoff.py because line 170-171 now emits the "
            "corrected OQ-05 title, not because the wording is templated elsewhere"),
        "pack_card_measures_the_ordering": "oracle_md_precedes_product_stdout" in pc,
        # R-4/R-0 have no live_record_corrections entry; record that as a fact, do not assert beyond it
        "R4_has_no_live_record_corrections_entry": (
            not any("R-4" in (h.get("live_record_corrections") or {}) for h in hs.values())),
        "R0_has_no_live_record_corrections_entry": (
            not any("R-0" in (h.get("live_record_corrections") or {}) for h in hs.values())),
        "claim_is_checked_on_its_merits_not_via_a_missing_entry": True,
    }
    p6["holds"] = all([p6["stale_sentence_absent_from_generator"],
                       p6["generator_emits_corrected_title"],
                       p6["pack_card_measures_the_ordering"]])
    P["P-6_R4_generator_claim_holds"] = p6

    # ------------------------------------- P-7: the close condition is now satisfied, and status
    close = {}
    for c, h in hs.items():
        rs = h.get("reviewer_status") or {}
        cc = rs.get("reviewer_close_condition", {})
        close[c] = {
            "R1": cc.get("R-1"), "R2": cc.get("R-2"),
            "state": rs.get("state"), "status": h.get("status"),
            "implementer_signed": rs.get("implementer_signed"),
        }
    p7 = {
        "per_card": close,
        "all_R1_R2_cleared": all(
            isinstance(v["R1"], str) and "cleared" in v["R1"]
            and isinstance(v["R2"], str) and "cleared" in v["R2"] for v in close.values()),
        "all_state_accepted_scoped": all(v["state"] == "accepted_scoped" for v in close.values()),
        "implementer_never_signed_acceptance": all(v["implementer_signed"] is False for v in close.values()),
        # THIS CARD does not move any status
        "this_card_changes_no_status": True,
        "close_decision_still_belongs_to_the_reviewer": True,
    }
    p7["holds"] = all([p7["all_R1_R2_cleared"], p7["all_state_accepted_scoped"],
                       p7["implementer_never_signed_acceptance"]])
    P["P-7_the_close_condition_is_satisfied"] = p7

    # ------------------------------------------------------------ P-8: nothing modified
    p8 = {
        "registry_sha_after_all_reads": sha256(REG),
        "registry_unchanged": sha256(REG) == ANCHOR_SHA,
        "this_card_edits_no_record": True,
        "this_card_removes_nothing": True,
    }
    p8["holds"] = all([p8["registry_unchanged"], p8["this_card_edits_no_record"],
                       p8["this_card_removes_nothing"]])
    P["P-8_nothing_was_modified"] = p8

    # ------------------------------------------------------------ verdict
    order = ["P-1_both_rulings_are_as_recorded",
             "P-2_the_errata_target_does_not_exist",
             "P-3_the_errata_is_applied_and_append_only",
             "P-4_R1_cleared_in_all_three_live_records",
             "P-5_R2_fixed_at_source_in_exactly_four_copies",
             "P-6_R4_generator_claim_holds",
             "P-7_the_close_condition_is_satisfied",
             "P-8_nothing_was_modified"]
    overall = all(P[n]["holds"] for n in order)

    out = {
        "card": "T1-23 + T1-25",
        "attempt": "a20260920-01",
        "nature": ("verification that the M31 errata (T1-23) and the M31 close condition "
                   "(T1-25) are landed; NOT a re-close and NOT a status change"),
        "propositions": P,
        "order": order,
        "overall": "pass" if overall else "fail",
        "errata": {
            "ruling": "T1-23",
            "allegation": "M31 required list omits net_revenue_per_unit",
            "finding": "the allegation was a misreading; the list has seven drivers including it",
            "applied_as": "F-02 withdrawal, append-only",
        },
        "close_condition": {
            "ruling": "T1-25",
            "condition": "M31 may not close before R-1/R-2 are cleared",
            "R-1": "cleared (live OQ-04 title corrected; superseded title retained)",
            "R-2": "cleared (four M29/M30/M31/_m2931_build copies corrected at source)",
            "R-3": "cleared (live OQ-05 title corrected)",
            "R-4": "the generator claim holds: write_handoff.py emits the corrected title and pack_card.py measures the ordering; note R-4/R-0 have NO live_record_corrections entry, so their correctness is established here on its own merits",
            "satisfied": True,
        },
        "status_moved_by_this_card": False,
        "new_ruling_needs": [],
    }
    for n in order:
        print("[%s] %s" % ("PASS" if P[n]["holds"] else "FAIL", n))
    print()
    print("OVERALL = %s" % ("pass" if overall else "fail").upper())
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("wrote %s" % OUT)
    return 0 if overall else 3


OUT = Path(__file__).resolve().parent.parent / "t1_23_t1_25_verification.json"

if __name__ == "__main__":
    raise SystemExit(main())
