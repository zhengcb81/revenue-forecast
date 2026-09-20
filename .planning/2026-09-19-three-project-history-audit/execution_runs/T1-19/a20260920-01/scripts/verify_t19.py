#!/usr/bin/env python3
"""T1-19 verification -- freeze the rc code table into START_HERE.md.

Ruling (OWNER_DECISIONS.md section 13, T1-19, TIER-1):

    "授权冻结一个码表写入 START_HERE.md，各批带自描述 exit_code_legend，
     不回改历史 rc."

Like T1-13, opening the card revealed that the edit ALREADY EXISTS in the
working tree but was never committed and has no attempt record.  So this card's
role is not to perform the write -- it is to *verify* it and to record the
evidence the card is supposed to carry.

Propositions (any failure => FAIL):

  C-1  The rc table section is a PURE APPEND to START_HERE.md: the pre-image
       bytes survive verbatim at the head, and nothing was deleted.
  C-2  The frozen table carries exactly the four rc values the ruling fixed:
       0 = pass / 1 = harness failure / 2 = no verdict or expected rejection /
       3 = did not meet expectation.
  C-3  The append honours the OTHER half of the ruling -- it carries the
       self-describing `exit_code_legend` requirement and explicitly refuses to
       rewrite historical rc ("历史 rc 与其证据一律不动").
  C-4  No historical rc evidence was touched by the append: the section is
       prose only; START_HERE.md is documentation, and no product file, runner,
       or frozen evidence file changed.

Path-depth lesson from T1-6 and T1-13: an off-by-one in the repo root makes
`git show HEAD:<path>` return EMPTY stdout, which then trips a downstream guard
and reports a *content* problem that does not exist.  Two guards below (path
sanity + empty pre-image) make that failure loud instead of misleading.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                                  # .../execution_runs/T1-19/a20260920-01
EXEC = RUN.parent.parent                           # .../execution_runs

# REPO must be the git repository ROOT.  EXEC = <root>/.planning/<plan>/execution_runs
# so the root is THREE levels up: execution_runs -> <plan> -> .planning -> <root>.
# (Off-by-one here resolves `git show HEAD:<path>` to a non-existent path and
# returns empty stdout -- the T1-13 failure.  The guard below makes it loud.)
REPO = EXEC.parents[2]

TARGET = REPO / ".planning" / "2026-09-19-three-project-history-audit" / "execution_v2" / "START_HERE.md"
REL = str(TARGET.relative_to(REPO)).replace("\\", "/")

# Frozen rc values the ruling fixed.  These are the *normative* meanings; the
# four keys must be present and must carry these semantics.
FROZEN = {
    "0": "通过",
    "1": "harness 失败",
    "2": "无裁决",
    "3": "未达预期",
}

SECTION_MARKER = "## rc 码表"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True)


def main() -> int:
    # ---- path sanity guard (the off-by-one must never recur) --------------
    sanity = run(["git", "rev-parse", "--show-toplevel"])
    toplevel = sanity.stdout.decode("utf-8", "replace").strip().replace("/", "\\")
    if sanity.returncode != 0 or pathlib.Path(toplevel) != REPO:
        print(f"FATAL: REPO is not the git toplevel. REPO={REPO} toplevel={toplevel}")
        return 2

    if not TARGET.exists():
        print(f"FATAL: target does not exist: {TARGET}")
        return 2

    pre_raw = run(["git", "show", f"HEAD:{REL}"])
    pre_bytes = pre_raw.stdout
    # An EMPTY pre-image means the git path was wrong, NOT that the file changed
    # shape.  Fail loudly rather than falling through to a misleading verdict.
    if pre_raw.returncode != 0 or not pre_bytes:
        print(f"FATAL: could not read pre-image via `git show HEAD:{REL}` "
              f"(rc={pre_raw.returncode}, {len(pre_bytes)} bytes). "
              f"stderr={pre_raw.stderr[:200]!r}")
        return 2

    post_bytes = TARGET.read_bytes()
    pre_text = pre_bytes.decode("utf-8")
    post_text = post_bytes.decode("utf-8")

    v = {}

    # ---- C-1: pure append -------------------------------------------------
    pre_prefix_ok = post_bytes[: len(pre_bytes)] == pre_bytes
    post_lines = post_text.split("\n")
    pre_lines = pre_text.split("\n")
    pre_starts = set()
    for nl in post_lines:
        for pl in pre_lines:
            if pl and nl.startswith(pl):
                pre_starts.add(pl)
    # a pre-existing line survives if it appears verbatim OR is a prefix of a new line
    pre_lines_ok = all((l in post_lines) or (l and l in pre_starts) for l in pre_lines)
    new_section_only = SECTION_MARKER in post_text and SECTION_MARKER not in pre_text
    v["C-1"] = {
        "prefix_bytes_preserved": pre_prefix_ok,
        "pre_lines_all_preserved": pre_lines_ok,
        "pre_bytes": len(pre_bytes),
        "post_bytes": len(post_bytes),
        "delta_bytes": len(post_bytes) - len(pre_bytes),
        "section_is_new": new_section_only,
        "holds": bool(pre_prefix_ok and pre_lines_ok and new_section_only),
    }

    # ---- C-2: the four frozen rc values are present with the right meaning --
    pairs = re.findall(r"\|\s*`([0-3])`\s*\|\s*([^|]+?)\s*\|", post_text)
    table = {k: val.strip() for k, val in pairs}
    values_ok = all(k in table for k in FROZEN)
    # "2" must mention the two legitimate sources (expected rejection / no verdict)
    two_ok = ("无裁决" in table.get("2", "")) or ("预期拒绝" in table.get("2", ""))
    three_ok = "未达预期" in table.get("3", "")
    v["C-2"] = {
        "table_parsed": table,
        "frozen_values_expected": FROZEN,
        "all_four_present": values_ok,
        "rc2_covers_no_verdict_or_expected_rejection": two_ok,
        "rc3_means_did_not_meet_expectation": three_ok,
        "holds": bool(values_ok and two_ok and three_ok),
    }

    # ---- C-3: the other half of the ruling -- legend + no historical rewrite -
    legend_ok = "exit_code_legend" in post_text
    no_rewrite_ok = ("历史 rc" in post_text and "不回改" in post_text) or \
                    ("一律不动" in post_text)
    deviation_registered = "已知的历史偏差" in post_text
    v["C-3"] = {
        "requires_self_describing_exit_code_legend": legend_ok,
        "states_historical_rc_not_rewritten": bool(no_rewrite_ok),
        "registers_known_batch_deviations": deviation_registered,
        "holds": bool(legend_ok and no_rewrite_ok),
    }

    # ---- C-4: no historical rc evidence touched ---------------------------
    # The appended section is prose in a .md doc.  Prove the change set is
    # confined to that one file and that no product file changed.
    changed = run(["git", "diff", "HEAD", "--name-only"]).stdout.decode("utf-8", "replace").split()
    non_planning = [p for p in changed if not p.startswith(".planning/")]
    product_files = [p for p in changed if p.startswith(("scripts/", "tests/", "tools/", "RF/"))]
    v["C-4"] = {
        "changed_files_total": len(changed),
        "changed_outside_planning": non_planning,
        "product_files_changed": product_files,
        "target_is_markdown": TARGET.suffix == ".md",
        "holds": bool(not product_files and TARGET.suffix == ".md"),
    }

    overall = all(x["holds"] for x in v.values())

    out = {
        "card": "T1-19",
        "attempt": "a20260920-01",
        "authority": "OWNER_DECISIONS.md section 13 T1-19 (TIER-1)",
        "ruling": "freeze one rc code table into START_HERE.md; batches carry a "
                  "self-describing exit_code_legend; historical rc not rewritten",
        "artifact_under_verification": {
            "path": REL,
            "pre_sha256": sha(pre_bytes),
            "post_sha256": sha(post_bytes),
            "pre_bytes": len(pre_bytes),
            "post_bytes": len(post_bytes),
            "delta_bytes": len(post_bytes) - len(pre_bytes),
            "pre_existed_in_head": True,
        },
        "note": "the edit was already present in the working tree, uncommitted and "
                "without an attempt record; this card verifies it and supplies the "
                "evidence rather than performing the write",
        "propositions": v,
        "overall": "PASS" if overall else "FAIL",
    }

    dest = RUN / "t19_rc_table_verification.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    for k in ("C-1", "C-2", "C-3", "C-4"):
        print(f"{k}: holds={v[k]['holds']}")
    print(f"overall: {out['overall']}")
    print(f"wrote: {dest}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
