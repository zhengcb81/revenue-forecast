#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
T1-16 verifier.

Card:  T1-16  (OWNER_DECISIONS.md section 13, TIER-1)
Ruling text (verbatim):
    T1-16 | section 4: whether an ignored field (M02-01) is still domain
    constrained | CHOSE A (keep fail-closed). Rationale: `base=-5` is still
    rejected in measurement, so the current behaviour is already fail-closed;
    switching to B (ignore unused fields) would loosen the validation surface,
    and the risk outweighs the benefit.

Ruling class: interpretation confirmation.

What makes THIS card different from T1-17 / T1-24
-------------------------------------------------
T1-17 and T1-24 confirmed that a ruling's *adopted textual form* is on disk.
T1-16 confirms something else, and it is a stronger kind of claim: the ruling
CHOOSES A = "keep the current behaviour", on the stated rationale that the
current behaviour ALREADY IS fail-closed. That rationale is a factual premise
about the PRODUCT, not about a document. If the premise were false -- if the
product had stopped rejecting a negative `base_revenue` -- then "choose A"
would be choosing nothing, or worse, choosing A while the product already
drifted to B.

So this card must reproduce the premise by EXECUTION, not by citation. Citing
the card's own recorded observation would be citing the very thing under test.
This is the same discipline as T1-13's directional trust: the justification for
a decision rests on a state of the world, and the card must show that state
holds NOW.

Legs
----
  S-1  The validator performs a UNIFORM pre-dispatch negative check on
       `base_revenue`, i.e. the check does not depend on whether the selected
       model actually consumes the field. Proven by (a) the source text and
       (b) execution against MULTIPLE models, including one that `del`s the
       field and one that consumes it.
  S-2  For the model the observation concerns (`direct_revenue`), the field is
       genuinely IGNORED: `base_revenue = 999` leaves the output identical to
       the positive case. This is what makes the "ignored field" premise true.
  S-3  The rejection is a real rejection with the recorded shape:
       `ModelRegistryError` whose message names `<model>.base_revenue cannot be
       negative`, raised for `base_revenue = -5`.
  S-4  The option the ruling REJECTED (B) is NOT in force: the product does not
       silently ignore a negative base. Equivalently: there is no code path in
       which a negative base_revenue yields a value instead of raising.
  S-5  Additivity/state: the ruling orders no write; the card's frozen evidence
       must be untouched and the registered gate must still record the item as
       owner-reserved (not self-decided).

Exit codes: 0 = PASS, 1 = harness failure, 2 = precondition/undetermined,
            3 = expectations not met.
"""

import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import traceback

EXEC = pathlib.Path(__file__).resolve().parent.parent          # .../T1-16/a20260920-01
# Depth, counted from EXEC:
#   parents[0]=T1-16  parents[1]=execution_runs  parents[2]=<audit dir>
#   parents[3]=.planning  parents[4]=<repo root>
# (Counted from EXEC, not from __file__ -- the file sits one level deeper.)
REPO = EXEC.parents[4]
PLAN = ".planning/2026-09-19-three-project-history-audit"
M02 = f"{PLAN}/execution_runs/M02/a20260919-01"

EXPECTED_ANCHOR = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"


def _fail(msg):
    print(f"FATAL: {msg}")
    return 2


def load_product():
    """Import the production model_registry with the same sys.path shim the
    project uses (it does `from model_extensions import ...`).

    Harness note: `@dataclass` resolves annotations via
    `sys.modules[cls.__module__]`, so the module MUST be present in sys.modules
    BEFORE exec_module runs. Loading without registering it first fails with
    "'NoneType' object has no attribute '__dict__'" -- a harness defect, not a
    product defect.
    """
    scripts = REPO / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    path = scripts / "model_registry.py"
    spec = importlib.util.spec_from_file_location("m02_model_registry", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod            # <-- required before exec_module
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return mod


def main():
    # ---- path sanity guard (T1-13 lesson)
    sanity = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                            cwd=str(REPO), capture_output=True)
    if sanity.returncode != 0:
        return _fail("REPO is not inside a git work tree")
    toplevel = pathlib.Path(sanity.stdout.decode("utf-8", "replace").strip())
    if toplevel != REPO:
        return _fail(f"REPO != git toplevel ({REPO} vs {toplevel})")

    anchor_path = REPO / "scripts/model_registry.py"
    if not anchor_path.is_file():
        return _fail(f"production registry missing: {anchor_path}")
    anchor_sha = hashlib.sha256(anchor_path.read_bytes()).hexdigest()
    anchor_ok = (anchor_sha == EXPECTED_ANCHOR)
    if not anchor_ok:
        return _fail(f"production anchor drifted: {anchor_sha} != {EXPECTED_ANCHOR} "
                     "(the ruling's premise is about THIS build)")

    src = anchor_path.read_text(encoding="utf-8")

    # ---- read the card's frozen evidence (for the gate leg, NOT as proof of S-1..S-3)
    m02_dir = REPO / M02
    if not m02_dir.is_dir():
        return _fail(f"M02 card dir missing: {m02_dir}")
    run_result = json.loads((m02_dir / "evidence/M02/run_result.json").read_text(encoding="utf-8"))
    m02_handoff = json.loads((m02_dir / "handoff.json").read_text(encoding="utf-8"))

    results = {}
    notes = []

    # ---- import the product (this also proves the module is importable)
    try:
        m = load_product()
    except Exception:
        traceback.print_exc()
        return _fail("could not import the production model_registry")

    # ===================== S-1  uniform pre-dispatch check =====================
    # (a) source text: the check sits in calculate_registered_model, BEFORE
    #     dispatch, and does not consult the selected model's metadata.
    src_ok = bool(re.search(
        r"def calculate_registered_model\(", src)) and bool(re.search(
        r"if base < 0:\s*\n\s*raise ModelRegistryError\(f\"\{model_id\}\.base_revenue cannot be negative\"\)",
        src))
    # Confirm the check precedes the dispatch to the per-model calculator.
    body_start = src.index("def calculate_registered_model(")
    body = src[body_start:]
    neg_pos = body.find("cannot be negative")
    # the dispatch happens via MODEL_REGISTRY[model_id]["calculate"] or similar
    dispatch_pos = body.find("spec[")
    check_is_early = (neg_pos != -1 and (dispatch_pos == -1 or neg_pos < dispatch_pos))

    # (b) execution across multiple models: pick a model that DELETES the field
    #     and one that CONSUMES it, then show the negative check fires for BOTH.
    models = sorted(getattr(m, "MODEL_REGISTRY", {}).keys())
    if not models:
        return _fail("MODEL_REGISTRY is empty; cannot run the uniformity probe")

    def driver_shape(spec):
        """Build a minimally-valid driver mapping for a ModelSpec.

        ModelSpec is a frozen dataclass (model_id / required / optional /
        defaults / dimensions / ratio_drivers / formula / calculator /
        driver_bounds) -- NOT a dict, so a `.get`-based probe is a harness bug.
        Every declared driver gets a positive series; `ratio_drivers` are fed
        dimensionless values and everything else is fed unit-scaled values, so
        the ONLY variable under test is the sign of base_revenue.
        """
        names = list(spec.required) + list(spec.optional)
        ratios = set(spec.ratio_drivers)
        drivers = {}
        for name in names:
            drivers[name] = [0.5, 0.5] if name in ratios else [10.0, 12.0]
        return drivers

    def try_negative(model_id):
        """Return (raised, message) for base_revenue=-5, using the model's own
        declared driver shape so the ONLY variable is the base sign."""
        spec = m.MODEL_REGISTRY[model_id]
        drivers = driver_shape(spec)
        try:
            m.calculate_registered_model(model_id=model_id, base_revenue=-5.0,
                                         drivers=drivers, years=[2026, 2027])
            return (False, None)
        except Exception as exc:  # noqa: BLE001 - we want the message
            return (True, f"{type(exc).__name__}: {exc}")

    # direct_revenue ignores the field (del), direct_growth consumes it.
    probe_targets = [x for x in ("direct_revenue", "direct_growth") if x in models]
    if len(probe_targets) < 2:
        return _fail(f"expected both direct_revenue and direct_growth in the registry; got {probe_targets}")

    uniformity = {}
    for mid in probe_targets:
        raised, msg = try_negative(mid)
        consumes = "del base_revenue" in src.split(f"def _{mid}(")[-1].split("\ndef ")[0] \
            if f"def _{mid}(" in src else None
        uniformity[mid] = {
            "raised": raised,
            "message": msg,
            "message_names_the_model": bool(msg and f"{mid}.base_revenue cannot be negative" in msg),
            "consumes_the_field": (consumes is False),
            "ignores_the_field": (consumes is True),
        }
    s1_ok = (src_ok and check_is_early
             and all(v["raised"] and v["message_names_the_model"]
                     for v in uniformity.values()))
    results["S-1"] = {
        "claim": "the validator performs a UNIFORM pre-dispatch negative check on base_revenue, independent of whether the selected model uses the field",
        "holds": bool(s1_ok),
        "evidence": {
            "source_check_present": src_ok,
            "check_precedes_dispatch": check_is_early,
            "execution_probe": uniformity,
            "note": "two models chosen on purpose: one `del`s the field, one consumes it; the negative check fires for both, so it cannot be model-conditional",
        },
    }

    # ===================== S-2  the field is genuinely ignored =====================
    # Reproduce BASE-INDEPENDENCE: for direct_revenue, base=999 == base=1 (positive).
    def run_positive(model_id, base):
        spec = m.MODEL_REGISTRY[model_id]
        drivers = driver_shape(spec)
        try:
            return m.calculate_registered_model(model_id=model_id, base_revenue=base,
                                                drivers=drivers, years=[2026, 2027])
        except Exception as exc:  # noqa: BLE001
            return f"RAISED:{type(exc).__name__}:{exc}"

    base_1 = run_positive("direct_revenue", 1.0)
    base_999 = run_positive("direct_revenue", 999.0)
    s2_ok = (base_1 == base_999 and not (isinstance(base_1, str) and base_1.startswith("RAISED")))
    results["S-2"] = {
        "claim": "for direct_revenue the field is genuinely ignored: a large positive base does not change the output",
        "holds": bool(s2_ok),
        "evidence": {
            "base_1": base_1,
            "base_999": base_999,
            "identical": base_1 == base_999,
            "source": "_direct_revenue begins with `del base_revenue, years` (model_registry.py line ~98)",
            "cross_check_card_observation": run_result["observations"][0],
        },
    }

    # ===================== S-3  the rejection has the recorded shape =====================
    raised, msg = uniformity["direct_revenue"]["raised"], uniformity["direct_revenue"]["message"]
    s3_ok = bool(raised and msg and msg.startswith("ModelRegistryError")
                 and "direct_revenue.base_revenue cannot be negative" in msg)
    results["S-3"] = {
        "claim": "the rejection is a real ModelRegistryError with the recorded message shape",
        "holds": bool(s3_ok),
        "evidence": {
            "raised": raised,
            "message": msg,
            "card_recorded": run_result["observations"][1]["message"],
            "matches_card_record": msg is not None and run_result["observations"][1]["message"] in msg,
        },
    }

    # ===================== S-4  the rejected option B is NOT in force =====================
    # Option B = "an unused field is semantically absent and must be ignored".
    # Under B, a negative base for an IGNORING model would NOT raise. Show it does.
    b_ok = False
    raised_f, _ = try_negative("direct_revenue")
    if raised_f:
        b_ok = True
    # also assert there is no conditional that could let a negative through:
    # the guard is a bare `if base < 0`, with no model membership test.
    guard_is_unconditional = bool(re.search(
        r"if base < 0:\s*\n\s*raise ModelRegistryError", src))
    s4_ok = (b_ok and guard_is_unconditional)
    results["S-4"] = {
        "claim": "the rejected option B is not in force: a negative base is never silently ignored, and the guard is unconditional",
        "holds": bool(s4_ok),
        "evidence": {
            "negative_base_still_raises_for_ignoring_model": raised_f,
            "guard_is_unconditional": guard_is_unconditional,
            "guard_text": "if base < 0: raise ModelRegistryError(f\"{model_id}.base_revenue cannot be negative\")",
            "note": "under option B this call would have returned a value; it raises",
        },
    }

    # ===================== S-5  state: no write, gate still reserved =====================
    # (a) no .planning-external product change
    diff = subprocess.run(["git", "diff", "HEAD", "--name-only", "--", ".", ":(exclude).planning"],
                          cwd=str(REPO), capture_output=True)
    product_touched = [x for x in diff.stdout.decode().splitlines() if x.strip()]
    # (b) the M02 card directory itself is clean (untouched by this card)
    dm02 = subprocess.run(["git", "diff", "HEAD", "--name-only", "--", M02],
                          cwd=str(REPO), capture_output=True)
    m02_touched = [x for x in dm02.stdout.decode().splitlines() if x.strip()]
    # (c) the gate is still registered as owner-reserved and NOT self-decided
    oq_blob = json.dumps(m02_handoff.get("open_questions", []), ensure_ascii=False)
    gate_reserved = ("requires_owner_or_specialist_ruling" in oq_blob)
    # (d) the reviewer explicitly did not decide it
    review_txt = (m02_dir / "review.md").read_text(encoding="utf-8")
    reviewer_did_not_self_decide = bool(re.search(
        r"F-M02-01[^\n]{0,80}(reserved|not self-decided|未自决)", review_txt, re.I)) or \
        bool(re.search(r"CLOSED-AS-RESERVED", review_txt))
    s5_ok = (not product_touched and not m02_touched and gate_reserved
             and reviewer_did_not_self_decide)
    results["S-5"] = {
        "claim": "the ruling orders no write; frozen evidence is untouched and the gate is still recorded as owner-reserved (not self-decided)",
        "holds": bool(s5_ok),
        "evidence": {
            "product_files_changed": product_touched,
            "m02_card_files_changed": m02_touched,
            "gate_still_owner_reserved": gate_reserved,
            "reviewer_did_not_self_decide": reviewer_did_not_self_decide,
        },
    }

    all_ok = all(results[k]["holds"] for k in ("S-1", "S-2", "S-3", "S-4", "S-5")) and anchor_ok

    print("=" * 72)
    print("T1-16 verification -- M02-01 (ignored field still domain constrained)")
    print("=" * 72)
    for k in ("S-1", "S-2", "S-3", "S-4", "S-5"):
        v = results[k]
        print(f"\n[{k}] {'PASS' if v['holds'] else 'FAIL'}  {v['claim']}")
    print(f"\n[anchor] {'PASS' if anchor_ok else 'FAIL'}  scripts/model_registry.py = {anchor_sha[:16]}...")
    if notes:
        print("\nnotes:")
        for n in notes:
            print("  -", n)

    print("\n" + "=" * 72)
    print("overall =", "PASS" if all_ok else "FAIL")

    payload = {
        "card": "T1-16",
        "attempt": "a20260920-01",
        "kind": "interpretation_confirmation",
        "ruling": "OWNER_DECISIONS.md section 13 T1-16: CHOSE A (keep fail-closed). Rationale: "
                  "base=-5 is still rejected in measurement, so the current behaviour is already "
                  "fail-closed; switching to B (ignore unused fields) would loosen the validation "
                  "surface and the risk outweighs the benefit.",
        "why_execution_not_citation": "choose-A rests on a factual premise about the PRODUCT "
                                      "(current behaviour already rejects a negative base). "
                                      "Reproducing it from the card's own recorded observation "
                                      "would be citing the thing under test; the probe below runs "
                                      "the production module directly.",
        "propositions": results,
        "production_anchor": {"path": "scripts/model_registry.py", "sha256": anchor_sha,
                              "expected": EXPECTED_ANCHOR, "matches": anchor_ok},
        "overall": "PASS" if all_ok else "FAIL",
    }
    (EXEC / "t16_m02_01_fail_closed_scope.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", (EXEC / "t16_m02_01_fail_closed_scope.json").relative_to(REPO))
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())
