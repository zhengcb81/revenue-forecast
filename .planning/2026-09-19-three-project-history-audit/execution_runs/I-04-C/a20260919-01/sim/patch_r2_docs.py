"""r2 doc patch: update the F-LK2 numbers in decision.md / handoff.json / review.md.

Run once; writes only inside the attempt directory.
"""

from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DECISION_OLD = ("5. **F-LK2 不可复现性（r2 P3-4）**：同一条无锁对照连续 5 次 = finals `[3, 15, 9, 2, 186]`")
DECISION_NEW = ("5. **F-LK2 不可复现性（r2 P3-4）**：同一条无锁对照连续 5 次（最终证据轮）= finals `[12, 19, 7, 26, 43]`")
DECISION_NOTE_OLD = "复审另一次独立复跑得 34/200（lost 166）。"
DECISION_NOTE_NEW = ("复审另一次独立复跑得 34/200（lost 166）；更早一轮还出现过 **261/200**"
                     "（无锁写本身不是原子的，撕裂/合并写会给出高于增量总数的值）。")
DECISION_TAIL_OLD = "**结论只能是定性的\"无锁必然丢更新\"，任何单一数字都不代表该对照的稳定行为**"
DECISION_TAIL_NEW = ("**结论只能是定性的\"无锁既丢更新、写也不原子\"，任何单一数字都不代表该对照的稳定行为**"
                     "（F-LK2 的断言因此只要求 `final != expected`）")

HANDOFF_OLD = ('"F-LK2_unlocked": "5 runs, finals [3, 15, 9, 2, 186], lost_updates [197, 185, 191, 198, 14]; '
               'the reviewer\'s independent run gave 34/200 (lost 166). QUALITATIVE only: unlocked '
               'read-modify-write always loses updates; no single number is reproducible."')
HANDOFF_NEW = ('"F-LK2_unlocked": "5 runs, finals [12, 19, 7, 26, 43] (final evidence round); the reviewer\'s '
               'independent run gave 34/200; an earlier round even produced 261/200 because the unlocked file '
               'write is itself non-atomic (torn/merged content). QUALITATIVE only: the exact total is never '
               'reproduced and no single number is stable, so the check asserts final != expected."')

REVIEW_OLD = "（finals `[3,15,9,2,186]`）"
REVIEW_NEW = "（最终轮 finals `[12,19,7,26,43]`；更早一轮曾出现 261/200 的撕裂写）"


def patch(path, pairs, required=True):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    for old, new in pairs:
        if old not in text:
            if required:
                print(f"MISS in {os.path.basename(path)}: {old[:60]}")
                return False
            continue
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"patched {os.path.basename(path)}")
    return True


def main():
    ok = True
    ok &= patch(os.path.join(ATTEMPT, "decision.md"), [
        (DECISION_OLD, DECISION_NEW),
        (DECISION_NOTE_OLD, DECISION_NOTE_NEW),
        (DECISION_TAIL_OLD, DECISION_TAIL_NEW),
    ])
    ok &= patch(os.path.join(ATTEMPT, "handoff.json"), [(HANDOFF_OLD, HANDOFF_NEW)])
    ok &= patch(os.path.join(ATTEMPT, "review.md"), [(REVIEW_OLD, REVIEW_NEW)], required=False)
    with open(os.path.join(ATTEMPT, "handoff.json"), "r", encoding="utf-8") as handle:
        json.load(handle)
    print("handoff.json still valid JSON; ok =", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
