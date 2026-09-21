"""REM-21 / B5, batch M13-M16 - scratch fixture builder.

Rebuilds each arm's scratch evidence dir from the FROZEN originals (read-only, never written):
  <PLAN>/execution_runs/<CARD>/a20260919-01/evidence/<CARD>/{input.json,cases.json,oracle.json}

  E : case NEG-CARD's "expected" stays "ModelRegistryError"      (green control)
  F : case NEG-CARD's "expected"  -> "ValueError"                (mutation arm; decoy superclass)
  B : same mutated cases.json as F                               (inertness control, OLD runner)
  G : case NEG-CARD's "expected" key DELETED                     (rc-classification arm)

The mutation is applied by literal text replacement of NEG-CARD's frozen `"expected":
"ModelRegistryError",` line, so nothing else in the document can drift and the rest of the
file stays byte-identical to the frozen revision.  Only the FIRST negative case (lowest id
whose frozen expected is "ModelRegistryError") is mutated.

NOTE: `negative_results.json` is deliberately NOT placed in the scratch evidence dir.  The
runner reads exactly input.json, oracle.json and cases.json from <attempt>/evidence/<CARD>/
and never opens negative_results.json; the historical B unit produced it as an OUTPUT of the
packaging step, not as a runner input.  Leaving it out means the raw process stdout/stderr can
be redirected straight onto the historical file names with no move-aside dance.
"""

from __future__ import annotations

import json
import os
import shutil
import sys

CARDS = ("M13", "M14", "M15", "M16")
ARMS = ("E", "F", "B", "G")
MUTANT_ID = "NEG-CARD"
FROZEN_EXPECTED = "ModelRegistryError"
DECOY = "ValueError"

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M13-M16")

FROZEN_LINE = '   "expected": "%s",\n' % FROZEN_EXPECTED


def frozen_dir(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)


def variant_text(arm, frozen_text):
    if arm in ("E",):
        return frozen_text, "unchanged (frozen)"
    if arm in ("F", "B"):
        # exactly one occurrence: NEG-CARD is the only case declaring the frozen name before the
        # other common negatives, and all cases share the same name -- so we must replace only the
        # FIRST occurrence, which is NEG-CARD's.
        assert frozen_text.count(FROZEN_LINE) >= 1, "frozen expected line not found"
        return frozen_text.replace(FROZEN_LINE, '   "expected": "%s",\n' % DECOY, 1), \
            "NEG-CARD expected -> %s" % DECOY
    if arm == "G":
        assert frozen_text.count(FROZEN_LINE) >= 1, "frozen expected line not found"
        return frozen_text.replace(FROZEN_LINE, "", 1), "NEG-CARD expected key DELETED"
    raise SystemExit("unknown arm " + arm)


def main():
    report = {"cards": {}, "arms": list(ARMS), "mutant_id": MUTANT_ID,
              "frozen_expected": FROZEN_EXPECTED, "decoy": DECOY}
    for card in CARDS:
        src = frozen_dir(card)
        frozen_cases_path = os.path.join(src, "cases.json")
        with open(frozen_cases_path, "r", encoding="utf-8") as handle:
            frozen_text = handle.read()

        # sanity: the frozen document really does declare the frozen name for the mutant id
        doc = json.loads(frozen_text)
        first = None
        for case in doc["cases"]:
            if case.get("expected") == FROZEN_EXPECTED:
                first = case["id"]
                break
        if first != MUTANT_ID:
            raise SystemExit("card %s: first frozen-expected case is %r, expected %r"
                             % (card, first, MUTANT_ID))
        # NEG-CARD's declaration must be the FIRST occurrence of the frozen declaration line, and
        # that occurrence must sit inside the NEG-CARD case object (after its "id" line and before
        # the next case's "id" line), so a single `replace(..., 1)` provably hits that case only.
        marker = '"id": "%s"' % MUTANT_ID
        at = frozen_text.index(FROZEN_LINE)
        start = frozen_text.index(marker)
        nexts = [frozen_text.find('"id": "', start + len(marker))]
        nxt = nexts[0] if nexts[0] != -1 else len(frozen_text)
        if not (start < at < nxt):
            raise SystemExit("card %s: the frozen declaration line does not first occur inside %s"
                             % (card, MUTANT_ID))

        entry = {"frozen_first_expected_case": first, "arms": {}}
        for arm in ARMS:
            dst = os.path.join(SCRATCH, arm, "evidence", card)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            os.makedirs(dst)
            for name in ("input.json", "oracle.json"):
                shutil.copyfile(os.path.join(src, name), os.path.join(dst, name))
            text, note = variant_text(arm, frozen_text)
            with open(os.path.join(dst, "cases.json"), "w",
                      encoding="utf-8", newline="\n") as handle:
                handle.write(text)

            # verify what we actually wrote
            written = json.load(open(os.path.join(dst, "cases.json"), "r", encoding="utf-8"))
            mutant = [c for c in written["cases"] if c.get("id") == MUTANT_ID][0]
            declared = mutant.get("expected", "<KEY ABSENT>")
            entry["arms"][arm] = {
                "note": note,
                "mutant_expected_present": "expected" in mutant,
                "mutant_expected": declared,
                "case_count": len(written["cases"]),
                "other_cases_unchanged": all(
                    c.get("expected") == FROZEN_EXPECTED
                    for c in written["cases"] if c.get("id") != MUTANT_ID),
            }
        report["cards"][card] = entry

    sys.stdout.write(json.dumps(report, indent=1, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
