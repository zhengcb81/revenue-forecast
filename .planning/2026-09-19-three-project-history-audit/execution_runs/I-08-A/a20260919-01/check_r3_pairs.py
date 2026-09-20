"""r3 independent PAIR check for the I-08-A frozen texts.

Why this exists (reviewer finding): `check_r2_consistency.py` only proves that the
SET of E-numbers used in decision.md / oracle.md is self-consistent with the set
defined in decision.md section 2.5. It does NOT check that an E-number still
carries the SAME code string in both places, so two mutations survive it:

  * mutation A: an oracle NEG row's E-number is repointed to a different code
                (e.g. E21 where E20 belongs);
  * mutation B: two code strings are swapped inside the section 2.5 table itself
                (e.g. E20 and E21 exchange their strings).

This script checks the PAIRS:
  1. code-number -> code-string from decision.md section 2.5;
  2. every "**E##** `string`" occurrence elsewhere in decision.md must agree;
  3. every NEG row's fourth cell in oracle.md must agree.

It also SELF-TESTS: it builds two mutated copies in a scratch directory, reruns
the same pair logic on them, and asserts that both mutations are detected. That
self-test is the evidence that this checker has the capability the reviewer
measured as missing.

Usage:  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B check_r3_pairs.py
Exit 0 = clean AND both mutations detected. Exit 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
SCRATCH = ATTEMPT / "iso" / "scratch" / "r3_mutations"

CODE_ROW = re.compile(r"\|\s*(E\d\d)\s*\|\s*`([a-z0-9_]+)`\s*\|")
# a normative reference looks like:  **E20** `provider_key_untrusted`  or  **E20**）
REF = re.compile(r"\*\*(E\d\d)\*\*\s*`([a-z0-9_]+)`")


def canonical_pairs(decision_text: str) -> dict[str, str]:
    start = decision_text.index("### 2.5 规范错误码表")
    end = decision_text.index("**两个参数、一个未决**")
    return {code: name for code, name in CODE_ROW.findall(decision_text[start:end])}


def oracle_neg_pairs(oracle_text: str) -> list[tuple[str, str, str]]:
    """(row_id, E-number, code string) for every NEG row carrying a canonical code."""
    out: list[tuple[str, str, str]] = []
    for line in oracle_text.splitlines():
        if not line.startswith("| NEG-"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        row_id = cells[0]
        num = re.search(r"\b(E\d\d)\b", cells[3])
        code = re.search(r"`([a-z0-9_]+)`", cells[3])
        if num and code:
            out.append((row_id, num.group(1), code.group(1)))
    return out


def check(decision_text: str, oracle_text: str, label: str) -> list[str]:
    problems: list[str] = []
    pairs = canonical_pairs(decision_text)
    print(f"[{label}] canonical_pairs={len(pairs)}")

    # duplicate E-numbers inside the canonical table
    nums = CODE_ROW.findall(decision_text[decision_text.index("### 2.5 规范错误码表"):
                                                decision_text.index("**两个参数、一个未决**")])
    seen: set[str] = set()
    for num, _ in nums:
        if num in seen:
            problems.append(f"duplicate canonical row {num}")
        seen.add(num)

    # 1+2. decision-side references must agree with the canonical table
    for num, name in REF.findall(decision_text):
        if num not in pairs:
            problems.append(f"decision references undefined {num} `{name}`")
        elif pairs[num] != name:
            problems.append(
                f"decision pair mismatch: {num} is `{pairs[num]}` in the table "
                f"but referenced as `{name}`"
            )

    # 3. oracle NEG rows must agree with the canonical table
    for row_id, num, name in oracle_neg_pairs(oracle_text):
        if num not in pairs:
            problems.append(f"{row_id} references undefined {num} `{name}`")
        elif pairs[num] != name:
            problems.append(
                f"{row_id} pair mismatch: {num} is `{pairs[num]}` in the table "
                f"but the row says `{name}`"
            )
    return problems


def mutate_a(decision_text: str, oracle_text: str) -> tuple[str, str]:
    """Repoint one oracle NEG row to a different code number (keep the string)."""
    target = "| NEG-REPLAY-1 |"
    for line in oracle_text.splitlines():
        if line.startswith(target) and "E09" in line:
            mutated = oracle_text.replace(
                line, line.replace("**E09**", "**E20**", 1), 1
            )
            return decision_text, mutated
    raise AssertionError("mutation A anchor not found")


def mutate_b(decision_text: str, oracle_text: str) -> tuple[str, str]:
    """Swap the code strings of two canonical rows inside section 2.5."""
    start = decision_text.index("### 2.5 规范错误码表")
    end = decision_text.index("**两个参数、一个未决**")
    section = decision_text[start:end]
    swapped = (
        section.replace("`provider_key_untrusted`", "`__TMP__`", 1)
        .replace("`issuer_key_binding_mismatch`", "`provider_key_untrusted`", 1)
        .replace("`__TMP__`", "`issuer_key_binding_mismatch`", 1)
    )
    if swapped == section:
        raise AssertionError("mutation B could not swap the two code strings")
    return decision_text[:start] + swapped + decision_text[end:], oracle_text


def main() -> int:
    decision_text = (ATTEMPT / "decision.md").read_text(encoding="utf-8")
    oracle_text = (ATTEMPT / "oracle.md").read_text(encoding="utf-8")

    real = check(decision_text, oracle_text, "REAL")
    print(f"[REAL] pair_problems={len(real)}")
    for problem in real:
        print("  PROBLEM " + problem)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    detections: dict[str, bool] = {}
    for name, mutator in (("A_repoint_one_row", mutate_a), ("B_swap_two_rows", mutate_b)):
        dec_m, ora_m = mutator(decision_text, oracle_text)
        (SCRATCH / f"{name}.decision.md").write_text(dec_m, encoding="utf-8")
        (SCRATCH / f"{name}.oracle.md").write_text(ora_m, encoding="utf-8")
        found = check(dec_m, ora_m, name)
        detections[name] = bool(found)
        print(f"[{name}] pair_problems={len(found)} detected={bool(found)}")
        for problem in found[:4]:
            print("  DETECTED " + problem)

    ok = not real and all(detections.values())
    print(
        "PAIR_CHECK_RESULT="
        + ("clean_and_both_mutations_detected" if ok else "FAILED")
    )
    print("detections=" + str(detections))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
