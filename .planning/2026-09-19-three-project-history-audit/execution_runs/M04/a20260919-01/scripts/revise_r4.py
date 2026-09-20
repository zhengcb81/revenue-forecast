"""Revision r4: point-review bookkeeping remediation for M01-M04.

Applies every item the independent point review requires (report sections 11-12),
WITHOUT touching any measured value, frozen expectation, threshold, negative-case
count or the disclosure_adaptation / accuracy qualification columns.

  P1-1  M02/M04 oracle.md: append an honest r2 index section (option (1) of 11.3)
  P1-2  M02/M03/M04: each card now has its own recovery/.../selfcheck_result.json
  P1-3  handoff.revision_history deduplicated to 4 + an r4 verdict entry
  P2-1  handoff.status / reviewer_status / reviewer_scope / reviewer_finding
  P2-2  qualification.json.formula -> accepted_scoped + independent_review block
  P2-3  source_manifest oracle version index: pre-append + current disk hash
  P3-1  revision_r3.json self-reference made explicit; real hash recorded outside
  P3-2  revision_r2.review_items scoped to this card; forensics pointer corrected
  P3-3  shared-copy files registered
  +     M03 frozen-body provenance event registered PERMANENTLY
  +     reviewer verdict text pasted from the report (extracted, not transcribed)
  +     reviewer "could not verify" list carried over verbatim

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import io
import json
import os

RF = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
PLAN = os.path.join(RF, ".planning", "2026-09-19-three-project-history-audit")
CARDS = ["M01", "M02", "M03", "M04"]
R4_INPUTS = os.path.join(PLAN, "execution_runs", "_r4_inputs")

REVIEWER_AT = "2026-09-20"
REVIEWER_NAME = "independent reviewer session (point review)"
REVIEWER_FINDING = ("independent reviewer session (point review), 2026-09-20; 4 P1 bookkeeping/delivery "
                    "findings raised; none changes the formula conclusion")


def attempt(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01")


def evidence(card):
    return os.path.join(attempt(card), "evidence", card)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def sub(path, old, new, expect=1, label=""):
    text = read_text(path)
    n = text.count(old)
    if n == 0 and text.count(new) >= 1:
        print("      [%s] already applied" % label)
        return False
    if n != expect:
        raise SystemExit("FATAL %s: expected %d of %r in %s, found %d" % (label, expect, old, path, n))
    write_text(path, text.replace(old, new))
    print("      [%s] replaced %d" % (label, n))
    return True


# ---------------------------------------------------------------------------
# P1-1: append an honest r2 index to M02 / M04 oracle.md (option (1) of 11.3)
# ---------------------------------------------------------------------------
R2_INDEX = """
---

## 修订 r2 索引（独立复审后追加，非重写）

**本节为事后补记：r2 轮曾声称已追加本节但实际未落盘。**

- 事实（盘上可核）：r2 稿件在 `review.md` 的 `### Frozen expectations were NOT rewritten` 段逐字声称
  "`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body"，
  但盘上 `oracle.md` 当时**没有任何 r2 段**，也从未被追加过。
- 根因（点复审定位）：共享脚本 `scripts/apply_r2_patches.py` 把 `oracle.md` 的追加**写死在
  `if card == "M03":` 分支内**；M01 的 r2 段由仅存在于 M01 的 `scripts/finalize_r2.py` 写入。
  本卡两者都不适用，因此 r2 的处置只落在 `review.md`、`evidence/<card>/revision_r2.json`
  与 `handoff.json`，**oracle 层无载体**。
- 后果与取舍：`source_manifest.json` 对本卡显示 MATCH，**恰恰因为从未追加**，
  **不得**读成"账目更规范"，也不得读成"已响应复审"。
- 本卡追加前状态（点复审实测，本 attempt 复算一致）：**%d B**，sha256 `%s`。
  下方补记的其他小节亦为 r4 追加，属同一性质。
- 三点状态索引（本卡适用者）：
  - `F-M01-02`（退出码承载裁决）：CLOSED。`run_card.py` 现为 rc=0 仅在正例在容差内、
    连续性正例通过且全部负例被 `ModelRegistryError` 拒绝时给出；rc=2 = positive 输入损坏致无裁决；
    rc=3 = 裁决为负；rc=1 = guard 之外的 harness 缺陷。本卡自检见
    `recovery/r2_exit_code_selfcheck/selfcheck_result.json`（A=3/B=1/C=0/D=2）。
  - `F-M01-03`（交付目录/编码）：CLOSED。`changes.diff`、`after/`、`recovery/README.md` 已补，
    日志统一 UTF-8。
  - `F-M02-01`（被忽略字段是否仍须满足域约束）：**保留待 owner 裁定**，未自决、未改产品；
    见 `decision.md` DEC-M02-3 与 `handoff.json.open_questions`。
- **本节不改变任何数值结论**：正例/负例预期、容差、披露映射数值、拒绝条件与三种资格均未改动。
"""


def do_p1_1(card):
    print("\nP1-1 (M02/M04 oracle.md honesty)")
    if card not in ("M02", "M04"):
        return None
    path = os.path.join(attempt(card), "oracle.md")
    before_bytes = os.path.getsize(path)
    before_hash = sha256_file(path)
    text = read_text(path)
    if "## 修订 r2 索引" in text:
        print("      already appended")
        return {"already": True}
    write_text(path, text.rstrip("\n") + "\n" + (R2_INDEX % (before_bytes, before_hash)))
    print("      appended r2 index; before=%d B / %s" % (before_bytes, before_hash[:16]))
    return {"before_bytes": before_bytes, "before_sha256": before_hash}

    # NOTE: option (2) of 11.3 (re-word review.md) is deliberately NOT taken;
    # option (1) is the recommended one and the claim in review.md is now TRUE.


# ---------------------------------------------------------------------------
# M03: register the frozen-body provenance event permanently
# ---------------------------------------------------------------------------
def do_m03_provenance():
    print("\nM03 frozen-body provenance event (permanent)")
    rec = os.path.join(attempt("M03"), "recovery", "README.md")
    note = """
## PERMANENT provenance event: the frozen body of `oracle.md` WAS modified once

This is recorded permanently and **must not be rewritten as "never modified"**.

- **What happened:** the `NEW-1` fix (point-review follow-up) changed the *frozen body* of `oracle.md`
  inside `## 7. 披露映射`: the printed derived unit price on the mapping-1/mapping-2 lines went from
  `123,751.5203...` to `123,751.503987` (full precision). The pre-change file was
  `d0bed79bd868cda3dd2a0a7f3fcd45fca738f7a0f3fdd5c4abe16cb52a208764`; after the change it is
  `45f10b58008f6020a97243d92375927170c69502ef9e2c32986d973a236ab2f3` (both stated in the r3 note in
  `oracle.md`).
- **Why it was allowed:** the edited text was a *transcription typo in a derived unit price*, not a
  formula expectation, tolerance, negative-case count or disclosure figure. The frozen decision values
  (`[305]`, 13/13 negatives, the 2% tolerance, the 14.3667% gap) were not touched, and `oracle.json` has
  not changed since the first freeze. The implementer disclosed it in the same revision.
- **Consequence for how this card must be described:** for M03 the statement "the frozen expectations
  were not rewritten" is **NOT** available. The correct statement is:
  **"the frozen body was modified once, for a printed typo, and was self-disclosed."**
- **Why it is not reverted:** reverting would restore a value inconsistent with the printed result, and
  would hide a real provenance event. The append-only form was broken once; that fact is permanent.
"""
    text = read_text(rec)
    if "PERMANENT provenance event" in text:
        print("      already registered")
    else:
        write_text(rec, text.rstrip("\n") + "\n" + note)
        print("      registered in recovery/README.md")

    hp = os.path.join(attempt("M03"), "handoff.json")
    h = load_json(hp)
    entry = ("M03 PERMANENT provenance event: the frozen body of oracle.md WAS modified once (r3, NEW-1: "
             "printed derived unit price 123,751.5203 -> 123,751.503987, d0bed79b... -> 45f10b58...). "
             "Disclosed in the same revision; the frozen decision values and oracle.json were not touched. "
             "For M03 the claim 'frozen expectations were not rewritten' is NOT available; the correct "
             "wording is 'the frozen body was modified once, for a printed typo, and was self-disclosed'. "
             "Not reverted, by design.")
    if not any(q.startswith("M03 PERMANENT provenance event") for q in h["open_questions"]):
        h["open_questions"].append(entry)
        dump_json(hp, h)
        print("      registered in handoff.open_questions")


# ---------------------------------------------------------------------------
# P1-3 / P2-1 / P3-2: handoff.json
# ---------------------------------------------------------------------------
def do_handoff(card):
    print("\nhandoff.json (P1-3, P2-1, P3-2)")
    hp = os.path.join(attempt(card), "handoff.json")
    h = load_json(hp)

    # P1-3: dedupe revision_history to the 4 real rounds, keep first of each
    seen = set()
    deduped = []
    for entry in h.get("revision_history", []):
        key = (entry.get("revision"), entry.get("review_outcome"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    r4_entry = {
        "revision": "r4",
        "review_outcome": ("point review returned: accepted_scoped (formula qualification only); "
                           "4 P1 bookkeeping findings open"),
        "reviewer": REVIEWER_NAME,
        "reviewed_at": REVIEWER_AT,
        "scope": "formula only",
    }
    if not any(e.get("revision") == "r4" for e in deduped):
        deduped.append(r4_entry)
    h["revision_history"] = deduped
    print("      revision_history: %d entries" % len(deduped))

    # P2-1: status vocabulary + reviewer fields
    h["status"] = "accepted_scoped"
    h["reviewer_status"] = "point_review_returned"
    h["reviewer_scope"] = "formula only"
    h["reviewer_finding"] = REVIEWER_FINDING
    # qualifications.formula kept verbatim; the other two columns untouched
    h["qualifications"]["disclosure_adaptation"] = "unmapped"
    h["qualifications"]["accuracy"] = "unproven"

    # P3-2: M01-specific forensics pointer corrected on the non-M01 cards
    if card != "M01":
        h["open_questions"] = [
            q.replace("Recorded in evidence/<card>/first_run_forensics.json (M01) and the review.md r2 section.",
                      "Recorded in M01's evidence/M01/first_run_forensics.json (this card has no such file; "
                      "the gap is M01-specific) and the review.md r2 section.")
            for q in h["open_questions"]
        ]
        print("      forensics pointer corrected")

    # P2-1: the raw-exit-code ledger gains the r4 self-check per card
    h.setdefault("raw_exit_codes", {})["R4_selfcheck_A_corrupted_oracle"] = 3
    h.setdefault("expected_exit_codes", {})["R4_selfcheck_A_corrupted_oracle"] = 3
    h["raw_exit_codes"]["R4_selfcheck_B_corrupted_case_plan"] = 1
    h["expected_exit_codes"]["R4_selfcheck_B_corrupted_case_plan"] = "non-zero"
    h["raw_exit_codes"]["R4_selfcheck_C_uncorrupted"] = 0
    h["expected_exit_codes"]["R4_selfcheck_C_uncorrupted"] = 0
    h["raw_exit_codes"]["R4_selfcheck_D_corrupted_positive_input"] = 2
    h["expected_exit_codes"]["R4_selfcheck_D_corrupted_positive_input"] = 2
    h["commands_executed"] = sorted(set(h.get("commands_executed", []) + ["R4-selfcheck-card"]))

    # P3-3: register the shared-copy files honestly
    h["shared_copy_registration"] = {
        "note": ("F-M01-03 asked for complete directories and UTF-8, not for per-card independence; the "
                 "following files are nevertheless byte-identical across the four attempts because they "
                 "record the SAME repository/tooling fact. They are not, and are not claimed to be, "
                 "per-card independent observations."),
        "identical_across_cards": {
            "before/git_status_revenue-forecast.txt": sha256_file(os.path.join(attempt(card), "before", "git_status_revenue-forecast.txt")),
            "before/pytest_version.txt": sha256_file(os.path.join(attempt(card), "before", "pytest_version.txt")),
            "after/rerun_stderr.txt": sha256_file(os.path.join(attempt(card), "after", "rerun_stderr.txt")),
        },
        "per_card_distinct_evidence": {
            "after/rerun_stdout.txt": sha256_file(os.path.join(attempt(card), "after", "rerun_stdout.txt")),
            "recovery/README.md": sha256_file(os.path.join(attempt(card), "recovery", "README.md")),
            "recovery/r2_exit_code_selfcheck/selfcheck_result.json":
                sha256_file(os.path.join(attempt(card), "recovery", "r2_exit_code_selfcheck",
                                         "selfcheck_result.json")),
            "comment": "these differ per card and therefore carry this card's own re-run evidence",
        },
    }

    # evidence paths: the self-check file now exists for EVERY card (P1-2 via option 1)
    h["evidence_paths"] = sorted(set(h.get("evidence_paths", []) + [
        "recovery/r2_exit_code_selfcheck/selfcheck_result.json",
        "evidence/%s/revision_r4.json" % card,
    ]))
    dump_json(hp, h)
    print("      status=%s reviewer_status=%s" % (h["status"], h["reviewer_status"]))


# ---------------------------------------------------------------------------
# P2-2: qualification.json
# ---------------------------------------------------------------------------
def do_qualification(card):
    print("\nqualification.json (P2-2)")
    qp = os.path.join(evidence(card), "qualification.json")
    q = load_json(qp)
    f = q["formula"]
    f["status"] = "accepted_scoped"
    f["not_yet_independently_reviewed"] = False
    f["implementer_claim"] = "pass"          # kept: self-assessment and independent verdict stay separate
    f["independent_review"] = {
        "reviewer": REVIEWER_NAME,
        "reviewed_at": REVIEWER_AT,
        "scope": "formula only",
        "verdict": "accepted_scoped",
        "basis": ("reviewer-authored inputs recomputed against iso/checkout_scripts; oracle.json regenerated "
                  "byte-identical; 18 reviewer-authored negatives all rejected with ModelRegistryError"),
    }
    q["disclosure_adaptation"] = q["disclosure_adaptation"]   # untouched by construction
    q["accuracy"] = q["accuracy"]
    dump_json(qp, q)
    print("      formula.status=%s not_yet_independently_reviewed=%s"
          % (f["status"], f["not_yet_independently_reviewed"]))


# ---------------------------------------------------------------------------
# P2-3 / P3-1 / P3-2: source_manifest.json and revision_r3.json
# ---------------------------------------------------------------------------
def do_manifests(card):
    print("\nsource_manifest.json (P2-3) + revision_r3.json (P3-1)")
    sp = os.path.join(evidence(card), "source_manifest.json")
    sm = load_json(sp)
    ov = sm.setdefault("oracle_versions", {})
    oracle_md = os.path.join(attempt(card), "oracle.md")
    current_hash = sha256_file(oracle_md)
    current_bytes = os.path.getsize(oracle_md)

    before_entry = None
    if card == "M01":
        before_entry = {
            "version": "v1_frozen_then_appended",
            "path": "oracle.md",
            "sha256": "88635eb46df3c3d13f6ac0bc9af884d1b8d92aac50c6f7703c2f29a7a227d99f",
            "bytes": 9889,
            "note": ("pre-r2-append frozen body, byte-boundary reproduced by the point review; the "
                     "authoritative r2-append boundary"),
        }
    elif card == "M03":
        before_entry = {
            "version": "v1_frozen_then_body_edited_in_r3",
            "path": "oracle.md",
            "sha256": "d0bed79bd868cda3dd2a0a7f3fcd45fca738f7a0f3fdd5c4abe16cb52a208764",
            "note": ("state accepted by the r2 review; the r3 NEW-1 fix then edited the FROZEN BODY "
                     "(printed unit price), which is registered as a permanent provenance event in "
                     "recovery/README.md. Unlike M01 this is an in-body edit, NOT an append, so there is "
                     "no clean byte boundary for it and the only evidence is the stated before/after hash."),
        }
    elif card in ("M02", "M04"):
        before_entry = {
            "version": "v1_frozen_unamended_until_r4",
            "path": "oracle.md",
            "sha256": None,   # filled below from the r4 append record
            "bytes": None,
            "note": ("the file was NEVER appended to during r2/r3; r4 appended an honest r2 index section "
                     "together with the word that r2 had claimed an append that never landed"),
        }

    if before_entry and before_entry["sha256"] is None:
        r4p = os.path.join(evidence(card), "revision_r4.json")
        if os.path.exists(r4p):
            r4 = load_json(r4p)
            rec = r4["items"].get("P1-1", {})
            before_entry["sha256"] = rec.get("oracle_md_sha256_before_r4_append")
            before_entry["bytes"] = rec.get("oracle_md_bytes_before_r4_append")
        else:
            before_entry["sha256"] = "PENDING (revision_r4.json not yet written)"
            before_entry["bytes"] = "PENDING"

    ov["oracle_md_versions"] = [e for e in [before_entry] if e] + [{
        "version": "current_on_disk_at_r4",
        "path": "oracle.md",
        "sha256": current_hash,
        "bytes": current_bytes,
        "note": ("this field is the r4 close-out state; the authoritative pin is "
                 "revision_r3.json.authoritative_hashes_at_r3_closeout (pre-r4) plus "
                 "revision_r4.json (post-r4)"),
    }]

    # P3-2: review_items scoped to this card
    r2 = sm.get("revision_r2", {})
    if r2:
        own = []
        for item in r2.get("review_items", []):
            if item.startswith("F-M03") and card != "M03":
                continue
            if item.startswith("F-M04") and card != "M04":
                continue
            own.append(item)
        own = [i for i in own if not (i.startswith("F-M01") and card != "M01")] or own
        # keep the card-agnostic harness/delivery items plus this card's own domain items
        keep = ["F-M01-02", "F-M01-03"]
        if card == "M01":
            keep = ["F-M01-01"] + keep
        if card == "M03":
            keep.append("F-M03-01")
        if card == "M04":
            keep.append("F-M04-01")
        keep.append("F-M02-01(pending ruling)")
        r2["review_items"] = keep
        r2["review_items_note"] = ("scoped to this card in r4; the previous list was a shared template that "
                                   "also named other cards' items (point review P3-2)")
        sm["revision_r2"] = r2

    dump_json(sp, sm)
    print("      oracle_md_versions entries: %d" % len(ov["oracle_md_versions"]))
    print("      review_items: %s" % sm.get("revision_r2", {}).get("review_items"))

    # ---- P3-1: the self-referential hash ----
    r3p = os.path.join(evidence(card), "revision_r3.json")
    r3 = load_json(r3p)
    block = r3.get("authoritative_hashes_at_r3_closeout", {})
    if "evidence/revision_r3.json" not in block:
        block["evidence/revision_r3.json"] = {}
    block["evidence/revision_r3.json"] = {
        "sha256": ("SELF-REFERENCE: a file cannot contain its own final sha256; use the value recorded by the "
                   "verifier outside this file"),
        "bytes": os.path.getsize(r3p),
        "external_record": "after/rerun_sha256.json -> self_hashes.evidence/revision_r3.json",
        "note": ("the point review found the previous number unreproducible under four different "
                 "self-reference reconstructions; this entry is now an explicit non-claim"),
    }
    r3["authoritative_hashes_at_r3_closeout"] = block
    dump_json(r3p, r3)

    real_r3_hash = sha256_file(r3p)
    ap = os.path.join(attempt(card), "after", "rerun_sha256.json")
    after = load_json(ap)
    after["self_hashes"] = {
        "note": ("external home for hashes that a file cannot state about itself; recomputed after every "
                 "write in r4"),
        "evidence/revision_r3.json": real_r3_hash,
    }
    dump_json(ap, after)
    print("      revision_r3.json real sha256 recorded outside: %s" % real_r3_hash[:16])


# ---------------------------------------------------------------------------
# verdict paste + reviewer scope block
# ---------------------------------------------------------------------------
REVIEWER_SCOPE_BLOCK = """
---

## 点复审未予验证的事项（原样承接，不得当作已证）

以下为独立点复审明确列为"未能验证"的事项，本 attempt 原样承接，**不**声称已解决：

1. `revision_r3.json` 自称的自我 sha256 不可核验（r4 已改为显式 non-claim 并把真实值外置）。
2. 首跑 stderr 的原始字节**客观已不存在**（被成功重跑覆盖）；"首跑确实发生 `KeyError: 'continuity'`"
   **无法独立证实**，只有会话转录捕获与 mtime 序列。
3. `oracle.md` **首冻版的运行前 hash 四卡均未记录**（`F-M01-01` 的实质缺口，不可回填）。
4. M03 冻结正文的改动**发生在哪一轮**无法独立复算（盘上无该中间态副本，只有实现者自述的前后 hash）。
5. `<PLAN>\\reviews` 的 4 个子目录对当前用户拒绝访问，**无法遍历排除内部被写**；
   整树最新 mtime 仍是 09-19 10:05:32，本 session 亦未写入该目录。
6. `scripts/model_registry.py` 的 mtime 变更**无法归因**（内容 hash 未变，不影响本卡）。
7. 本卡的 D/E/F **会计/行业实质**未获审阅（需签署方）；本裁决仅覆盖 A–C（formula）+ 记账。
8. 并发卡 M05–M31 的任何陈述均为**时点观察**，其后可能已被其他 session 改变。
"""


def do_verdict(card):
    print("\nreviewer verdict paste + scope block")
    review = os.path.join(attempt(card), "review.md")
    text = read_text(review)
    if "## 独立 reviewer session 点复审（裁决）" in text:
        print("      verdict already present")
        return
    vp = os.path.join(R4_INPUTS, "verdict_%s.md" % card)
    verdict = read_text(vp)
    write_text(review, text.rstrip("\n") + "\n\n---\n\n" + verdict.rstrip("\n") + "\n"
               + REVIEWER_SCOPE_BLOCK)
    print("      pasted verdict (%d chars) + scope block" % len(verdict))


def main():
    for card in CARDS:
        print("\n================ %s ================" % card)
        # ordering matters: manifests read revision_r4.json, so write it first
        rec = do_p1_1(card)
        r4 = {
            "card_id": card,
            "revision": "r4",
            "scope": "point-review bookkeeping remediation (report sections 11-12)",
            "product_calls_rerun": False,
            "measurements_changed": False,
            "production_repos_written": False,
            "items": {
                "P1-1": ({"status": "fixed_by_append",
                          "option_taken": "(1) append an honest r2 index to oracle.md",
                          "oracle_md_bytes_before_r4_append": rec["before_bytes"] if rec else None,
                          "oracle_md_sha256_before_r4_append": rec["before_sha256"] if rec else None,
                          "note": ("r2 claimed an append that never landed; the appended section says so. "
                                   "MATCH in source_manifest before r4 was a by-product of never appending "
                                   "and must not be read as better bookkeeping.")}
                         if card in ("M02", "M04") else
                         {"status": "not_applicable", "reason": "only M02/M04 lacked the r2 section"}),
                "P1-2": {"status": "fixed_by_option_1",
                         "detail": ("each card now has its own "
                                    "recovery/r2_exit_code_selfcheck/selfcheck_result.json, produced by that "
                                    "card's own scripts/selfcheck_card.py, with harness hash and rc values"),
                         "harness_sha256": sha256_file(os.path.join(attempt(card), "scripts", "run_card.py")),
                         "cases": {"A": 3, "B": 1, "C": 0, "D": 2}},
                "P1-3": {"status": "fixed",
                         "detail": "handoff.revision_history deduplicated to the 4 real rounds + r4 entry"},
                "P2-1": {"status": "fixed",
                         "detail": "status=accepted_scoped, reviewer_status=point_review_returned, "
                                   "reviewer_scope=formula only, reviewer_finding added; the other two "
                                   "qualification columns untouched"},
                "P2-2": {"status": "fixed",
                         "detail": "qualification.json.formula -> accepted_scoped, "
                                   "not_yet_independently_reviewed=false, independent_review block added; "
                                   "implementer_claim kept"},
                "P2-3": {"status": "fixed",
                         "detail": "source_manifest oracle_md_versions now carries pre-append + current, with "
                                   "the authoritative pin pointed at revision_r3/r4 records"},
                "P3-1": {"status": "fixed",
                         "detail": "self-referential hash replaced by an explicit non-claim; real value "
                                   "recorded in after/rerun_sha256.json.self_hashes"},
                "P3-2": {"status": "fixed",
                         "detail": "review_items scoped to this card; M01-specific forensics pointer "
                                   "corrected on non-M01 cards"},
                "P3-3": {"status": "registered",
                         "detail": "shared-copy files registered in handoff.shared_copy_registration; no "
                                   "per-card independence is claimed for them"},
                "M03_provenance": ({"status": "registered_permanently",
                                    "detail": "frozen-body edit recorded in recovery/README.md and "
                                              "handoff.open_questions; NOT reverted and NOT relabelled"}
                                   if card == "M03" else {"status": "not_applicable"}),
            },
            "discipline_assertion": {
                "measurements_unchanged": ["[220,110,0]", "[80,0,120]", "[305]", "[730]"],
                "negative_counts_unchanged": {"M01": 11, "M02": 11, "M03": 13, "M04": 15},
                "tolerances_unchanged": {"M03": "2%", "M04": "0.5%"},
                "gaps_unchanged": {"M03": "14.3667%", "M04": "21.4045%"},
                "qualification_columns_untouched": ["disclosure_adaptation=unmapped", "accuracy=unproven"],
            },
        }
        dump_json_r4 = os.path.join(evidence(card), "revision_r4.json")
        dump_json(dump_json_r4, r4)
        do_handoff(card)
        do_qualification(card)
        do_manifests(card)
        if card == "M03":
            do_m03_provenance()
        do_verdict(card)
        # refresh the r4 record with the final hashes of everything it names
        r4["final_hashes"] = {}
        for rel in ("oracle.md", "review.md", "handoff.json", "recovery/README.md",
                    "after/rerun_sha256.json",
                    "recovery/r2_exit_code_selfcheck/selfcheck_result.json"):
            p = os.path.join(attempt(card), rel.replace("/", os.sep))
            if os.path.exists(p):
                r4["final_hashes"][rel] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
        for rel in ("qualification.json", "source_manifest.json", "revision_r3.json", "revision_r4.json"):
            p = os.path.join(evidence(card), rel)
            if os.path.exists(p):
                r4["final_hashes"]["evidence/" + rel] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
        dump_json(dump_json_r4, r4)
    print("\nr4 remediation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
