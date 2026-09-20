#!/usr/bin/env python3
"""T1-21 verification -- policy for post-hoc `oracle.md` editing.

Ruling (OWNER_DECISIONS.md section 13, T1-21, TIER-1):

    "采纳建议口径：允许追加式 provenance 登记（写明何时、为何、新 hash），
     禁止回改为『从未编辑』。"

Origin: section 6 of the owner's decisions, item on `oracle.md` post-hoc editing
(I-08-B N2): hash moved 8d6dc81b -> bd67211f, binding re-registered.  The
reviewer wrote "治理裁定我无权作出" (the governance ruling is not mine to make).
The implementer likewise refused to rule: binding.json:246 carries
`governance_status = "OWNER DECISION REQUIRED: whether post-hoc editing of a
frozen oracle is acceptable. The implementer registers the event and does NOT
rule on it."`

T1-21 is the owner's answer to that escalation.  It sets an INTERPRETATION, not a
new edit, so the card's job is to verify that the prescribed form is what is
actually on disk, and that the prohibited form is absent.

Propositions (any failure => FAIL):

  P-1  The allowed form is present: there is an APPENDED provenance registration
       that states WHEN, WHY and the NEW HASH of the post-hoc edit.
  P-2  The prohibited form is absent: nothing anywhere rewrites the record to
       claim the oracle was "never edited".  The earlier hash survives.
  P-3  The event was escalated rather than self-ruled: the attempt records that
       the governance question is for the owner, and does not itself decide it.
  P-4  The registration is ADDITIVE: the pre-edit value is preserved alongside
       the post-edit value (the ledger keeps both, so no earlier value is lost).

Guards as in T1-13/T1-19/T1-20: a repo-root off-by-one makes `git show HEAD:` return
empty stdout and trips a downstream guard with a misleading content verdict.
"""

import hashlib
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent                                  # .../execution_runs/T1-21/a20260920-01
EXEC = RUN.parent.parent                           # .../execution_runs

# REPO = git root: EXEC = <root>/.planning/<plan>/execution_runs => THREE levels up.
REPO = EXEC.parents[2]

I08B = EXEC / "I-08-B" / "a20260919-01"
ORACLE = I08B / "oracle.md"
BINDING = I08B / "binding.json"
HANDOFF = I08B / "handoff.json"

# The two hashes the section-6 event names, and the implementer-measured predecessor.
PRE_HASH_SHORT = "8d6dc81b"      # pre-round-1 measured value (must survive)
POST_HASH_FULL = "60a86ef8"      # current value recorded in the ledger


def run(cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True)


def main() -> int:
    # ---- path sanity guard --------------------------------------------------
    sanity = run(["git", "rev-parse", "--show-toplevel"])
    toplevel = sanity.stdout.decode("utf-8", "replace").strip().replace("/", "\\")
    if sanity.returncode != 0 or pathlib.Path(toplevel) != REPO:
        print(f"FATAL: REPO is not the git toplevel. REPO={REPO} toplevel={toplevel}")
        return 2

    if not (ORACLE.exists() and BINDING.exists() and HANDOFF.exists()):
        print("FATAL: expected I-08-B artifacts missing")
        return 2

    oracle_text = ORACLE.read_text(encoding="utf-8")
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    binding_text = BINDING.read_text(encoding="utf-8")
    handoff_text = HANDOFF.read_text(encoding="utf-8")

    v = {}

    # ---- P-1: the allowed form -- appended provenance with WHEN / WHY / NEW HASH
    # WHEN: the ledger timeline + oracle section
    has_when = bool(re.search(r"03:49:26|first_runs|first round|首轮|运行之后", oracle_text)
                    or re.search(r"03:49:26", binding_text))
    # WHY
    has_why = "复核驱动" in oracle_text or "errata" in oracle_text.lower() or \
              "勘误" in oracle_text
    # NEW HASH
    has_new_hash = "60a86ef8" in binding_text or POST_HASH_FULL in binding_text
    # the registration is an APPENDED section in oracle.md (numbered, after prior content)
    appended_section = bool(re.search(r"^\s*9\.\s+\*\*本文件的编辑 provenance", oracle_text, re.M))
    v["P-1"] = {
        "states_when": bool(has_when),
        "states_why": bool(has_why),
        "records_new_hash": bool(has_new_hash),
        "is_an_appended_section": appended_section,
        "holds": bool(has_when and has_why and has_new_hash and appended_section),
    }

    # ---- P-2: prohibited form absent -- no rewrite to "never edited" ---------
    # Look for any claim that the oracle was never edited, or that the first hash
    # is the only one.  The honest record says edited_after_first_runs = true.
    claims_never_edited = bool(re.search(r"从未(被)?编辑|never edited|no edit.{0,20}occur",
                                         oracle_text + binding_text + handoff_text, re.I))
    ledger = binding.get("documentation_edit_ledger", {})
    edits = ledger.get("edits", []) if isinstance(ledger, dict) else []
    # some builds nest differently; also accept a top-level key
    edited_flag = None
    for e in (edits or []):
        if isinstance(e, dict) and e.get("document") == "oracle.md":
            edited_flag = e.get("edited_after_first_runs")
            break
    if edited_flag is None:
        edited_flag = "edited_after_first_runs\": true" in binding_text or \
                      "\"WAS edited after the first test runs\"" in handoff_text
    v["P-2"] = {
        "claims_never_edited_anywhere": claims_never_edited,
        "ledger_records_edit_as_having_happened": bool(edited_flag),
        "holds": bool((not claims_never_edited) and edited_flag),
    }

    # ---- P-3: escalated, not self-ruled ------------------------------------
    escalated_binding = "OWNER DECISION REQUIRED" in binding_text
    escalated_oracle = bool(re.search(r"本卡无权自行裁定|已登记为待 owner 裁决", oracle_text))
    implementer_did_not_rule = "does NOT rule on it" in binding_text or \
                               "does not rule" in binding_text.lower()
    v["P-3"] = {
        "binding_flags_owner_decision_required": escalated_binding,
        "oracle_says_card_may_not_self_rule": escalated_oracle,
        "binding_says_implementer_does_not_rule": implementer_did_not_rule,
        "holds": bool(escalated_binding and escalated_oracle),
    }

    # ---- P-4: additive -- the pre-edit value survives ----------------------
    pre_survives = PRE_HASH_SHORT in binding_text or PRE_HASH_SHORT in handoff_text
    note_about_no_value_lost = "no earlier value is lost" in binding_text
    first_freeze_kept = "08281f2d" in binding_text  # the I-08-A-recorded first hash
    v["P-4"] = {
        "pre_edit_hash_survives": pre_survives,
        "states_no_earlier_value_lost": note_about_no_value_lost,
        "earlier_freeze_hash_kept": first_freeze_kept,
        "holds": bool(pre_survives and note_about_no_value_lost),
    }

    overall = all(x["holds"] for x in v.values())

    out = {
        "card": "T1-21",
        "attempt": "a20260920-01",
        "authority": "OWNER_DECISIONS.md section 13 T1-21 (TIER-1)",
        "ruling": "adopt the recommended interpretation: append-only provenance "
                  "registration is allowed (stating when, why, and the new hash); "
                  "rewriting the record to claim 'never edited' is forbidden",
        "origin": "section 6 of the owner's decisions -- I-08-B N2 post-hoc oracle.md "
                  "edit (8d6dc81b -> re-registered); the reviewer wrote 'the governance "
                  "ruling is not mine to make' and the implementer likewise refused to rule",
        "ratified_policy": {
            "allowed": "append-only provenance registration stating WHEN, WHY and NEW HASH",
            "forbidden": "rewriting the record to claim the document was never edited",
        },
        "propositions": v,
        "overall": "PASS" if overall else "FAIL",
    }

    dest = RUN / "t21_oracle_edit_policy_verification.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    for k in ("P-1", "P-2", "P-3", "P-4"):
        print(f"{k}: holds={v[k]['holds']}")
    print(f"overall: {out['overall']}")
    print(f"wrote: {dest}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
