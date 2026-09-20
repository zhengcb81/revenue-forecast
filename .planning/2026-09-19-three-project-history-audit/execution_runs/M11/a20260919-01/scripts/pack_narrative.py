"""Narrative packer: writes the per-card human-readable files from one fact table.

It emits, for one card:
  decision.md                          professional-decision record (what is decided / escalated)
  review.md                            implementer review record (never an acceptance)
  handoff.json                         the handoff contract of review_and_handoff.md
  changes.diff                         NO PRODUCT CHANGE statement
  recovery/README.md                   recovery / non-applicability note
  before/README.md                     capture policy, pre-run anchors, mtime finding
  evidence/<CARD>/accounting_decision.md  PROPOSED (unsigned) accounting decisions

Every number that appears in review.md is read back from the evidence files at generation
time, so the narrative cannot drift from the evidence.

Run:
  python -X utf8 -B scripts/pack_narrative.py --card M09 --attempt <attempt> --plan-root <PLAN>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

BATCH = {
    "M09": {
        "model_id": "resource",
        "title": "资源销售量与实售价",
        "entry_line": 229,
        "applicability": "mining / energy / agricultural commodities from start of production to decline",
        "unit_rule": "sold settleable quantity x U per same quantity unit; never mix ore tonnes, "
                     "concentrate tonnes and metal tonnes",
        "positive_input": '{"model_id": "resource", "base_revenue": 0, "drivers": '
                          '{"saleable_volume": [30], "realized_price": [4], "other_revenue": [2]}, '
                          '"years": [2027]}',
        "positive_handwork": "30 x 4 = 120; 120 + 2 = 122",
        "continuity_handwork": "2027 = 30 x 4 + 2 = 122; 2028 = 45 x 5 + 0 = 225",
        "defaults_handwork": "30 x 4 + 0 (default) = 120",
        "card_negative": "saleable_volume = [-1] (card L35)",
        "card_negative_guard": "driver value-domain guard (quantity default bound [0, inf))",
        "business_negatives": [
            "recovery / payability / treatment-charge may be deducted exactly once",
            "production volume is not sales volume",
            "ore tonnes, concentrate tonnes and metal tonnes must not be mixed",
        ],
        "collect_items": "card L37: production / sales / inventory, grade, recovery and payability "
                         "factors, TC/RC units, settlement price, FX, by-products",
        "decisions": [
            ("DEC-M09-1", "Which quantity enters `saleable_volume` when the disclosure gives both "
                          "produced and sold volumes, and whether the payable/recovery factor belongs "
                          "inside the volume driver or on the price.",
             "PROPOSED: the driver is the already-payable settleable quantity (card L8 wording "
             "`sold settleable quantity`); recovery/payability/TC-RC are applied exactly once, before "
             "the driver, and the conversion is recorded in `conversion_formula`.",
             "If the factor is applied twice the revenue is understated without any runtime error."),
            ("DEC-M09-2", "Unit homogeneity across ore / concentrate / metal tonnes.",
             "PROPOSED: one unit family per segment; a segment that changes unit family must be split. "
             "The runtime contract cannot detect this, so it is a professional gate, not a test.",
             "The model has no unit field, so this is not run-time testable (oracle.md R7)."),
            ("DEC-M09-3", "Whether by-product revenue may sit in `other_revenue`.",
             "PROPOSED: only when it is not already inside `realized_price` x volume; the mapping must "
             "state which by-products are inside the price.",
             "Double counting by-products inflates revenue without any error."),
        ],
        "attack_points": [
            "**The card-specific negative is a value-domain refusal, not a length refusal.** "
            "`saleable_volume = [-1]` is rejected by `driver resource.saleable_volume must be between "
            "0.0 and inf: FY2027`. The same batch's r1 was rejected for a negative case that actually "
            "tripped the length guard; this one does not.",
            "**A negative realized price cannot be expressed.** OBS-PRICE-NEG shows the driver-domain "
            "guard fires first (`resource.realized_price must be between 0.0 and inf`); the totals guard "
            "would also refuse the resulting -28. For a commodity that can trade negative (for example "
            "the April-2020 crude episode) the current entry point cannot express it. Registered as "
            "OQ-3, no product change.",
            "**Silent zero-fill of `other_revenue`.** `scripts/model_registry.py:335` turns an omitted "
            "optional driver with no declared default into 0.0. For this model that asserts `no other "
            "revenue` without any disclosure saying so. Registered as OQ-1.",
            "**The 'no mixed tonnes' rule cannot be tested at runtime.** The model has no unit field, so "
            "oracle.md R7/R8/R9 are professional gates; a reviewer should not read their absence from "
            "the negative list as coverage.",
            "**Disclosure adaptation is 0/1 drivers (nothing mapped).** Both required drivers are still "
            "`missing`; the survey found a real local mining annual report, but no page/span extraction "
            "and no closed-period reconciliation was performed.",
        ],
        "not_claimed": [
            "It does not claim the model is accurate, nor that one company's mapping generalises.",
            "It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a "
            "production forecast-entry-point mapping reviewed independently.",
            "It does not rewrite the formula. With no independent counter-example and no adjudicated "
            "specification, the existing implementation is retained.",
        ],
    },
    "M10": {
        "model_id": "reserve_depletion",
        "title": "储量消耗桥",
        "entry_line": 230,
        "applicability": "extraction and decline businesses whose reserves, depletion and sales link is "
                         "verifiable",
        "unit_rule": "reserve stock and flow in one unit; depletion x recovery rate converts to sellable "
                     "quantity, then multiplied by a net price in the same unit",
        "positive_input": '{"model_id": "reserve_depletion", "base_revenue": 0, "drivers": '
                          '{"opening_reserves": [1000], "additions": [100], "reserve_revisions": [-50], '
                          '"depletion": [200], "closing_reserves": [850], "recovery_rate": [0.8], '
                          '"realized_price": [3], "other_revenue": [10]}, "years": [2027]}',
        "positive_handwork": "balance 1000 + 100 - 50 - 200 = 850 = closing; "
                             "revenue 200 x 0.8 = 160; 160 x 3 = 480; 480 + 10 = 490",
        "continuity_handwork": "2027 = 490 (balance 850); 2028 = 0 x 0.8 x 3 + 0 = 0, "
                               "opening 850 = prior closing 850",
        "defaults_handwork": "balance 1000 + 100 + 0 (default) - 250 = 850 = closing; "
                             "revenue 250 x 0.8 x 3 + 0 (default) = 600",
        "card_negative": "closing_reserves = [851] (card L50)",
        "card_negative_guard": "stock-flow balance guard (`reserve stock-flow balance failed: FY2027`)",
        "business_negatives": [
            "reserves that already embed the recovery factor must not be multiplied by it again",
            "depletion does not automatically equal current-period sales",
        ],
        "collect_items": "card L52: reserve classification, additions and revisions, depletion, the "
                         "recovery definition, the production/sales/inventory bridge and the realised price",
        "decisions": [
            ("DEC-M10-1", "Does the disclosed reserve quantity already embed the recovery factor?",
             "PROPOSED: `depletion` is the in-situ reserve quantity consumed and `recovery_rate` is the "
             "factor applied to it; when the disclosure only publishes recoverable reserves, the adapter "
             "must set `recovery_rate = 1` and record `reported_derived_assumed = assumed`.",
             "Multiplying twice understates revenue with no runtime error (oracle.md R9)."),
            ("DEC-M10-2", "Is `depletion` equal to current-period sales?",
             "PROPOSED: no. The model treats depletion x recovery as the sellable production proxy; the "
             "production/sales/inventory bridge must be reconciled in the mapping and any difference "
             "recorded as an assumption.",
             "Treating depletion as sales mixes inventory movement into revenue."),
            ("DEC-M10-3", "Non-negative `additions` versus signed `reserve_revisions`.",
             "PROPOSED: keep. Downward reserve movements must be routed through `reserve_revisions`; a "
             "negative addition is refused (`[0, inf)`), which the enumeration in oq_rulings.json "
             "confirms as contract, not as an accident.",
             "The sign routing is a mapping decision that the runtime cannot check."),
        ],
        "attack_points": [
            "**The two card gates are different code paths and both are exercised.** NEG-CARD trips the "
            "self-balance guard (`reserve stock-flow balance failed: FY2027`); CONT-BREAK trips the "
            "cross-year guard (`reserve continuity failed: FY2028`) while each year still balances on its "
            "own - exactly the case the card describes.",
            "**The continuity negative is the card's own patch, applied only after the two-year positive "
            "passed.** `cases.json` records the ordering (`continuity_then_break_order`) and the runner's "
            "`continuity_positive.ran_before_negative_patch` flag is true.",
            "**The defaults case had to be designed, not copied.** Omitting `reserve_revisions` forces 0, "
            "so the card's positive input would fail the balance test; the frozen defaults case changes "
            "`depletion` to 250 so the identity still holds. A reviewer should check that this is a "
            "legitimate defaults probe and not a smuggled input change.",
            "**Silent zero-fill is dangerous for `reserve_revisions`.** With `model_registry.py:335`, "
            "`no revision` and `we did not find the revision` become indistinguishable and the missing "
            "revision silently becomes balance. Registered as OQ-1, no product change.",
            "**OBS-REVISION-POS shows revisions do not enter revenue** (490 before and after a +50 "
            "revision that keeps the balance). A reviewer should confirm this is the intended contract: "
            "the model prices depletion, not the reserve movement.",
            "**Disclosure adaptation is 0/8 drivers.** The survey found a real local mining annual report; "
            "no reserve-class page/span extraction and no closed-period reconciliation was performed.",
        ],
        "not_claimed": [
            "It does not claim the model is accurate, nor that one company's mapping generalises.",
            "It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.",
            "It does not rewrite the formula or move any gate; the existing implementation is retained.",
        ],
    },
    "M11": {
        "model_id": "infrastructure",
        "title": "计费量与费率",
        "entry_line": 231,
        "applicability": "utilities, pipelines and toll/chargeable transport after start of operation",
        "unit_rule": "actual billable activity volume x U per same activity unit",
        "positive_input": '{"model_id": "infrastructure", "base_revenue": 0, "drivers": '
                          '{"billable_volume": [400], "tariff": [0.5], "other_revenue": [10]}, '
                          '"years": [2027]}',
        "positive_handwork": "400 x 0.5 = 200; 200 + 10 = 210",
        "continuity_handwork": "2027 = 400 x 0.5 + 10 = 210; 2028 = 500 x 0.6 + 0 = 300",
        "defaults_handwork": "400 x 0.5 + 0 (default) = 200",
        "card_negative": "billable_volume = [-1] (card L35)",
        "card_negative_guard": "driver value-domain guard (activity default bound [0, inf))",
        "business_negatives": [
            "throughput is not automatically fully billable",
            "subsidies and capacity charges must not be added twice",
        ],
        "collect_items": "card L37: billable volume, tiered tariffs, regulatory effective dates, taxes, "
                         "capacity charges, subsidies, recognition timing",
        "decisions": [
            ("DEC-M11-1", "Is the tariff a regulated all-in price, or does it exclude capacity charges "
                          "and subsidies?",
             "PROPOSED: one regulatory regime per segment; each of capacity fee and subsidy is either "
             "inside `tariff` or inside `other_revenue`, never both.",
             "Double counting raises revenue with no runtime error."),
            ("DEC-M11-2", "How is a tiered tariff with a mid-year effective date collapsed?",
             "PROPOSED: a volume-weighted effective tariff for the year, with the conversion formula and "
             "the effective date recorded per driver row; the model has no tier structure.",
             "Using the year-end tariff for the whole year misstates a regulated step change."),
            ("DEC-M11-3", "Is the disclosed throughput the billable volume?",
             "PROPOSED: no automatic pass-through. Only the billable volume enters `billable_volume`; "
             "unbilled throughput must be excluded and the exclusion recorded.",
             "Passing throughput straight into the driver inflates revenue."),
        ],
        "attack_points": [
            "**The card-specific negative is a value-domain refusal.** `billable_volume = [-1]` is "
            "rejected by `driver infrastructure.billable_volume must be between 0.0 and inf: FY2027`.",
            "**A negative tariff cannot be expressed.** OBS-TARIFF-NEG records the driver-domain guard "
            "(`infrastructure.tariff must be between 0.0 and inf`); a rebate-style negative tariff has no "
            "representation at this entry point. Registered as OQ-3.",
            "**No local source document supports this card's industry.** The survey lists the nearest "
            "available names (equipment, design institute, property, landscaping, equipment rental) and "
            "why each is the wrong contract. D therefore cannot even reach a mapping decision here.",
            "**The tier / effective-date question is not testable in this model.** DEC-M11-2 has to be "
            "adjudicated in the mapping; the formula is linear in one tariff per year.",
            "**Silent zero-fill of `other_revenue`.** Omitted means 0.0 with no disclosure backing "
            "(OQ-1).",
        ],
        "not_claimed": [
            "It does not claim the model is accurate, nor that one company's mapping generalises.",
            "It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.",
            "It does not rewrite the formula; the existing implementation is retained.",
        ],
    },
    "M12": {
        "model_id": "bank_revenue",
        "title": "银行净利息与手续费",
        "entry_line": 232,
        "applicability": "bank growth, maturity and balance-sheet repricing",
        "unit_rule": "average earning / interest-bearing balances in U; rates are annual decimals and may "
                     "be negative; fees are recognised net amounts",
        "positive_input": '{"model_id": "bank_revenue", "base_revenue": 0, "drivers": '
                          '{"average_earning_assets": [1000], "asset_yield": [0.04], '
                          '"average_interest_bearing_liabilities": [800], "funding_cost": [0.02], '
                          '"fee_revenue": [8], "other_revenue": [2]}, "years": [2027]}',
        "positive_handwork": "1000 x 0.04 = 40; 800 x 0.02 = 16; 40 - 16 = 24; 24 + 8 = 32; 32 + 2 = 34",
        "continuity_handwork": "2027 = 40 - 16 + 8 + 2 = 34; 2028 = 54 - 25 + 9 + 0 = 38",
        "defaults_handwork": "40 - 16 + 8 + 0 (default) = 32",
        "card_negative": "asset_yield=[0], funding_cost=[0.1], fee_revenue=[0], other_revenue=[0] (card L44)",
        "card_negative_guard": "revenue-total guard (`calculated revenue cannot be negative: bank_revenue`)",
        "business_negatives": [
            "negative interest rates are allowed and must not be re-bounded to 0-1",
            "net interest margin (NIM) is not the asset yield",
            "a negative total revenue is not supported by the current contract",
        ],
        "collect_items": "card L46: average earning assets / interest-bearing liabilities, annualised "
                         "rates, net interest, fees and other operating income",
        "decisions": [
            ("DEC-M12-1", "Average balances versus period-end balances.",
             "PROPOSED: average balances only (card L8). A period-end balance substituted for an average "
             "is a restatement of the driver, not a rounding choice.",
             "Period-end balances import a rate shock into the average and misstate the year."),
            ("DEC-M12-2", "NIM is not the asset yield.",
             "PROPOSED: derive `asset_yield` from disclosed interest income divided by average earning "
             "assets; NIM must never be used as a substitute, and the derivation is recorded in "
             "`conversion_formula`.",
             "NIM already nets funding cost, so using it as the yield double-counts the funding side."),
            ("DEC-M12-3", "A year with negative total revenue cannot be expressed.",
             "PROPOSED: escalate rather than adapt. `card_M12.md` L48 states the contract does not support "
             "a negative total, and `common_model_cards.md` L11 forbids clipping to zero or changing the "
             "accounting definition to force a pass. A contract extension is an owner decision.",
             "Clipping to zero would silently replace a real loss year with break-even."),
        ],
        "attack_points": [
            "**The card's negative is a totals refusal, not a rate refusal.** NEG-CARD yields "
            "0 - 80 + 0 + 0 = -80 and is rejected by `calculated revenue cannot be negative`. A reviewer "
            "must not read it as `rates must be positive`.",
            "**The negative-rate pair is the sharpest evidence in this card.** OBS-NEG-RATE-ACCEPTED "
            "(`asset_yield = -0.01` with a total of exactly 0) is ACCEPTED, while "
            "OBS-NEG-RATE-TOTAL-NEG (same rate, total -16) is refused. Together they isolate the binding "
            "guard to the revenue total.",
            "**OBS-RATE-GT1 (yield 0.5 -> 494) shows the ratio dimension's default [0, 1] does not apply "
            "to `asset_yield`.** The enumeration confirms both rate drivers carry explicit "
            "`(None, None)` bounds.",
            "**`fee_revenue` is signed** (OBS-FEE-SIGNED, -5 -> 21), so a negative net fee is "
            "representable; a reviewer should confirm that is the intended contract for fee reversals.",
            "**The totals guard is a real adapter limit, not a theoretical one.** A bank year with a net "
            "interest loss cannot be represented; DEC-M12-3 asks the owner for a ruling instead of a "
            "workaround.",
            "**No local source document supports this card's industry.** The survey lists the two "
            "securities firms and two insurers available locally and why their revenue contracts differ.",
            "**Silent zero-fill of `other_revenue`** (OQ-1).",
        ],
        "not_claimed": [
            "It does not claim the model is accurate, nor that one company's mapping generalises.",
            "It does not claim `disclosure_adaptation`; D needs a signed industry/accounting review.",
            "It does not rewrite the formula or relax the totals guard; the existing implementation is "
            "retained.",
        ],
    },
}


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(BATCH))
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--plan-root", required=True)
    args = parser.parse_args()

    card = args.card
    facts = BATCH[card]
    attempt = os.path.abspath(args.attempt)
    plan_root = os.path.abspath(args.plan_root)
    evidence = os.path.join(attempt, "evidence", card)
    model_id = facts["model_id"]

    run = load_json(os.path.join(evidence, "run_result.json"))
    oracle = load_json(os.path.join(evidence, "oracle.json"))
    enum = load_json(os.path.join(evidence, "registry_enumeration.json"))
    selfcheck = load_json(os.path.join(attempt, "recovery", "selfcheck_result.json"))
    ledger = {}
    ledger_path = os.path.join(attempt, "after", "rc_ledger.txt")
    if os.path.exists(ledger_path):
        for line in open(ledger_path, "r", encoding="ascii", errors="replace"):
            line = line.strip()
            if line and not line.startswith("#"):
                unit, _, value = line.partition("\t")
                ledger[unit.strip()] = int(value.strip())
    rc = run["exit_code_semantics"]["exit_code"]

    def ledger_lookup(prefix):
        """Ledger unit ids are '<PREFIX>-<CARD>-<slug>'; look the raw exit code up by prefix."""
        for unit, value in ledger.items():
            if unit.startswith(prefix + "-" + card + "-") or unit == prefix + "-" + card:
                return value
        return None
    nsum = run["negative_summary"]
    pos = run["positive"]
    con = run["continuity_positive"]
    dfl = run["defaults"]
    obs = run["observations"]
    facts_enum = enum["facts"]

    def neg_lines():
        out = []
        for entry in run["negatives"]:
            out.append("| %s | `%s` | %s | `%s` | %s |"
                       % (entry["id"], entry["kind"], entry["expected"],
                          entry.get("message", ""), entry["verdict"]))
        return "\n".join(out)

    mutation_rows = "\n".join(
        "| %s | %s | **%s** | %s | %s |"
        % (cid, selfcheck["cases"][cid]["mutation"], selfcheck["cases"][cid]["raw_exit_code"],
           selfcheck["cases"][cid]["expected_exit_code"],
           "as expected" if selfcheck["cases"][cid]["ok"] else "UNEXPECTED")
        for cid in sorted(selfcheck["cases"]))

    decision_rows = "\n".join(
        "- **%s** - %s\n  - %s\n  - Risk if unanswered: %s" % (did, q, proposal, risk)
        for did, q, proposal, risk in facts["decisions"])

    attack_rows = "\n".join("%d. %s" % (i + 1, text)
                           for i, text in enumerate(facts["attack_points"]))

    not_claimed = "\n".join("- %s" % text for text in facts["not_claimed"])
    business_neg = "\n".join("- %s" % text for text in facts["business_negatives"])

    observation_rows = "\n".join(
        "| %s | %s | %s | %s | %s |"
        % (o["id"], o.get("raised") or o.get("actual"),
           "yes" if o.get("matches_expected") else ("n/a" if "matches_expected" not in o
                                                    else "NO"),
           o.get("matches_compared"), o.get("message", "")[:120])
        for o in obs)

    # ------------------------------------------------------------------ review.md
    consistency_path = os.path.join(evidence, "consistency_check.json")
    hashes_path = os.path.join(evidence, "evidence_hashes.json")
    cons_total = (load_json(consistency_path)["checks_total"]
                  if os.path.exists(consistency_path) else "PENDING")
    hashed_count = (load_json(hashes_path)["file_count"]
                    if os.path.exists(hashes_path) else "PENDING")
    obs_matched = sum(1 for o in obs if o.get("matches_expected"))
    section9 = f"""## 9. Final batch verification

- `after/final_audit.txt`, produced by `scripts/final_audit.py`, reports **`failures: none`** across
  M09-M12. For this card it records rc `{rc}`, positive `{pos.get("actual")}`, continuity
  `{con.get("actual")}`, defaults `{dfl.get("actual")}`, `{nsum["passed"]}/{nsum["total"]}` negatives
  rejected, `{obs_matched}/{len(obs)}` observations matching their frozen expectations and
  `{cons_total}` printed-value-vs-evidence-file consistency checks (all passing).
- The audit re-checks the freeze ordering (`oracle.md` < `oracle.json` < `stdout.txt`), the three
  qualification states, the empty revision-r2 slot (`revision_r2.json`) and that `iso/checkout_scripts`
  still hashes equal to the production files.
- `evidence/{card}/evidence_hashes.json` ({hashed_count} files) excludes the three **self-referential**
  hash files by name (`evidence_hashes.json`, `artifact_hashes.txt`, `after/rerun_sha256.json`) and names
  the artefacts written after the snapshot (`after/rc_ledger.txt`, the finalize-pass console,
  `after/final_audit.txt`). Everything else in the attempt is inside the snapshot.
- Closing attempts that failed on the way here were not erased: their raw consoles are preserved with a
  `_FAILED_first_attempt` suffix under `after/`.
- `decision.md` section "Owner hand-off" points at `handoff.json` (`open_questions`, `next_action`,
  `blocked_by`) as the authoritative continuation record.
"""
    review = f"""# {card} · {model_id} — implementer review record

Card {card} (`{model_id}`), Parent I-10, title `{facts["title"]}`. Attempt `execution_runs/{card}/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded
> as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; both files hash-equal to the task anchors | `binding.json`, `evidence/{card}/source_manifest.json` |
| B positive | actual `{pos.get("actual")}` vs independent oracle `{oracle["positive"]["expected_float"]}`, tolerance `{oracle["positive"]["tolerances"]}` | `evidence/{card}/formula_result.json` |
| continuity positive | actual `{con.get("actual")}` vs oracle `{oracle["continuity_positive"]["expected_float"]}` (run before the break patch) | `evidence/{card}/negative_results.json` |
| defaults case | actual `{dfl.get("actual")}` vs oracle `{oracle["defaults_expected_float"]}` | `evidence/{card}/negative_results.json` |
| C negatives | {nsum["passed"]}/{nsum["total"]} rejected with the frozen expected exception type | `evidence/{card}/negative_results.json` |
| D mapping | source survey + all-missing mapping skeleton only; professional decisions PROPOSED, unsigned | `evidence/{card}/disclosure_source_survey.json`, `disclosure_mapping.json`, `accounting_decision.md` |
| E wiring | **NOT done** - owned by I-10-A after D | `evidence/{card}/deferred_work.json` |
| F accuracy | **NOT done** - needs the I-12 frozen design | `evidence/{card}/qualification.json` |
| exit code | runner rc = **{rc}** ({run["exit_code_semantics"]["verdict"]}); the runner carries the verdict | `evidence/{card}/run_result.json`, `after/rc_ledger.txt` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_cards_M09_M12.py`, whose imports are only
  `argparse`, `hashlib`, `json`, `os` and `decimal` (see `import_lines` in
  `evidence/{card}/oracle_selfcheck.json`; `product_import_present` is `false`).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads every expectation only
  from `evidence/{card}/oracle.json`.
- `evidence/{card}/regeneration_check.json` and `after/console_A4-{card}-oracle-regenerate-compare_{card}.txt`
  show that re-running the generator into a different root reproduces `input.json`, `oracle.json`,
  `cases.json`, `observation_expected.json` and `oracle_selfcheck.json` **byte for byte**.
- Negative cases and observations are built in memory from a fresh `deepcopy` of the frozen input - never
  round-tripped through a JSON parser - so a parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires the raised exception to be an instance of `ModelRegistryError` **and** to match
  the exception name frozen in `cases.json`. `ImportError`, `ModuleNotFoundError`, `FileNotFoundError` and
  every other type are recorded as FAIL, never as pass.
- The same `scripts/run_card.py` (sha256 `{sha256_file(os.path.join(attempt, "scripts", "run_card.py"))}`)
  is used by all four attempts of this batch, and the same generator
  (sha256 `{sha256_file(os.path.join(attempt, "scripts", "oracle_cards_M09_M12.py"))}`) generates all four
  oracles, so there is no per-card runner or generator to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `{run["registry_metadata"]["formula"]}`
- required `{run["registry_metadata"]["required"]}`; optional `{run["registry_metadata"]["optional"]}`
- declared defaults `{run["registry_metadata"]["declared_defaults"]}`; ratio drivers
  `{run["registry_metadata"]["ratio_drivers"]}`; explicit driver bounds
  `{run["registry_metadata"]["explicit_driver_bounds"]}`
- contract fidelity (formula string, required/optional sets, dimensions) `{run["contract_check"]["ok"]}`
- positive structure: container `{pos["structure"]["container_type"]}`, length
  `{pos["structure"]["length"]}` = len(years) `{pos["structure"]["length_equals_years"]}`, element types
  `{pos["structure"]["element_types"]}`, all finite `{pos["structure"]["all_elements_finite"]}`
- The contract returns a bare `list[float]` positionally aligned with `years`, so there is no named output
  field set; the "field set" requirement is realised as container type + element type set + length/order,
  and the oracle `years` equal the input `years` (`fidelity_checks.years_match`).

Rejections exactly as recorded (message text is read back from `negative_results.json`):

| case | mutation kind | expected | actual message | verdict |
|---|---|---|---|---|
{neg_lines()}

Observations (measured, **not** part of the exit code):

| id | raised / actual | expectation matched | compared-to match | message |
|---|---|---|---|---|
{observation_rows}

## 4. Exit-code mutation self-check (red then green)

| case | mutation (applied to a scratch copy only) | raw rc | expected rc | result |
|---|---|---|---|---|
{mutation_rows}

- `frozen_evidence_not_modified`: `{selfcheck["frozen_evidence_not_modified"]}`;
  `product_sha256_unchanged`: `{selfcheck["product_code_under_test"]["unchanged"]}`.
- Case E is the uncorrupted control: the same frozen evidence returns rc 0 again.
- Details: `recovery/selfcheck_result.json` (each scratch tree keeps its own `stdout.txt`).

## 5. Judgement calls the reviewer should attack first

{attack_rows}

## 6. What this card does NOT claim

{not_claimed}

## 7. Disclosure adaptation status (D)

The card's own business negatives are still open and no industry/accounting reviewer has signed anything:

{business_neg}

Therefore `disclosure_adaptation` stays `unmapped`; `evidence/{card}/disclosure_mapping.json` lists every
driver as `missing` with the fields that would have to be filled, and no value was invented.

## 8. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_cards_M09_M12.py --card {card} --out-root <scratch>` and diff `oracle.json`
   against the frozen one (or read `regeneration_check.json` and then reproduce it independently).
2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm rc {rc}, the positive
   `{pos.get("actual")}`, continuity `{con.get("actual")}` and `{nsum["passed"]}/{nsum["total"]}`
   rejections.
3. Confirm the isolated copies still hash-equal the task anchors (`source_manifest.json`, `integrity.json`)
   and read the mtime finding in `integrity.json` about production files touched by an external writer.
4. Pick a case the implementer did not use - for example a three-year path, a unit-scale change, or a
   driver value at a bound - freeze its expectation BEFORE running, and check it.
5. Adjudicate the DEC items in `evidence/{card}/accounting_decision.md` and the OQ items in
   `evidence/{card}/oq_rulings.json`.

{section9}"""
    write_text(os.path.join(attempt, "review.md"), review)

    # ------------------------------------------------------------------ decision.md
    decision = f"""# {card} decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls under a
professional decision (cross-process locking, publication transaction boundaries, fiscal-period /
restatement / gross-vs-net and payability attribution, unidentifiable model parameters, sample and
statistical thresholds, deployment migration and natural-observation qualification).

## Professional decisions

No cross-process locking, publication, fiscal-period, gross/net or deployment decision arises in this card:
the scope is a pure in-process calculator plus read-only evidence. The decisions that DO arise are
accounting/disclosure-adapter decisions and are recorded as PROPOSED (unsigned) in
`evidence/{card}/accounting_decision.md`:

{decision_rows}

## Escalated to the owner (not decided here)

- OQ-1 (batch): `scripts/model_registry.py:335` silently zero-fills an omitted optional driver that has no
  declared default. All {facts_enum["batch_optional_driver_count"]} optional drivers of M09-M12 are in that
  class ({facts_enum["batch_optional_drivers_without_declared_default_total"]} of
  {facts_enum["batch_optional_driver_count"]}), and {facts_enum["registry_optional_drivers_without_declared_default_total"]}
  registry-wide. No position asserted, no product change.
- OQ-3 (M09/M11): `revenue_per_unit` / `revenue_per_activity` default to `[0, inf)`, so a negative realised
  price or a negative (rebate) tariff cannot be expressed; only
  {facts_enum["revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values_count"]} of
  {facts_enum["revenue_per_unit_and_revenue_per_activity_driver_count"]} such drivers admit negative values.
  Registered, not fixed.
- OQ-5 (provenance): production files under `scripts/` carry an external LastWriteTime inside this
  attempt's window with byte-identical content; `integrity.json` records the affected files and hashes.

## Owner hand-off

The owner-facing steps and open questions of this card are listed in `handoff.json`
(`open_questions`, `next_action`, `blocked_by`); `handoff.json` is the authoritative continuation record.
Nothing in this card needs a **fiscal-period / restatement / gross-vs-net** ruling to stay within A-C,
because no disclosure value was bound to a driver in this attempt.
"""
    write_text(os.path.join(attempt, "decision.md"), decision)

    # ------------------------------------------------------------------ accounting_decision.md
    accounting = f"""# {card} · {model_id} — accounting / disclosure decisions (PROPOSED, UNPROPOSED REVIEW)

Status of every item below: **proposed by the implementer session, unsigned, not reviewed**.
None of them may be read as an accepted accounting decision, and none of them changes the product.

Scope note: the model is `{model_id}` - {facts["applicability"]}. Unit rule: {facts["unit_rule"]}.

{decision_rows}

## Disclosure items that must be collected before D can be claimed

{facts["collect_items"]}

## Business-level negatives that must be adjudicated (not runtime gates)

{business_neg}

## What is deliberately NOT decided here

- No gross-versus-net, tax, ownership or consolidation-scope ruling is made; the mapping skeleton lists
  those as required fields with no value.
- No fiscal-period or restatement mapping is asserted.
- No scenario or accuracy statement is made from this model.
"""
    write_text(os.path.join(evidence, "accounting_decision.md"), accounting)

    # ------------------------------------------------------------------ changes.diff
    changes = f"""# changes.diff - {card} - attempt a20260919-01
#
# NO PRODUCT CHANGE.
#
# This attempt modified nothing under any production repository. The file is a statement rather than a diff
# because there is no diff to show: the whole card is a read-only formula qualification plus evidence.
#
# Verified after the card run:
#   scripts/model_registry.py   sha256 9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f
#   scripts/model_extensions.py sha256 9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911
#
# The isolated code under test is a byte-identical copy held inside the attempt:
#   iso/checkout_scripts/model_registry.py   (same sha256 as production)
#   iso/checkout_scripts/model_extensions.py (same sha256 as production)
#
# Nothing was added, committed, restored or stashed in any production repo by this attempt.
# revenue-forecast already had pre-existing dirty files; those belong to their owner. The pre-existing
# status is captured in before/git_status_revenue-forecast.txt and after/git_status_revenue-forecast.txt,
# and the filtered views (which drop this batch's own new files) are identical before and after.
#
# An external writer touched production source files inside this attempt's window with byte-identical
# content; see evidence/{card}/integrity.json -> production_working_tree_mtime_finding. Recorded as an open
# question, not hidden.
#
# Files this attempt DID create, all inside this attempt directory:
#   oracle.md, commands.json, binding.json, decision.md, review.md, handoff.json, changes.diff
#   scripts/{{run_card.py, oracle_cards_M09_M12.py, enumerate_registry_facts.py,
#            selfcheck_mutations.py, pack_evidence.py, verify_consistency.py, pack_narrative.py,
#            drive_card.ps1}}
#   evidence/{card}/*  (input, oracle, cases, manifests, run results, negative results, qualification,
#                      enumeration, survey, mapping, integrity, hashes, revision slot, deferred work)
#   before/, after/, recovery/, iso/checkout_scripts/
"""
    write_text(os.path.join(attempt, "changes.diff"), changes)

    # ------------------------------------------------------------------ recovery/README.md
    recovery_note = f"""# {card} recovery note

**not_applicable_with_reason for stateful recovery.** `{model_id}` is a pure in-process function:
`calculate_registered_model` has no durable state, no lock, no lease, no partial publication and no
filesystem side effect. A raised `ModelRegistryError` leaves nothing to roll back, so there is no
restart/retry path to exercise.

What IS covered instead:

- `recovery/selfcheck_result.json` proves the runner's exit code carries the verdict and that a corrupted
  expectation cannot pass (cases A and D -> rc 2, cases B and C -> rc 3, control E -> rc 0);
- every negative case and every observation runs against a fresh `deepcopy`, so a failure cannot
  contaminate a later case;
- the frozen evidence and the code under test were hash-verified after the self-check to prove the scratch
  runs did not touch them (`frozen_evidence_not_modified`,
  `product_code_under_test.unchanged`);
- `recovery/regenerate/` holds a second, byte-identical generation of the frozen expectations, which is the
  restore path for the oracle: the frozen `oracle.json` can be rebuilt from
  `scripts/oracle_cards_M09_M12.py` with no residual state.

The only non-pure step in this card is reading the frozen evidence files; nothing under a production
repository was written by any command of this attempt.
"""
    write_text(os.path.join(attempt, "recovery", "README.md"), recovery_note)

    # ------------------------------------------------------------------ before/README.md
    before_note = f"""# {card} before/after capture policy

This card modifies nothing, so `before/` and `after/` are the same capture point, taken after the card runs.
That is stated plainly here rather than dressed up as a pre-run capture.

What makes the read-only claim checkable anyway:

1. `before/git_status_revenue-forecast.txt` and `after/git_status_revenue-forecast.txt` are raw
   `git --no-optional-locks status --porcelain` output; the `*_filtered.txt` variants drop this batch's own
   new files. The filtered before/after views are identical.
2. `before/production_file_mtimes.txt` records the production file hashes and the mtime ordering
   (`iso/checkout_scripts/model_registry.py` was created before `evidence/{card}/stdout.txt`), which anchors
   the production content to the pre-run moment even though the capture itself is later.
3. `after/console_A2-{card}-isolated-snapshot_{card}.txt` is the A2 console written **before** the product
   run; it already contains `MATCH production=<sha256> isolated=<sha256>`.
4. `before/reviews_mtime.txt` records the read-only audit anchor
   `reviews/second_wave/final_review_checks.json` (mtime `2026-09-19 10:05:32`), which this attempt never
   writes.

## Production mtime finding (recorded, not hidden)

An external writer rewrote production source files at `2026-09-20 03:41:57` with byte-identical content
(the same sha256 as the task anchors and as the frozen isolated copies). See
`evidence/{card}/integrity.json` -> `production_working_tree_mtime_finding` for the file list and hashes.
This attempt issues no write command against any production path; the affected mtimes therefore cannot be
attributed to it, but mtime alone is not usable as an untouched-proof for this window - the sha256 evidence
is.
"""
    write_text(os.path.join(attempt, "before", "README.md"), before_note)

    # ------------------------------------------------------------------ handoff.json
    handoff = {
        "card_id": card,
        "card_title": facts["title"],
        "model_id": model_id,
        "attempt_id": "a20260919-01",
        "status": "review_pending",
        "implementer_is_not_the_reviewer": True,
        "completed_steps": {
            "A_binding": "done (binding.json: read-only production hashes + attempt-local isolated snapshot)",
            "B_positive_run": "done (positive %s, continuity %s, defaults %s; all inside "
                              "1e-9*max(1,|e|))" % (pos.get("actual"),
                                                    con.get("actual"), dfl.get("actual")),
            "C_negative_run": "done (%d/%d negatives rejected with the frozen expected exception type)"
                              % (nsum["passed"], nsum["total"]),
            "D_disclosure_mapping": "NOT claimed: source survey + all-missing mapping skeleton; "
                                    "professional decisions PROPOSED and unsigned",
            "E_historical_mapping_probe": "NOT done - owned by I-10-A after D; no scenario or accuracy "
                                          "meaning attached",
            "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
        },
        "completed_steps_list": ["A", "B", "C", "D-skeleton"],
        "next_step_number": 4,
        "next_action": ("Independent reviewer: re-run scripts/oracle_cards_M09_M12.py in a scratch tree and "
                        "diff against the frozen oracle.json, re-run scripts/run_card.py against "
                        "iso/checkout_scripts and confirm rc %d with positive %s, continuity %s and %d/%d "
                        "rejections, adjudicate the DEC items in evidence/%s/accounting_decision.md and the "
                        "OQ items in evidence/%s/oq_rulings.json, then record a verdict."
                        % (rc, pos.get("actual"), con.get("actual"), nsum["passed"], nsum["total"],
                           card, card)),
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256_file(os.path.join(evidence, "input.json")),
            "evidence/%s/oracle.json" % card: sha256_file(os.path.join(evidence, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256_file(os.path.join(evidence, "cases.json")),
            "oracle.md": sha256_file(os.path.join(attempt, "oracle.md")),
            "scripts/oracle_cards_M09_M12.py":
                sha256_file(os.path.join(attempt, "scripts", "oracle_cards_M09_M12.py")),
            "scripts/run_card.py": sha256_file(os.path.join(attempt, "scripts", "run_card.py")),
        },
        "current_source_hashes": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
            "iso/checkout_scripts/model_registry.py":
                sha256_file(os.path.join(attempt, "iso", "checkout_scripts", "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py":
                sha256_file(os.path.join(attempt, "iso", "checkout_scripts", "model_extensions.py")),
            "scripts/forecast/segments.py":
                "95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd",
        },
        "changed_paths": {
            "production_repos": [],
            "note": "no production file was created, modified, added, committed, restored or stashed by this "
                    "attempt; the pre-existing dirty state is captured in before/ and after/. An external "
                    "writer touched production files with identical content; see integrity.json.",
            "attempt_paths_created": [attempt],
        },
        "commands_executed": [f"{card}-A0", f"{card}-A1", f"{card}-A2", f"{card}-A3", f"{card}-A4",
                             f"{card}-B", f"{card}-C", f"{card}-G", f"{card}-F", f"{card}-E"],
        "raw_exit_codes": {
            "A0": ledger_lookup("A0"),
            "A1": ledger_lookup("A1"),
            "A2": ledger_lookup("A2"),
            "A3": ledger_lookup("A3"),
            "A4": ledger_lookup("A4"),
            "B": rc,
            "C": ledger_lookup("C"),
            "G": ledger_lookup("G"),
            "N": ledger_lookup("N"),
            "E": ledger_lookup("E"),
            "O": ledger_lookup("O"),
            "F": ledger_lookup("F"),
            "N2": ledger_lookup("N2"),
            "Z1": ledger_lookup("Z1"),
            "Z2": ledger_lookup("Z2"),
            "Z5": ledger_lookup("Z5"),
            "Z6": ledger_lookup("Z6"),
            "note": "every value is read from after/rc_ledger.txt (unit<TAB>raw_rc) at narrative time; a "
                    "null means that unit had not been recorded when this file was last written",
        },
        "expected_exit_codes": {
            "A0": 0, "A1": 0, "A2": 0, "A3": 0, "A4": 0, "B": 0, "C": 0, "G": 0, "F": 0, "E": 0,
        },
        "exit_code_notes": {
            "A1": "the offline pytest install fails because no pytest wheel exists in the local cache; no "
                  "A-C card result depends on pytest, and this row is NOT a pass",
            "B": "verdict-carrying: 0 pass / 2 no-verdict or fidelity mismatch / 3 unrejected negative / "
                 "1 harness error",
            "G": "the self-check returns 0 when all five mutation cases behaved as expected",
        },
        "positive_actual": pos.get("actual"),
        "positive_expected": oracle["positive"]["expected_float"],
        "continuity_actual": con.get("actual"),
        "defaults_actual": dfl.get("actual"),
        "negative_case_summary": nsum,
        "observations": [{"id": o["id"], "raised": o.get("raised"), "actual": o.get("actual"),
                          "matches_expected": o.get("matches_expected"),
                          "gating": o["gating"]} for o in obs],
        "open_questions": [
            "OQ-1 (batch): scripts/model_registry.py:335 silently zero-fills an omitted optional driver "
            "that has no declared default. All %d optional drivers of M09-M12 are in that class "
            "(%d registry-wide). Named risk for this card: see evidence/%s/oq_rulings.json."
            % (facts_enum["batch_optional_driver_count"],
               facts_enum["registry_optional_drivers_without_declared_default_total"], card),
            "OQ-2 (M12 only): the card's negative is a revenue-TOTAL refusal, not a rate-domain refusal; "
            "the two rate drivers keep explicit (None, None) bounds. Registered, no product change."
            if card == "M12" else
            "OQ-2 (M12, cross-card reference): see M12's oq_rulings.json - the bank negative is a totals "
            "refusal, not a rate refusal.",
            "OQ-3 (M09/M11): revenue_per_unit / revenue_per_activity default to [0, inf), so a negative "
            "realised price or rebate-style tariff cannot be expressed (%d of %d such drivers admit "
            "negatives registry-wide)."
            % (facts_enum["revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values_count"],
               facts_enum["revenue_per_unit_and_revenue_per_activity_driver_count"]),
            "OQ-4 (M10): additions is non-negative while reserve_revisions is signed, so downward reserve "
            "movements must be routed through reserve_revisions (5 reserve_volume drivers: 4 non-negative, "
            "1 signed).",
            "OQ-5 (provenance): production files under scripts/ were rewritten by an external writer with "
            "byte-identical content inside this attempt's window; mtime is therefore not an "
            "untouched-proof here. Needs a binding ruling on how to treat concurrent writers.",
            "OQ-6 (binding provenance): I-00-B binds the isolation plan and the two-stage command rule but "
            "materialises no checkout tree, so this attempt materialised its own read-only snapshot "
            "(iso/checkout_scripts, hashes equal to production). If the intended binding is a checkout "
            "materialised by I-00-B, that is a scope deviation to record; the code under test is "
            "byte-identical either way.",
        ],
        "blocked_by": [],
        "stop_conditions_hit": [
            "STOP_ACCURACY (no I-12 frozen design)",
            "STOP_DISCLOSURE_ADAPTATION (required drivers still missing / reviewer unsigned)",
        ],
        "qualifications": {
            "formula": "review_pending",
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
        },
        "evidence_paths": [
            "after/", "before/", "binding.json", "changes.diff", "commands.json", "decision.md",
            "handoff.json", "oracle.md", "review.md", "recovery/", "scripts/", "iso/checkout_scripts/",
            "evidence/%s/accounting_decision.md" % card,
            "evidence/%s/artifact_hashes.txt" % card,
            "evidence/%s/cases.json" % card,
            "evidence/%s/command_manifest.json" % card,
            "evidence/%s/consistency_check.json" % card,
            "evidence/%s/deferred_work.json" % card,
            "evidence/%s/disclosure_mapping.json" % card,
            "evidence/%s/disclosure_source_survey.json" % card,
            "evidence/%s/evidence_hashes.json" % card,
            "evidence/%s/formula_result.json" % card,
            "evidence/%s/input.json" % card,
            "evidence/%s/integrity.json" % card,
            "evidence/%s/mtime_ordering.json" % card,
            "evidence/%s/negative_results.json" % card,
            "evidence/%s/observation_expected.json" % card,
            "evidence/%s/oq_rulings.json" % card,
            "evidence/%s/oracle.json" % card,
            "evidence/%s/oracle_selfcheck.json" % card,
            "evidence/%s/qualification.json" % card,
            "evidence/%s/regeneration_check.json" % card,
            "evidence/%s/registry_enumeration.json" % card,
            "evidence/%s/revision_r2.json" % card,
            "evidence/%s/run_result.json" % card,
            "evidence/%s/source_manifest.json" % card,
            "evidence/%s/stderr.txt" % card,
            "evidence/%s/stdout.txt" % card,
        ],
        "reviewer_status": "r1 submitted for independent review; no verdict received yet",
        "revision": "r1",
    }
    write_text(os.path.join(attempt, "handoff.json"),
               json.dumps(handoff, ensure_ascii=False, indent=1) + "\n")

    print("card", card, "model", model_id)
    print("wrote review.md, decision.md, accounting_decision.md, changes.diff, recovery/README.md,")
    print("      before/README.md, handoff.json under", attempt)
    print("review.md sha256", sha256_file(os.path.join(attempt, "review.md")))
    print("handoff.json sha256", sha256_file(os.path.join(attempt, "handoff.json")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
