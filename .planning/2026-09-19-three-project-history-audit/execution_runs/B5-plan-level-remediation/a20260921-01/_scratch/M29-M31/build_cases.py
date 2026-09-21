"""Build (or rebuild) the four arm scratch trees for REM-21 batch M29-M31.

Read-only with respect to the historical tree: every frozen file is *copied*, the
mutation is applied to the scratch copy only, and the frozen original is re-hashed
afterwards to prove it was not touched.

Arms (PROPAGATION_CONTRACT.md section 5):
  E  frozen cases.json, unchanged           -> new runner must give rc=0
  F  first negative case's expected -> "ValueError"  -> new runner must give rc=3
  B  same mutated cases.json as F, OLD runner        -> old runner must give rc=0 (fabricated green)
  G  first negative case's expected key DELETED      -> new runner must give rc=2

The mutated case is the first negative case (lowest id) whose frozen expected is
"ModelRegistryError".  For M29/M30/M31 that is NEG-CARD (cases[0]).
"""
import hashlib
import json
import os
import shutil
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        "\\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M29-M31")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M29-M31")
ISO = os.path.join(PLAN, "execution_runs", "M29", "a20260919-01", "iso", "checkout_scripts")
CARDS = ["M29", "M30", "M31"]
FROZEN = ["input.json", "cases.json", "oracle.json", "negative_results.json"]
DECOY = "ValueError"


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def frozen_evidence(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)


def dump(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def pick_mutated_case(cases_doc):
    """The first negative case whose frozen expected is ModelRegistryError.

    CONTRACT DEVIATION (recorded, not hidden).  PROPAGATION_CONTRACT.md section 5 says
    "the first negative case (lowest id)".  Those two clauses disagree on this batch:
    under real ASCII ordering '-' (0x2D) < '0' (0x30) < 'A', so sorted(ids)[0] is
    'CONT-BREAK', not 'NEG-CARD'.  The primary clause ("the FIRST negative case" = the
    first entry of the frozen cases array, which is also the order the runner judges
    them in, and which the independent reviewers mutated in M29 review.md P2) is used.
    For M29/M30/M31 that is cases[0] == 'NEG-CARD'; the lexicographic reading would have
    picked 'CONT-BREAK'.  Both candidates raise ModelRegistryError, so either would
    exercise the delta; the deviation is recorded for the reviewer.
    """
    eligible = [c for c in cases_doc["cases"] if c.get("expected") == "ModelRegistryError"]
    if not eligible:
        raise SystemExit("FATAL: no case declares ModelRegistryError")
    return eligible[0]


def main():
    info = {"cards": {}, "isolated_code_root_sha256": {}, "frozen_after_build": {}}
    frozen_before = {c: {f: sha256_file(os.path.join(frozen_evidence(c), f)) for f in FROZEN}
                     for c in CARDS}

    # code_root: one per arm (isolated copy, never the historical iso dir)
    for arm in ("E", "F", "B", "G"):
        dst = os.path.join(SCRATCH, arm, "code_root")
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(ISO, dst)
    for name in sorted(os.listdir(os.path.join(SCRATCH, "E", "code_root"))):
        info["isolated_code_root_sha256"][name] = sha256_file(
            os.path.join(SCRATCH, "E", "code_root", name))

    for card in CARDS:
        src = frozen_evidence(card)
        frozen_cases = json.load(open(os.path.join(src, "cases.json"), encoding="utf-8"))
        target = pick_mutated_case(frozen_cases)
        target_id = target["id"]

        # frozen case order + the exact first-negative selection rule
        order = [c["id"] for c in frozen_cases["cases"]]
        if order[0] != target_id:
            raise SystemExit("FATAL: first case %s != selected %s" % (order[0], target_id))

        cardinfo = {"frozen_cases_sha256": frozen_before[card]["cases.json"],
                    "mutated_case": target_id,
                    "mutated_case_frozen_expected": target["expected"],
                    "mutated_case_frozen_index": frozen_cases["cases"].index(target),
                    "decoy": DECOY,
                    "blanket_rewrite_case_count": len(frozen_cases["cases"]),
                    "lexicographic_first_eligible_id": sorted(
                        c["id"] for c in frozen_cases["cases"]
                        if c.get("expected") == "ModelRegistryError")[0],
                    "frozen_case_order": order,
                    "arms": {}}

        for arm in ("E", "F", "B", "G"):
            ev = os.path.join(SCRATCH, arm, "evidence", card)
            os.makedirs(ev, exist_ok=True)
            for f in FROZEN:
                shutil.copyfile(os.path.join(src, f), os.path.join(ev, f))

            cases_path = os.path.join(ev, "cases.json")
            if arm == "F" or arm == "B":
                doc = json.load(open(cases_path, encoding="utf-8"))
                for case in doc["cases"]:
                    if case["id"] == target_id:
                        case["expected"] = DECOY
                dump(cases_path, doc)
            elif arm == "G":
                doc = json.load(open(cases_path, encoding="utf-8"))
                for case in doc["cases"]:
                    if case["id"] == target_id:
                        del case["expected"]
                dump(cases_path, doc)

            scratch_cases = json.load(open(cases_path, encoding="utf-8"))
            got = [entry.get("expected", "<KEY-ABSENT>") for entry in scratch_cases["cases"]
                   if entry["id"] == target_id][0]
            cardinfo["arms"][arm] = {
                "cases_json_sha256": sha256_file(cases_path),
                "mutated_case_expected_in_scratch": got,
                "runner": "run_card_before.py" if arm == "B" else "run_card.py",
            }

        # blanket-rewrite arm (the reviewers' exact historical experiment: EVERY case -> "ImportError")
        ev = os.path.join(SCRATCH, "H_blanket", "evidence", card)
        os.makedirs(ev, exist_ok=True)
        for f in FROZEN:
            shutil.copyfile(os.path.join(src, f), os.path.join(ev, f))
        cases_path = os.path.join(ev, "cases.json")
        doc = json.load(open(cases_path, encoding="utf-8"))
        for case in doc["cases"]:
            case["expected"] = "ImportError"
        dump(cases_path, doc)
        cardinfo["arms"]["H_blanket"] = {"cases_json_sha256": sha256_file(cases_path),
                                         "mutated_case_expected_in_scratch": "ImportError (all cases)",
                                         "runner": "run_card_before.py"}

        info["cards"][card] = cardinfo

    # code_root for the blanket arm too
    dst = os.path.join(SCRATCH, "H_blanket", "code_root")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(ISO, dst)

    # prove the frozen tree was not touched by this build
    for card in CARDS:
        after = {f: sha256_file(os.path.join(frozen_evidence(card), f)) for f in FROZEN}
        if after != frozen_before[card]:
            raise SystemExit("FATAL: frozen evidence for %s changed during build" % card)
        info["frozen_after_build"][card] = after

    out = os.path.join(SCRATCH, "cases_manifest.json")
    dump(out, info)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    print("\nwritten: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
