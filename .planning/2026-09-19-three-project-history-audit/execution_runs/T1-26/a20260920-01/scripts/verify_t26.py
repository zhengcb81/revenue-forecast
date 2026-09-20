#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T1-26 verification — I-14-A D1/D2/D3 "owner-level release" (a HALF-authorisation).

OWNER_DECISIONS.md §13 T1-26 (TIER-1):
    "owner 层面放行：授权将该补丁的晋升流程启动，但 D1/D2/D3 的专业签字仍属他方
     （见 TIER-2）。未获该三方签字前仍禁止把 iso/slo_probe_patched.py 拷进 RF/tools/；
     I-16 实测前必须先提供 bundle 测量文件。"

WHAT KIND OF OBJECT IS THIS RULING?

It is NOT "the ruling is done, go verify it was carried out". It is a HALF-authorisation with a
verb that has no disk effect on one side and an explicit PROHIBITION on the other:

  granted half  : "authorise STARTING the promotion process"  -- a permission, not an act.
                  Nothing on disk should look different because of it.
  withheld half : professional sign-off for D1/D2/D3 belongs to OTHER parties (TIER-2).
  standing ban  : until those three signatures exist, copying iso/slo_probe_patched.py into
                  RF/tools/ is FORBIDDEN, and a bundle measurement file must be supplied before
                  I-16's production measurement.

So the card must verify BOTH halves. The failure mode this card exists to catch is the classic
"authorised => done" collapse: reading "owner 层面放行" as if it lifted the ban, or as if it
supplied the three signatures, and therefore promoting the file. That is the exact move the
"执行纪律（本批新增第 7 条）" forbids: 「总的批准」不得膨胀为「所有的结论」.

The card CANNOT verify that the three signatures are absent "because they don't exist yet" --
that would be circular. It verifies that the ABSENCE is registered on disk, that the ban is
registered on disk, that the tool genuinely is NOT promoted, and that the TIER-2 rows still say
"待裁方" rather than "owner 已裁".

Five propositions:

  V-1 GRANTED HALF IS A PERMISSION AND LEFT NO DISK EFFECT
      the ruling says "授权...启动" (authorise starting), and the granted object is a *process*,
      not an artifact. Check: there is no promoted copy, no change-window card, no new artifact
      that the ruling would have created. A permission that has an artifact is not a permission.

  V-2 WITHHELD HALF IS STILL WITHHELD (the three signatures are still owned by other parties)
      D1 -> an ops reviewer who is NOT the author of this probe;
      D2 -> the production SLO / probe owner;
      D3 -> I-16.
      Every carrier must still say UNSIGNED / awaiting / not the author. Any carrier that says
      "signed" or "confirmed" would be a forged signature.

  V-3 THE BAN IS ON DISK AND IS EXPLICIT
      the promotion prohibition must be present in decision.md, review.md, oracle.md and
      handoff.json (promotion_blocked), and must name RF/tools/ explicitly.

  V-4 THE BAN IS OBEYED (the tool is genuinely not promoted)  <-- the load-bearing leg
      RF/tools/slo_probe.py must be byte-identical to the frozen PRE-PATCH image; the patched
      file must exist ONLY in iso/; no test copy in RF/tools/tests/.

  V-5 THE TIER-2 ROWS STILL SAY "待裁方", NOT "owner 已裁"
      TIER-2 is exactly where owner authorises *starting* and the final ruling belongs to the
      other party. Check: the T2 rows for D1/D2/D3 name 待裁方 and carry "授权送签"/"授权启动",
      and no TIER-2 row records a conclusion as if the owner had produced it.

Exit codes: 0 = all pass; 1 = harness failure; 2 = no ruling found / expected refusal; 3 = unmet.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

EXEC = Path(__file__).resolve().parent.parent          # .../T1-26/a20260920-01
ATTEMPT = EXEC
# REPO is four levels above EXEC: a20260920-01 -> T1-26 -> execution_runs -> <audit dir> -> repo
# NOTE: count from EXEC, not from __file__ (EXEC already climbed out of scripts/).
REPO = EXEC.parents[4]
PLAN = REPO / ".planning" / "2026-09-19-three-project-history-audit"
T14A = PLAN / "execution_runs" / "I-14-A" / "a20260919-01"

# ---- known constants (pre-images) ------------------------------------------
PROD_SLO_SHA256 = "f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059"
PROD_SLO_BLOB = "413aad5f788732520ace76acbaebcf06633f34d5"
PATCHED_SHA256 = "14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e"

results = {}
failures = []


def record(key, ok, **evidence):
    results[key] = {"holds": bool(ok), **evidence}
    if not ok:
        failures.append(key)
    return bool(ok)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# path sanity guardrail -- if REPO is wrong, every git lookup below silently
# returns empty stdout and gets misread as a content defect (the T1-13 failure
# mode). Fail hard and loud instead.
# ---------------------------------------------------------------------------
def guard():
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         cwd=REPO, capture_output=True, text=True)
    if top.returncode != 0:
        print("FATAL: git rev-parse failed:", top.stderr.strip())
        sys.exit(1)
    got = Path(top.stdout.strip()).resolve()
    if got != REPO:
        print(f"FATAL: REPO != git toplevel ({got} vs {REPO})")
        sys.exit(1)
    if not (PLAN / "OWNER_DECISIONS.md").exists():
        print("FATAL: OWNER_DECISIONS.md not found at expected path")
        sys.exit(1)


def main():
    guard()

    owner_dec = read(PLAN / "OWNER_DECISIONS.md")
    t1_26 = re.search(r"^\|\s*T1-26\s*\|(.+)$", owner_dec, re.M)
    if not t1_26:
        print("FATAL: T1-26 ruling row not found in OWNER_DECISIONS.md")
        sys.exit(2)
    ruling = t1_26.group(1)

    decision = read(T14A / "decision.md")
    review = read(T14A / "review.md")
    oracle = read(T14A / "oracle.md")
    handoff = json.loads(read(T14A / "handoff.json"))

    # =======================================================================
    # V-1  GRANTED HALF IS A PERMISSION AND LEFT NO DISK EFFECT
    # =======================================================================
    # The ruling says "授权将该补丁的晋升流程启动" -- authorise STARTING the process.
    granted_verb_is_permission = bool(
        re.search(r"授权", ruling) and re.search(r"晋升流程启动|启动", ruling)
    )
    # A permission has no artifact. "Promotion" here has exactly ONE destination in this repo:
    # RF/tools/ -- i.e. tools/slo_probe.py (RF is the repo root's former name; see decision.md
    # "RF/tools/slo_probe.py"). So the check must be scoped to the *destination*, not to any file
    # anywhere whose name contains "promot". (An earlier draft of this probe matched
    # portfolio_promoter.py in an unrelated subsystem -- a name collision, not evidence.)
    unrelated_promoter_files = [
        str(p.relative_to(REPO)).replace("\\", "/")
        for p in (REPO / "tools").rglob("*")
        if p.is_file() and re.search(r"(promot|change[-_]?window)", p.name, re.I)
    ]
    # (b) is there a promoted test copy?
    promoted_test = (REPO / "tools" / "tests" / "test_slo_probe_patched.py").exists()
    # (c) the patched file must live ONLY inside this attempt's directory tree -- and note it
    #     legitimately appears TWICE inside the attempt (iso/ and harness/), byte-identical.
    patched_sites = [
        str(p.relative_to(REPO)).replace("\\", "/")
        for p in REPO.rglob("slo_probe_patched.py")
        if "venv" not in p.parts
    ]
    patched_only_in_attempt = bool(patched_sites) and all(
        s.startswith(".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/")
        for s in patched_sites
    )
    also_present_as_iso_and_harness = sorted(
        Path(s).parent.name for s in patched_sites
    ) == ["harness", "iso"]
    record(
        "V-1_granted_half_is_permission_with_no_artifact",
        granted_verb_is_permission and not unrelated_promoter_files
        and not promoted_test and patched_only_in_attempt,
        granted_verb_is_permission=granted_verb_is_permission,
        promoter_named_files_under_tools=unrelated_promoter_files,
        promoted_test_present=promoted_test,
        patched_file_sites=patched_sites,
        patched_only_in_attempt=patched_only_in_attempt,
        also_present_as_iso_and_harness=also_present_as_iso_and_harness,
        note="a permission that has an artifact is not a permission; the granted object is a process",
    )

    # =======================================================================
    # V-2  WITHHELD HALF IS STILL WITHHELD
    # =======================================================================
    # Each of D1/D2/D3 must still name its OTHER-party owner, and none may read as "signed".
    ownership = {
        "D1": bool(re.search(r"D1[^\n]{0,120}(ops reviewer)", decision)
                   and re.search(r"must NOT be (the )?(author|this probe's author)", decision)),
        "D2": bool(re.search(r"D2[^\n]{0,160}(production SLO\s*/\s*probe owner|probe owner)", decision)),
        "D3": bool(re.search(r"D3[^\n]{0,160}(I-16)", decision)),
    }
    # signed-claims: a line that ASSERTS a decision is signed/confirmed/closed, with no
    # awaiting/unsigned marker AND no prohibition/denial on the same line.
    #
    # NEGATION AND CONDITIONALITY BOTH DISQUALIFY A LINE. This is the T1-18 U-3 / T1-24 Q-4
    # lesson, hit twice here on the first run:
    #   * "D1/D2/D3 none self-closed"          -- a DENIAL of closure (contains "closed")
    #   * "`RF/tools/` must not happen until D1 is signed"  -- a CONDITIONAL prohibition
    #     (contains "signed", and is exactly the ban V-3 requires to be present)
    # Grepping for the keyword alone reports the prohibition as the violation.
    DENY = re.compile(
        r"(UNSIGNED|unsigned|not signed|NOT signed|none self-closed|self-closed|"
        r"awaiting|forbidden|blocked|must not|must \*\*not\*\*|不得|未|待|不)",
    )
    # THE PRECISE QUESTION: is there a clause that AFFIRMATIVELY claims D1 (or D2/D3) is signed /
    # confirmed / closed? That is what a forged signature would look like.
    #
    # Three earlier drafts were wrong, and each failure is instructive:
    #   draft 1 (per-line keyword grep) -> flagged the PROHIBITION "must not happen until D1 is
    #        signed", i.e. the rule itself. A keyword-grep cannot tell "D1 is signed" from
    #        "nothing may happen until D1 is signed".
    #   draft 2 (paragraph-level co-occurrence) -> matched unrelated clauses in any block that
    #        merely mentioned D1, e.g. "the reviewer independently confirmed the --as-of-date fact".
    #   draft 3 (clause = sign-verb AND D-label) -> still matched three non-claims:
    #        "**Signer:** I-16" (names who WOULD sign -- a future actor, not a completed act),
    #        "It fails closed" ("closed" as in fail-closed, a technical term), and
    #        "for the D2 signature" ("signature" as the artifact still to be produced).
    #
    # The lesson across all three: the criterion must test the SIGNEDNESS PREDICATE (is the
    # decision in the signed state?), not the vocabulary of signing. So: require a STATE verb form
    # bound to the decision label, and explicitly exclude the lexical traps.
    # draft 4 added a state-verb form but kept "accepted" as a signature verb, which collided with
    #        the card's own reviewer verdict vocabulary: "Decide D1 (below) -- it is a specialist
    #        decision and is **not** self-accepted" is an instruction not to self-accept, and the
    #        em-dash split defeated the negation guard.
    #
    # Final form: the question is SIGNEDNESS of D1/D2/D3 specifically. "accepted" is removed --
    # a decision being "accepted" in this corpus most often means the *reviewer* accepted the
    # card (accepted_scoped), which is a different predicate from a specialist signing a decision.
    # And the negation guard now runs on the wider window, not the split clause.
    CLAIM = re.compile(
        r"\b(D1|D2|D3)\b[^.]{0,50}?\b(is|are|was|were|has been|have been)\b[^.]{0,30}?"
        r"\b(signed|confirmed|closed)\b"
        r"|\b(signed|confirmed|closed)\b[^.]{0,40}?\b(D1|D2|D3)\b",
        re.I,
    )
    # lexical traps: these are NOT claims of signedness even though they contain the vocabulary
    LEXICAL_TRAP = re.compile(
        r"(Signer:|signature\b(?!\s+(?:is|has|was))|fail[-\s]?closed|fails closed|"
        r"self-closed|none self-closed|change[-\s]?window|unsigned|UNSIGNED)",
        re.I,
    )
    CLAUSE_SPLIT = re.compile(r"(?<=[.;:。；：])\s+|\n\s*(?=[-*\d|>])|\s+\|\s+")

    forged = []
    for tag, text in (("decision.md", decision), ("review.md", review), ("oracle.md", oracle)):
        for sent in CLAUSE_SPLIT.split(text):
            s = sent.strip()
            if not CLAIM.search(s):
                continue
            if DENY.search(s) or LEXICAL_TRAP.search(s):
                continue
            forged.append(f"{tag}: {s[:170]}")

    # positive side: the three status statements must still read unsigned/pending
    d2_awaiting = bool(re.search(r"awaiting owner confirmation", decision))
    d3_awaiting = bool(re.search(r"awaiting I-16", decision))

    # ------------------------------------------------------------------
    # SELF-TEST: is the criterion RESPONSIVE, or is its PASS vacuous?
    # A criterion that never fires proves nothing by not firing. Feed it synthetic
    # claims of signedness (must fire) and synthetic non-claims that merely use the
    # vocabulary of signing (must NOT fire). If either side misbehaves, this card's
    # V-2 PASS would be worthless.
    # ------------------------------------------------------------------
    def claim_fires(s: str) -> bool:
        return bool(CLAIM.search(s)) and not DENY.search(s) and not LEXICAL_TRAP.search(s)

    must_fire = [
        "D1 is signed by the ops reviewer.",
        "D1 has been signed.",
        "D2 and D3 are confirmed.",
        "Confirmed: D1 is signed off.",
        "The ops reviewer signed D1.",
    ]
    must_not_fire = [
        "D1 is UNSIGNED and blocks promotion.",
        "must not happen until D1 is signed by an ops reviewer",
        "**Signer:** I-16 (the review assigned D3 there).",
        "It fails closed and needs the reviewer to confirm it.",
        "listed as a known limitation for the D2 signature.",
        "Decide D1 (below) -- it is a specialist decision and is **not** self-accepted.",
        "D1/D2/D3 none self-closed",
    ]
    missed = [s for s in must_fire if not claim_fires(s)]
    spurious = [s for s in must_not_fire if claim_fires(s)]
    responsive = not missed and not spurious
    record(
        "V-2b_criterion_is_responsive_self_test",
        responsive,
        must_fire_count=len(must_fire),
        missed_claims_false_negatives=missed,
        wrongly_flagged_false_positives=spurious,
        note="a criterion that cannot fire proves nothing by not firing",
    )

    # the status table in decision.md must still read UNSIGNED for D1
    d1_still_unsigned = bool(re.search(r"UNSIGNED\s*[—-]\s*blocks promotion", decision))
    d2_awaiting = bool(re.search(r"awaiting owner confirmation", decision))
    d3_awaiting = bool(re.search(r"awaiting I-16", decision))

    record(
        "V-2_withheld_half_still_withheld",
        all(ownership.values()) and not forged and d1_still_unsigned and d2_awaiting
        and d3_awaiting and responsive,
        ownership=ownership,
        forged_signature_claims=forged,
        d1_status_reads_UNSIGNED=d1_still_unsigned,
        d2_status_reads_awaiting=d2_awaiting,
        d3_status_reads_awaiting=d3_awaiting,
        criterion_responsive=responsive,
        note=("any carrier reading as 'signed' would be a forged signature; the criterion is "
              "bound to the SIGNEDNESS PREDICATE, not to the vocabulary of signing"),
    )

    # =======================================================================
    # V-3  THE BAN IS ON DISK AND IS EXPLICIT
    # =======================================================================
    ban = {
        "decision.md": bool(re.search(r"must not\s+\n?>?\s*happen until D1 is signed|must not\s+enter", decision)
                            or re.search(r"RF/tools/", decision)),
        "review.md": bool(re.search(r"must\s+\*\*not\*\*\s+enter|promotion prohibition|promotion is forbidden", review)),
        "oracle.md": bool(re.search(r"promotion into `RF/tools/` must not happen until D1 is signed", oracle)),
        "handoff.json": bool(handoff.get("promotion_blocked", {}).get("statement")),
    }
    names_rf_tools = {
        "decision.md": "RF/tools/" in decision,
        "review.md": "RF/tools/" in review,
        "oracle.md": "RF/tools/" in oracle,
        "handoff.json": "RF/tools/" in json.dumps(handoff, ensure_ascii=False),
    }
    hb = handoff.get("promotion_blocked", {})
    signers = hb.get("signers", {})
    record(
        "V-3_ban_is_on_disk_and_explicit",
        all(ban.values()) and all(names_rf_tools.values())
        and bool(signers.get("D1")) and bool(signers.get("D2")) and bool(signers.get("D3")),
        carriers_with_ban=ban,
        carriers_naming_RF_tools=names_rf_tools,
        handoff_signers=signers,
        note="the ban must name the destination explicitly, not merely say 'blocked'",
    )

    # =======================================================================
    # V-4  THE BAN IS OBEYED  <-- load-bearing
    # =======================================================================
    # CRITICAL: `core.autocrlf = true` in this repo means the on-disk iso/ copy is CRLF while
    # the checked-out production file is LF. A raw byte/sha256 comparison of the two therefore
    # reports "the files differ" for two files with IDENTICAL content -- and would have led
    # straight to the false and serious conclusion "the patched tool WAS promoted".
    # This is the same trap that has now fired five times in this repo (see memory log).
    # The load-bearing question is a CONTENT question, so the criterion must normalise newlines.
    def content_only(p: Path) -> bytes:
        return p.read_bytes().replace(b"\r\n", b"\n")

    prod = REPO / "tools" / "slo_probe.py"
    before = T14A / "iso" / "tool_prod" / "slo_probe.py"
    patched = T14A / "iso" / "slo_probe_patched.py"

    prod_sha = sha256_file(prod) if prod.exists() else None
    before_sha = sha256_file(before) if before.exists() else None
    patched_sha = sha256_file(patched) if patched.exists() else None
    prod_blob = subprocess.run(["git", "hash-object", str(prod)],
                               cwd=REPO, capture_output=True, text=True).stdout.strip()
    head_blob = subprocess.run(["git", "rev-parse", "HEAD:tools/slo_probe.py"],
                               cwd=REPO, capture_output=True, text=True).stdout.strip()

    # (1) the production file and the frozen PRE-PATCH image must be the same CONTENT
    prod_is_pre_patch_content = (content_only(prod) == content_only(before))
    # (2) and the pre-patch image must be the hashed before-image the review cited
    before_is_the_cited_image = (before_sha == PROD_SLO_SHA256)
    # (3) the patched tool must be the patched tool (and differ in content, not just CRLF)
    patched_is_the_patch = (patched_sha == PATCHED_SHA256)
    patched_differs_in_content = (content_only(patched) != content_only(prod))
    # (4) the working copy must equal HEAD (no uncommitted promotion)
    workspace_clean = (prod_blob == head_blob == PROD_SLO_BLOB)

    # (5) no promoted test copy -- only the two files that already existed
    slo_files = sorted(
        str(p.relative_to(REPO)).replace("\\", "/")
        for p in (REPO / "tools").rglob("*") if p.is_file() and "slo_probe" in p.name
    )
    no_promoted_test = set(slo_files) <= {"tools/slo_probe.py", "tools/tests/test_slo_probe.py"}

    record(
        "V-4_ban_is_obeyed_not_promoted",
        prod_is_pre_patch_content and before_is_the_cited_image and patched_is_the_patch
        and patched_differs_in_content and workspace_clean and no_promoted_test,
        production_tools_slo_probe_sha256=prod_sha,
        frozen_pre_patch_sha256=before_sha,
        production_content_equals_frozen_pre_patch=prod_is_pre_patch_content,
        production_byte_difference_is_only_newlines=(
            prod_sha != before_sha and prod_is_pre_patch_content
        ),
        iso_patched_sha256=patched_sha,
        iso_patched_is_the_patch=patched_is_the_patch,
        iso_patched_differs_from_production_in_content=patched_differs_in_content,
        production_git_blob=prod_blob,
        head_git_blob=head_blob,
        working_copy_equals_HEAD=workspace_clean,
        slo_probe_files_under_tools=slo_files,
        note=("this leg carries the card: the ban is real only if the file really is not there. "
              "Compared by CONTENT because iso/ is CRLF and production is LF."),
    )

    # =======================================================================
    # V-5  THE TIER-2 ROWS STILL SAY "待裁方", NOT "owner 已裁"
    # =======================================================================
    tier2_block = ""
    m = re.search(r"### TIER-2(.*?)### TIER-3", owner_dec, re.S)
    if m:
        tier2_block = m.group(1)
    rows = {}
    for tid in ("T2-5", "T2-6", "T2-7"):
        r = re.search(r"^\|\s*" + tid + r"\s*\|(.+)$", owner_dec, re.M)
        rows[tid] = r.group(1) if r else ""
    t2_rows_name_other_party = all(
        re.search(r"(待裁方|跨仓双方|reviewer|owner|I-16)", rows[t]) for t in rows
    )
    t2_rows_say_authorise_start = all(
        re.search(r"授权(送签|启动|对接|同批启动)", rows[t]) for t in rows
    )
    # no TIER-2 row may record a *conclusion* as if the owner produced it.
    # NEGATION-BLINDNESS GUARD: the whole POINT of the TIER-2 preamble is to say
    # "本类**不得**记为「owner 已裁」" -- i.e. it contains the forbidden phrase inside a
    # PROHIBITION. A keyword grep flags the prohibition as the violation. Exclude any line
    # carrying a prohibition/negation marker. (Third instance of this bug in this card.)
    OWNER_DECIDED = re.compile(r"(owner 已裁|OWNER DECIDED|已是 owner 裁定)")
    NEG = re.compile(r"(不得|禁止|未能|不是|非|未|勿|must not|MUST NOT|not\b)")
    tier2_conclusion_smuggling = [
        ln.strip()[:160] for ln in tier2_block.split("\n")
        if OWNER_DECIDED.search(ln) and not NEG.search(ln)
    ]
    # and the execution-discipline clause must be present
    discipline = bool(re.search(r"「总的批准」不得膨胀为「所有的结论」", owner_dec))
    record(
        "V-5_tier2_rows_still_say_pending_party",
        t2_rows_name_other_party and t2_rows_say_authorise_start
        and not tier2_conclusion_smuggling and discipline,
        t2_rows_name_other_party=t2_rows_name_other_party,
        t2_rows_say_authorise_start=t2_rows_say_authorise_start,
        tier2_conclusion_smuggling=tier2_conclusion_smuggling,
        execution_discipline_clause_present=discipline,
        t2_rows={k: v[:150] for k, v in rows.items()},
        note="TIER-2 is exactly where owner authorises starting and the other party rules",
    )

    # =======================================================================
    # verdict
    # =======================================================================
    overall = "PASS" if not failures else "FAIL"
    print(json.dumps({
        "card": "T1-26",
        "attempt": "a20260920-01",
        "overall": overall,
        "failures": failures,
        "propositions": results,
    }, ensure_ascii=False, indent=2))
    return 0 if overall == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
