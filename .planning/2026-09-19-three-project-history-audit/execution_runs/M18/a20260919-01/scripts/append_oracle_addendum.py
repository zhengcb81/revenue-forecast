"""Append the sanctioned r2 addendum to M17's oracle.md (and prove the boundary rule).

This is the only action in this batch that touches a frozen file, and it is deliberately a
separate, independently recorded command:

  * it refuses to run unless oracle.md's current sha256 equals the declared pre-append hash;
  * it refuses to run if any "revision r2" section already exists (at most ONE is allowed);
  * it APPENDS ONLY - the r1 body above the boundary is not edited by a single byte;
  * it records the byte offset of the appended section's first line, which is a real line
    boundary, and proves that truncating the appended file there reproduces the pre-append hash;
  * it writes evidence/<CARD>/oracle_addendum_record.json and prints every value it records.

Usage:
  python -X utf8 -B append_oracle_addendum.py --card M17 --attempt-root <attempt> \
      --expected-pre-append-sha256 <sha256>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

CARDS = {"M17": "licensing_commercial"}

ADDENDUM = """

## 13. 修订 r2（仅更正描述行，不动任何期望值）

本节由**独立复核结论之后**的一次独立命令追加；该命令的 argv / raw rc / stdout 单独留档在
`evidence/{card}/runs/R2-append-oracle-addendum/`。**上方正文（r1 冻结版）逐字未改**：
正例/连续性/默认值期望、容差、负例清单、拒绝条件、停止条件与 runner 判定口径**一律未改**。

### 更正内容

- **错在何处**：第 1 节「有效域（枚举取得）」一行的来源列指向
  `evidence/{card}/registry_enumeration.json`，但该行把 `milestone_revenue` / `royalty_revenue` /
  `service_revenue` 写成 `[0, inf)`；枚举文件记录的实测值是 `['-inf', 'inf']`，
  即**该行与它自己标注的出处相反**。
- **正确域与源码出处**：这三个金额 driver 属于 `_SIGNED_DRIVERS`（`scripts/model_registry.py:265-269`），
  而 `driver_value_bounds` 对 signed driver 返回 `(-inf, inf)`（同文件 `:289-290`），
  故三个金额项的有效域是 `(-inf, inf)`，**不是**非负域；`treated_units` 与
  `net_revenue_per_unit` 仍为 `[0, inf)`（本卡 NEG-CARD 的成立条件未变）。
- **实测证据**（`evidence/{card}/extra_probes.json`，非判定性探针）：
  `PROBE-NEG-MILESTONE`（`milestone_revenue=[-5]`）实测 `[90.0]`（= 40×2−5+5+10），**被接受**；
  `PROBE-NEG-TOTAL-REVENUE`（`milestone_revenue=[-200]`）实测 `ModelRegistryError`——
  实现里唯一的负值守卫是"总收入不得为负"，单笔负数冲回可静默通过。
- **为何"只在别处登记"不充分**：`oracle.md` 是本卡的规范文件。只在 `oq_rulings.json` /
  `review.md` 登记，会让只读 oracle.md 的读者在 **D 阶段**把 signed 域误当非负域，
  从而误判"负数冲回不可能发生"——而这正是 D 需要判断的那类问题。
- **冻结期望未受影响**：没有任何期望值、容差或判据依赖该描述行，因此本节**不含任何数值变更**。
  追加前 `oracle.md` sha256 = `{pre_hash}`，该值可在**真实行边界**（本节首行 `## 13.` 的字节偏移
  处）截断复现；证明见 `evidence/{card}/oracle_addendum_record.json` 与
  `evidence/{card}/revision_r2.json`。
- **范围限定**：本次更正**只**针对 M17。M18 / M19 / M20 的第 1 节有效域行经复核是正确的，
  不得由本节外推为"四卡都有描述错误"。
"""


def repair_restore(oracle_md: str, record_path: str, dry_run: bool = False) -> int:
    """Undo a VERIFIED append: truncate back to the recorded boundary, hash-checked both ways.

    Purpose (this batch): the first execution of this script appended correctly but computed its
    boundary flag with the wrong comparison, so the unit returned rc=3.  The append itself is
    recorded with a pre-append hash and a boundary offset, and truncating there reproduces the
    pre-append bytes; that makes a byte-exact restore possible instead of hand-editing the file.
    """
    if not os.path.isfile(record_path):
        print("REFUSED: no addendum record at", record_path)
        return 3
    with open(record_path, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    with open(oracle_md, "rb") as handle:
        raw = handle.read()
    if hashlib.sha256(raw).hexdigest() != record["oracle_md_sha256_after_addendum"]:
        print("REFUSED: current oracle.md is not the recorded post-append file")
        return 3
    boundary = record["boundary_byte_offset"]
    truncated = raw[:boundary]
    truncated_hash = hashlib.sha256(truncated).hexdigest()
    if truncated_hash != record["oracle_md_sha256_before_addendum"]:
        print("REFUSED: truncation does not reproduce the recorded pre-append hash")
        return 3
    if dry_run:
        print("WOULD RESTORE (dry run, nothing written)")
        print("boundary_byte_offset:", boundary)
        print("truncated_prefix_sha256:", truncated_hash)
        print("equals recorded pre-append hash: True")
        print("current file equals recorded post-append hash: True")
        print("lossless_round_trip_verified: True")
        return 0
    with open(oracle_md, "wb") as handle:
        handle.write(truncated)
    print("restored oracle.md to the recorded pre-append bytes")
    print("boundary_byte_offset:", boundary)
    print("restored sha256:", truncated_hash)
    print("equals recorded pre-append hash:", truncated_hash == record["oracle_md_sha256_before_addendum"])
    return 0


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def boundary_metadata(appended: bytes, boundary_offset: int):
    """Metadata for the boundary between the r1 body and the appended section.

    P2-C (independent review r2): the boundary offset is the offset of the FIRST APPENDED BYTE, i.e.
    the start of the blank separator line that precedes the appended `## ...` header.  A real line
    boundary therefore means "the byte before it is LF" (the pre-append file ended with a newline);
    it does NOT mean "the offset points at a '## ' heading".  The header's own line number must be
    counted in the RESULTING file, not in the pre-append prefix.
    """
    boundary_is_line_start = boundary_offset == 0 or appended[boundary_offset - 1:boundary_offset] == b"\n"
    tail = appended[boundary_offset:].decode("utf-8")
    header_line = next((line for line in tail.splitlines() if line.startswith("## ")), "")
    if header_line:
        header_bytes = header_line.encode("utf-8")
        header_offset = appended.index(header_bytes, boundary_offset)
        header_line_number = appended[:header_offset].count(b"\n") + 1
    else:
        header_offset = None
        header_line_number = None
    return {
        "added_section_header_line": header_line,
        "added_section_header_byte_offset": header_offset,
        "added_section_header_line_number": header_line_number,
        "boundary_is_a_real_line_boundary": bool(boundary_is_line_start),
        "boundary_semantics": ("boundary_byte_offset is the offset of the FIRST APPENDED BYTE; since "
                               "the pre-append file ended with a newline, that offset is the start of "
                               "the blank separator line preceding the appended section header"),
    }


def rebuild_record_only(oracle_md: str, record_path: str) -> int:
    """Recompute the record's metadata from the CURRENT oracle.md without touching oracle.md.

    P2-C: the append itself was correct (the reviewer verified the round trip independently), only two
    metadata values were wrong.  Fixing metadata must not become a second write to a frozen file.
    """
    if not os.path.isfile(record_path):
        print("REFUSED: no addendum record at", record_path)
        return 3
    with open(record_path, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    with open(oracle_md, "rb") as handle:
        raw = handle.read()
    current = sha256_bytes(raw)
    if current != record["oracle_md_sha256_after_addendum"]:
        print("REFUSED: current oracle.md (%s) is not the recorded post-append file (%s)"
              % (current, record["oracle_md_sha256_after_addendum"]))
        return 3
    boundary = record["boundary_byte_offset"]
    truncated_hash = sha256_bytes(raw[:boundary])
    if truncated_hash != record["oracle_md_sha256_before_addendum"]:
        print("REFUSED: truncation at the recorded boundary does not reproduce the pre-append hash")
        return 3

    old = {k: record.get(k) for k in ("added_section_header_line", "added_section_header_byte_offset",
                                      "added_section_header_line_number",
                                      "boundary_is_a_real_line_boundary")}
    meta = boundary_metadata(raw, boundary)
    record.update(meta)
    record["truncated_prefix_sha256"] = truncated_hash
    record["truncated_prefix_equals_pre_append_hash"] = (truncated_hash
                                                         == record["oracle_md_sha256_before_addendum"])
    record["record_rebuilt_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record["record_rebuilt_reason"] = ("P2-C of the r2 independent review: two metadata values were "
                                       "computed with the wrong comparison / the wrong line-count "
                                       "basis; oracle.md itself was NOT touched by this rebuild")
    record["boundary_metadata_correction"] = {
        "source": "independent review r2, finding P2-C",
        "previous_values": old,
        "corrected_values": {k: record.get(k) for k in old},
        "oracle_md_untouched": True,
        "oracle_md_sha256_now": current,
    }
    record["repair_history"] = (record.get("repair_history") or {})
    record["repair_history"]["original_repair_invocation_recorded"] = False
    record["repair_history"]["original_repair_invocation"] = {
        "argv": ["<attempt venv python>", "-X", "utf8", "-B",
                 os.path.join(os.path.dirname(oracle_md), "scripts", "append_oracle_addendum.py"),
                 "--card", record["card_id"], "--attempt-root", os.path.dirname(oracle_md),
                 "--repair-restore"],
        "observed_raw_rc": 0,
        "capture_status": ("honest_gap: this destructive-on-success invocation was run in the "
                           "interactive session BEFORE the R2 unit became a captured unit, so no "
                           "rc.json/stdout was preserved for it. A safe, non-writing replay is "
                           "recorded as the unit R2b-repair-restore-dry-run."),
        "effect_on_oracle_md": ("truncated oracle.md back to the recorded pre-append bytes; the "
                               "truncated result's sha256 equalled the recorded pre-append hash, and "
                               "the file was then re-appended by the corrected R2 unit"),
    }
    with open(record_path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)

    print("record rebuilt WITHOUT touching oracle.md")
    print("oracle_md_sha256_now:", current, "(unchanged:", True, ")")
    print("boundary_byte_offset:", boundary)
    print("added_section_header_line:", record["added_section_header_line"])
    print("added_section_header_byte_offset:", record["added_section_header_byte_offset"])
    print("added_section_header_line_number:", record["added_section_header_line_number"],
          "(was", old["added_section_header_line_number"], ")")
    print("boundary_is_a_real_line_boundary:", record["boundary_is_a_real_line_boundary"],
          "(was", old["boundary_is_a_real_line_boundary"], ")")
    print("truncated_prefix_equals_pre_append_hash:",
          record["truncated_prefix_equals_pre_append_hash"])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--expected-pre-append-sha256", default=None,
                        help="required unless --repair-restore is used")
    parser.add_argument("--repair-restore", action="store_true",
                        help=("verified undo of a previously recorded append: truncate oracle.md at "
                              "the recorded boundary and check the hash in both directions"))
    parser.add_argument("--dry-run", action="store_true",
                        help=("with --repair-restore: perform every check but write nothing, so the "
                              "lossless round trip can be recorded without touching oracle.md"))
    parser.add_argument("--rebuild-record-only", action="store_true",
                        help=("recompute oracle_addendum_record.json's metadata from the CURRENT "
                              "oracle.md without appending or truncating anything (P2-C fix)"))
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    oracle_md = os.path.join(attempt, "oracle.md")
    evidence = os.path.join(attempt, "evidence", card)

    if args.rebuild_record_only:
        return rebuild_record_only(oracle_md,
                                   os.path.join(evidence, "oracle_addendum_record.json"))

    if args.repair_restore:
        return repair_restore(oracle_md, os.path.join(evidence, "oracle_addendum_record.json"),
                              dry_run=args.dry_run)

    if not args.expected_pre_append_sha256:
        print("REFUSED: --expected-pre-append-sha256 is required for an append")
        return 3

    with open(oracle_md, "rb") as handle:
        raw = handle.read()
    pre_hash = sha256_bytes(raw)
    if pre_hash != args.expected_pre_append_sha256:
        print("REFUSED: oracle.md sha256 %s != declared pre-append hash %s"
              % (pre_hash, args.expected_pre_append_sha256))
        return 3
    text = raw.decode("utf-8")
    existing_r2 = [line for line in text.splitlines() if line.startswith("##") and "r2" in line]
    if existing_r2:
        print("REFUSED: oracle.md already contains an r2 section: %r" % existing_r2)
        return 3
    if not raw.endswith(b"\n"):
        print("REFUSED: oracle.md does not end at a line boundary")
        return 3

    addendum = ADDENDUM.format(card=card, pre_hash=pre_hash).encode("utf-8")
    boundary_offset = len(raw)
    appended = raw + addendum
    with open(oracle_md, "wb") as handle:
        handle.write(appended)

    post_hash = sha256_bytes(appended)
    truncated_prefix = appended[:boundary_offset]
    truncated_hash = sha256_bytes(truncated_prefix)
    meta = boundary_metadata(appended, boundary_offset)
    header_line = meta["added_section_header_line"]
    header_offset = meta["added_section_header_byte_offset"]
    line_number = meta["added_section_header_line_number"]

    record = {
        "card_id": card,
        "model_id": CARDS[card],
        "action": "append-only r2 correction of one descriptive row in section 1",
        "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "oracle_md_path": oracle_md,
        "oracle_md_sha256_before_addendum": pre_hash,
        "oracle_md_sha256_after_addendum": post_hash,
        "declared_pre_append_hash_matched": True,
        "r2_sections_before": 0,
        "r2_sections_after": 1,
        "added_section_header_line": header_line,
        "added_section_header_byte_offset": header_offset,
        "added_section_header_line_number": line_number,
        "boundary_byte_offset": boundary_offset,
        "boundary_is_a_real_line_boundary": meta["boundary_is_a_real_line_boundary"],
        "boundary_semantics": meta["boundary_semantics"],
        "truncated_prefix_sha256": truncated_hash,
        "truncated_prefix_equals_pre_append_hash": truncated_hash == pre_hash,
        "frozen_expectations_unchanged": True,
        "expectation_values_touched": [],
        "repair_history": None,
        "scope_note": ("only M17; the section-1 domain rows of M18/M19/M20 were verified correct and "
                       "are not modified"),
        "product_files_changed": [],
    }
    os.makedirs(evidence, exist_ok=True)
    preserved = os.path.join(evidence, "runs", "R2-append-oracle-addendum",
                             "first_execution_failed")
    if os.path.isfile(os.path.join(preserved, "rc.json")):
        with open(os.path.join(preserved, "rc.json"), "r", encoding="utf-8") as handle:
            failed_rc = json.load(handle)
        record["repair_history"] = {
            "first_execution_raw_rc": failed_rc.get("raw_returncode"),
            "first_execution_stdout": os.path.join(preserved, "stdout.txt"),
            "reason": ("the first execution appended correctly (truncation reproduced the pre-append "
                       "hash) but compared the wrong byte range when computing the line-boundary flag, "
                       "so it returned rc=3; the append was undone with --repair-restore, which "
                       "verifies the current file against the recorded post-append hash and the "
                       "truncated prefix against the recorded pre-append hash, and then this second "
                       "execution re-appended with the corrected comparison"),
            "restore_verified_by_hashes": True,
            "preserved_failure_artifacts": preserved,
        }
    out = os.path.join(evidence, "oracle_addendum_record.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)

    print("oracle_md_sha256_before_addendum:", pre_hash)
    print("oracle_md_sha256_after_addendum:", post_hash)
    print("r2_sections_before: 0 r2_sections_after: 1")
    print("added_section_header_line:", header_line)
    print("added_section_header_byte_offset:", header_offset)
    print("added_section_header_line_number:", line_number)
    print("boundary_byte_offset:", boundary_offset)
    print("boundary_is_a_real_line_boundary:", record["boundary_is_a_real_line_boundary"])
    print("truncated_prefix_equals_pre_append_hash:", record["truncated_prefix_equals_pre_append_hash"])
    print("frozen_expectations_unchanged: True")
    print("record ->", out)
    ok = (record["boundary_is_a_real_line_boundary"]
          and record["truncated_prefix_equals_pre_append_hash"])
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
