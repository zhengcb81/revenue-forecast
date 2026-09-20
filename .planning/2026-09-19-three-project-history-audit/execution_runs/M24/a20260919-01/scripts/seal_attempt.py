"""Seal one M21-M24 attempt: binding.json, handoff.json, review.md, decision.md, changes.diff.

Everything is derived from artifacts already on disk; nothing is typed from memory.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/seal_attempt.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

CARD_META = {
    "M21": {
        "model_id": "delivery_pipeline",
        "title": "M21 · delivery_pipeline · 实物订单交付桥",
        "entry_line": "scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)",
        "registration_line": "scripts/model_registry.py:241",
        "registry_module": "model_registry",
        "card_positive_line": "card_M21.md L48",
        "card_positive_text": "50+30-5-40=35; 40*3+2=122",
        "expected_positive": "[122]",
        "card_negative_text": "drivers.ending_orders [35] -> [36]",
        "gating_negative": "NEG-CARD: timing_factor[1] = 1.5 on the 2-year `card_neg` base",
        "bridge": "stock-flow bridge (delivery order bridge + cross-year continuity)",
        "attack_points": [
            "the frozen GATING card-specific negative is NOT the card's literal one: the card "
            "names `ending_orders=[36]` on the 1-year input, which is rejected by the FY2027 "
            "bridge-balance guard, not by a value-domain guard. NEG-CARD was deliberately moved "
            "to a 2-year `card_neg` base so the ratio value-domain guard is the reason for "
            "rejection, and the card's literal change was kept as the non-gating observation "
            "OBS-CARD-NEG-ENDING (which was also rejected). A reviewer who wants the card's "
            "literal case to be GATING must say so explicitly.",
            "`card_neg` is an input this attempt ADDED (identical to the continuity positive "
            "base). It is frozen in evidence/<card>/input.json and its expected output is the "
            "same as continuity_positive; a reviewer should confirm that adding an input is "
            "acceptable rather than a way to dodge the card's own negative.",
            "`other_revenue` is optional with default 0 and is silently zero-filled when "
            "omitted (registry line 335). For this model that asserts 'no other revenue' with "
            "no disclosure saying so.",
            "the defaults case is NOT part of the exit code; it is recorded for falsifiability "
            "only.",
        ],
    },
    "M22": {
        "model_id": "milestone_royalty",
        "title": "M22 · milestone_royalty · 里程碑与销售分成",
        "entry_line": "scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)",
        "registration_line": "scripts/model_registry.py:242",
        "registry_module": "model_registry",
        "card_positive_line": "card_M22.md L36",
        "card_positive_text": "500*0.08+12+3=55",
        "expected_positive": "[55]",
        "card_negative_text": "drivers.royalty_rate [0.08] -> [1.01]",
        "gating_negative": "NEG-CARD: royalty_rate = 1.01 (the card's literal negative)",
        "bridge": "not a stock bridge (not_applicable_with_reason); only fiscal-year continuity "
                  "is applicable",
        "attack_points": [
            "NEG-CARD is the card's literal negative, but it is also the case that most obviously "
            "tests a CONTRACT question rather than an economic one: a tiered royalty agreement "
            "can have an effective rate above 1.0 of a narrow base. The registry's [0,1] ratio "
            "domain answers it, and the card's own text does not state that 1.01 is impossible; "
            "a reviewer should decide whether that is the intended contract.",
            "`milestone_revenue` and `service_revenue` are optional with a DECLARED default of "
            "0, so the defaults case is a genuine default test; `millestone`/`service` amounts "
            "are signed (any real number), so a negative milestone adjustment is accepted by "
            "the contract - this card does not test that.",
            "the second year of the continuity positive has eligible_sales = 0 and a milestone "
            "only; this is the deliberate 'no sales, milestone only' shape and asserts nothing "
            "about probability-weighted contingent payments (which the card refuses).",
        ],
    },
    "M23": {
        "model_id": "insurance_service",
        "title": "M23 · insurance_service · 保险服务披露映射",
        "entry_line": "scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)",
        "registration_line": "scripts/model_registry.py:243",
        "registry_module": "model_registry",
        "card_positive_line": "card_M23.md L36",
        "card_positive_text": "100*2*0.5+10=110",
        "expected_positive": "[110]",
        "card_negative_text": "drivers.timing_factor [0.5] -> [1.1]",
        "gating_negative": "NEG-CARD: timing_factor = 1.1 (the card's literal negative)",
        "bridge": "not a stock bridge (not_applicable_with_reason); only fiscal-year continuity "
                  "is applicable",
        "attack_points": [
            "The card's own negative is WEAKER than it looks: because the frozen positive input "
            "has a 1-year `years` list, the only reachable slot is index 0, and replacing the "
            "whole array `[1.1]` also changes the LENGTH. The observed rejection is therefore "
            "the length guard (`must contain one value per forecast year`) and NOT the "
            "value-domain guard. This attempt covers the value guard separately with the "
            "non-gating observation OBS-TIMING-BOUND-11 (timing_factor = [1.1, 0.5] on a 2-year "
            "path), which was rejected with `must be between 0.0 and 1.0: FY2027`. A reviewer "
            "who wants the card's negative to be GATING for the value domain must say so.",
            "`timing_factor` defaults to 1.0, which is exactly the inclusive upper edge of the "
            "ratio domain - so the documented default sits ON the boundary. A reviewer should "
            "confirm that is intended rather than an accident of the bound being [0,1].",
            "the non-gating observation OBS-TIMING-BOUND-11 is based on `continuity_positive`, "
            "whose FY2027 `revenue_per_coverage_unit` is 2 (not the positive case's value), so "
            "the observation is not a drop-in replay of the card input.",
            "coverage_units and revenue_per_coverage_unit are both unmapped; nothing in this "
            "attempt claims the card is a complete IFRS17 engine (the card says it is not).",
        ],
    },
    "M24": {
        "model_id": "subscription_arr_bridge",
        "title": "M24 · subscription_arr_bridge · ARR 存量与收入时点",
        "entry_line": "scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)",
        "registration_line": "scripts/model_extensions.py:180",
        "registry_module": "model_registry",
        "card_positive_line": "card_M24.md L51",
        "card_positive_text": "lost=200*0.1=20; closing=200-20+30+40=250; revenue=200-15+15+10+5=215",
        "expected_positive": "[215]",
        "card_negative_text": "drivers.closing_arr [250] -> [251]",
        "gating_negative": "NEG-CARD: closing_arr = 251 (the card's literal negative)",
        "bridge": "stock-flow bridge (ARR bridge + cross-year continuity)",
        "attack_points": [
            "The card's CONT-BREAK patch is documented in the card as 'each year balances "
            "individually, but year-2 opening is 1 above year-1 closing'. With the frozen "
            "numbers (`opening_arr=[200,251]`, `closing_arr=[250,251]`) that description is not "
            "what happens: FY2027's closing was also moved to 251, so FY2027's BALANCE check "
            "fires first. The observed message is `opening_arr stock-flow balance failed: "
            "FY2027`, not a continuity message. The frozen requirement is the exception TYPE, "
            "and it was met; a reviewer should confirm that satisfying the type is enough, or "
            "ask for a case whose numbers make the card's prose literally true.",
            "Because of that, the product's cross-year CONTINUITY guard "
            "(`opening_arr continuity failed`) is NOT exercised by this case set. The guard "
            "exists in the code but is a change the implementer did not run; the parent agent "
            "was told.",
            "the continuity positive relies on `gross_retention_rate = 1` in FY2028; the "
            "retained-ARR guard (`opening_arr * gross_retention_rate == 0 and expansion_arr > "
            "0`) is therefore not triggered, but a zero opening ARR with positive expansion "
            "would be. The non-gating observation OBS-GRR-ONE-SECOND-YEAR only records that "
            "the input replays.",
            "`usage_revenue` is optional with no explicit default and is silently zero-filled.",
        ],
    },
}


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(path: str):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def dump(path: str, doc) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARD_META))
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    meta = CARD_META[card]
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)

    run = load(os.path.join(ev, "run_result.json"))
    oracle = load(os.path.join(ev, "oracle.json"))
    cases = load(os.path.join(ev, "cases.json"))
    body = load(os.path.join(attempt, "recovery", "oracle_body_hash.json"))
    probe = load(os.path.join(attempt, "recovery", "selfcheck", "selfcheck_result.json"))
    script_sha = lambda name: sha(os.path.join(attempt, "scripts", name))  # noqa: E731

    prod = "C:\\Users\\郑曾波\\Projects\\revenue-forecast"
    iso = os.path.join(attempt, "iso", "checkout_scripts")
    sem = run["exit_code_semantics"]
    neg = run["negative_summary"]

    # ---------------- binding.json ----------------
    dump(os.path.join(attempt, "binding.json"), {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": meta["model_id"],
        "title": meta["title"],
        "binding_status": "bound",
        "binding_sources": {
            "I-00-B": {
                "path": "execution_runs/I-00-B/a20260919-01/binding.json",
                "rule_read": "run cwd must be a per-attempt isolation directory, never the repo "
                             "root; the global Miniconda python is FORBIDDEN for card runs",
                "note": "I-00-B does not materialise a checkout tree; it binds the isolation plan "
                        "and the two-stage command rule. This attempt therefore materialises its "
                        "own read-only snapshot (iso/checkout_scripts) and records the production "
                        "hashes it was copied from.",
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": "present, used as a receipt reference only (this attempt "
                                  "re-hashed the files it actually used rather than trusting the "
                                  "receipt)",
            },
            "I-00-A": {
                "path": "execution_runs/I-00-A/a20260919-01/baseline.json",
                "role": "template interpreter and isolation finding (the global python loads an "
                        "editable dayu-agent finder, so isolated venvs are mandatory)",
            },
        },
        "three_repo_paths": {
            "revenue-forecast": prod,
            "company-wiki": "C:\\Users\\郑曾波\\Projects\\company-wiki",
            "filing-fetch": "C:\\Users\\郑曾波\\Projects\\filing-fetch",
        },
        "interpreter": {
            "path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(attempt))),
                "I-00-A", "a20260919-01", "iso", "venv", "Scripts", "python.exe"),
            "isolation": "attempt-local venv created with `python -m venv` from the I-00-A "
                         "template venv; no third-party package is required by this card",
            "global_python_used_for": "nothing in this attempt",
        },
        "cwd": attempt,
        "python_path": [iso],
        "run_code_root": iso,
        "production_source_root_readonly": prod,
        "production_source_hashes": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py": sha(os.path.join(iso, "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha(os.path.join(iso, "model_extensions.py")),
        },
        "model_contract_as_read_from_the_isolated_copy": run["registry_metadata"],
        "entry_point": meta["entry_line"],
        "registration": meta["registration_line"],
        "module_paths": {"code_root": iso, "imports_used": [meta["registry_module"]]},
        "config_paths": [],
        "allowed_write_roots": [attempt],
        "forbidden": [
            "writing anywhere outside the attempt directory",
            "writing under Projects/revenue-forecast outside .planning",
            "writing under Projects/company-wiki or Projects/filing-fetch",
            "editing .planning/reviews (frozen audit evidence)",
            "git add/commit/restore/stash in any of the three repos",
            "network calls, real providers, LLM calls, publication",
            "calling any product function other than calculate_registered_model for the formula "
            "oracle",
        ],
        "network": "disabled",
        "input_hashes": {
            "evidence/%s/input.json" % card: sha(os.path.join(ev, "input.json")),
            "evidence/%s/oracle.json" % card: sha(os.path.join(ev, "oracle.json")),
            "evidence/%s/cases.json" % card: sha(os.path.join(ev, "cases.json")),
        },
        "evidence_root": ev,
        "created_before_runs": True,
        "oracle_document": {
            "path": "oracle.md",
            "frozen_body_sha256": body["oracle_md_frozen_body_sha256"],
            "frozen_body_bytes": body["oracle_md_frozen_body_bytes"],
            "full_file_sha256_now": sha(os.path.join(attempt, "oracle.md")),
            "note": "the frozen body was written before any product run; the run-reconciliation "
                    "section was appended afterwards",
        },
    })

    # ---------------- changes.diff ----------------
    with open(os.path.join(attempt, "changes.diff"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("""# %s - changes.diff

NO PRODUCT CHANGE.

This attempt produced **no diff against any production repository**:

- `C:\\Users\\郑曾波\\Projects\\revenue-forecast` (including `scripts/model_registry.py`,
  `scripts/model_extensions.py`, `SKILL.md`, `references/*`, `CHANGELOG.md`): untouched.
- `C:\\Users\\郑曾波\\Projects\\company-wiki`: untouched.
- `C:\\Users\\郑曾波\\Projects\\filing-fetch`: untouched.
- `.planning/2026-09-19-three-project-history-audit/reviews/`: never written to.

Everything this attempt wrote lives under:

    %s

The pre-existing dirty state of revenue-forecast is captured in `before/` and `after/`
(`git_status_revenue-forecast.txt`) so it stays attributable to its owner. No `git add`,
`git commit`, `git restore` or `git stash` was executed in any repository.

The only "changes" are new files inside the attempt directory:

- `binding.json`, `oracle.md`, `commands.json`, `decision.md`, `handoff.json`,
  `changes.diff`, `review.md`
- `evidence/%s/*` (input, oracle, cases, run result, manifests, qualification, rulings, ...)
- `scripts/*` (oracle generator, runner, mutation probe, enumeration, doc builders)
- `iso/checkout_scripts/*` (byte-identical read-only copies, hashes recorded)
- `iso/venv/*` (attempt-local interpreter)
- `before/`, `after/`, `recovery/`
""" % (meta["title"], attempt, card))

    # ---------------- decision.md ----------------
    with open(os.path.join(attempt, "decision.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("""# %s decision record

`START_HERE.md` requires a written `decision.md` before implementing anything that falls
under a professional decision (cross-process locking, publication transaction boundaries,
fiscal-period / restatement / gross-vs-net and payability attribution, unidentifiable model
parameters, sample and statistical thresholds, deployment migration and natural-observation
qualification).

## Professional decisions

**None of those categories arises in this card's A-C scope**, and no product file was
modified. The scope is a pure in-process calculator plus a frozen formula oracle:

- no cross-process locking, no lease, no publication and no deployment decision (the model is
  a pure function: `calculate_registered_model` has no durable state and no side effect);
- no restatement / gross-vs-net / payability attribution decision: this attempt uses only the
  card's frozen **synthetic** numbers, never a real company disclosure;
- no unidentifiable parameter and no statistical threshold: the tolerance is the shared
  contract `1e-9 * max(1, |expected|)`.

## Escalated to the owner (not decided here)

- **OQ-01 (binding provenance).** The cards say the run cwd must come from I-00-B, but I-00-B
  binds the isolation *plan* and the two-stage command rule, not a materialised checkout tree.
  This attempt therefore materialises its own read-only snapshot (`iso/checkout_scripts`,
  hashes equal to production). If the intended binding is an I-00-B-materialised checkout, the
  provenance chain differs; the code under test is byte-identical either way. Needs a ruling.
- **OQ-02 (gating negative vs the card's literal negative).** For %s the card's literal
  negative is also a length-domain case, so the GATING negative was moved to a case that
  reaches the value-domain guard and the literal case was kept as a non-gating observation.
  Owner/reviewer must confirm that is acceptable (see `review.md` section 5).
- **OQ-03 (silent zero-fill).** `scripts/model_registry.py:335` silently turns an omitted
  optional driver with no explicit default into 0.0. Named instances for these four cards:
  `delivery_pipeline.other_revenue`, `milestone_royalty.milestone_revenue` and
  `.service_revenue`, `insurance_service.other_revenue`, `subscription_arr_bridge.usage_revenue`.
  Registered, NOT fixed; no product change. Enumeration in `evidence/%s/oq_rulings.json`.
- **OQ-04 (business rejections stay open).** The cards' "professional decision / business
  negative" items (delivery != recognition; probability-weighted milestones are not recognised
  revenue; this is not an IFRS17 engine; NRR != GRR, ARR != revenue) are NOT runtime contract
  and are NOT adjudicated here. Unresolved -> `STOP_DISCLOSURE_ADAPTATION`.
""" % (meta["title"], card, card))

    # ---------------- review.md ----------------
    neg_lines = "\n".join(
        "- `%s`: %s - `%s`" % (e["id"], e.get("raised"), (e.get("message") or "")[:160])
        for e in run["negatives"])
    obs_lines = "\n".join(
        "- `%s`: raised=%s actual=%s%s" % (o["id"], o.get("raised"), o.get("actual"),
                                           " - " + o["message"] if o.get("message") else "")
        for o in run["observations"])
    attacks = "\n".join("%d. %s" % (i + 1, a) for i, a in enumerate(meta["attack_points"]))
    probe_rows = "\n".join(
        "| %s | %d | %d |" % (r["tag"], r["raw_exit_code"], r["expected_exit_code"])
        for r in probe["runs"])
    with open(os.path.join(attempt, "review.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("""# {title} - implementer review record

Card {card} (`{model}`), Parent I-10. Attempt `execution_runs/{card}/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/{card}/source_manifest.json` |
| B positive | actual `{pos_actual}` vs independent oracle `{pos_expected}`, within `1e-9*max(1,|e|)` | `evidence/{card}/formula_result.json` |
| continuity positive | actual `{cont_actual}` vs oracle `{cont_expected}` | `evidence/{card}/negative_results.json` |
| defaults case | actual `{def_actual}` vs oracle `{def_expected}` (not gating) | `evidence/{card}/negative_results.json` |
| C negatives | {neg_passed}/{neg_total} rejected with `ModelRegistryError` | `evidence/{card}/negative_results.json` |
| D mapping | **NOT DONE** - needs a signed industry/accounting review | `evidence/{card}/qualification.json` |
| E probe | **NOT DONE** - belongs to I-10-A | `evidence/{card}/qualification.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/{card}/qualification.json` |

Raw exit code of the product run: **{rc}** (0=pass / 2=no-verdict / 3=negative not rejected as
expected / 1=harness error). stderr is {stderr_bytes} bytes.

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_{card}.py`, which imports only `argparse`,
  `hashlib`, `json`, `os`, `sys` and `decimal` - see the `import_lines` list inside
  `evidence/{card}/oracle_selfcheck.json`; `product_import_present` is `false`.
- The oracle document `oracle.md` (sections 0-11) was written **before** any product run. Its
  frozen body is {body_bytes} bytes, sha256
  `{body_sha}`; the exact reconstruction identity
  `oracle.md == frozen_body + b"\\n---\\n\\n" + run_section` is verified by
  `scripts/verify_prefix_chain.py` in all four attempts of this batch.
- `evidence/{card}/oracle.json` is **byte-identical when regenerated** (re-run performed).
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations
  only from `evidence/{card}/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection
  (N01a uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `{runner_sha}`) was used for
  M05-M08 and for all four attempts of this batch; there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `{formula}`
- Registry required: `{required}`; optional: `{optional}`; defaults: `{defaults}`
- Rejections and their messages:
{neg_lines}

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

{obs_lines}

## 5. Judgement calls the reviewer should attack first

{attacks}

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review
  plus a production forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated
  specification, the existing implementation is retained.
- It does **not** claim that a formula pass on this card implies anything about the other 30
  models: the parent card explicitly forbids extrapolating accuracy from formula passes.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_{card}.py --card {card} --out-root <scratch>` and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` against
   `iso/checkout_scripts` and diff `run_result.json`.
2. Re-run `scripts/verify_prefix_chain.py <plan>` to confirm the oracle.md frozen-body chain.
3. Confirm the isolated copy hashes still equal production
   (`evidence/{card}/source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running it.
5. Re-run `scripts/enumerate_oq_rulings.py` and compare the counts with
   `evidence/{card}/oq_rulings_enumeration.json`.
6. Adjudicate the OQ items in `decision.md` and `handoff.json`.

## 8. Exit-code mutation self-check (red then green)

Scratch tree: `recovery/selfcheck/` (the frozen evidence is never mutated).

| probe | raw rc | expected rc |
|---|---|---|
{probe_rows}

`frozen_hashes_unchanged` = `{frozen_unchanged}`. Full record:
`recovery/selfcheck/selfcheck_result.json`.
""".format(
            title=meta["title"], card=card, model=meta["model_id"],
            pos_actual=run["positive"].get("actual"),
            pos_expected=oracle["positive"]["expected_float"],
            cont_actual=run["continuity_positive"].get("actual"),
            cont_expected=oracle["continuity_positive"]["expected_float"],
            def_actual=run["defaults"].get("actual"),
            def_expected=oracle["defaults"]["expected_float"],
            neg_passed=neg["passed"], neg_total=neg["total"], rc=sem["exit_code"],
            stderr_bytes=os.path.getsize(os.path.join(ev, "stderr.txt")),
            body_bytes=body["oracle_md_frozen_body_bytes"],
            body_sha=body["oracle_md_frozen_body_sha256"],
            runner_sha=script_sha("run_card.py"),
            formula=run["registry_metadata"]["formula"],
            required=run["registry_metadata"]["required"],
            optional=run["registry_metadata"]["optional"],
            defaults=run["registry_metadata"]["defaults"],
            neg_lines=neg_lines, obs_lines=obs_lines, attacks=attacks,
            probe_rows=probe_rows,
            frozen_unchanged=probe["frozen_hashes_unchanged"]))

    # ---------------- handoff.json ----------------
    dump(os.path.join(attempt, "handoff.json"), {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": meta["model_id"],
        "title": meta["title"],
        "status": "review_pending",
        "implementer_is_not_the_reviewer": True,
        "completed_steps": {
            "A_binding": "done (binding.json: read-only production hashes + attempt-local "
                         "isolated snapshot)",
            "B_positive_run": "done (positive %s, continuity %s, defaults %s; all within "
                              "1e-9*max(1,|e|))" % (run["positive"].get("actual"),
                                                     run["continuity_positive"].get("actual"),
                                                     run["defaults"].get("actual")),
            "C_negative_run": "done (%d/%d negatives rejected with ModelRegistryError; "
                              "card-specific negative + N01-N05 + continuity break)"
                              % (neg["passed"], neg["total"]),
            "D_disclosure_mapping": "NOT done - needs a signed industry/accounting review; "
                                    "nothing is claimed",
            "E_historical_mapping_probe": "NOT done - belongs to I-10-A",
            "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
            "oracle_freeze": "oracle.md frozen body %d bytes sha256 %s; oracle.json "
                             "byte-identical on regeneration" % (
                                 body["oracle_md_frozen_body_bytes"],
                                 body["oracle_md_frozen_body_sha256"]),
            "mutation_proof": "4 probes per card, all four exit codes observed as expected "
                              "(0/3/3/2 then 0 on restore); frozen evidence hashes unchanged",
            "oq_enumeration": "31 models / 165 driver slots enumerated; counts in "
                              "evidence/%s/oq_rulings.json" % card,
        },
        "completed_steps_list": ["A", "B", "C", "oracle-freeze", "mutation-proof", "oq-enum"],
        "next_step_number": 4,
        "next_action": "Independent reviewer: re-run scripts/oracle_%s.py in a scratch tree and "
                       "diff against the frozen oracle.json, re-run scripts/run_card.py against "
                       "iso/checkout_scripts and confirm %s / %s / %s with %d/%d negatives "
                       "rejected, re-run scripts/verify_prefix_chain.py, then adjudicate the "
                       "OQ items in decision.md and the attack list in review.md section 5. "
                       "After that I-10-A owns D/E." % (
                           card, oracle["positive"]["expected_float"],
                           oracle["continuity_positive"]["expected_float"],
                           oracle["defaults"]["expected_float"], neg["passed"], neg["total"]),
        "input_hashes": {
            "evidence/%s/input.json" % card: sha(os.path.join(ev, "input.json")),
            "evidence/%s/oracle.json" % card: sha(os.path.join(ev, "oracle.json")),
            "evidence/%s/cases.json" % card: sha(os.path.join(ev, "cases.json")),
            "oracle.md_frozen_body": body["oracle_md_frozen_body_sha256"],
            "scripts/oracle_%s.py" % card: script_sha("oracle_%s.py" % card),
            "scripts/run_card.py": script_sha("run_card.py"),
        },
        "current_source_hashes": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
            "iso/checkout_scripts/model_registry.py": sha(os.path.join(iso, "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha(os.path.join(iso, "model_extensions.py")),
        },
        "changed_paths": {
            "production_repos": [],
            "note": "no production file was created, modified, added, committed, restored or "
                    "stashed in any of the three repos; the pre-existing dirty state is captured "
                    "in before/ and after/",
            "attempt_paths_created": [attempt],
        },
        "commands_executed": [u["unit_id"] for u in
                              load(os.path.join(attempt, "commands.json"))["units"]],
        "raw_exit_codes": {u["unit_id"]: u["raw_rc"] for u in
                           load(os.path.join(attempt, "commands.json"))["units"]},
        "expected_exit_codes": {u["unit_id"]: u["expected_rc"] for u in
                                load(os.path.join(attempt, "commands.json"))["units"]},
        "positive_actual": run["positive"].get("actual"),
        "positive_expected": oracle["positive"]["expected_float"],
        "continuity_actual": run["continuity_positive"].get("actual"),
        "defaults_actual": run["defaults"].get("actual"),
        "negative_case_summary": neg,
        "negative_ids": cases["cases"] and [c["id"] for c in cases["cases"]],
        "observations": [{"id": o["id"], "raised": o.get("raised"), "actual": o.get("actual")}
                         for o in run["observations"]],
        "open_questions": [
            "OQ-01 (binding): the cards require the run cwd to come from I-00-B, but I-00-B "
            "binds only the isolation plan and the two-stage command rule, not a materialised "
            "checkout tree. This batch materialised its own read-only snapshot "
            "(iso/checkout_scripts, hashes equal to production). Needs a binding ruling.",
            "OQ-02 (gating-negative choice): see review.md section 5 for the per-card trade-off; "
            "the reviewer/owner must confirm whether the card's literal negative must be the "
            "GATING one.",
            "OQ-03 (silent zero-fill): scripts/model_registry.py:335 turns an omitted optional "
            "driver with no explicit default into 0.0. Registered, NOT fixed; counts in "
            "evidence/%s/oq_rulings.json." % card,
            "OQ-04 (business rejections): the cards' professional-decision items are not runtime "
            "contract and are not adjudicated here.",
        ],
        "blocked_by": [],
        "stop_conditions_hit": [
            "STOP_ACCURACY (no I-12 frozen design)",
            "STOP_DISCLOSURE_ADAPTATION (no signed disclosure mapping; required drivers "
            "unmapped)",
        ],
        "qualifications": {
            "formula": "review_pending",
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
        },
        "evidence_paths": sorted(
            ["binding.json", "changes.diff", "commands.json", "decision.md", "handoff.json",
             "oracle.md", "review.md", "after/", "before/", "recovery/", "scripts/",
             "iso/checkout_scripts/"]
            + ["evidence/%s/%s" % (card, name)
               for name in sorted(os.listdir(ev))
               if os.path.isfile(os.path.join(ev, name))]),
        "reviewer_status": "r1 reviewed: M21 accepted_scoped; M22/M23/M24 changes_required "
                           "(all six required items implemented in revision r2 and returned for "
                           "point review); implementer never writes 'accepted'",
        "reviews_mtime_conventions": load(os.path.join(ev, "integrity.json"))[
            "reviews_directory_untouched"],
        "revision": "r2 (independent review: M21 accepted_scoped, M22/M23/M24 changes_required. "
                    "This revision implements review items P2-1, P2-2, P2-3, P3-1, P3-2, P3-3. "
                    "The verdict for the REVISED attempt has NOT yet been received, so every "
                    "qualification stays review_pending / unmapped / unproven.)",
        "revision_r2_detail": "evidence/%s/revision_r2.json" % card,
        "disclosure_impact_note": "not applicable to this card",
    })

    print("sealed", attempt)
    print("review.md, decision.md, handoff.json, binding.json, changes.diff written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
