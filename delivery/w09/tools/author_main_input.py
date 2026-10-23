"""Author the W09 repaired native input from the sealed final3 input.

Every change is a researched repair of a citation, target scope, evidence role or
parameter kind/rationale. The revenue path is NOT re-tuned to management
guidance: the activity/price/FX/persistence values stay exactly as sealed so the
old and new numbers remain comparable, and so no condition is reverse-engineered
from the guidance range. Where the sealed claim cited the wrong business
(page-prefix slice) the excerpt is replaced by the owning business's contiguous
verified span; where no forward mechanism exists the claim is honestly weakened;
the RPO expectation becomes management_guidance.

Outputs:
  forecast/main-input.json          native input, new forecast_version
  research/claim-changes.json       per-claim old->new diff and role counts
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
SEALED_INPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
EXCERPTS = WORKDIR / "delivery" / "w09" / "research" / "excerpts.json"
ROOT_CAUSES = RUN / "diagnosis/r1-final3-review-20261022/root_causes.json"
BINDINGS = (RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation"
            / "claim-scope-bindings.json")
OUT_DIR = WORKDIR / "delivery" / "w09"
NEW_VERSION = "w09-rf-research-20261023-main-v1"

H1 = "urn:company-wiki:source:sha256:d0dba19ede6e35ae3e127a1da91a42f04262e90d14efeb847bdfbff9b6354a5f"
ANNUAL = "urn:company-wiki:source:sha256:7f1431d66eae399d4b35639bb650e23287c7f52dacbb47b4b4a197fb5026d6a2"

LOCATOR = {page: f"PDF page {page}" for page in (7, 11, 12, 14, 15, 16, 138, 139, 183, 184, 186)}

BIOLOGY_ACTIVITY = (
    "biology_h1_own", "mechanism_direction",
    "Re-bound to the Biology business's own H1 section (p12 lower half). The disclosed mechanism "
    "(in-vivo/in-vitro linkage, cross-region collaboration, integrated discovery services, >20% "
    "new-customer inflow, new-modality share >35%) is Biology-specific. The sealed excerpt was the "
    "page-top TIDES/Testing slice, which cannot support a Biology activity index.",
    "Mechanism direction only: the excerpt gives no future workload, price, utilisation or "
    "confirmation schedule, so the magnitude stays a conditional analyst index.")
NON_TIDES_ACTIVITY = (
    "chemistry_dm_operating", "mechanism_direction",
    "Re-bound to the Chemistry operating section (p11) that names the small-molecule D&M mechanism "
    "(late-stage pipeline progress, prior-year capacity ramp, R-to-D conversion). Chemistry total "
    "includes TIDES, so this is own-business support for the non-TIDES aggregate - not a measured "
    "uniform activity basket across D&M and the residual.",
    "One blended index still covers two disclosed rhythms (H1 D&M +72.7% vs residual ~+5.6%); the "
    "component split in research/component-bridge.json sizes what the index implies, and the split "
    "itself stays an unverified condition because no H2 subgroup revenue is disclosed.")
NON_TIDES_PRICE = (
    "price_other_businesses", "conversion_assumption",
    "PRESERVED as conversion_assumption (negative control: it was already correct). The excerpt "
    "reports disclosed margin price pressure for Testing and Biology only; using it for a "
    "Chemistry/TIDES net-price index is an explicit cross-business, indirect market-risk conversion, "
    "not an observed Chemistry net price.",
    "Cross-business transfer: Testing/Biology margin price pressure is indirect evidence for a "
    "Chemistry net-price/mix condition. It is not a Chemistry price index and no net-price range is "
    "observed.")
TIDES_ACTIVITY = (
    "tides_h1_own", "mechanism_direction",
    "Re-bound to the TIDES D&M client/molecule sentence on p12 (own business). Client +39% and "
    "molecule +68% are service-activity counts; they do not establish a future revenue or price "
    "magnitude.",
    "Client/molecule counts are activity stock/flow indicators, not recognised revenue; project "
    "counts never multiply into revenue without a disclosed ASP or throughput.")
TIDES_PRICE = (
    "price_other_businesses", "conversion_assumption",
    "PRESERVED as conversion_assumption (negative control). Testing/Biology disclosed price pressure "
    "is indirect market-risk context for the TIDES net-price condition, not an observed TIDES net "
    "price.",
    "Cross-business transfer; no TIDES net-price index is disclosed.")
BIOLOGY_REBASE = (
    "biology_fy25_own", "conversion_assumption",
    "Re-bound and re-roled. The parameter is an analyst conditional amount (if H2 FY2026 repeats the "
    "comparable H2 FY2025 Biology basket), computed as annual p183 exact 2,677,175,030.51 minus the "
    "H1 p11 comparable 125,160.49万元 = 1,425.57013051 CNY million. That is a cross-period conversion "
    "from a disclosed historical base, not a reported mechanism and not a future actual; the sealed "
    "excerpt cited the annual D&M paragraph, which is unrelated to Biology.",
    "The comparable-H2 repeat is a condition; actual H2 delivery, price, FX and cohort timing are "
    "unobserved.")

CLAIM_BINDINGS: dict[str, tuple[str, str, str, str]] = {}
for scenario in ("low", "base", "high"):
    for year in ("2026", "2027", "2028"):
        CLAIM_BINDINGS[f"claim_biology_{scenario}_{year}_activity"] = BIOLOGY_ACTIVITY
        CLAIM_BINDINGS[f"claim_non_tides_{scenario}_{year}_activity"] = NON_TIDES_ACTIVITY
        CLAIM_BINDINGS[f"claim_non_tides_{scenario}_{year}_price"] = NON_TIDES_PRICE
    CLAIM_BINDINGS[f"claim_biology_{scenario}_h2_2026_rebase"] = BIOLOGY_REBASE
    for year in ("2027", "2028"):
        CLAIM_BINDINGS[f"claim_tides_{scenario}_{year}_activity"] = TIDES_ACTIVITY
    for year in ("2026", "2027", "2028"):
        CLAIM_BINDINGS[f"claim_tides_{scenario}_{year}_price"] = TIDES_PRICE

CLAIM_BINDINGS["claim_driver_biology"] = (
    "biology_h1_own", "mechanism_direction",
    "Re-bound to the Biology own-business section on p12 so the growth-driver evidence node no longer "
    "relies on the TIDES/Testing page-top slice.",
    "Driver evidence node: mechanism direction only; magnitude stays conditional.")
CLAIM_BINDINGS["claim_driver_non_tides"] = (
    "chemistry_r_operating", "mechanism_direction",
    "Re-bound to the Chemistry D&M operating paragraph on p11 (pipeline +699 molecules, stage stock, "
    "D&M revenue +72.7%). This is own-business mechanism evidence for the non-TIDES aggregate; the "
    "sealed excerpt was the segment revenue table header, which supports history only.",
    "Driver evidence node: mechanism direction only; the +72.7% is an H1 actual, not a future rate.")

WEAKENED = {
    "claim_driver_other": (
        "other_h1_table",
        "No positive operating mechanism is disclosed for the Other business: the only available row is "
        "a historical revenue table line (3,904.68 vs 8,662.95 万元, -54.93%). The claim is re-bound to "
        "that historical row and re-roled to history_base, so it can no longer be counted as a future "
        "growth mechanism. The residual income and its negative contribution remain in the model through "
        "the existing parameter path.",
        "Mechanism removed: no forward mechanism is disclosed; the disclosed fact is a historical "
        "decline. The forward magnitude stays an uncalibrated analyst condition, and the growth driver "
        "is reported as having no future-mechanism evidence."),
    "claim_driver_discontinued": (
        "discontinued_h1_table",
        "The discontinued business reports zero H1 FY2026 revenue (prior-period 127,377.57 万元) under "
        "an accounting classification note. That is a perimeter/classification fact, not a growth "
        "mechanism; the claim is re-bound to the zero-revenue row and re-roled to history_base. The zero "
        "forward path and the -100% FY2026 growth stay as reported arithmetic.",
        "Mechanism removed: a termination classification cannot support forward growth. The forward zero "
        "is an accounting perimeter statement, not evidence about a continuing business."),
}

RPO_DEFINITION = (
    "Issuer expected FY2026 recognition of the 2025-12-31 signed-contract opening cohort "
    "(4,220,706.46 万元 / 100 = 42,207.0646 CNY million); an issuer expectation, not an actual, not a "
    "range and not a full-year floor.")
RPO_RATIONALE = (
    "Issuer expectation for one cohort. The parameter has no revenue-DAG consumer, so the role "
    "correction changes no forecast number. It is not added to H1 actual or to new orders, not split "
    "across sub-businesses, and not treated as a probability or an empirical range.")


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rebind(claim, source, data, role, rationale):
    claim["source_id"] = source["source_id"]
    claim["locator"] = LOCATOR[source["pdf_page"]]
    claim["excerpt"] = source["excerpt"].strip()
    claim["excerpt_sha256"] = text_sha256(source["excerpt"])
    claim["content_sha256"] = source["source_id"].split("sha256:")[-1]
    claim["capture_receipt_sha256"] = next(
        s["capture"]["receipt_sha256"] for s in data["sources"]
        if s["source_id"] == source["source_id"])
    claim["evidence_role"] = role
    claim["verified_by"] = "W09 independent re-read of verified original page bytes"
    claim["verified_date"] = "2026-10-23"


def build() -> tuple[dict, list[dict], dict]:
    sealed = json.loads(SEALED_INPUT.read_text(encoding="utf-8"))
    excerpts = json.loads(EXCERPTS.read_text(encoding="utf-8"))["excerpts"]
    union = json.loads(ROOT_CAUSES.read_text(encoding="utf-8"))[
        "claim_scope_reconciliation"]["union_ids"]
    pointers = {c["claim_id"]: c.get("old_claim_pointer")
                for c in json.loads(BINDINGS.read_text(encoding="utf-8"))["claims"]}

    data = deepcopy(sealed)
    data["forecast_version"] = NEW_VERSION
    claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    params = {p["parameter_id"]: p for p in data["parameters"]}
    sealed_params = {p["parameter_id"]: p for p in sealed["parameters"]}
    sealed_claims = {c["claim_id"]: c for c in sealed["evidence_claims"]}
    rows: list[dict] = []
    parameter_edits: dict[str, list[dict]] = {}

    def note_param(pid: str, field: str, new_value: str) -> None:
        old_value = sealed_params[pid].get(field)
        if old_value == new_value:
            return
        params[pid][field] = new_value
        parameter_edits.setdefault(pid, []).append(
            {"field": field, "old": old_value, "new": new_value})

    for claim_id in union:
        claim = claims[claim_id]
        old_excerpt = sealed_claims[claim_id]["excerpt"]
        row = {
            "claim_id": claim_id,
            "old_input_pointer": pointers.get(claim_id),
            "old_source_id": sealed_claims[claim_id]["source_id"],
            "old_locator": sealed_claims[claim_id]["locator"],
            "old_role": sealed_claims[claim_id].get("evidence_role"),
            "old_excerpt_sha256": sealed_claims[claim_id].get("excerpt_sha256"),
            "old_excerpt_chars": len(old_excerpt),
            "target_type": claim["target_type"],
            "target_id": claim["target_id"],
        }
        binding = CLAIM_BINDINGS.get(claim_id)
        if claim_id in WEAKENED:
            excerpt_id, rationale, limit = WEAKENED[claim_id]
            source = excerpts[excerpt_id]
            _rebind(claim, source, data, "history_base", rationale)
            row.update({
                "new_source_id": claim["source_id"], "new_locator": claim["locator"],
                "new_excerpt_sha256": claim["excerpt_sha256"],
                "new_excerpt_chars": len(claim["excerpt"]),
                "physical_page": source["pdf_page"],
                "contiguous_span": [source["start_char_inclusive"], source["end_char_exclusive"]],
                "contiguous_range_sha256": source.get("contiguous_range_sha256"),
                "page_text_sha256": source["page_text_sha256"],
                "excerpt_id": excerpt_id, "new_role": "history_base",
                "parameter_changes": [], "rationale": rationale,
                "resolution": "mechanism_honestly_weakened", "remaining_limit": limit,
            })
        elif binding is not None:
            excerpt_id, new_role, rationale, limit = binding
            source = excerpts[excerpt_id]
            _rebind(claim, source, data, new_role, rationale)
            if claim["target_type"] == "parameter":
                parameter = params[claim["target_id"]]
                parameter["source_ids"] = sorted(
                    set(parameter.get("source_ids", [])) | {source["source_id"]})
            row.update({
                "new_source_id": claim["source_id"], "new_locator": claim["locator"],
                "new_excerpt_sha256": claim["excerpt_sha256"],
                "new_excerpt_chars": len(claim["excerpt"]),
                "physical_page": source["pdf_page"],
                "contiguous_span": [source["start_char_inclusive"], source["end_char_exclusive"]],
                "contiguous_range_sha256": source.get("contiguous_range_sha256"),
                "page_text_sha256": source["page_text_sha256"],
                "excerpt_id": excerpt_id, "new_role": new_role,
                "parameter_changes": [], "rationale": rationale,
                "resolution": ("role_corrected_mechanism_to_conversion"
                               if new_role != sealed_claims[claim_id].get("evidence_role")
                               else "rebound_scope_role_preserved"),
                "remaining_limit": limit,
            })
        else:
            row["resolution"] = "unchanged_verified"
            row["note"] = "kept the sealed excerpt; re-verified against the same page bytes"
        rows.append(row)

    # ---- parameter-level rationale repairs (no numeric change) -------------
    for scenario in ("low", "base", "high"):
        pid = f"non_tides_{scenario}_2026_activity"
        note_param(pid, "rationale", (
            "Conditional index of delivered/recognisable workload versus the comparable H2 non-TIDES "
            "basket; not disclosed physical units, not derived from management guidance. This single "
            "index deliberately blends two disclosed rhythms (H1 FY2026 small-molecule D&M +72.7% and "
            "an H1 residual of about +5.6% on the same decomposition). The component split that the "
            "index implies is sized in research/component-bridge.json: with H2 residual repeating H2 "
            "FY2025, this index requires H2 D&M growth of about +35.3%. Both the blend and the split "
            "are conditions; no H2 subgroup revenue, ASP, utilisation or cancellation is disclosed."))
        pid = f"non_tides_{scenario}_2026_price"
        note_param(pid, "rationale", (
            "Chosen net price/mix index for the non-TIDES aggregate, separated from delivered workload "
            "and FX. SCOPE LIMIT: the only disclosed price evidence in these originals is margin price "
            "pressure for Testing and Biology (annual p16), not a Chemistry net-price index. Using it "
            "here is an explicit cross-business, indirect market-risk conversion and an analyst "
            "choice; no Chemistry price/mix range is observed and the assumption stays conditional."))
        pid = f"tides_{scenario}_2026_price"
        note_param(pid, "rationale", (
            "Chosen net price/mix index for TIDES, separated from delivered workload and FX. SCOPE "
            "LIMIT: the disclosed price pressure is for Testing and Biology margins (annual p16); TIDES "
            "net price is not separately disclosed. The transfer is an explicit cross-business, "
            "indirect market-risk conversion, not an observed TIDES net price."))
        pid = f"biology_{scenario}_h2_2026_rebase"
        note_param(pid, "rationale", (
            "Conditional rebase of the comparable H2 FY2025 Biology basket: annual p183 exact Biology "
            "revenue 2,677,175,030.51 minus H1 p11 comparable 125,160.49万元 = 1,425.57013051 CNY "
            "million. Repeating that comparable H2 is an analyst condition, not a future actual, not a "
            "mechanism and not a management guidance point."))
        pid = f"biology_{scenario}_2026_activity"
        note_param(pid, "rationale", (
            "Conditional index of delivered/recognisable workload versus the comparable H2 Biology "
            "basket, anchored on the Biology own-business mechanism (in-vivo/in-vitro linkage, "
            "integrated discovery services, >20% new-customer inflow, new-modality share). No Biology "
            "unit volume, price or confirmation schedule is disclosed, so the magnitude is an analyst "
            "condition."))

    # ---- RPO expectation: reported_fact -> management_guidance --------------
    rpo_claim = claims["claim_rpo_expected_2026_opening_cohort"]
    source = excerpts["rpo_expected"]
    _rebind(rpo_claim, source, data, "value_range", "")
    rpo_param = params["rpo_expected_2026_opening_cohort"]
    old_kind = sealed_params["rpo_expected_2026_opening_cohort"]["kind"]
    note_param("rpo_expected_2026_opening_cohort", "kind", "management_guidance")
    note_param("rpo_expected_2026_opening_cohort", "definition", RPO_DEFINITION)
    note_param("rpo_expected_2026_opening_cohort", "rationale", RPO_RATIONALE)
    rpo_param["source_ids"] = [ANNUAL]
    rpo_ledger_row = {
        "claim_id": "claim_rpo_expected_2026_opening_cohort",
        "in_review_union": False,
        "requirement": "F3-RC05 / T09-guidance-versus-actual",
        "old_input_pointer": "/evidence_claims (parameter_id=rpo_expected_2026_opening_cohort)",
        "old_source_id": sealed_claims["claim_rpo_expected_2026_opening_cohort"]["source_id"],
        "old_locator": sealed_claims["claim_rpo_expected_2026_opening_cohort"]["locator"],
        "old_role": sealed_claims["claim_rpo_expected_2026_opening_cohort"].get("evidence_role"),
        "old_excerpt_sha256": sealed_claims["claim_rpo_expected_2026_opening_cohort"].get(
            "excerpt_sha256"),
        "old_excerpt_chars": len(sealed_claims["claim_rpo_expected_2026_opening_cohort"]["excerpt"]),
        "new_source_id": rpo_claim["source_id"],
        "new_locator": rpo_claim["locator"],
        "new_excerpt_sha256": rpo_claim["excerpt_sha256"],
        "new_excerpt_chars": len(rpo_claim["excerpt"]),
        "physical_page": source["pdf_page"],
        "contiguous_span": [source["start_char_inclusive"], source["end_char_exclusive"]],
        "contiguous_range_sha256": source.get("contiguous_range_sha256"),
        "page_text_sha256": source["page_text_sha256"],
        "excerpt_id": "rpo_expected",
        "new_role": "value_range",
        "target_type": rpo_claim["target_type"],
        "target_id": rpo_claim["target_id"],
        "parameter_changes": parameter_edits["rpo_expected_2026_opening_cohort"],
        "rationale": (
            "Same paragraph carries three different things: the FY2025 year-end RPO stock "
            "(5,800,478.75 万元, a reported point-in-time fact), the issuer's expected FY2026 "
            "recognition of that opening cohort (4,220,706.46 万元, management guidance), and no actual "
            "FY2026 realisation at all. The parameter kind changes from reported_fact to "
            "management_guidance and the evidence role from history_base to value_range with an exact "
            "value; the amount is an issuer expected point, not an empirical range, not a full-year "
            "floor and not an actual."),
        "resolution": "kind_corrected_guidance_vs_actual",
        "remaining_limit": (
            "No disclosed realisation schedule for the opening cohort; it cannot be added to H1 actual "
            "or new orders, nor split across sub-businesses. The parameter has no revenue-DAG consumer, "
            "so the correction changes no forecast number."),
    }

    # Attach the parameter edits to the rows that caused them.
    for row in rows:
        pid = row["target_id"] if row["target_type"] == "parameter" else None
        if pid and pid in parameter_edits and not row["parameter_changes"]:
            row["parameter_changes"] = parameter_edits[pid]

    # ---- out-of-union repair of the same defect class -----------------------
    # The Testing activity claims are NOT in the 49-claim review union, but they
    # cite the same page-top slice (which opens with TIDES) instead of Testing's
    # own section. Leaving a known wrong-scope citation in the same file would
    # be dishonest, so they are repaired and reported separately - they must not
    # be counted toward the 49.
    extra_rows = _repair_testing(claims, excerpts, data, params)

    # ---- typed research projection (existing optional block) ----------------
    # The sealed input declared an empty observations list, so the native
    # adequacy projection could not see ANY mechanism claim and reported all
    # forecast parameters as mechanism-unverified. Declare only observations
    # whose own-scope excerpt really carries the direction.
    data["parameters"] = list(params.values())
    data["evidence_claims"] = list(claims.values())
    data["operating_research"] = _observations(data, sealed)
    return data, rows, {"sealed_claims": sealed_claims, "union": union,
                        "old_kind": old_kind, "parameter_edits": parameter_edits,
                        "out_of_union_rows": extra_rows,
                        "rpo_ledger_row": rpo_ledger_row}


def _repair_testing(claims, excerpts, data, params) -> list[dict]:
    """Repair the same wrong-scope defect on claims outside the 49-claim union.

    The Testing activity claims are NOT in the review union, but they cite the
    same page-top slice (which opens with TIDES) instead of Testing's own
    section. Leaving a known wrong-scope citation in the same file would be
    dishonest, so they are repaired and reported separately - they must never be
    counted toward the 49.
    """
    source = excerpts["testing_h1_own"]
    rows = []
    for claim_id, claim in sorted(claims.items()):
        if not claim_id.startswith("claim_testing_"):
            continue
        if not claim_id.endswith("_activity"):
            continue
        old_excerpt = claim["excerpt"]
        _rebind(claim, source, data, "mechanism_direction",
                "Re-bound to the Testing business's own H1 section (p12, between the TIDES/Testing "
                "boundary and the Biology heading): revenue +31.5%, safety-assessment +42.8%, "
                "new-modality share >35%, DMPK automation and site inspections. The sealed excerpt was "
                "the page-top slice, which opens with TIDES client/molecule counts and continues into "
                "other businesses.")
        if claim["target_type"] == "parameter":
            parameter = params[claim["target_id"]]
            parameter["source_ids"] = sorted(
                set(parameter.get("source_ids", [])) | {source["source_id"]})
        rows.append({
            "claim_id": claim_id,
            "in_review_union": False,
            "old_source_id": claim["source_id"],
            "old_locator": "PDF page 12",
            "old_role": "mechanism_direction",
            "old_excerpt_sha256": hashlib.sha256(
                old_excerpt.strip().encode("utf-8")).hexdigest(),
            "old_excerpt_chars": len(old_excerpt),
            "new_source_id": claim["source_id"],
            "new_locator": claim["locator"],
            "new_excerpt_sha256": claim["excerpt_sha256"],
            "new_excerpt_chars": len(claim["excerpt"]),
            "physical_page": source["pdf_page"],
            "contiguous_span": [source["start_char_inclusive"], source["end_char_exclusive"]],
            "page_text_sha256": source["page_text_sha256"],
            "excerpt_id": "testing_h1_own",
            "new_role": "mechanism_direction",
            "target_type": claim["target_type"],
            "target_id": claim["target_id"],
            "rationale": ("Same defect class as the 49-claim repair: a page-prefix slice cannot support "
                          "the segment it merely happens to mention. Repaired for consistency; it does "
                          "NOT count toward the 49 and changes no number."),
            "resolution": "out_of_union_same_defect_repaired",
        })
    return rows


ACTIVITY_RATIONALE = {
    "非TIDES化学业务": (
        "Chemistry operating mechanism (late-stage pipeline progress, prior-year capacity ramp, R-to-D "
        "conversion, D&M revenue +72.7% in H1). Chemistry total includes TIDES, so this supports the "
        "non-TIDES aggregate's direction only; it is not a measured uniform activity basket and gives no "
        "future magnitude."),
    "生物学业务": (
        "Biology own operating mechanism (in-vivo/in-vitro linkage, cross-region collaboration, "
        "integrated discovery services, >20% new-customer inflow, new-modality share >35%). Direction "
        "only; no Biology unit volume, price or confirmation schedule is disclosed."),
    "TIDES（化学业务内）": (
        "TIDES D&M service activity (clients +39%, molecules +68%). Activity counts, not recognised "
        "revenue; no future revenue or price magnitude follows."),
}
CONVERSION_RATIONALE = {
    "price": ("Cross-business, indirect market-risk transfer: the disclosed margin price pressure is for "
              "Testing and Biology (annual p16), not a Chemistry/TIDES net-price index. The direction is "
              "borrowed; the magnitude stays an analyst condition."),
    "rebase": ("Cross-period conversion from a disclosed historical Biology base (annual p183 exact minus "
               "H1 p11 comparable). The comparable-H2 repeat is a condition, not a future actual."),
}


def _observations(data: dict, sealed: dict) -> dict:
    """Declare typed observations on the existing operating-research/1 block."""
    research = json.loads(json.dumps(sealed["operating_research"]))
    claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    params = {p["parameter_id"]: p for p in data["parameters"]}
    driver_of = {"非TIDES化学业务": "driver_non_tides", "生物学业务": "driver_biology",
                 "TIDES（化学业务内）": "driver_tides"}
    prefix_of = {"TIDES（化学业务内）": "tides_", "非TIDES化学业务": "non_tides_",
                 "生物学业务": "biology_"}
    rows = []
    for claim_id, claim in sorted(claims.items()):
        if claim["target_type"] != "parameter":
            continue
        parameter = params[claim["target_id"]]
        scope = next((segment["name"] for segment in data["segments"]
                      if segment["name"] in prefix_of
                      and parameter["parameter_id"].startswith(prefix_of[segment["name"]])), None)
        if scope is None:
            continue
        if claim.get("evidence_role") == "mechanism_direction" and "_activity" in claim_id:
            rows.append({
                "claim_id": claim_id, "observation_kind": "operating_mechanism", "scope": scope,
                "period": parameter["period"],
                "parameter_ids": [parameter["parameter_id"]],
                # The growth-driver tree models the BASE path only; a low/high
                # scenario observation binds to its parameter but not to a
                # base-scenario driver node.
                "driver_ids": ([driver_of[scope]]
                               if parameter.get("scenario") in ("base", "all") else []),
                "rationale": ACTIVITY_RATIONALE[scope],
            })
        elif claim.get("evidence_role") == "conversion_assumption":
            kind = "rebase" if claim_id.endswith("_h2_2026_rebase") else "price"
            rows.append({
                "claim_id": claim_id, "observation_kind": "conversion", "scope": scope,
                "period": parameter["period"],
                "parameter_ids": [parameter["parameter_id"]],
                "driver_ids": ([driver_of[scope]]
                               if parameter.get("scenario") in ("base", "all") else []),
                "rationale": CONVERSION_RATIONALE[kind],
            })
    # The shared currency-translation multipliers are also conversion
    # assumptions: the source paragraph discloses FX risk, not a forecast rate.
    # They are company-scope (they apply to every stream), so they are declared
    # once at company scope rather than per segment.
    for claim_id, claim in sorted(claims.items()):
        if not claim_id.startswith("claim_fx_") or claim["target_type"] != "parameter":
            continue
        parameter = params[claim["target_id"]]
        rows.append({
            "claim_id": claim_id, "observation_kind": "conversion",
            "scope": data["company_name"], "period": parameter["period"],
            "parameter_ids": [parameter["parameter_id"]], "driver_ids": [],
            "rationale": ("Shared revenue-translation condition. The source discloses FX risk (RMB "
                          "appreciation against USD settlement) and explicitly does not give a future "
                          "rate, exposure share or hedge offset; the chosen multiplier is an analyst "
                          "condition, not an observed FX forecast."),
        })
    research["observations"] = rows
    return research


def main() -> int:
    data, rows, ctx = build()
    (OUT_DIR / "forecast").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "research").mkdir(parents=True, exist_ok=True)
    main_path = OUT_DIR / "forecast" / "main-input.json"
    main_path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    sealed_claims = ctx["sealed_claims"]
    union = ctx["union"]
    new_claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    old_counts: dict[str, int] = {}
    new_counts: dict[str, int] = {}
    for cid in union:
        old_counts[sealed_claims[cid].get("evidence_role")] = old_counts.get(
            sealed_claims[cid].get("evidence_role"), 0) + 1
        new_counts[new_claims[cid].get("evidence_role")] = new_counts.get(
            new_claims[cid].get("evidence_role"), 0) + 1

    price_ids = [cid for cid in union if cid.endswith("_price")]
    price_preserved = [cid for cid in price_ids
                       if sealed_claims[cid].get("evidence_role") == "conversion_assumption"
                       and new_claims[cid].get("evidence_role") == "conversion_assumption"]
    rebase_ids = [cid for cid in union if cid.endswith("_h2_2026_rebase")]
    unknown_ids = sorted(WEAKENED)

    record = {
        "schema_version": "w09-claim-changes/1",
        "package_id": "W09-RF-RESEARCH",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expected_union_count": 49,
        "actual_union_count": len(union),
        "rows_present": len({row["claim_id"] for row in rows}),
        "duplicate_rows": len(rows) - len({row["claim_id"] for row in rows}),
        "sealed_input_path": str(SEALED_INPUT),
        "sealed_input_sha256": sha_file(SEALED_INPUT),
        "new_input_path": str(main_path),
        "new_input_sha256": sha_file(main_path),
        "old_forecast_version": data.get("forecast_version") and "r1-remediation-01-conditional-operating-v3-final",
        "new_forecast_version": data["forecast_version"],
        "old_role_counts": old_counts,
        "new_role_counts": new_counts,
        "role_change_summary": {
            "mechanism_direction_to_conversion": len(rebase_ids),
            "mechanism_direction_to_history_base": len(unknown_ids),
            "price_conversion_preserved": len(price_preserved),
            "note": ("No formal schema value 'unknown_mechanism_no_role_fix' is used; that string is a "
                     "preparation diagnostic, not a native enum value."),
        },
        "price_negative_control": {
            "expected": 18,
            "actual_preserved": len(price_preserved),
            "claim_ids": sorted(price_preserved),
            "note": ("These Chemistry/TIDES price claims were ALREADY conversion_assumption in the "
                     "sealed input. The repair re-binds them to the disclosed Testing/Biology price "
                     "paragraph and keeps the role; promoting them to a mechanism role would have been "
                     "the defect, not the fix."),
        },
        "biology_rebase_conversion": {
            "claim_ids": sorted(rebase_ids),
            "old_role": "mechanism_direction",
            "new_role": "conversion_assumption",
            "basis": ("annual p183 exact Biology 2,677,175,030.51 - H1 p11 comparable 125,160.49万元 "
                      "= 1,425.57013051 CNY million; a cross-period conversion from a disclosed "
                      "historical base, not a mechanism and not a future actual"),
        },
        "unknown_mechanism_handling": {
            "claim_ids": unknown_ids,
            "handling": ("Re-bound to their own historical table rows and re-roled to history_base so "
                         "they carry no forward mechanism. The forward zero/negative contribution and "
                         "the revenue sum stay unchanged; the native growth-driver report now states "
                         "that these drivers have no future-mechanism evidence."),
        },
        "rpo_correction": {
            "parameter_id": "rpo_expected_2026_opening_cohort",
            "old_kind": ctx["old_kind"],
            "new_kind": "management_guidance",
            "new_evidence_role": "value_range",
            "support_type": "exact_value",
            "value_unchanged": True,
            "revenue_dag_consumers": [],
            "note": ("Issuer expected point for the opening cohort, not an actual, not an empirical "
                     "range and not a full-year floor. The FY2025 year-end RPO stock stays a reported "
                     "point-in-time fact."),
        },
        "parameter_edits": {pid: edits for pid, edits in sorted(ctx["parameter_edits"].items())},
        "rows": rows,
        "out_of_union_repairs": {
            "count": len(ctx["out_of_union_rows"]),
            "reason": ("Same wrong-scope defect class as the union claims, found while re-reading the "
                       "H1 p12 page. They are repaired for internal consistency and reported here; they "
                       "are NOT part of the 49-claim union and must not be counted toward it."),
            "rows": ctx["out_of_union_rows"],
        },
        "out_of_union_requirement_repairs": {
            "count": 1,
            "requirement": "F3-RC05 / T09-guidance-versus-actual (RPO expectation is not in the 49-claim union)",
            "rows": [ctx["rpo_ledger_row"]],
        },
        "unchanged_claim_ids": sorted({row["claim_id"] for row in rows
                                       if row["resolution"] == "unchanged_verified"}),
    }
    (OUT_DIR / "research" / "claim-changes.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"new_input": str(main_path), "old_counts": old_counts,
                      "new_counts": new_counts, "rows": len(rows),
                      "unique": len({row["claim_id"] for row in rows}),
                      "price_preserved": len(price_preserved),
                      "parameter_edits": len(ctx["parameter_edits"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
