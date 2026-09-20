#!/usr/bin/env python3
"""T1-24 verification -- is `oracle.md` text 'pre-run frozen evidence'?

Ruling (OWNER_DECISIONS.md section 13, T1-24, TIER-1):

    "口径确认：不采纳『文本事前冻结』这一更强主张；formula 资格以可逐字节重生成的
     oracle.json + 生成器代码运行前 hash 已落盘 + oracle.json mtime 早于产品 stdout
     为准。不重跑。"

Origin: OQ-05 (M29-M31). The reviewer's own ruling anticipated this exactly:
`oracle.md`'s present mtime is a POST-HOC value and is not offered as pre-run
evidence; what was anchored before the generator ran is the generator CODE
(scripts/oracle_<CARD>.py, 3177247f...). The reviewer drew the boundary too:
"if the owner wants oracle.md treated as pre-run frozen evidence, this attempt
is NOT sufficient and a re-run is required."

T1-24 declines that stronger claim, so no re-run is needed.  This card's job is to
verify that the accepted basis (three legs) actually holds on disk, and that the
declined stronger claim is NOT being asserted anywhere.

This is an interpretation confirmation: it authorises NO edit and requires NO
re-run.  Claiming otherwise would be the overreach the ruling itself avoids.

Propositions (any failure => FAIL):

  Q-1  Leg 1 holds: the frozen oracle files ARE regenerable byte-for-byte from
       the independent generator script.
  Q-2  Leg 2 holds: the generator CODE hash landed on disk BEFORE the run.
  Q-3  Leg 3 holds: oracle.json's mtime precedes the product stdout.
  Q-4  The declined stronger claim is ABSENT: nothing asserts oracle.md text is
       pre-run frozen evidence.  (If it were asserted, T1-24's refusal would be
       contradicted by the artifact itself.)

Guards as in T1-13/T1-19/T1-20/T1-21.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                                  # .../execution_runs/T1-24/a20260920-01
EXEC = RUN.parent.parent                           # .../execution_runs
REPO = EXEC.parents[2]                             # git root (THREE levels up)

CARDS = ["M29", "M30", "M31"]


def run(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True)


def main() -> int:
    # ---- path sanity guard --------------------------------------------------
    sanity = run(["git", "rev-parse", "--show-toplevel"])
    toplevel = sanity.stdout.decode("utf-8", "replace").strip().replace("/", "\\")
    if sanity.returncode != 0 or pathlib.Path(toplevel) != REPO:
        print(f"FATAL: REPO is not the git toplevel. REPO={REPO} toplevel={toplevel}")
        return 2

    v = {}

    # ---- Q-1: leg 1 -- byte-for-byte regenerability -------------------------
    regen = {}
    for c in CARDS:
        p = EXEC / c / "a20260919-01" / "evidence" / c / "oracle_regen_proof.json"
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            regen[c] = {
                "all_byte_identical": d.get("all_byte_identical"),
                "raw_returncode": d.get("raw_returncode"),
                "frozen_files_untouched_by_this_step": d.get("frozen_files_untouched_by_this_step"),
            }
        else:
            # some cards record regenerability inline; look for a related file
            regen[c] = {"present": False}
    q1_ok = all(x.get("all_byte_identical") is True and x.get("raw_returncode") == 0
                for x in regen.values())
    v["Q-1"] = {
        "detail": regen,
        "holds": q1_ok,
    }

    # ---- Q-2: leg 2 -- generator code hash landed before the run -----------
    gen_hash_expected = "3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e"
    q2 = {}
    for c in CARDS:
        p = EXEC / c / "a20260919-01" / "evidence" / c / "oracle_document_freeze.json"
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            od = d.get("oracle_document", {})
            q2[c] = {
                "generator_sha256": od.get("oracle_md_sha256"),
                "existed_before_generation": od.get("oracle_md_existed_before_generation"),
                "recorded_utc": od.get("recorded_utc"),
            }
        else:
            q2[c] = {"present": False}
    q2_ok = all(x.get("generator_sha256") == gen_hash_expected
                and x.get("existed_before_generation") is True for x in q2.values())
    v["Q-2"] = {
        "expected_generator_sha256": gen_hash_expected,
        "detail": q2,
        "holds": q2_ok,
    }

    # ---- Q-3: leg 3 -- oracle.json mtime precedes product stdout -----------
    q3 = {}
    for c in CARDS:
        p = EXEC / c / "a20260919-01" / "evidence" / c / "oracle_document_freeze.json"
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            gen = d.get("generated_files", {})
            oj = gen.get(f"evidence/{c}/oracle.json", {})
            order = d.get("mtime_ordering_within_this_step", {})
            # the product stdout lives in run_result.json / stdout.txt
            stdout_p = EXEC / c / "a20260919-01" / "evidence" / c / "stdout.txt"
            so_mtime = stdout_p.stat().st_mtime if stdout_p.exists() else None
            q3[c] = {
                "oracle_json_mtime_in_record": oj.get("mtime"),
                "oracle_md_precedes_oracle_json": order.get("oracle_md_precedes_oracle_json"),
                "stdout_txt_mtime": so_mtime,
                "oracle_json_mtime_precedes_stdout": (oj.get("mtime") is not None
                                                      and so_mtime is not None
                                                      and oj.get("mtime") < so_mtime),
            }
        else:
            q3[c] = {"present": False}
    q3_ok = all(x.get("oracle_md_precedes_oracle_json") is True
                and x.get("oracle_json_mtime_precedes_stdout") is True for x in q3.values())
    v["Q-3"] = {"detail": q3, "holds": q3_ok}

    # ---- Q-4: declined stronger claim is absent ----------------------------
    # Scan M29-M31 handoff/oq_rulings for any ASSERTION that oracle.md TEXT itself
    # is pre-run frozen evidence.  The honest record says it is NOT.
    #
    # Naive substring matching fails here (measured, then fixed): the phrases
    #   "if the owner wants oracle.md treated as pre-run frozen evidence, ..."
    #   "oracle.md is NOT described anywhere ... as pre-run frozen"
    # both CONTAIN the substring but are a BOUNDARY CONDITIONAL and a DENIAL,
    # not assertions.  A criterion that cannot tell asserting from conditioning
    # or denying reports a violation that does not exist -- the same class of
    # mistake as the earlier pure-insertion and -inf-boundary errors.  So we
    # require the assertion to be POSITIVE and UNQUALIFIED: the sentence must not
    # be preceded by "if", "wants", "NOT", "not", "never".
    denied_re = re.compile(
        r"(is\s+NOT\s+described[^\"]{0,60}pre-run frozen|"
        r"NOT\s+pre-run evidence|"
        r"is outside the anchor scope|"
        r"carries no gating expectation)", re.I)
    boundary_re = re.compile(r"\bif\b[^\"]{0,80}\bwants?\b", re.I)
    # positive assertion = "oracle.md ... <is/are> ... pre-run frozen" with no negation
    positive_re = re.compile(r"oracle\.md[^\".]{0,60}\bis\s+(?:the\s+)?pre-run frozen", re.I)

    asserted_pre_frozen = []
    denied_anywhere = 0
    for c in CARDS:
        for rel in ("handoff.json", f"evidence/{c}/oq_rulings.json",
                    f"evidence/{c}/source_manifest.json"):
            p = EXEC / c / "a20260919-01" / rel
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            if denied_re.search(t):
                denied_anywhere += 1
            # find positive assertions that are neither inside a conditional nor negated
            for m in positive_re.finditer(t):
                # widen to the enclosing sentence-ish window for negation/condition checks
                s = max(0, m.start() - 120)
                window = t[s:m.end() + 40]
                if boundary_re.search(window):
                    continue
                if re.search(r"\bNOT\b|\bnever\b|is not\b", window, re.I):
                    continue
                asserted_pre_frozen.append({"file": f"{c}/{rel}",
                                            "match": m.group(0)})
    v["Q-4"] = {
        "files_asserting_oracle_md_text_is_pre_run_frozen": asserted_pre_frozen,
        "files_denying_it": denied_anywhere,
        "criterion_note": "positive-and-unqualified assertions only; boundary conditionals "
                          "and explicit denials are excluded by construction, because a "
                          "substring match cannot tell asserting from conditioning or denying",
        "holds": bool(not asserted_pre_frozen and denied_anywhere > 0),
    }

    overall = all(x["holds"] for x in v.values())

    out = {
        "card": "T1-24",
        "attempt": "a20260920-01",
        "authority": "OWNER_DECISIONS.md section 13 T1-24 (TIER-1)",
        "ruling": "adopt the interpretation confirmation: the stronger claim 'oracle.md text is "
                  "pre-run frozen evidence' is NOT adopted; formula qualification rests on "
                  "(1) byte-for-byte regenerable oracle.json, (2) the generator code's hash "
                  "already on disk before the run, (3) oracle.json mtime earlier than the "
                  "product stdout. No re-run.",
        "origin": "OQ-05 (M29-M31); the reviewer's own ruling already drew the same boundary",
        "accepted_basis": [
            "leg 1: byte-for-byte regenerability of the frozen oracle files from the independent generator",
            "leg 2: the generator code hash landed on disk before the run",
            "leg 3: oracle.json mtime precedes the product stdout",
        ],
        "declined_claim": "oracle.md TEXT treated as pre-run frozen evidence",
        "propositions": v,
        "overall": "PASS" if overall else "FAIL",
    }

    dest = RUN / "t24_oracle_pre_frozen_scope.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    for k in ("Q-1", "Q-2", "Q-3", "Q-4"):
        print(f"{k}: holds={v[k]['holds']}")
    print(f"overall: {out['overall']}")
    print(f"wrote: {dest}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
