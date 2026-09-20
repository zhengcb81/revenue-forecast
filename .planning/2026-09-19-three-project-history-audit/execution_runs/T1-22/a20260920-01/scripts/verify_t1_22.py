"""verify_t1_22.py -- T1-22 product-defect characterisation for the two cards the ruling authorises.

WHAT THE RULING SAYS (OWNER_DECISIONS.md section 13, T1-22)
  "Authorise carding": (1) model_registry.py:335 silently fills 0 -- (31 slots / 24 models) --
  should raise ModelRegistryError when a driver is omitted; (2) _SIGNED_DRIVERS should become a
  SEMANTIC-ROLE based sign rule. "Both handled in the same card."

WHAT THIS CARD IS, AND IS NOT
  It is a CHARACTERISATION + CARD-CONTENT card. It verifies that the two defects exist exactly
  as the ruling describes, measures their blast radius, and writes the card contents (scope,
  acceptance criteria, the oracle each card needs) so the cards can be opened.
  It does NOT modify model_registry.py. The ruling authorises carding; it does not authorise the
  fix. A card that edits the product file would be the fix, not the card.

WHY THE PREMISES ARE CHECKED FIRST
  A ruling can only be executed if the thing it names is still the thing on disk. The ruling
  names three specifics: line 335, the pair (31 slots / 24 models), and the name _SIGNED_DRIVERS.
  Each is checked as a claim rather than assumed. In particular "31 slots / 24 models" is a
  COUNT WITH A SCOPE, and I had to find out what it counts: my first pass measured 156 slots
  lacking a default across 31 models, which is a DIFFERENT number describing the same defect.
  The ruling's 31/24 turns out to count OPTIONAL slots lacking a declared default. Both numbers
  are correct; they are counting different things. Reporting mine as "the ruling is wrong" would
  have been the mistake.

Contrast with last round's lesson: I do NOT guess the API. The call signature used below
  (calculate_registered_model(model_id, base_revenue, drivers, years)) was read from the source,
  after a first attempt at calculate_model() failed -- which is the same trap as lesson #23.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
REG = REPO / "scripts" / "model_registry.py"
AGENT_ROOT = REPO / ".planning/2026-09-19-three-project-history-audit"

ANCHOR_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"

sys.path.insert(0, str(REPO / "scripts"))
import model_registry as mr  # noqa: E402

P: dict[str, dict] = {}


def main() -> int:
    # ---------------------------------------------------------------- scope guard (hard gate)
    p_scope = {
        "registry_exists": REG.is_file(),
        "registry_sha": sha256(REG),
        "registry_matches_anchor": sha256(REG) == ANCHOR_SHA,
        "scope_guard_not_vacuous": REG.is_file() and len(mr.MODEL_REGISTRY) > 0,
    }
    if not p_scope["scope_guard_not_vacuous"]:
        print("HARNESS FAILURE: registry missing or empty")
        return 1
    P["SCOPE"] = p_scope

    src = REG.read_text(encoding="utf-8")
    lines = src.splitlines()

    # ---------------------------------------------------------------- P-1: the ruling text
    dec = (AGENT_ROOT / "OWNER_DECISIONS.md").read_text(encoding="utf-8", errors="replace")
    flat = re.sub(r"\s+", " ", dec)          # \s+ not [ \t]+ -- lesson #24
    p1 = {
        "t1_22_named": "T1-22" in flat,
        "authorises_carding": bool(re.search(r"授权立卡", flat)),
        "names_line_335": bool(re.search(r"model_registry\.py:335", flat)),
        "names_silent_zero": bool(re.search(r"静默补\s*0", flat)),
        "quotes_the_count_31_24": bool(re.search(r"31\s*槽位\s*/\s*24\s*模型", flat)),
        "requires_ModelRegistryError": "ModelRegistryError" in flat,
        "names_signed_drivers": "_SIGNED_DRIVERS" in flat,
        "requires_semantic_role_rule": bool(re.search(r"基于语义角色", flat)),
        "says_both_in_one_card": bool(re.search(r"两项同卡处理", flat)),
    }
    p1["holds"] = all(p1.values())
    P["P-1_ruling_names_both_defects_and_the_count"] = p1

    # ---------------------------------------------------------------- P-2: line 335 is the site
    target_line = lines[334] if len(lines) >= 335 else ""
    p2 = {
        "line_335_in_range": len(lines) >= 335,
        "line_335_text": target_line.strip(),
        "line_335_contains_silent_default": bool(
            re.search(r"drivers\.get\(\s*driver\s*,\s*\[.*defaults\.get\(.*0\.0", target_line)),
        "the_default_is_0.0": "0.0" in target_line,
        "no_raise_on_that_line": "raise" not in target_line,
    }
    # also confirm the caller does not pre-validate omission elsewhere on this path
    p2["the_default_appears_once_in_the_file"] = src.count("defaults.get(driver, 0.0)") == 1
    p2["holds"] = all(v for k, v in p2.items() if k != "line_335_text")
    P["P-2_the_defect_site_is_line_335"] = p2

    # ---------------------------------------------------------------- P-3: the 31/24 count
    reg = mr.MODEL_REGISTRY
    opt_no_default = 0
    opt_models = set()
    for mid, spec in reg.items():
        for d in spec.optional:
            if d not in spec.defaults:
                opt_no_default += 1
                opt_models.add(mid)

    all_no_default = 0
    all_models = set()
    for mid, spec in reg.items():
        for d in list(spec.required) + list(spec.optional):
            if d not in spec.defaults:
                all_no_default += 1
                all_models.add(mid)

    p3 = {
        "optional_slots_without_default": opt_no_default,
        "models_with_such_a_slot": len(opt_models),
        "ruling_count_reproduced": opt_no_default == 31 and len(opt_models) == 24,
        "whole_registry_slots_without_default": all_no_default,
        "whole_registry_models_affected": len(all_models),
        "models_total": len(reg),
        "scope_note": ("the ruling's 31/24 counts OPTIONAL slots lacking a declared default; "
                       "the whole registry has more (required slots too). Both are the same "
                       "defect seen at different scope; the ruling's number is reproduced "
                       "exactly and is not an error."),
    }
    p3["holds"] = p3["ruling_count_reproduced"] is True
    P["P-3_the_31_24_count_reproduces_for_optional_slots"] = p3

    # ---------------------------------------------------------------- P-4: live silent-zero
    years = [2026, 2027]
    base_rev = 1000.0
    d_omit = {"units": [100.0, 110.0], "unit_revenue": [10.0, 10.0]}
    d_zero = {"units": [100.0, 110.0], "unit_revenue": [10.0, 10.0], "other_revenue": [0.0, 0.0]}
    out_omit = mr.calculate_registered_model("unit_sales", base_rev, d_omit, years)
    out_zero = mr.calculate_registered_model("unit_sales", base_rev, d_zero, years)
    p4 = {
        "omitted_result": out_omit,
        "explicit_zero_result": out_zero,
        "omission_is_indistinguishable_from_explicit_zero": out_omit == out_zero,
        "no_error_raised_for_omission": True,   # we reached this line, so nothing raised
        "ruling_requires_error_instead": True,
    }
    p4["holds"] = p4["omission_is_indistinguishable_from_explicit_zero"] is True
    P["P-4_omission_is_live_and_indistinguishable_from_zero"] = p4

    # ---------------------------------------------------------------- P-5: name-based sign rule
    p5 = {
        "signed_drivers_is_a_name_frozenset": isinstance(mr._SIGNED_DRIVERS, frozenset),
        "signed_drivers_members": sorted(mr._SIGNED_DRIVERS),
        "rule_order_in_source": ("explicit metadata > _SIGNED_DRIVERS name > ratio > (0, inf)"),
        "rule_read_at_line_289": bool(
            re.search(r"if driver in _SIGNED_DRIVERS", src)),
        "unbounded_sign_granted_by_name_alone": 0,
        "dimensions_involved": {},
    }
    from collections import Counter
    dims = Counter()
    n_by_name = 0
    for mid, spec in reg.items():
        for d in list(spec.required) + list(spec.optional):
            if d in mr._SIGNED_DRIVERS and d not in spec.driver_bounds:
                n_by_name += 1
                dims[spec.dimensions.get(d)] += 1
    p5["unbounded_sign_granted_by_name_alone"] = n_by_name
    p5["dimensions_involved"] = dict(dims)
    # the discrimination test: same model, two drivers -- one whose NAME is in the frozenset,
    # one whose name is not. If the NAME is what decides the sign, their domains differ AND
    # the width of the difference follows the name. NC-3 (a negative control that overwrote
    # name_decides_not_role with a bare True) came back GREEN, which exposed that the test as
    # first written could pass while asserting something false -- so the discrimination is now
    # rebuilt to be self-standing and falsifiable rather than partly a restatement of the
    # bounds I had just read.
    a = mr.driver_value_bounds("unit_sales", "other_revenue")   # "other_revenue" IS name-listed
    b = mr.driver_value_bounds("unit_sales", "units")           # "units" is NOT name-listed
    p5["other_revenue_bounds"] = list(a)
    p5["units_bounds"] = list(b)
    p5["other_revenue_is_name_listed"] = "other_revenue" in mr._SIGNED_DRIVERS
    p5["units_is_not_name_listed"] = "units" not in mr._SIGNED_DRIVERS
    # FALSIFIABLE CORE: name-listed => signed below zero; not listed => lower bound pinned at 0.
    p5["name_listed_driver_admits_negative_values"] = a[0] < 0.0
    p5["unlisted_driver_forbids_negative_values"] = b[0] == 0.0
    p5["the_two_domains_differ"] = a != b
    # and the flip test: a bare "True" assignment (NC-3) would set these to constants, so the
    # premise must be derived from the OBSERVED numbers, not from a literal.
    p5["premise_is_derived_from_observations_not_a_literal"] = (
        p5["name_listed_driver_admits_negative_values"] == (a[0] < 0.0)
        and p5["unlisted_driver_forbids_negative_values"] == (b[0] == 0.0)
    )
    p5["holds"] = all([
        p5["signed_drivers_is_a_name_frozenset"],
        p5["rule_read_at_line_289"],
        p5["unbounded_sign_granted_by_name_alone"] > 0,
        p5["other_revenue_is_name_listed"],
        p5["units_is_not_name_listed"],
        p5["name_listed_driver_admits_negative_values"] is True,
        p5["unlisted_driver_forbids_negative_values"] is True,
        p5["the_two_domains_differ"] is True,
        p5["premise_is_derived_from_observations_not_a_literal"] is True,
    ])
    P["P-5_sign_permission_is_decided_by_driver_name"] = p5

    # ---------------------------------------------------------------- P-6: no edit made
    #
    # FIRST ATTEMPT (kept here because the failure is instructive): I tested
    #   not re.search(r"授权(修复|实施|改写)", flat)          # flat = the WHOLE file
    # It came back RED. The data is fine; the gate was broken. "授权实施" occurs twice in
    # OWNER_DECISIONS.md, but at OTHER tiers (T1-26, T2-1), not in T1-22's row. A file-wide scan
    # therefore mixes T1-22's authorisation with unrelated tiers' -- it can never come back green,
    # which makes it not a test but a constant. This is lesson #19 seen from the other side: not
    # a test that cannot fail, but a test that cannot pass.
    # Fix: SCOPE the judgement to T1-22's own table row. A ruling about T1-22 is a claim about
    # T1-22's row; the rest of the file is other tiers' business and has no say here.
    row = re.search(r"\|\s*T1-22\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", flat)
    row_text = (row.group(1) + " " + row.group(2)) if row else ""
    p6 = {
        "registry_sha_unchanged_after_all_calls": sha256(REG) == ANCHOR_SHA,
        "matches_recorded_anchor": sha256(REG) == ANCHOR_SHA,
        "this_card_is_characterisation_not_fix": True,
        "t1_22_row_isolated": bool(row),
        "t1_22_row_text": row_text,
        "t1_22_row_authorises_carding": bool(re.search(r"授权立卡", row_text)),
        "t1_22_row_does_not_authorise_the_fix": not bool(
            re.search(r"授权(修复|实施|改写)", row_text)),
        # the reason the first gate was red, recorded explicitly rather than silently dropped:
        "whole_file_contains_授权实施_but_at_other_tiers": len(re.findall(r"授权实施", flat)),
        "therefore_a_whole_file_scan_is_not_a_test": len(re.findall(r"授权实施", flat)) > 0,
    }
    p6["holds"] = all([
        p6["registry_sha_unchanged_after_all_calls"],
        p6["matches_recorded_anchor"],
        p6["this_card_is_characterisation_not_fix"],
        p6["t1_22_row_isolated"],
        p6["t1_22_row_authorises_carding"],
        p6["t1_22_row_does_not_authorise_the_fix"],
    ])
    P["P-6_nothing_was_modified"] = p6

    # ---------------------------------------------------------------- verdict
    order = ["P-1_ruling_names_both_defects_and_the_count",
             "P-2_the_defect_site_is_line_335",
             "P-3_the_31_24_count_reproduces_for_optional_slots",
             "P-4_omission_is_live_and_indistinguishable_from_zero",
             "P-5_sign_permission_is_decided_by_driver_name",
             "P-6_nothing_was_modified"]
    overall = all(P[n]["holds"] for n in order)

    out = {
        "card": "T1-22",
        "attempt": "a20260920-01",
        "nature": ("characterisation of the two product defects the ruling authorises carding; "
                   "NOT the fix"),
        "propositions": P,
        "order": order,
        "overall": "pass" if overall else "fail",
        "defect_1": {
            "site": "scripts/model_registry.py:335",
            "behaviour": ("an omitted driver is silently substituted with spec.defaults.get("
                          "driver, 0.0) repeated over the horizon; omission and an explicit "
                          "0.0 are indistinguishable in the result"),
            "required_behaviour": "raise ModelRegistryError on omission (省缺即抛)",
            "blast_radius_ruling_scope": {"optional_slots": opt_no_default,
                                          "models": len(opt_models)},
            "blast_radius_whole_registry": {"slots": all_no_default,
                                            "models": len(all_models)},
            "models_total": len(reg),
        },
        "defect_2": {
            "site": "scripts/model_registry.py:265-269 (_SIGNED_DRIVERS), consulted at :289",
            "behaviour": ("unbounded sign is granted by driver NAME membership in a hardcoded "
                          "frozenset, not by the driver's semantic role"),
            "required_behaviour": "a semantic-role based sign rule",
            "name_granted_slots": n_by_name,
            "dimensions_involved": dict(dims),
            "note": ("one model (renewable_generation) narrows its own 'other_revenue' via "
                     "explicit metadata; explicit metadata takes precedence, so the name list "
                     "is a default, not an override"),
        },
    }
    for n in order:
        print("[%s] %s" % ("PASS" if P[n]["holds"] else "FAIL", n))
        if n == "P-3_the_31_24_count_reproduces_for_optional_slots":
            print("        optional %d slots / %d models | whole registry %d / %d | total models %d"
                  % (opt_no_default, len(opt_models), all_no_default, len(all_models), len(reg)))
        if n == "P-4_omission_is_live_and_indistinguishable_from_zero":
            print("        omitted=%s explicit0=%s identical=%s"
                  % (out_omit, out_zero, P[n]["omission_is_indistinguishable_from_explicit_zero"]))
        if n == "P-5_sign_permission_is_decided_by_driver_name":
            print("        by-name slots=%d dims=%s" % (n_by_name, dict(dims)))
    print()
    print("OVERALL = %s" % ("pass" if overall else "fail").upper())
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("wrote %s" % OUT)
    return 0 if overall else 3


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


OUT = Path(__file__).resolve().parent.parent / "t1_22_defect_characterisation.json"

if __name__ == "__main__":
    raise SystemExit(main())
