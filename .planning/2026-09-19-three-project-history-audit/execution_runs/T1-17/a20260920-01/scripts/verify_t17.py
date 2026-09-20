#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
T1-17 verifier.

Card:  T1-17  (OWNER_DECISIONS.md section 13, TIER-1)
Ruling text (verbatim):
    T1-17 | section 4: I-04-C C2 (OPEN-3) |
    ADOPTED: the naming/boundary acceptance of `lock_budget_for(x)=min(x,60)`
    is frozen per the current formulation, and `worker-pause` STAYS INSIDE the
    lock (the card does not block sign-off).

Ruling class: interpretation confirmation.

What this card is actually for
------------------------------
The ruling does NOT order a write. It (a) ADOPTS the reviewer's naming/scope
reading for the 60 s waiting cap, and (b) DECIDES the one item that was
genuinely open -- whether `worker-pause` may stay inside the lock -- by saying
"stays inside the lock".

So the real work is to establish, on disk, three things:

  R-1  The presence leg. The ruling's OWN two halves have a home in the frozen
       card text, and the `min(x,60)` formulation is the single governing
       formula (no competing `min(10,...)` survives as live text).
  R-2  The absence leg. The FORBIDDEN form is absent: no live text asserts
       `worker-pause` is OUTSIDE the lock, and no live text still promotes the
       superseded `10` cap as the governing value.
  R-3  The gate leg. Every registered carrier of C2/OPEN-3 is internally
       consistent about status: it is an owner ruling item that does NOT block
       sign-off, and the implementer did NOT self-rule on it.
  R-4  Additivity. The C1/OPEN-3 corrections landed append-only: the pre-change
       blobs survive as prefixes.

Why R-1 and R-2 are separate legs (the recurring lesson of this project)
-----------------------------------------------------------------------
A criterion that cannot tell "the ruling's adopted form" from "a stale
alternative the ruling superseded" will either pass everything or fail
everything. R-1 asks "is the adopted form present and governing"; R-2 asks
"is the superseded/forbidden form really gone as live text". One leg alone is
worthless: presence without absence lets a contradiction survive; absence
without presence lets a deletion masquerade as a resolution.

History discipline
------------------
This project keeps superseded values in place as history (T1-12 form (1)).
Therefore "the 10 cap is absent" cannot mean the character sequence `min(10`
appears nowhere -- it appears inside the correction notes that SAY it is
withdrawn. R-2 must therefore test for the FORBIDDEN FORM (a live assertion),
not for a substring. A substring criterion here would be exactly the misfire
class already logged as this project's 6th-10th same-root lesson.

Exit codes: 0 = PASS, 1 = harness failure, 2 = undetermined/precondition,
            3 = expectations not met.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

EXEC = pathlib.Path(__file__).resolve().parent.parent          # .../T1-17/a20260920-01
# Depth check, counted from EXEC (= .../execution_runs/T1-17/a20260920-01):
#   parents[0]=T1-17  parents[1]=execution_runs  parents[2]=<audit dir>
#   parents[3]=.planning  parents[4]=<repo root>
# NOTE: count from EXEC, not from __file__. The file sits one level deeper
# (inside scripts/), so a depth that is right for the file is off by one here.
# Getting this wrong yields an EMPTY pre-image from `git show`, which then gets
# misreported as a content defect -- the T1-13 failure mode. The guard below is
# exactly what catches it.
REPO = EXEC.parents[4]                                          # repo root
PLAN = ".planning/2026-09-19-three-project-history-audit"
CARD = f"{PLAN}/execution_runs/I-04-C/a20260919-01"
OD_PATH = f"{PLAN}/OWNER_DECISIONS.md"


def _fail(msg):
    print(f"FATAL: {msg}")
    return 2


def main():
    # ---- path sanity guard (the T1-13 lesson: a wrong REPO yields an EMPTY
    #      pre-image and the emptiness is then misreported as a content defect)
    sanity = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                            cwd=str(REPO), capture_output=True)
    if sanity.returncode != 0:
        return _fail("REPO is not inside a git work tree")
    toplevel = pathlib.Path(sanity.stdout.decode("utf-8", "replace").strip())
    if toplevel != REPO:
        return _fail(f"REPO != git toplevel ({REPO} vs {toplevel})")

    card_dir = REPO / CARD
    if not card_dir.is_dir():
        return _fail(f"card dir missing: {card_dir}")

    def read(rel):
        return (card_dir / rel).read_bytes().decode("utf-8")

    decision = read("decision.md")
    oracle = read("oracle.md")
    review = read("review.md")
    handoff_raw = read("handoff.json")

    try:
        handoff = json.loads(handoff_raw)
    except Exception as exc:
        return _fail(f"handoff.json is not parseable JSON: {exc}")

    results = {}
    notes = []

    # ======================= R-1  presence leg =======================
    # (a) the two halves of the ruling have a home in the frozen card text.
    r1a_ok = True
    r1a_where = []
    if "lock_budget_for(相位预算) = min(相位预算, 60)" in oracle:
        r1a_where.append("oracle.md: the governing formula is min(phase_budget, 60)")
    else:
        r1a_ok = False
    if re.search(r"lock_budget_for\(x\)\s*=\s*min\(x,\s*60\)", decision):
        r1a_where.append("decision.md: lock_budget_for(x)=min(x,60) present")
    else:
        r1a_ok = False
    if re.search(r"锁预算[^\n]{0,40}min\(相位预算,\s*60\)", decision) or \
       re.search(r"min\(相位预算,\s*60\)", decision):
        r1a_where.append("decision.md: min(phase_budget, 60) present")
    else:
        r1a_ok = False

    # (b) the `worker-pause`-inside-the-lock half is asserted, not merely named.
    #     The card's ADR-11 text says worker-status AND worker-pause are now
    #     actions taken AFTER entering the critical section.
    r1b_ok = bool(re.search(
        r"worker-pause[^\n]{0,40}现在是\s*\*\*进入临界区后\*\*\s*的动作", decision))
    if r1b_ok:
        r1a_where.append("decision.md ADR-11: worker-pause is an action AFTER entering the critical section")

    # (c) how many competing `min(10` LIVE formulas remain? They must be zero
    #     as governing text.
    #
    #     Shape-matching note (this is where a naive criterion misfires): the
    #     sequence `min(10` legitimately appears in TWO historical forms --
    #       (i)  inside a "withdrawn" correction note on the same line, and
    #       (ii) inside the "old text (already changed)" COLUMN of the
    #            F-I04C-13 cleanup table, whose header declares that column's
    #            semantics.
    #     Both are history per T1-12 form (1), not live governance. A criterion
    #     that just greps the substring would report two violations that do not
    #     exist -- the same misfire class already logged in this project.
    d_lines = decision.split("\n")
    o_lines = oracle.split("\n")

    # Detect whether a line falls inside the F-I04C-13 cleanup table by
    # scanning for its header and tracking until the table ends.
    in_cleanup_table = set()
    start = None
    for i, line in enumerate(d_lines, 1):
        if "F-I04C-13" in line and "正文旧值清理" in line:
            start = i
            continue
        if start is not None:
            if line.startswith("|"):
                in_cleanup_table.add(i)
            elif line.strip() == "" and i > start + 2:
                if i - 1 in in_cleanup_table:
                    break

    live_10 = []
    for name, lines in (("decision.md", d_lines), ("oracle.md", o_lines)):
        for i, line in enumerate(lines, 1):
            if "min(10" not in line:
                continue
            same_line_disowns = bool(re.search(
                r"旧文本|作废|更正|已改|不一致|stale|superseded|v1\.3|已被.*取代", line))
            in_history_table = (name == "decision.md" and i in in_cleanup_table)
            if not (same_line_disowns or in_history_table):
                live_10.append(f"{name}:{i}")
    r1c_ok = (len(live_10) == 0)
    if not r1c_ok:
        notes.append("live (un-disowned) min(10...) occurrences: " + ", ".join(live_10))
    else:
        notes.append(
            f"min(10...) retained as history at decision.md rows "
            f"{sorted(in_cleanup_table)[:2]}..{sorted(in_cleanup_table)[-1:]} "
            f"(F-I04C-13 'old text' column, per T1-12 form (1)) -- not live governance")

    results["R-1"] = {
        "claim": "the ruling's two halves are present, and min(x,60) is the single governing formula",
        "holds": bool(r1a_ok and r1b_ok and r1c_ok),
        "evidence": r1a_where,
        "un_disowned_min10_sites": live_10,
    }

    # ======================= R-2  absence leg =======================
    # The forbidden form: any live text asserting worker-pause is OUTSIDE the
    # lock. We must not count negations ("is NOT outside") nor conditionals
    # ("if ... wants ... outside") nor the explicitly-rejected alternatives.
    forbidden_re = re.compile(
        r"(worker-pause|`worker-pause`)[^\n]{0,80}"
        r"(不再|不)\s*(留在|在)\s*锁内|"
        r"(worker-pause|`worker-pause`)[^\n]{0,80}(移出|挪出|outside)[^\n]{0,20}锁",
        re.I)
    r2_hits = []
    for name, text in (("decision.md", decision), ("oracle.md", oracle),
                       ("review.md", review)):
        for i, line in enumerate(text.split("\n"), 1):
            if forbidden_re.search(line):
                # exclude if the same window carries a denial or a conditional
                if re.search(r"(?:不|未|never|NOT|拒绝|refused|否决|不接受)", line) and \
                   re.search(r"(?:不|未|never|NOT)\s*(?:允许|再|会)", line):
                    continue
                r2_hits.append(f"{name}:{i}")
    r2a_ok = (len(r2_hits) == 0)

    # Second half of the absence leg: no LIVE text still presents 10 as the
    # governing cap. (Same predicate as R-1(c), asserted separately because it
    # is a distinct claim: "the superseded value is not live".)
    r2b_ok = r1c_ok

    results["R-2"] = {
        "claim": "the forbidden forms are absent: no live text puts worker-pause outside the lock, and no live text still carries the superseded 10 cap",
        "holds": bool(r2a_ok and r2b_ok),
        "evidence": {
            "forbidden_live_assertions": r2_hits,
            "superseded_10_cap_still_live": (not r2b_ok),
            "note": "the sequence `min(10` DOES occur inside correction notes; those are history per T1-12 form (1) and are deliberately not counted",
        },
    }

    # ======================= R-3  gate leg =======================
    gates = handoff.get("owner_gates", [])
    gate0 = next((g for g in gates if g.get("gate") == "OPEN-3"), None)
    rcc = handoff.get("review_carry_conditions", {})
    c2 = rcc.get("C2_OPEN3_owner_gate") or rcc.get("C2") or {}

    r3_checks = {
        "owner_gates[OPEN-3] registered": gate0 is not None,
        "owner_action_required true": bool(gate0 and gate0.get("owner_action_required") is True),
        "does NOT block sign-off": bool(gate0 and gate0.get("blocks_signoff") is False),
        "carry_condition C2": bool(gate0 and gate0.get("carry_condition") == "C2"),
        "fallback_until_ruled records the frozen 60": bool(
            gate0 and "60" in str(gate0.get("fallback_until_ruled", ""))),
        "blocked_by is empty": (handoff.get("blocked_by") == []),
        "review.md records 'does not block this sign-off'": bool(
            re.search(r"C2\s*=\s*OPEN-3[^\n]{0,120}不阻塞本次签收", review)),
        "review.md records 'owner has not ruled; implementation keeps 60'": bool(
            re.search(r"owner 未裁前实现继续使用冻结值\s*60", review)),
    }
    r3_ok = all(r3_checks.values())
    if not r3_ok:
        notes.append("R-3 failed sub-checks: " +
                     ", ".join(k for k, v in r3_checks.items() if not v))

    # The implementer must NOT have self-ruled: the gate text must ask the
    # owner, not announce a decision.
    r3_asks_owner = bool(re.search(
        r"(请\s*owner\s*裁定|owner\s*裁定项|OWNER RULING item|待裁)", decision + review))
    r3_checks["the card ASKS the owner, it does not self-rule"] = r3_asks_owner
    r3_ok = all(r3_checks.values())

    results["R-3"] = {
        "claim": "every registered C2/OPEN-3 carrier is consistent: it is an owner ruling item that does not block sign-off, and the implementer did not self-rule",
        "holds": bool(r3_ok),
        "evidence": r3_checks,
    }

    # ======================= R-4  additivity =======================
    # The C1/OPEN-3 corrections must have landed append-only. We prove it the
    # only way that is sound: the current on-disk bytes must have the pre-change
    # blob as a PREFIX (strictly trailing addition => nothing was deleted or
    # rewritten anywhere).
    add = {}
    for rel in ("decision.md", "oracle.md", "review.md"):
        blob = subprocess.run(["git", "show", f"HEAD:{CARD}/{rel}"],
                              cwd=str(REPO), capture_output=True)
        if blob.returncode != 0 or not blob.stdout:
            return _fail(f"could not read pre-image for {rel}")
        pre, now = blob.stdout, (card_dir / rel).read_bytes()
        add[rel] = {
            "pre_bytes": len(pre),
            "now_bytes": len(now),
            "delta_bytes": len(now) - len(pre),
            "prefix_preserved": now[: len(pre)] == pre,
            "pre_sha256": hashlib.sha256(pre).hexdigest(),
            "now_sha256": hashlib.sha256(now).hexdigest(),
        }
    # handoff.json is JSON: byte-level append is not the right criterion there.
    # (This is the shape-matching rule again: use the criterion that fits the
    #  object. For a JSON file the meaningful question is whether the ruling
    #  item is REGISTERED and the file parses -- R-3 already covers that.)
    r4_ok = all(v["prefix_preserved"] for v in add.values())
    results["R-4"] = {
        "claim": "the C1/OPEN-3 text corrections landed append-only (pre-change bytes survive as prefixes)",
        "holds": bool(r4_ok),
        "evidence": add,
        "shape_note": "handoff.json is JSON; append-only is not its coherence criterion -- R-3 covers its registration instead",
    }

    # =======================  production anchor =======================
    # Shape-matching note: the registered anchor is a SHA-256 of the file's
    # on-disk bytes. `git hash-object` returns a git BLOB hash (SHA-1 of
    # "blob <len>\0" + content), which is a different quantity -- comparing the
    # two compares unlike things and reports a drift that does not exist. The
    # criterion must hash the file with the same function the anchor was made
    # with.
    anchor_path = REPO / "scripts/model_registry.py"
    if not anchor_path.is_file():
        return _fail(f"production anchor missing: {anchor_path}")
    anchor_sha = hashlib.sha256(anchor_path.read_bytes()).hexdigest()
    EXPECTED_ANCHOR = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
    anchor_ok = (anchor_sha == EXPECTED_ANCHOR)

    # product files touched?
    diff = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--", ".", ":(exclude).planning"],
        cwd=str(REPO), capture_output=True)
    product_touched = [x for x in diff.stdout.decode().splitlines() if x.strip()]

    # =======================  verdict =======================
    all_ok = all(results[k]["holds"] for k in ("R-1", "R-2", "R-3", "R-4")) \
        and anchor_ok and not product_touched

    print("=" * 72)
    print("T1-17 verification -- oracle.md / I-04-C C2 (OPEN-3) interpretation scope")
    print("=" * 72)
    for k in ("R-1", "R-2", "R-3", "R-4"):
        v = results[k]
        print(f"\n[{k}] {'PASS' if v['holds'] else 'FAIL'}  {v['claim']}")
        if k == "R-3":
            for kk, vv in v["evidence"].items():
                print(f"      {'ok ' if vv else 'BAD'}  {kk}")
    print(f"\n[anchor] {'PASS' if anchor_ok else 'FAIL'}  "
          f"scripts/model_registry.py = {anchor_sha[:16]}...")
    print(f"[scope ] {'PASS' if not product_touched else 'FAIL'}  "
          f"product files changed outside .planning: {len(product_touched)}")

    if notes:
        print("\nnotes:")
        for n in notes:
            print("  -", n)

    print("\n" + "=" * 72)
    print("overall =", "PASS" if all_ok else "FAIL")

    payload = {
        "card": "T1-17",
        "attempt": "a20260920-01",
        "kind": "interpretation_confirmation",
        "ruling": "OWNER_DECISIONS.md section 13 T1-17: ADOPTED -- the naming/scope "
                  "acceptance of lock_budget_for(x)=min(x,60) is frozen per the current "
                  "formulation, and worker-pause STAYS INSIDE the lock (does not block sign-off)",
        "propositions": results,
        "production_anchor": {
            "path": "scripts/model_registry.py",
            "sha256": anchor_sha,
            "expected": EXPECTED_ANCHOR,
            "matches": anchor_ok,
        },
        "product_files_changed": product_touched,
        "overall": "PASS" if all_ok else "FAIL",
    }
    out_path = EXEC / "t17_i04c_c2_open3_scope.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("wrote", out_path.relative_to(REPO))
    return 0 if all_ok else 3


if __name__ == "__main__":
    sys.exit(main())
