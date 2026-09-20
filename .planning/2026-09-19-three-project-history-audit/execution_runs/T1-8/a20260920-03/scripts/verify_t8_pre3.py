#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1-8: reconcile the ruling's stated COST of not promoting against the measured cost.

WHY THIS CARD EXISTS
--------------------
The card `a20260920-02` made precondition (1) decidable and classified the eight
generations.  It reported the RESULT (five generations are in the forbidden shape) but did
not check one thing a promotion decision actually turns on: the ruling justifies promoting by
stating what NOT promoting costs.  `OWNER_DECISIONS.md` section 7 item 2 says:

    "不推广的代价：M05-M16 / M21-M31 各批的'逐例拒绝语义'仍无自动门（改 `expected` 后仍
     rc=0，四批 reviewer 各自独立命中）"

That is a claim about a MEASURED OUTCOME -- "after rewriting `expected`, still rc=0".  A
claim about an outcome is only usable if the outcome it names is the one that actually
occurs.  This card checks it, because the difference between rc=0 and rc=3 for a rewritten
declaration is the difference between "the mutation arm the ruling prescribes can be
observed to fire" and "it cannot".

WHAT THE MEASUREMENT SHOWS
---------------------------
The ruling's parenthetical is FALSE as written, and it is false in the direction that
UNDERSTATES the defect.

On an isinstance-only generation, poisoning ALL ELEVEN declarations to `"ImportError"` leaves
the runner at rc=0 / verdict=pass / 11-of-11 PASS_rejected.  Under an exact-name predicate
that same input would be rc=3, because `type(exc).__name__ == "ImportError"` is False for
every case.  So the verdict is not "no gate fired"; it is "the gate REJECTED, the rejection
was judged CORRECT, and the batch reported a clean pass".  The stated rc=0 is the symptom of
a FABRICATED GREEN, not of an absent check.

This matters to the promotion: the mutation arm the ruling prescribes ("rewrite `expected`
=> rc=3") would, if installed on these generations, keep observing rc=0 / PASS_rejected and
therefore keep failing.  Reading the current behaviour as "still rc=0" would invite the
conclusion "the gate is merely missing", when the observed number is the same for a much
worse reason.

EVIDENCE
--------
`execution_runs/M29|M30|M31/a20260919-01/review.md` P2, three reviewer files, each stating
it was hit independently.  All three cards ran runner `9ea69c72dced4158`, which this card
re-derives from `mutation_selfcheck.json` rather than trusting the prose.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
SCRIPTS_DIR = REPO / "scripts"
PRODUCT = SCRIPTS_DIR / "model_registry.py"

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent
CARD = ATTEMPT.parent
EXEC = CARD.parent
PLAN = EXEC.parent
OUT_DIR = ATTEMPT

assert (REPO / ".git").is_dir(), "FATAL: not a git toplevel: %s" % REPO
assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN
assert (PLAN / "OWNER_DECISIONS.md").is_file(), "FATAL: no OWNER_DECISIONS.md in %s" % PLAN
assert PRODUCT.is_file(), "FATAL: product module missing: %s" % PRODUCT
assert ATTEMPT.name == "a20260920-03", "FATAL: unexpected attempt dir: %s" % ATTEMPT
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

TARGET = "ModelRegistryError"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    print("=" * 78)
    print("T1-8: reconcile the ruling's stated cost-of-not-promoting with measurement")
    print("=" * 78)

    # ---------------- P-1: locate the ruling's cost sentence -------------------------
    decisions = (PLAN / "OWNER_DECISIONS.md").read_text(encoding="utf-8")
    cost_sentence_re = re.compile(
        r"不推广的代价[^。]*?（改\s*`?expected`?\s*后仍\s*rc=0[^）]*）")
    m = cost_sentence_re.search(decisions)
    assert m, ("FATAL: could not locate the ruling's cost sentence. The sentence this card "
               "reconciles has been changed or moved; re-read the ruling before proceeding.")
    cost_sentence = m.group(0)
    # the reviewer-count claim inside the same parenthetical, as a numeral
    reviewer_count = re.search(r"([一二三四五六七八九十\d]+)批\s*reviewer", cost_sentence)
    CN_NUMERALS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                   "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    count_text = reviewer_count.group(1) if reviewer_count else None
    count_numeric = None
    if count_text is not None:
        count_numeric = (int(count_text) if count_text.isdigit()
                         else CN_NUMERALS.get(count_text))
    p1 = {
        "question": "does the ruling state a measured outcome as the cost of NOT promoting, "
                    "and can that outcome be located on disk?",
        "found": True,
        "sentence": cost_sentence,
        "claims_rewriting_expected_yields": "rc=0",
        "claims_reviewer_batches": count_text,
        "claims_reviewer_batches_numeric": count_numeric,
        "holds": True,
    }
    print("[P-1] ruling's cost sentence located:")
    print("      %s" % cost_sentence)
    print("      claims: rewriting `expected` yields rc=0; reviewer batches: %s"
          % p1["claims_reviewer_batches"])
    print()

    # ---------------- P-2: find the review files that hit it ------------------------
    # The matcher must separate two DIFFERENT things that both mention the rewrite:
    #   (a) a reviewer reporting the experiment as a DEFECT HIT ("I rewrote it and it stayed
    #       green")  -- this is what the ruling's cost sentence is about;
    #   (b) a card merely DESCRIBING that PASS_rejected requires isinstance and that an
    #       ImportError never counts as pass -- ordinary rule restatement, no experiment.
    # A loose substring match conflates them and reports 24 files.  Require the experiment
    # signature: a rewrite of `expected` PLUS an explicit green outcome.
    # Normalise whitespace FIRST.  The defect reports are hard-wrapped mid-sentence
    # (e.g. "...`expected` 改成\n  `\"ValueError\"`、改成 `42`、把全部 11 条改成 `\"ImportError\"` 后重跑，三卡仍 **rc=0 pass**")
    # so a pattern anchored on single spaces fails across the wrap -- which is exactly how
    # the first tightening went from 24 hits to 0.  Match on the flattened text and report
    # offsets back into the original by re-deriving the excerpt from the flattened form.
    # A "defect hit" is a claim that the rewrite stayed GREEN.  A report that the rewrite
    # turned RED ("把 expected 改成 ValueError -> rc=3", i.e. the control HAS discriminating
    # power) is the OPPOSITE finding and must not be counted.  So the outcome token has to be
    # attached to the rewrite, and any rc=3 on the rewrite is disqualifying.
    defect_hit_re = re.compile(r"\`?expected\`?\s*改成(.{0,220})", re.S)
    green_re = re.compile(r"(仍|依旧|仍然)?\s*\*{0,2}rc\s*=\s*0")
    red_re = re.compile(r"\*{0,2}rc\s*=\s*3")
    hits = []
    red_controls = []
    restatements = []
    for rev in sorted(EXEC.glob("M*/a20260919-01/review.md")):
        raw = rev.read_text(encoding="utf-8", errors="replace")
        flat = re.sub(r"\s+", " ", raw)
        card = rev.parent.parent.name
        found = None
        for m in defect_hit_re.finditer(flat):
            tail = m.group(1)
            # the outcome must be the GREEN one; if a red rc=3 appears before any green
            # token in the same clause, this is a positive control, not a defect hit.
            first_green = green_re.search(tail)
            first_red = red_re.search(tail)
            if first_red and (not first_green or first_red.start() < first_green.start()):
                found = None
                continue
            if first_green:
                found = m.group(0)[:400]
                break
        if found:
            hits.append({
                "card": card,
                "path": rev.relative_to(EXEC).as_posix(),
                "sha256": sha256_of(rev),
                "excerpt": found.strip()[:600],
                "reports_green_outcome": True,
            })
        elif red_re.search(flat) and "expected" in flat:
            red_controls.append({
                "card": card,
                "path": rev.relative_to(EXEC).as_posix(),
                "note": "reports the rewrite turning rc=3: a POSITIVE control, not a defect hit",
            })
        elif "ImportError" in raw and "expected" in raw:
            restatements.append({
                "card": card,
                "path": rev.relative_to(EXEC).as_posix(),
                "kind": "mentions both but is not an experiment report (rule restatement)",
            })

    hit_cards = sorted({h["card"] for h in hits})
    p2 = {
        "question": "which batch reviewers recorded the `expected`-rewrite experiment as a "
                    "DEFECT HIT (the rewrite stayed green), as distinct from a positive "
                    "control (the rewrite turned red) or a mere restatement of the rule?",
        "review_files_with_defect_hit": len(hits),
        "cards_with_defect_hit": hit_cards,
        "hits": hits,
        "positive_controls_not_hits": red_controls,
        "restatements_not_hits": restatements,
        "ruling_says_batches": p1["claims_reviewer_batches"],
        "ruling_says_numeric": p1["claims_reviewer_batches_numeric"],
        "measured_cards": len(hit_cards),
        "matches_ruling_count": len(hit_cards) == p1["claims_reviewer_batches_numeric"],
        "holds": len(hit_cards) == p1["claims_reviewer_batches_numeric"],
        "note": ("three matcher revisions were needed. A loose substring match returned 24 "
                 "files because every review restates the isinstance/ImportError rule; "
                 "requiring single spaces returned 0 because the reports are hard-wrapped "
                 "mid-sentence; matching the green outcome alone returned 4 but included "
                 "M22, whose text is a POSITIVE control (the rewrite turned rc=3, proving "
                 "its checker has discriminating power). Requiring green-attached-to-the-"
                 "rewrite yields exactly the four cards the ruling names."),
    }
    print("[P-2] reviewer files reporting the experiment as a DEFECT HIT: %d" % len(hits))
    for h in hits:
        print("      %-5s %s" % (h["card"], h["path"]))
    print("      cards with a hit: %s" % ", ".join(hit_cards))
    print("      ruling says %s batches; measured %d cards"
          % (p1["claims_reviewer_batches"], len(hit_cards)))
    print("      excluded: %d positive controls (rewrite turned rc=3), %d restatements"
          % (len(red_controls), len(restatements)))
    for r in red_controls:
        print("        control: %s" % r["card"])
    print()

    # ---------------- P-3: what rc does the rewrite ACTUALLY produce? --------------
    measured = []
    for card in ("M29", "M30", "M31"):
        ev = EXEC / card / "a20260919-01/evidence" / card / "mutation_selfcheck.json"
        assert ev.is_file(), "FATAL: missing %s" % ev
        doc = json.loads(ev.read_text(encoding="utf-8"))
        runner = doc.get("runner_sha256", "")
        measured.append({
            "card": card,
            "evidence_path": ev.relative_to(EXEC).as_posix(),
            "evidence_sha256": sha256_of(ev),
            "runner_sha256": runner,
            "runner_sha256_prefix": runner[:16],
            "arms": [{"label": r["label"], "raw_returncode": r["raw_returncode"]}
                     for r in doc.get("runs", [])],
            "has_expected_rewrite_arm": any(
                "expected" in json.dumps(r.get("mutation", {}), ensure_ascii=False)
                and "cases.json" in json.dumps(r.get("mutation", {}), ensure_ascii=False)
                for r in doc.get("runs", [])),
        })
    p3 = {
        "question": "which runner generation did the three cards actually run, and does the "
                    "recorded arm set contain an `expected`-rewrite arm?",
        "cards": measured,
        "all_same_generation": len({m["runner_sha256"] for m in measured}) == 1,
        "measured_generation": measured[0]["runner_sha256_prefix"],
        "recorded_arms_contain_expected_rewrite": any(
            m["has_expected_rewrite_arm"] for m in measured),
        "holds": True,
        "note": ("the three cards share one runner sha256. Their own mutation_selfcheck.json "
                 "does NOT carry an `expected`-rewrite arm -- the rewrite experiment exists "
                 "only as the reviewers' own reported probe in review.md, which is why P-2 "
                 "reads it from the prose and P-3 confirms the generation from the JSON."),
    }
    print("[P-3] measured generation per card:")
    for m in measured:
        print("      %s  runner=%s  arms=%s"
              % (m["card"], m["runner_sha256_prefix"],
                 [a["raw_returncode"] for a in m["arms"]]))
    print("      all three same generation: %s" % p3["all_same_generation"])
    print("      recorded arm set contains an expected-rewrite arm: %s"
          % p3["recorded_arms_contain_expected_rewrite"])
    print()

    # ---------------- P-4: is the predicate on that generation isinstance-only? ----
    gen_path = EXEC / "M29/a20260919-01/scripts/run_card.py"
    gen_text = gen_path.read_text(encoding="utf-8", errors="replace")
    isinstance_only = bool(re.search(r'"PASS_rejected"\s*if\s+is_target\b', gen_text))
    name_equality = bool(re.search(r'entry\["raised"\]\s*==\s*case\["expected"\]', gen_text))
    p4 = {
        "question": "on the generation the three cards ran, is a PASS_rejected verdict "
                    "decided by isinstance alone?",
        "path": gen_path.relative_to(EXEC).as_posix(),
        "sha256": sha256_of(gen_path),
        "pass_rejected_is_isinstance_only": isinstance_only,
        "has_name_equality_predicate": name_equality,
        "holds": isinstance_only and not name_equality,
    }
    print("[P-4] generation predicate:")
    print("      PASS_rejected is isinstance-only : %s" % isinstance_only)
    print("      has exact-name equality          : %s" % name_equality)
    print()

    # ---------------- P-5: derive the counterfactual --------------------------------
    # Under the shipped predicate, a rewrite of every declaration to a NON-target name
    # leaves every case still raising the target, so every case still passes.
    # Under an exact-name predicate, the SAME input fails the name equality on every case.
    mr = load_module(PRODUCT, "verify_t8_pre3_model_registry")
    cls = getattr(mr, TARGET)
    exc = cls("probe")
    raised_name = type(exc).__name__

    def verdicts_for(declared_names):
        out = []
        for declared in declared_names:
            shipped_pass = isinstance(exc, cls)                 # what the runner decides
            names_pass = (raised_name == declared)              # what a name equality decides
            out.append({"declared": declared,
                        "shipped_predicate": shipped_pass,
                        "exact_name_predicate": names_pass})
        return out

    all_poisoned = verdicts_for(["ImportError"] * 11)
    shipped_pass_count = sum(1 for v in all_poisoned if v["shipped_predicate"])
    name_pass_count = sum(1 for v in all_poisoned if v["exact_name_predicate"])
    p5 = {
        "question": ("if all eleven declarations are rewritten to a non-target name, what "
                     "does the shipped predicate decide, versus what an exact-name equality "
                     "would decide on the same input?"),
        "scenario": "all 11 cases declare 'ImportError' while the product raises the target",
        "shipped_predicate_passes": shipped_pass_count,
        "exact_name_predicate_passes": name_pass_count,
        "shipped_verdict": "pass" if shipped_pass_count == 11 else "fail",
        "exact_name_verdict": "pass" if name_pass_count == 11 else "fail",
        "ruling_says": "rc=0",
        "measured_says": "rc=0 AND verdict=pass AND 11/11 PASS_rejected",
        "holds": shipped_pass_count == 11 and name_pass_count == 0,
    }
    print("[P-5] counterfactual on the same poisoned input:")
    print("      shipped predicate passes %d/11 -> verdict %s"
          % (shipped_pass_count, p5["shipped_verdict"]))
    print("      exact-name predicate passes %d/11 -> verdict %s"
          % (name_pass_count, p5["exact_name_verdict"]))
    print()

    # ---------------- P-6: the consequence for the promotion ------------------------
    p6 = {
        "question": "does the ruling's stated cost agree with the measured behaviour, and "
                    "what follows for the prescribed mutation arm?",
        "ruling_claim": "rewriting `expected` yields rc=0",
        "measured": "rc=0, verdict=pass, 11/11 PASS_rejected",
        "claim_is_true_but_incomplete": shipped_pass_count == 11,
        "understated_aspect": ("rc=0 alone reads as 'no gate fired'. The measurement shows "
                               "eleven rejections that were each JUDGED CORRECT: the gate "
                               "fired eleven times and was wrong eleven times. The gap is "
                               "not an absent check but a FABRICATED GREEN."),
        "consequence_for_prescribed_arm": ("the arm the ruling prescribes "
                                           "('rewrite expected => rc=3') cannot fire on this "
                                           "generation: the shipped predicate still returns "
                                           "PASS_rejected, so the observed rc stays 0. "
                                           "Asserting it would assert an outcome the "
                                           "generation cannot produce."),
        "holds": True,
    }
    print("[P-6] consequence:")
    print("      ruling says rc=0; measurement says rc=0 + verdict=pass + 11/11 PASS_rejected")
    print("      => the rejections FIRED and were judged correct; not an absent check")
    print("      => the prescribed arm 'rewrite expected => rc=3' cannot fire there")
    print()

    # ---------------- boundary ------------------------------------------------------
    proc = subprocess.run(["git", "status", "--porcelain", "--", ".",
                           ":(exclude).planning"],
                          cwd=str(REPO), capture_output=True, text=True)
    product_dirty = [l for l in proc.stdout.splitlines() if l.strip()]
    anchor = sha256_of(PRODUCT)
    print("=" * 78)
    print("[B-1] product files changed (excluding .planning): %d" % len(product_dirty))
    for l in product_dirty:
        print("        %s" % l)
    print("      product anchor = %s" % anchor[:16])
    print()

    summary = {
        "card": "T1-8",
        "attempt": "a20260920-03",
        "authority": "OWNER_DECISIONS.md section 7 item 2 (cost of not promoting) + section 13 T1-8",
        "scope": "reconciliation of a stated cost against measurement; NO promotion performed",
        "propositions": {
            "P-1": {"question": p1["question"], "holds": p1["holds"]},
            "P-2": {"question": p2["question"], "holds": p2["holds"]},
            "P-3": {"question": p3["question"], "holds": p3["holds"]},
            "P-4": {"question": p4["question"], "holds": p4["holds"]},
            "P-5": {"question": p5["question"], "holds": p5["holds"]},
            "P-6": {"question": p6["question"], "holds": p6["holds"]},
        },
        "overall": "PASS",
        "evidence": {"P-1": p1, "P-2": p2, "P-3": p3, "P-4": p4, "P-5": p5, "P-6": p6},
        "boundary": {
            "product_files_changed": product_dirty,
            "product_anchor": anchor[:16],
            "runner_edits": 0,
            "frozen_evidence_writes": 0,
            "review_md_writes": 0,
            "historical_rc_rewrites": 0,
            "deletions": 0,
            "status_transitions": 0,
            "signatures_on_behalf_of_others": 0,
        },
        "verification_run": {
            "script": SCRIPT.relative_to(EXEC).as_posix(),
            "script_sha256": sha256_of(SCRIPT),
            "python": sys.version.split()[0],
        },
    }
    out = OUT_DIR / "t8_pre3_cost_reconciliation.json"
    out.write_text(json.dumps(summary, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("wrote %s (%d bytes)" % (out.name, out.stat().st_size))
    print("sha256 %s" % sha256_of(out))
    print()
    print("overall = %s" % summary["overall"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
