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


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--expected-pre-append-sha256", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    oracle_md = os.path.join(attempt, "oracle.md")
    evidence = os.path.join(attempt, "evidence", card)

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
    first_line = appended[boundary_offset:].decode("utf-8").splitlines()[0]
    line_number = appended[:boundary_offset].decode("utf-8").count("\n") + 2  # +1 for the blank line

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
        "added_section_first_line": first_line,
        "added_section_first_line_number": line_number,
        "boundary_byte_offset": boundary_offset,
        "boundary_is_a_real_line_boundary": bool(appended[boundary_offset:boundary_offset + 3] == b"## "),
        "truncated_prefix_sha256": truncated_hash,
        "truncated_prefix_equals_pre_append_hash": truncated_hash == pre_hash,
        "frozen_expectations_unchanged": True,
        "expectation_values_touched": [],
        "scope_note": ("only M17; the section-1 domain rows of M18/M19/M20 were verified correct and "
                       "are not modified"),
        "product_files_changed": [],
    }
    os.makedirs(evidence, exist_ok=True)
    out = os.path.join(evidence, "oracle_addendum_record.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)

    print("oracle_md_sha256_before_addendum:", pre_hash)
    print("oracle_md_sha256_after_addendum:", post_hash)
    print("r2_sections_before: 0 r2_sections_after: 1")
    print("added_section_first_line:", first_line)
    print("added_section_first_line_number:", line_number)
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
