"""Revision r2, part 2: content corrections and handoff updates.

Applies:
  F-M03-01  arithmetic typo in four M03 files -> corrected to the values that
            evidence/M03/oracle.json already contained (full-precision unit price)
  F-M04-01  "781,861 wafers/month" -> "780,860.59 wafers/month"
  F-M01-03  revision r2 sections appended to review.md, handoff.json refreshed
  F-M02-01  reserved for owner/specialist adjudication, written into
            handoff.json.open_questions (NOT self-decided)

Corrected values are READ FROM oracle.json at runtime so the files can never
diverge from the artefact again.

ASCII-only stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone, timedelta

STALE_REBUILD = "528,681,308,161.71"
STALE_GAP = "88,700,626,838.29"


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("  wrote", os.path.relpath(path))


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sub_exact(path, old, new, expect=1, label=""):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    count = text.count(old)
    if count != expect:
        raise SystemExit("FATAL %s: expected %d occurrences of %r in %s, found %d"
                         % (label, expect, old, path, count))
    write_text(path, text.replace(old, new))
    print("    replaced %d x %r -> %r (%s)" % (count, old, new, label))


def fmt_money(raw):
    """84051820000.00 -> 84,051,820,000.00"""
    if "." in raw:
        whole, frac = raw.split(".")
        return "{:,}".format(int(whole)) + "." + frac
    return "{:,}".format(int(raw))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    args = parser.parse_args()
    card = args.card

    rf = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    plan = os.path.join(rf, ".planning", "2026-09-19-three-project-history-audit")
    attempt = os.path.join(plan, "execution_runs", card, "a20260919-01")
    evidence = os.path.join(attempt, "evidence", card)
    print("=== r2 patches for", card, "===")

    oracle = load_json(os.path.join(evidence, "oracle.json"))
    rev = load_json(os.path.join(evidence, "revision_r2.json"))

    # ---------------- F-M03-01 ----------------
    if card == "M03":
        m2 = oracle["disclosure_arithmetic"]["mapping_2_scope_residual"]
        good_rebuild = fmt_money(m2["rebuild_using_vehicle_total_at_pv_unit_price_cny"])
        good_gap = fmt_money(m2["gap_cny"])
        print("  correct values from oracle.json:", good_rebuild, good_gap)
        targets = [
            os.path.join(attempt, "oracle.md"),
            os.path.join(evidence, "historical_reconciliation.json"),
            os.path.join(evidence, "disclosure_mapping.json"),
            os.path.join(evidence, "accounting_decision.md"),
        ]
        for path in targets:
            sub_exact(path, STALE_REBUILD, good_rebuild, 1, "F-M03-01 rebuild")
            sub_exact(path, STALE_GAP, good_gap, 1, "F-M03-01 gap")

        note = """
### r2 更正 F-M03-01（算术笔误，非结论变更）

独立复审发现：`528,681,308,161.71` / `88,700,626,838.29` 是用**截断后的单价**（123,751.503987229
的四舍五入中间值）算出的，与 `evidence/M03/oracle.json` 中由**全精度单价 123,751.503986712** 得出的
`{rebuild}` / `{gap}` 不一致。四处（本文件、`historical_reconciliation.json`、
`disclosure_mapping.json`、`accounting_decision.md`）已改为与 `oracle.json` 一致的数值。

- 差异来源：中间步骤对单价取整；**结论不变**——gap 占分部收入 14.3667%（四舍五入相同），
  仍远超运行前冻结的 2% 容差，仍**严禁**把 gap 填入 `other_revenue`。
- 正例 `[305]`、负例 13/13、M03 的披露映射行/列选择与 hash **均未改动**。
- 自 r2 起，更正值改为从 `oracle.json` 读取后再写入，避免文件间再次分叉。
""".format(rebuild=good_rebuild, gap=good_gap)
        with open(os.path.join(attempt, "oracle.md"), "a", encoding="utf-8", newline="\n") as handle:
            handle.write(note)
        print("  appended F-M03-01 correction note to oracle.md")
        rev["items"]["F-M03-01"] = {
            "stale_rebuild": STALE_REBUILD, "stale_gap": STALE_GAP,
            "corrected_rebuild": good_rebuild, "corrected_gap": good_gap,
            "source_of_truth": "evidence/M03/oracle.json disclosure_arithmetic.mapping_2_scope_residual "
                               "(full-precision unit price 123,751.503986712)",
            "files_corrected": [os.path.relpath(p, attempt) for p in targets],
            "conclusion_unchanged": True,
            "gap_pct_unchanged": m2["gap_pct_of_segment"],
        }
        write_json_local = os.path.join(evidence, "revision_r2.json")
        with open(write_json_local, "w", encoding="utf-8") as handle:
            json.dump(rev, handle, ensure_ascii=False, indent=1)
        print("  recomputed evidence/M03/revision_r2.json")

    # ---------------- F-M04-01 ----------------
    if card == "M04":
        review = os.path.join(attempt, "review.md")
        sub_exact(review, "781,861", "780,860.59", 1, "F-M04-01 unit")
        rev["items"]["F-M04-01"] = {
            "file": "review.md", "stale": "781,861 wafers/month",
            "corrected": "780,860.59 wafers/month",
            "source_of_truth": "evidence/M04/oracle.json wafer_count_reconciliation."
                               "implied_monthly_capacity_diagnostic_only = 780,860.59",
            "note": "typo only; the other M04 files already carried the correct value",
        }
        with open(os.path.join(evidence, "revision_r2.json"), "w", encoding="utf-8") as handle:
            json.dump(rev, handle, ensure_ascii=False, indent=1)
        print("  recomputed evidence/M04/revision_r2.json")

    # ---------------- F-M02-01 (reserved for ruling) ----------------
    if card == "M02":
        note = """
## r2 追加：F-M02-01（跨模型一致性，**等待 owner/专业裁定，未自决**）

独立复审指出的行为不一致（本 attempt 实测，未改产品）：

| 观察点 | 实测内容 | 出处 |
|---|---|---|
| 校验器层面 | `calculate_registered_model` 在 dispatch 之前统一执行 `base < 0 -> ModelRegistryError`，对**所有**模型一致，不看该模型是否真的使用 `base_revenue` | `iso/checkout_scripts/model_registry.py`（sha256 9ec65295…），`evidence/M02/run_result.json` 的 `OBS-NEG-BASE` |
| 实现层面 | `_direct_revenue` 首行 `del base_revenue`（完全不用）；`_direct_growth` 用 `current = base_revenue` 递推（真实使用） | 同上（只读） |
| 实测 A | `base_revenue = 999` → 输出与正例**完全一致**，证明 `direct_revenue` 不把 base 用作项 | M02 `observations[BASE-INDEPENDENCE]` |
| 实测 B | `base_revenue = -5` → 仍抛 `ModelRegistryError: direct_revenue.base_revenue cannot be negative` | M02 `observations[OBS-NEG-BASE]` |

**为什么不自决**：这是"被忽略的输入字段是否仍须满足域约束"的**契约语义**问题，
涉及跨模型一致性（direct_growth 需要该字段，direct_revenue 不需要），
按 `START_HERE.md` 属于必须交专业审查的边界，且卡 L65 禁止在无独立反例与审定规格时改写实现。
两种候选语义及其后果已写在 DEC-M02-3；**本 attempt 不做任何代码改动**，
该议题已登记在 `handoff.json.open_questions`，标注 `requires_owner_or_specialist_ruling`。
"""
        with open(os.path.join(evidence, "accounting_decision.md"), "a", encoding="utf-8", newline="\n") as handle:
            handle.write(note)
        print("  appended F-M02-01 ruling-pending note to accounting_decision.md")
        rev["items"]["F-M02-01"] = {
            "status": "PENDING_OWNER_OR_SPECIALIST_RULING",
            "self_decided": False,
            "product_changed": False,
            "observed": {
                "validator_level": "base_revenue < 0 is rejected uniformly before dispatch for every model",
                "implementation_level": "_direct_revenue deletes base_revenue; _direct_growth consumes it",
                "base_999_replay": "output identical to the positive case",
                "base_negative_5": "ModelRegistryError: direct_revenue.base_revenue cannot be negative",
            },
            "options_for_ruling": [
                "A keep fail-closed: validate every supplied field even if unused (current behaviour, no change)",
                "B ignore unused fields: an unused base_revenue is semantically absent and must not be validated",
            ],
            "recorded_in": ["decision.md DEC-M02-3", "evidence/M02/accounting_decision.md (r2 section)",
                            "handoff.json.open_questions"],
        }
        with open(os.path.join(evidence, "revision_r2.json"), "w", encoding="utf-8") as handle:
            json.dump(rev, handle, ensure_ascii=False, indent=1)
        print("  recomputed evidence/M02/revision_r2.json")

    # ---------------- review.md r2 section (all cards) ----------------
    items = rev["items"]
    b_rc = items["F-M01-02"]["rerun_raw_returncode"]
    lines = [
        "",
        "---",
        "",
        "## revision r2 - response to the independent review (status stays `review_pending`)",
        "",
        "The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one",
        "item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was",
        "touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.",
        "",
        "### Verdict-carrying exit code (F-M01-02)",
        "",
        "| item | change | evidence |",
        "|---|---|---|",
        "| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when "
        "the positive path matches the independent oracle within tolerance, the continuity positive passes and "
        "**all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce "
        "a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so "
        "a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | "
        "`scripts/run_card.py`, `evidence/%s/revision_r2.json`, `after/rerun_sha256.json` |" % card,
        "| re-run | the same `calculate_registered_model` call was re-executed unchanged | "
        "**raw rc = %d** (expected 0), `evidence/%s/exit_code_semantics` = `verdict` / `exit_code` |"
        % (b_rc, "run_result.json"),
        "",
        "### Delivery completeness (F-M01-03)",
        "",
        "- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run"
        " hashes.",
        "- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no"
        " durable state, lock, lease or partial publication to recover.",
        "- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.",
        "- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).",
        "- `evidence/%s/first_run_forensics.json`: F-M01-01 record." % card,
        "",
        "### Frozen expectations were NOT rewritten",
        "",
        "`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and"
        " `evidence/%s/source_manifest.json.oracle_versions` now indexes the oracle document and script"
        " versions with hashes and timestamps." % card,
        "",
    ]
    if card == "M01":
        lines += [
            "### F-M01-01 - first-run evidence and version provenance (honest gap)",
            "",
            "- The first product run's stderr **cannot be recovered**: the corrected re-run redirected stderr"
            " to the same path and overwrote it, and `-B` suppressed `__pycache__`, so no bytecode record of"
            " the pre-fix oracle exists (a directory search confirmed this).",
            "- What is recorded instead: the exact first-run argv, `raw_rc = 1`, and the transcribed"
            " `KeyError: 'continuity'` traceback, explicitly labelled as a **session-transcript capture, not an"
            " original artefact** (`evidence/M01/first_run_forensics.json`).",
            "- oracle script v1 is stored as `scripts/oracle_M01.v1.reconstructed.py`, derived by reversing the"
            " one documented token change and explicitly marked **RECONSTRUCTED**.",
            "- **Remaining gap the reviewer should note:** the pre-run frozen hash of `oracle.md` was never"
            " captured (the manifest was generated after the re-run), so \"the frozen version was not edited to"
            " fit the result\" is supported only by the mtime sequence and by the fact that the frozen body is"
            " unmodified; it is not supported by a pre-run hash. This is stated rather than papered over.",
            "",
        ]
    elif card == "M03":
        lines += [
            "### F-M03-01 - arithmetic typo corrected",
            "",
            "- The rebuild/gap figures in `oracle.md`, `evidence/M03/historical_reconciliation.json`,"
            " `evidence/M03/disclosure_mapping.json` and `evidence/M03/accounting_decision.md` used a"
            " **truncated unit price**; they now match `evidence/M03/oracle.json`, which was always correct"
            " (full-precision unit price 123,751.503986712 -> rebuild %s, gap %s)."
            % (items["F-M03-01"]["corrected_rebuild"], items["F-M03-01"]["corrected_gap"]),
            "- Cause: intermediate rounding of the unit price. **Conclusion unchanged**: the gap is still"
            " 14.3667%% of the segment line, still far outside the pre-frozen 2%% tolerance, and filling it"
            " into `other_revenue` remains forbidden.",
            "- The corrected values are now **read from `oracle.json`** before being written, so the files"
            " cannot diverge again.",
            "",
        ]
    elif card == "M04":
        lines += [
            "### F-M04-01 - typo corrected",
            "",
            "- \"781,861 wafers/month\" -> **\"780,860.59 wafers/month\"**, matching"
            " `evidence/M04/oracle.json.wafer_count_reconciliation.implied_monthly_capacity_diagnostic_only`."
            " The other M04 files already carried the correct value; this was a prose typo only, and the"
            " ACTIVE `STOP_DISCLOSURE_ADAPTATION` conclusion is unchanged.",
            "",
        ]
    else:
        lines += [
            "### F-M02-01 - reserved for owner/specialist adjudication (not self-decided)",
            "",
            "- The reviewer asked for the two behaviours to be written up rather than resolved. Both are"
            " recorded in `decision.md` DEC-M02-3 and in the appended r2 section of"
            " `evidence/M02/accounting_decision.md`: the validator rejects `base_revenue < 0` uniformly before"
            " dispatch, while `_direct_revenue` deletes the field and `_direct_growth` consumes it. Measured:"
            " `base_revenue = 999` leaves the output identical; `base_revenue = -5` still raises"
            " `ModelRegistryError`.",
            "- No product change was made and no position is asserted; the item is carried in"
            " `handoff.json.open_questions` marked `requires_owner_or_specialist_ruling`.",
            "",
        ]
    lines += [
        "### Status",
        "",
        "- `formula`: still **`review_pending`** - the implementer does not sign acceptance.",
        "- `disclosure_adaptation`: still **`unmapped`**.",
        "- `accuracy`: still **`unproven`**.",
        "",
    ]
    with open(os.path.join(attempt, "review.md"), "a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    print("  appended revision r2 section to review.md")

    # ---------------- handoff.json refresh ----------------
    handoff_path = os.path.join(attempt, "handoff.json")
    handoff = load_json(handoff_path)
    handoff["status"] = "review_pending"
    handoff["revision"] = "r2"
    handoff["revision_history"] = [
        {"revision": "r1", "review_outcome": "accepted_scoped (formula qualification only)",
         "review_note": "negative counts, positive values, disclosure source hashes/pages and the absence of "
                        "an accuracy claim were reproduced independently; five required fixes were returned"},
        {"revision": "r2", "review_outcome": "pending re-review of the five fixes only",
         "generated_at": datetime.now(timezone(timedelta(hours=8))).astimezone(timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")},
    ]
    handoff["commands_executed"] = handoff.get("commands_executed", []) + ["R2-B-rerun", "R2-pack-evidence"]
    handoff["raw_exit_codes"]["R2_B_rerun"] = b_rc
    handoff["expected_exit_codes"]["R2_B_rerun"] = 0
    handoff["qualifications"] = {
        "formula": "review_pending (implementer claim: pass; r1 independent review returned accepted_scoped, "
                   "r2 fixes pending re-review)",
        "disclosure_adaptation": "unmapped",
        "accuracy": "unproven",
    }
    existing = "requires_owner_or_specialist_ruling"
    handoff["open_questions"] = [q for q in handoff.get("open_questions", []) if existing not in q]
    handoff["open_questions"].append(
        "F-M02-01 requires_owner_or_specialist_ruling: should an IGNORED input field still have to satisfy its "
        "domain? Measured on M02: `calculate_registered_model` rejects base_revenue < 0 uniformly before "
        "dispatch for every model, while `_direct_revenue` deletes base_revenue and `_direct_growth` consumes "
        "it. base=999 leaves the output identical; base=-5 raises ModelRegistryError. Options A (keep "
        "fail-closed) / B (ignore unused fields). No product change was made and no position is asserted; the "
        "ruling is reserved for the owner/specialist.")
    handoff["open_questions"].append(
        "F-M01-01 residual gap: the pre-run frozen hash of oracle.md was never captured, so the frozen version "
        "cannot be hash-proven to predate the run; only the mtime sequence and the unmodified frozen body "
        "support it. Recorded in evidence/<card>/first_run_forensics.json (M01) and the review.md r2 section.")
    if card == "M04":
        handoff["open_questions"].append(
            "F-M04-01 was a prose typo only (781,861 -> 780,860.59 wafers/month); the ACTIVE "
            "STOP_DISCLOSURE_ADAPTATION conclusion is unchanged and still needs adjudication.")
    handoff["evidence_paths"] = sorted(set(handoff.get("evidence_paths", []) + [
        "changes.diff", "after/", "recovery/README.md",
        "evidence/%s/revision_r2.json" % card,
        "evidence/%s/source_manifest.json" % card,
    ]))
    if card == "M01":
        handoff["evidence_paths"] = sorted(set(handoff["evidence_paths"] + [
            "evidence/M01/first_run_forensics.json",
            "scripts/oracle_M01.v1.reconstructed.py",
        ]))
    handoff["reviewer_status"] = "pending"
    with open(handoff_path, "w", encoding="utf-8") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)
    print("  refreshed handoff.json")
    print("=== r2 patches done for", card, "===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
