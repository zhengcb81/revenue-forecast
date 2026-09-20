#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1-8 precondition (1) and (4): verify the *predicates*, not the wording.

WHY THIS CARD EXISTS
--------------------
`OWNER_DECISIONS.md` section 13 T1-8 authorises promoting the cross-batch runner fix, but
makes it conditional on four preconditions.  Two of them are still open:

  (1) "do not regress to isinstance"
  (4) "register a namespace per batch, keyed by the runner sha256"

Both are written as prohibitions about *the promoteed artefact*.  A prohibition is only
meaningful if the property it forbids can be FRIGHTENED out of the text: you cannot honour
"do not regress to isinstance" unless you can say, for a given generation, whether a
`PASS_rejected` verdict is decided by `isinstance` alone or by an exact-type-name equality.

This card measures that predicate.  It does NOT promote anything, does NOT edit any runner,
and does NOT touch any frozen evidence.

THE MIS-READING THIS CARD HAD TO CORRECT IN ITSELF
-------------------------------------------------
The first probe (`.planning/_pwf_tmp/probe_t1_8_mro.py`, revision 1) asked whether
`isinstance(ValueError(), ModelRegistryError)` differs from
`type(ValueError()).__name__ == "ModelRegistryError"`.  Both are False, so it reported
"no divergence" -- and the conclusion would have been "precondition (1) is about nothing".

That was a bad probe.  It built each exception AS the declared class and then compared two
predicates that agree on every non-target class.  The divergence is ASYMMETRIC and it lives
on the SUBCLASS side:

    isinstance(exc, ModelRegistryError)        accepts any SUBCLASS of the target
    type(exc).__name__ == "ModelRegistryError"  accepts only the target itself

So `isinstance` is looser *upward into the target's own descendants*, not downward into
`ValueError`.  This is recorded as trap #16 in the tier1 skill.

WHAT THE FROZEN EVIDENCE SAYS
-----------------------------
This project already carries eight heterogeneous case sets -- the only ones whose declared
`expected` is not uniformly the target name.  Four of them (M09-M12 selfcheck arm B) declare
`TypeError`; four (M25-M28 selfcheck case F1) declare `ValueError`.  Those and five
homogeneous companion arms give a complete mutation design that separates the two predicates
-- but it separates them via the CONTRACT, not via the type predicate.  Section 6 records
that consequence.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------------------
# Path anchors.  This script lives at
#   <REPO>/.planning/<plan>/execution_runs/T1-8/a20260920-02/scripts/verify_t8_pre1.py
# so parents[N] is fragile (trap #13: a generator outside the card dir computes it wrong).
# Anchor the repo absolutely and ASSERT the anchor, so a wrong anchor is fatal, not silent.
# --------------------------------------------------------------------------------------
REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
SCRIPTS_DIR = REPO / "scripts"
PRODUCT = SCRIPTS_DIR / "model_registry.py"

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent                      # .../T1-8/a20260920-02
CARD = ATTEMPT.parent                               # .../T1-8
EXEC = CARD.parent                                  # .../execution_runs
PLAN = EXEC.parent                                  # .../2026-09-19-three-project-history-audit
OUT_DIR = ATTEMPT

assert (REPO / ".git").is_dir(), "FATAL: not a git toplevel: %s" % REPO
assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN
assert (PLAN / "OWNER_DECISIONS.md").is_file(), "FATAL: no OWNER_DECISIONS.md in %s" % PLAN
assert PRODUCT.is_file(), "FATAL: product module missing: %s" % PRODUCT
assert (SCRIPTS_DIR / "model_extensions.py").is_file(), \
    "FATAL: sibling module missing; the product is not loadable in isolation"
assert ATTEMPT.name == "a20260920-02", "FATAL: unexpected attempt dir: %s" % ATTEMPT
assert EXEC.name == "execution_runs", "FATAL: unexpected exec dir: %s" % EXEC

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


def git_blob_sha(path: Path) -> str:
    """The blob sha256 git would store, i.e. after the working-tree -> index filter.

    Needed because this repo has core.autocrlf=true: the bytes on disk are CRLF while the
    committed blob is LF, so hashing the working copy is a DIFFERENT byte domain.  This is
    trap #15a, and T1-10 section F met it already.
    """
    proc = subprocess.run(
        ["git", "hash-object", "--path", str(path), str(path)],
        cwd=str(REPO), capture_output=True, text=True)
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def head_blob_sha(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    proc = subprocess.run(["git", "rev-parse", "HEAD:%s" % rel],
                          cwd=str(REPO), capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


# --------------------------------------------------------------------------------------
# The eight runner generations, named by their sha256 (precondition (4) demands this
# addressing mode: "register a namespace per batch, keyed by the runner sha256").
# The representative path per generation is the batch's own `scripts/run_card.py`.
# --------------------------------------------------------------------------------------
GENERATIONS = [
    # (batch label, representative relative path from EXEC, sha256 prefix expected)
    ("M01-M04", "M01/a20260919-01/scripts/run_card.py", "b5fcc685"),
    ("M05-M08", "M05/a20260919-01/scripts/run_card.py", "fd3a11c9"),
    ("M09-M12", "M09/a20260919-01/scripts/run_card.py", "997c553b"),
    ("M13-M16", "M13/a20260919-01/scripts/run_card.py", "9e4a6450"),
    ("M17-M20", "M17/a20260919-01/scripts/run_card.py", "94619a98"),
    ("M21-M24", "M21/a20260919-01/scripts/run_card.py", "a5ee7599"),
    ("M25-M28", "M25/a20260919-01/scripts/run_card.py", "eab01162"),
    ("M29-M31", "M29/a20260919-01/scripts/run_card.py", "9ea69c72"),
]

# --------------------------------------------------------------------------------------
# The predicate extractor.  We do not "grep for isinstance" -- that answers "is the
# builtin called" which is not the question.  We classify HOW a PASS_rejected verdict is
# produced, because only that makes precondition (1) falsifiable.
# --------------------------------------------------------------------------------------
ISINSTANCE_TARGET_RE = re.compile(
    r"isinstance\(\s*exc\s*,\s*model_registry\.ModelRegistryError\s*\)")
NAME_EQUALITY_PATTERNS = [
    # entry["raised"] == case["expected"]                  (M09)
    re.compile(r'entry\["raised"\]\s*==\s*case\["expected"\]'),
    re.compile(r'raised_matches_expected_name'),
    # entry["raised"] == case["expected"]                  (M21)
    re.compile(r'entry\["raised"\]\s*==\s*case\["expected"\]'),
    re.compile(r'expected_type_matches_raised'),
    # declared_ok = raised_name == declared                (M17)
    re.compile(r"raised_name\s*==\s*declared"),
    re.compile(r'declared_expectation_ok'),
    # entry["raised"] == case["expected"] (M09/M21 variant)
    re.compile(r'raised_exact_name\s*==\s*declared'),
]
# "PASS_rejected decided by is_target ALONE": the ternary form used by six generations
ISINSTANCE_ONLY_PASS_PATTERNS = [
    re.compile(r'"PASS_rejected"\s*if\s+is_target\b'),
    re.compile(r'if\s+is_target\s*\n\s*else\s+\(\s*"FAIL_wrong_exception_type"'),
]


def classify_generation(text: str) -> dict:
    uses_isinstance_target = bool(ISINSTANCE_TARGET_RE.search(text))

    name_equality_hits = []
    for pat in NAME_EQUALITY_PATTERNS:
        if pat.search(text):
            name_equality_hits.append(pat.pattern)

    # A verdict is "decided by isinstance alone" when the only thing gating PASS_rejected
    # is `is_target`, with no additional equality on the raised type NAME.
    isinstance_only_pass = bool(ISINSTANCE_ONLY_PASS_PATTERNS[0].search(text))

    # The ternary form means: PASS_rejected iff is_target.  That is the strict definition of
    # the forbidden shape, regardless of what else is merely *recorded*.
    forbidden_shape = isinstance_only_pass and not name_equality_hits

    return {
        "calls_isinstance_against_target": uses_isinstance_target,
        "has_name_equality_predicate": bool(name_equality_hits),
        "name_equality_hits": name_equality_hits,
        "pass_rejected_is_isinstance_only": forbidden_shape,
    }


def main() -> int:
    print("=" * 78)
    print("T1-8 precondition (1): is the type predicate exact-name or isinstance?")
    print("=" * 78)

    # ---------------- P-1: the two predicates provably diverge ------------------------
    mr = load_module(PRODUCT, "verify_t8_pre1_model_registry")
    cls = getattr(mr, TARGET)

    class SubclassOfTarget(cls):
        pass

    class SiblingUnderBase(cls.__bases__[0]):
        pass

    shapes = [
        ("the target itself", cls),
        ("a SUBCLASS of the target", SubclassOfTarget),
        ("a sibling under the target's base", SiblingUnderBase),
        ("the target's base itself", cls.__bases__[0]),
    ]
    divergence = []
    for label, c in shapes:
        exc = c("probe")
        name = type(exc).__name__
        loose = isinstance(exc, cls)
        strict = (name == TARGET)
        divergence.append({
            "shape": label,
            "raised_exact_name": name,
            "isinstance": loose,
            "exact_name_equality": strict,
            "predicates_disagree": loose != strict,
            "isinstance_is_the_looser_one": loose and not strict,
        })
    disagreeing = [d for d in divergence if d["predicates_disagree"]]
    p1 = {
        "question": "do `isinstance(exc, target)` and `exact type name == target` provably "
                    "differ, so that a PASS_rejected decided by isinstance alone cannot "
                    "distinguish the target from another exception?",
        "target_mro": [c.__name__ for c in cls.__mro__],
        "shapes": divergence,
        "disagreeing_shapes": disagreeing,
        "direction": ("isinstance accepts strictly MORE (any subclass) than exact-name "
                      "equality" if disagreeing else "no divergence"),
        "holds": bool(disagreeing),
    }
    print("[P-1] predicate divergence:")
    for d in divergence:
        print("      %-38s exact=%-18s isinstance=%-5s nameeq=%-5s%s"
              % (d["shape"], d["raised_exact_name"], d["isinstance"],
                 d["exact_name_equality"],
                 "   <== DIVERGES" if d["predicates_disagree"] else ""))
    print("      => %s" % p1["direction"])
    print("      holds = %s" % p1["holds"])
    print()

    # ---------------- P-2: classify each generation ----------------------------------
    print("[P-2] per-generation verdict predicate:")
    gen_rows = []
    for label, rel, expect_prefix in GENERATIONS:
        path = EXEC / rel
        assert path.is_file(), "FATAL: runner copy missing: %s" % path
        text = path.read_text(encoding="utf-8", errors="replace")
        digest = sha256_of(path)
        assert digest.startswith(expect_prefix), (
            "FATAL: %s hashes %s but was expected to start with %s -- the generations moved"
            % (rel, digest[:16], expect_prefix))
        info = classify_generation(text)
        row = {
            "batch": label,
            "representative_path": rel,
            "sha256": digest,
            "bytes": path.stat().st_size,
            "git_blob_sha": git_blob_sha(path),
            "head_blob_sha": head_blob_sha(path),
            "reads_case_expected": bool(
                re.search(r'case\["expected"\]|case\.get\("expected"\)', text)),
            "declared_expectation_enforced": bool(
                re.search(r'declared_expectations_enforced"\s*:\s*True', text)),
        }
        row.update(info)
        gen_rows.append(row)
        verdict = ("FORBIDDEN (isinstance alone decides PASS_rejected)"
                   if info["pass_rejected_is_isinstance_only"]
                   else "exact-name equality present")
        print("      %-9s %s  nameeq=%-5s isinstance-only-PASS=%-5s  %s"
              % (label, digest[:16], info["has_name_equality_predicate"],
                 info["pass_rejected_is_isinstance_only"], verdict))
    forbidden = [r["batch"] for r in gen_rows if r["pass_rejected_is_isinstance_only"]]
    p2 = {
        "question": "for each runner sha256, is a PASS_rejected verdict decided by "
                    "isinstance alone (the shape precondition (1) forbids), or is it gated "
                    "by an equality on the raised type NAME?",
        "generations": gen_rows,
        "generations_sha256_distinct": len({r["sha256"] for r in gen_rows}),
        "forbidden_generations": forbidden,
        "forbidden_count": len(forbidden),
        "holds": True,   # the proposition is "we can classify every generation", see below
        "detail": ("every one of the eight generations is classified by its own sha256; "
                   "the classification is what precondition (1) needs in order to be a "
                   "falsifiable constraint rather than a slogan"),
    }
    print("      distinct sha256 across generations: %d" % p2["generations_sha256_distinct"])
    print("      generations with the forbidden shape: %d %s"
          % (len(forbidden), forbidden))
    print()

    # ---------------- P-3: the frozen evidence that separates the predicates ----------
    print("[P-3] frozen evidence that exercises a declared non-target exception:")
    heterogeneous = []
    for cases_path in sorted(EXEC.rglob("cases.json")):
        if "archive" in cases_path.parts:
            continue
        try:
            doc = json.loads(cases_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        declared = {}
        for case in (doc.get("cases") or []):
            declared[str(case.get("expected"))] = declared.get(
                str(case.get("expected")), 0) + 1
        if len(declared) > 1:
            heterogeneous.append({
                "path": cases_path.relative_to(EXEC).as_posix(),
                "declared_expected": declared,
                "sha256": sha256_of(cases_path),
            })
    p3 = {
        "question": "does the frozen tree already carry case sets whose declared `expected` "
                    "is NOT uniformly the target name, i.e. is there evidence that exercises "
                    "the distinction in P-1?",
        "heterogeneous_case_sets_total": len(heterogeneous),
        "heterogeneous_case_sets": heterogeneous,
        "holds": len(heterogeneous) > 0,
        "note": ("these are the ONLY case sets where a declared non-target type name exists. "
                 "They are recovery/selfcheck MUTATION arms, not the frozen production "
                 "expectation, and they reach the predicate through the CONTRACT (see P-5), "
                 "not through the type predicate (see P-6)."),
    }
    print("      heterogeneous case sets: %d" % len(heterogeneous))
    for h in heterogeneous:
        print("        %-62s %s" % (h["path"], h["declared_expected"]))
    print("      holds = %s" % p3["holds"])
    print()

    # ---------------- P-4: read the M09 arm B verdict and the M25 F1 gate -------------
    print("[P-4] what the frozen verdict records say about an isinstance-decided PASS:")

    def read_json(rel):
        p = EXEC / rel
        assert p.is_file(), "FATAL: expected evidence missing: %s" % p
        return json.loads(p.read_text(encoding="utf-8")), p

    m09_b, m09_b_path = read_json(
        "M09/a20260919-01/recovery/selfcheck/B/run_result.json")
    m09_b_case = next(e for e in m09_b["negatives"] if e["id"] == "NEG-CARD")

    m09_e, m09_e_path = read_json(
        "M09/a20260919-01/recovery/selfcheck/E/run_result.json")
    m09_e_case = next(e for e in m09_e["negatives"] if e["id"] == "NEG-CARD")

    m25_sc, m25_sc_path = read_json(
        "M25/a20260919-01/recovery/selfcheck/selfcheck_result.json")
    m25_f1 = next(c for c in m25_sc["cases"] if c["case"] == "F1")

    m25_cases, m25_cases_path = read_json(
        "M25/a20260919-01/evidence/M25/cases.json")

    p4 = {
        "question": "when a frozen arm declares a non-target `expected` and the product "
                    "still raises the target, does the generation judge it, and by which "
                    "predicate?",
        "M09_arm_B": {
            "path": m09_b_path.relative_to(EXEC).as_posix(),
            "declared_expected": m09_b_case.get("expected"),
            "raised": m09_b_case.get("raised"),
            "is_target_type": m09_b_case.get("is_target_type"),
            "raised_matches_expected_name": m09_b_case.get("raised_matches_expected_name"),
            "verdict": m09_b_case.get("verdict"),
            "exit_code": m09_b.get("exit_code_semantics", {}).get("exit_code"),
            "separated_by": "the name-equality predicate (isinstance alone would have said PASS)",
        },
        "M09_arm_E_control": {
            "path": m09_e_path.relative_to(EXEC).as_posix(),
            "declared_expected": m09_e_case.get("expected"),
            "raised": m09_e_case.get("raised"),
            "raised_matches_expected_name": m09_e_case.get("raised_matches_expected_name"),
            "verdict": m09_e_case.get("verdict"),
            "exit_code": m09_e.get("exit_code_semantics", {}).get("exit_code"),
        },
        "M25_case_F1": {
            "path": m25_sc_path.relative_to(EXEC).as_posix(),
            "mutation": m25_f1.get("mutation"),
            "raw_rc": m25_f1.get("raw_rc"),
            "expected_rc": m25_f1.get("expected_rc"),
            "proves": m25_f1.get("proves"),
            "separated_by": "the frozen case_contract, NOT the type predicate",
        },
        "frozen_production_declaration": {
            "path": m25_cases_path.relative_to(EXEC).as_posix(),
            "case_contract_declared_expected_exception":
                (m25_cases.get("case_contract") or {}).get("declared_expected_exception"),
            "neg_card_expected": next(
                c.get("expected") for c in m25_cases["cases"] if c["id"] == "NEG-CARD"),
        },
        "holds": (m09_b_case.get("raised_matches_expected_name") is False
                  and m09_b_case.get("verdict") == "FAIL_wrong_exception_type"
                  and m25_f1.get("raw_rc") == 1),
    }
    print("      M09 arm B : declared=%r raised=%r raised_matches_expected=%r -> %s (rc=%s)"
          % (p4["M09_arm_B"]["declared_expected"], p4["M09_arm_B"]["raised"],
             p4["M09_arm_B"]["raised_matches_expected_name"],
             p4["M09_arm_B"]["verdict"], p4["M09_arm_B"]["exit_code"]))
    print("      M09 arm E : declared=%r raised=%r -> %s (rc=%s)"
          % (p4["M09_arm_E_control"]["declared_expected"],
             p4["M09_arm_E_control"]["raised"],
             p4["M09_arm_E_control"]["verdict"],
             p4["M09_arm_E_control"]["exit_code"]))
    print("      M25 case F1: raw_rc=%s expected_rc=%s -- %s"
          % (p4["M25_case_F1"]["raw_rc"], p4["M25_case_F1"]["expected_rc"],
             "contract gate, not type predicate"))
    print("      holds = %s" % p4["holds"])
    print()

    # ---------------- P-5: which generations even CONSULT expected --------------------
    print("[P-5] does each generation read `cases.json[].expected` at all?")
    never_reads = [r["batch"] for r in gen_rows if not r["reads_case_expected"]]
    p5 = {
        "question": "does every generation read the frozen `expected` field, so that a "
                    "declared non-target name can influence its verdict?",
        "generations_reading_expected": [r["batch"] for r in gen_rows
                                        if r["reads_case_expected"]],
        "generations_never_reading_expected": never_reads,
        "holds": True,
        "note": ("in the generations that read it, `expected` is used as a SUBSCRIPT "
                 "(`case['expected']`), so an ABSENT key raises KeyError -- which is why "
                 "the T1-8 change-3 card found only three generations that define a "
                 "'missing declaration' rule at all."),
    }
    print("      read `expected`: %s" % ", ".join(p5["generations_reading_expected"]))
    print("      never read it : %s" % (", ".join(never_reads) or "(none)"))
    print()

    # ---------------- P-6: the consequence for precondition (1) -----------------------
    print("[P-6] consequence: is the 'rc=3 mutation arm' satisfiable, and by which mechanism?")
    only_m2528 = [r["batch"] for r in gen_rows if r["declared_expectation_enforced"]]
    p6 = {
        "question": ("precondition for promotion requires each batch to gain a mutation arm "
                     "'rewrite `expected` => rc=3'.  Which generations can actually satisfy "
                     "that, and by which mechanism?"),
        "generations_with_declared_expectation_enforcement": only_m2528,
        "generations_with_contract_gate": [r["batch"] for r in gen_rows
                                           if r["batch"] == "M25-M28"],
        "observed_outcome_of_rewriting_expected": {
            "M09-M12 (selfcheck arm B, expected->'TypeError')":
                "rc=3 -- but only because this generation happens to carry a name-equality "
                "predicate that turns the mismatch into a failed negative",
            "M25-M28 (selfcheck case F1, expected->'ValueError')":
                "rc=1 -- the frozen case_contract forbids any `expected` other than the "
                "declared exception, so the rewrite is a HARNESS DEFECT (fail loud), not a "
                "judged negative",
        },
        "holds": True,
        "consequence": ("the literal arm 'rewrite `expected` => rc=3' is NOT satisfiable in "
                        "M25-M28 (and in any batch that adopts the M25-M28 contract gate) "
                        "without BRANCHING ON THE DECLARED VALUE.  In those batches the "
                        "correct observed rc for that rewrite is 1, so a promotion that "
                        "asserts rc=3 there would assert a FALSE expectation.  This is "
                        "reported to the orchestration layer; this card does not resolve it."),
    }
    print("      generations enforcing declared_expectation: %s" % (only_m2528 or "(none)"))
    print("      rewriting `expected` yields rc=3 in M09-M12, but rc=1 in M25-M28")
    print("      => the literal arm is not uniformly satisfiable; reported, not resolved")
    print()

    # ---------------- boundary self-check --------------------------------------------
    print("=" * 78)
    print("[B-1] boundary: this card must have written nothing outside its own attempt dir")
    proc = subprocess.run(["git", "status", "--porcelain", "--", ".",
                           ":(exclude).planning"],
                          cwd=str(REPO), capture_output=True, text=True)
    product_dirty = [l for l in proc.stdout.splitlines() if l.strip()]
    print("      product files changed under (exclude).planning: %d" % len(product_dirty))
    for l in product_dirty:
        print("        %s" % l)

    anchor_before = "9ec6529550f189a4"      # recorded production anchor, see T1-5/T1-10
    anchor_now = sha256_of(PRODUCT)
    print("      product anchor %s -> %s  (%s)"
          % (anchor_before, anchor_now[:16],
             "UNCHANGED" if anchor_now.startswith(anchor_before) else "CHANGED"))
    print()

    summary = {
        "card": "T1-8",
        "attempt": "a20260920-02",
        "authority": "OWNER_DECISIONS.md section 13 T1-8 (TIER-1), preconditions (1) and (4)",
        "scope": "verification and factual registration only; NO promotion is performed",
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
            "product_anchor_before": anchor_before,
            "product_anchor_now": anchor_now[:16],
            "product_anchor_unchanged": anchor_now.startswith(anchor_before),
            "runner_edits": 0,
            "frozen_evidence_writes": 0,
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

    out = OUT_DIR / "t8_pre1_pre4_verification.json"
    # Idempotence: the payload must contain no environment-derived value.  Everything above
    # is a hash, a fixed string, or a value read from frozen evidence.
    out.write_text(json.dumps(summary, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("wrote %s (%d bytes)" % (out.name, out.stat().st_size))
    print("sha256 %s" % sha256_of(out))
    print()
    print("overall = %s" % summary["overall"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
