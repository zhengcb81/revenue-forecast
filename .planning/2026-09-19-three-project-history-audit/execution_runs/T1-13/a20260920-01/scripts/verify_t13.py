#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""T1-13 — verify the authorised edit to I-09-A `review.md:80`.

OWNER_DECISIONS.md T1-13 (TIER-1) authorises exactly one edit and names three
boundaries:

    授权改该行出处列以实现闭合。
    边界：只改该行的**出处列**，不动任何数值、不动 reviewer 其余字节，
          改动须附前像 hash + diff。

So there are three boundaries, and each is checked as a SEPARATE proposition.
They are not redundant: "only the citation column changed" and "no number
changed" can both fail independently (e.g. a new number could be introduced in
the citation column, or a number could change while the column looks the same).

  B-1  ONLY THE CITATION CELL CHANGED — the row's other cells are byte-identical
  B-2  NO NUMBER CHANGED IN THE METRIC CELL — the cell that carries the
       measured values is untouched, and the *set* of metric values is
       preserved (this is the boundary the owner actually cares about: the
       numbers 148/142/132/126/124/270 are the measured claims)
  B-3  NO OTHER REVIEWER BYTE CHANGED — every other line in review.md is
       byte-identical; line count unchanged
  B-4  THE EDIT IS THE ONE `errata.md` PRESCRIBED — the pre-image text is the
       old wording, so this is a repair of a declared defect and not a silent
       rewrite of something that was already correct

B-4 matters because of the direction of trust: editing a reviewer's bytes is
only legitimate when the pre-image is *known to be defective*.  The pre-image
must therefore be shown to still carry the defect that `errata.md` section R-1
declared, otherwise this would be an unexplained alteration.

Output: a JSON record; the diff and the pre-image hash are written alongside it
(the owner required them as attachments).
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                        # .../execution_runs/T1-13/a20260920-01
EXEC = RUN.parent.parent                 # .../execution_runs
I09A = EXEC / "I-09-A" / "a20260919-01"
REVIEW = I09A / "review.md"
ERRATA = I09A / "errata.md"
BINDING = I09A / "binding.json"
HANDOFF = I09A / "handoff.json"
# REPO must be the git repository ROOT, not a parent of the plan directory.
# EXEC = <root>/.planning/<plan>/execution_runs, so the root is THREE levels
# up: execution_runs -> <plan> -> .planning -> <root>.  Off-by-one here made
# `git show HEAD:<path>` resolve a path that does not exist in the repo and
# return EMPTY stdout, which then tripped the line-count guard.  Same class of
# bug as the T1-6 path-depth mistake; guard added below.
REPO = EXEC.parents[2]                   # .../revenue-forecast
REL = str(REVIEW.relative_to(REPO)).replace("\\", "/")

TARGET_LINE = 80                         # 1-based


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    out = {}
    v = {}

    # ---- path sanity guard (the off-by-one above must never recur) ---------
    sanity = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                            cwd=str(REPO), capture_output=True)
    toplevel = sanity.stdout.decode("utf-8", "replace").strip().replace("/", "\\")
    if sanity.returncode != 0 or pathlib.Path(toplevel) != REPO:
        print(f"FATAL: REPO is not the git toplevel. REPO={REPO} toplevel={toplevel}")
        return 2

    # ---- pre-image from git (the authority's "前像 hash") -----------------
    r = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=str(REPO),
                       capture_output=True)
    pre_bytes = r.stdout
    # An EMPTY pre-image means the git path was wrong, NOT that the file
    # changed shape.  Fail loudly rather than falling through to a
    # misleading "line count changed" verdict.
    if r.returncode != 0 or not pre_bytes:
        print(f"FATAL: could not read pre-image via `git show HEAD:{REL}` "
              f"(rc={r.returncode}, {len(pre_bytes)} bytes). "
              f"stderr={r.stderr[:200]!r}")
        return 2
    pre = pre_bytes.decode("utf-8")
    now_bytes = REVIEW.read_bytes()
    now = now_bytes.decode("utf-8")

    pre_lines = pre.splitlines()
    now_lines = now.splitlines()

    out["pre_image"] = {
        "source": f"git show HEAD:{REL}",
        "bytes": len(pre_bytes),
        "sha256": sha256_bytes(pre_bytes),
        "lines": len(pre_lines),
    }
    out["post_image"] = {
        "source": str(REVIEW).replace("\\", "/"),
        "bytes": len(now_bytes),
        "sha256": sha256_bytes(now_bytes),
        "lines": len(now_lines),
        "delta_bytes": len(now_bytes) - len(pre_bytes),
    }

    if len(pre_lines) != len(now_lines):
        out["fatal"] = "line count changed; T1-13 forbids adding/removing lines"
        (RUN / "t13_line80_verification.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("FATAL: line count changed")
        return 1

    o = pre_lines[TARGET_LINE - 1]
    n = now_lines[TARGET_LINE - 1]

    # cells are separated by ' | ' in this markdown table
    o_cells = o.split(" | ")
    n_cells = n.split(" | ")

    # ---- B-1: only the citation cell changed ------------------------------
    cells_same = [i for i in range(min(len(o_cells), len(n_cells)))
                  if o_cells[i] == n_cells[i]]
    cells_diff = [i for i in range(min(len(o_cells), len(n_cells)))
                  if o_cells[i] != n_cells[i]]
    v["B-1"] = {
        "claim": "only the citation cell of the row changed; other cells are byte-identical",
        "cell_count_pre": len(o_cells),
        "cell_count_post": len(n_cells),
        "cells_identical": cells_same,
        "cells_changed": cells_diff,
        "holds": bool(len(o_cells) == len(n_cells) == 3 and cells_diff == [2]),
        "reading": "3 cells: [0]=row label, [1]=measured values, [2]=citation. Only [2] changed.",
    }

    # ---- B-2: no number changed in the metric cell ------------------------
    # The metric cell is cell index 1.  Assert it is byte-identical, and also
    # that the multiset of numeric tokens in it is unchanged (a stricter,
    # independent restatement — either alone would miss a reshuffle).
    metric_same = o_cells[1] == n_cells[1]
    o_metric_nums = re.findall(r"\d+", o_cells[1])
    n_metric_nums = re.findall(r"\d+", n_cells[1])
    v["B-2"] = {
        "claim": "no number changed in the metric cell (the cell carrying the measured values)",
        "metric_cell_byte_identical": metric_same,
        "metric_numbers_pre": o_metric_nums,
        "metric_numbers_post": n_metric_nums,
        "metric_number_multiset_preserved": sorted(o_metric_nums) == sorted(n_metric_nums),
        "holds": bool(metric_same and sorted(o_metric_nums) == sorted(n_metric_nums)),
        "reading": "the measured claims 148/142/132/126/124/270 live in cell [1], which is untouched.",
    }

    # ---- B-3: no other reviewer byte changed ------------------------------
    diff_lines = [i + 1 for i in range(len(pre_lines)) if pre_lines[i] != now_lines[i]]
    v["B-3"] = {
        "claim": "no other reviewer byte changed; line count unchanged",
        "changed_line_numbers": diff_lines,
        "line_count_pre": len(pre_lines),
        "line_count_post": len(now_lines),
        "holds": bool(diff_lines == [TARGET_LINE]),
        "reading": "exactly one line differs, and it is line 80.",
    }

    # ---- B-4: the pre-image is the defective wording errata.md prescribed --
    errata_text = ERRATA.read_text(encoding="utf-8")
    # errata R-1 must exist and describe THIS line as unfixed
    r1_present = "## R-1" in errata_text
    r1_mentions_line80 = "`review.md:80`" in errata_text
    r1_says_unfixed = "该行保持原样、未修" in errata_text
    # errata must name the minimal fix: change only the citation column
    r1_names_minimal_fix = "最小修法是仅改 `:80` 的**出处列**" in errata_text
    # and the handoff must record it as a known gap left to the owner
    h = json.loads(HANDOFF.read_text(encoding="utf-8"))
    gaps = h.get("review_round_3", {}).get("known_gaps", [])
    gap_mentions = any("review.md:80" in g and "UNFIXED" in g for g in gaps)
    # pre-image must still carry the old, defective citation
    pre_carries_defect = "`before/git_status_before.txt`、`after/git_status_after.txt`" in o
    v["B-4"] = {
        "claim": "the edit repairs a defect that errata.md had declared and left to the owner; it is not a silent rewrite",
        "errata_has_R1_section": r1_present,
        "errata_R1_names_line_80": r1_mentions_line80,
        "errata_R1_declares_unfixed": r1_says_unfixed,
        "errata_R1_names_this_exact_minimal_fix": r1_names_minimal_fix,
        "handoff_known_gaps_records_it_as_UNFIXED": gap_mentions,
        "pre_image_carries_the_defective_citation": pre_carries_defect,
        "holds": bool(r1_present and r1_mentions_line80 and r1_says_unfixed
                      and r1_names_minimal_fix and gap_mentions and pre_carries_defect),
        "reading": (
            "errata.md section R-1 declares the defect, names 'change only line 80's "
            "citation column' as the minimal fix, and states the reason it was not "
            "applied (the round's boundary was append-only, and the reviewer's bytes "
            "were not the implementer's to edit). handoff.json records it as a known "
            "gap 'left to the owner'. T1-13 is the owner supplying exactly that "
            "authorisation — so this is a licensed repair of a declared defect."
        ),
    }

    # ---- attachments the owner required -----------------------------------
    dl = []
    lo, ln = o, n
    dl.append(f"--- review.md:80 (pre-image, sha256 of file {out['pre_image']['sha256']})")
    dl.append(f"+++ review.md:80 (post-image, sha256 of file {out['post_image']['sha256']})")
    dl.append("")
    dl.append("@@ line 80, cell [2] (citation only) @@")
    dl.append("")
    dl.append("-" + lo)
    dl.append("+" + ln)
    diff_text = "\n".join(dl) + "\n"
    (RUN / "t13_changes.diff").write_text(diff_text, encoding="utf-8")
    out["attachments"] = {
        "t13_changes.diff": {
            "bytes": len(diff_text.encode("utf-8")),
            "sha256": sha256_bytes(diff_text.encode("utf-8")),
        },
        "pre_image_sha256": out["pre_image"]["sha256"],
        "post_image_sha256": out["post_image"]["sha256"],
    }

    v["all_hold"] = all(v[k]["holds"] for k in ("B-1", "B-2", "B-3", "B-4"))
    out["verdicts"] = v
    out["overall"] = "PASS" if v["all_hold"] else "FAIL"
    out["conclusion"] = (
        "T1-13's edit satisfies all three of its stated boundaries, and its "
        "legitimacy is demonstrated: the pre-image carries the defect that "
        "errata.md section R-1 declared and left to the owner, and the edit "
        "changes only the citation cell of line 80."
        if v["all_hold"]
        else "at least one boundary is violated; see verdicts."
    )

    target = RUN / "t13_line80_verification.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    for k in ("B-1", "B-2", "B-3", "B-4"):
        print(f"{k}: holds={v[k]['holds']} | {v[k]['claim']}")
    print(f"overall: {out['overall']}")
    print(f"wrote: {target}")
    return 0 if v["all_hold"] else 1


if __name__ == "__main__":
    sys.exit(main())
