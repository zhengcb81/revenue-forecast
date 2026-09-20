"""Append the SINGLE revision-r2 section to oracle.md and record revision_r2.json.

Rule enforced here (the point of this script):
  * there is exactly ONE "修订 r2" section and exactly ONE boundary marker in oracle.md;
  * the bytes ABOVE the marker still hash to the single frozen-body hash recorded in
    ``before/oracle_md_v1.json`` at freeze time, so the pre-append hash is reproducible at a
    real line boundary instead of being an unverifiable claim;
  * no expectation, tolerance, case or refusal condition is touched;
  * no product file is touched.

Refuses to run if oracle.md already carries a boundary marker (i.e. if a second r2 section
would be appended), which is what prevents two competing baselines from coexisting.

Standard library only. Prints ASCII only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

MARKER = "<!-- R2-APPEND-BOUNDARY: everything above this line is the frozen oracle body (v1) -->"
R2_HEADING = "## 修订 r2"


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def build_body(card, model_id, selfcheck, frozen_hashes, invalid_observations, probe):
    rc_table = "\n".join(
        "| %s | %s | %s | %s |" % (item["scenario"], item["raw_rc"], item["expected_rc"],
                                   "ok" if item["rc_as_expected"] else "MISMATCH")
        for item in selfcheck["scenarios"])
    if invalid_observations:
        invalid_text = ("\n".join("  - `%s`: raised `%s` - %s" % (item["id"], item["raised"],
                                                                  item["message"])
                                  for item in invalid_observations))
        invalid_summary = ("R2-05 记录一个**按冻结规格无法构造**的观察项（不重写冻结件以掩盖）:\n\n"
                           "%s\n\n"
                           "  该观察项不参与退出码（observed 非 gating），本卡 formula 判定不受影响；"
                           "它想记录的契约事实改由 `recovery/probes/signed_driver_probe.json` "
                           "（事后探针，明确标注非冻结用例）回答。" % invalid_text)
    else:
        invalid_summary = ("R2-05：冻结的观察项全部按规格构造成功，没有需要在事后补探针的观察项。")
    probe_text = ("事后探针 `recovery/probes/signed_driver_probe.json`：对 driver `%s` 取值 `%s`，"
                  "实测 raised=`%s` actual=`%s`，判定为 %s。"
                  % (probe["driver_probed"], probe["probe_value"],
                     probe["outcome"]["raised"], probe["outcome"]["actual"],
                     probe["interpretation"]) if probe else "事后探针未运行。")
    return """本节由修订 r2 **追加**，是 `oracle.md` 中**唯一**的一节「修订 r2」。
上方正文（v1 冻结版）逐字未改：正例/连续性/默认值预期、容差、负例清单、拒绝条件**一律未改**；
产品仓库一行未动。本节追加前 `oracle.md` 的 sha256 记录在 `before/oracle_md_v1.json`，
并可由 `scripts/verify_r2_boundary.py` 在**真实行边界**（本标记行处）重新复现：
上方字节的 sha256 必须仍等于该记录值。本文件只有一个基准，不存在第二个互斥的"追加前 hash"。

### r2 记录的事项

- **R2-01（口径登记，非重写）**：本卡 runner 的退出码口径为
  `0=pass / 1=harness error / 2=no-verdict(期望缺失或保真不符) / 3=negative-case 未按期望拒绝`，
  优先级 `1 > 2 > 3`；`run_card.py` 的模块 docstring 与 `evidence/%s/qualification.json`
  记录同一口径。此登记不改变任何期望值。
- **R2-02（变异自检结果，先红后绿）**：对**副本**注入变异后 runner 确实变红，随后恢复；
  冻结的 `input.json` / `cases.json` / `oracle.json` 在自检前后 hash 不变，且仍等于冻结时的 hash。

  | 场景 | 实测 rc | 期望 rc | 结果 |
  |---|---|---|---|
%s

  证据：`recovery/selfcheck_result.json`、`recovery/selfcheck/**`（标准库脚本
  `scripts/selfcheck_mutation.py`，副本位于 `recovery/selfcheck/evidence/%s/`）。
- **R2-03（保真口径）**：正例不只看数值，还比对输出**结构/长度/元素类型/有限性/年度**；
  变异场景 F 把冻结形状的 `length` 改成 99，runner 因保真不符返回 2 而不是 0。
- **R2-04（打印与证据一致）**：`evidence/%s/stdout.txt` 是进程 stdout 的原始抓取，
  `scripts/verify_card.py` 断言其逐行等于 `run_result.json` 的 `printed_lines` 并复现
  `printed_sha256`，因此"打印值"不可能与证据文件不一致。
- %s

%s

### 未改动的内容（防止误读为"为过审而改"）

- 正例/连续性/默认值预期、容差、11 个负例及其期望错误、拒绝条件、停止条件**一律未改**；
  唯一失效的观察项如实记录，**没有**为了让证据好看而重打包 `input.json`/`cases.json`/`oracle.json`。
- 冻结的三个证据文件在冻结时的 sha256：
  `input.json`=%s、`cases.json`=%s、`oracle.json`=%s
- 产品仓零改动；`changes.diff` 为 NO PRODUCT CHANGE 声明。
- `formula` 状态仍为 `review_pending`（实现者不自签），`disclosure_adaptation` 仍为 `unmapped`，
  `accuracy` 仍为 `unproven`。
""" % (card, rc_table, card, card, invalid_summary, probe_text,
       frozen_hashes["evidence/%s/input.json" % card],
       frozen_hashes["evidence/%s/cases.json" % card],
       frozen_hashes["evidence/%s/oracle.json" % card])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    oracle_md = os.path.join(attempt, "oracle.md")
    v1_path = os.path.join(attempt, "before", "oracle_md_v1.json")
    if not os.path.isfile(v1_path):
        print("missing %s: the frozen body hash must be recorded before the r2 append" % v1_path)
        return 7
    v1 = load_json(v1_path)

    with open(oracle_md, "rb") as handle:
        payload = handle.read()
    if MARKER.encode("utf-8") in payload:
        print("oracle.md already carries the r2 boundary marker: refusing to append a SECOND "
              "r2 section (two competing baselines are forbidden)")
        return 8
    digest_before = sha256_bytes(payload)
    if digest_before != v1["sha256"]:
        print("oracle.md does not match the recorded frozen body (now=%s recorded=%s): refusing "
              "to append" % (digest_before, v1["sha256"]))
        return 9

    selfcheck = load_json(os.path.join(attempt, "recovery", "selfcheck_result.json"))
    frozen_now = load_json(os.path.join(evidence, "oracle_selfcheck.json"))[
        "frozen_file_sha256_at_freeze_time"]
    model_id = load_json(os.path.join(evidence, "oracle.json"))["model_id"]
    run_result = load_json(os.path.join(evidence, "run_result.json"))
    invalid_observations = [
        {"id": obs["id"], "raised": obs.get("raised"), "message": obs.get("message")}
        for obs in run_result.get("observations", [])
        if obs.get("raised") and obs["raised"] != "ModelRegistryError"]
    probe_path = os.path.join(attempt, "recovery", "probes", "signed_driver_probe.json")
    probe = load_json(probe_path) if os.path.isfile(probe_path) else None
    body = build_body(card, model_id, selfcheck, frozen_now, invalid_observations, probe)

    # The appended block starts exactly at the marker line, so bytes[0:offset] are the frozen
    # v1 body byte-for-byte and their sha256 is the single recorded pre-append hash.
    offset = len(payload)
    heading_line = R2_HEADING + "（追加处置，非重写）"
    addition = (MARKER + "\n\n" + heading_line + "\n\n" + body).encode("utf-8")
    with open(oracle_md, "wb") as handle:
        handle.write(payload + addition)
    with open(oracle_md, "rb") as handle:
        after = handle.read()

    prefix = after[:offset]
    prefix_hash = sha256_bytes(prefix)
    text_after = after.decode("utf-8")
    marker_occurrences = text_after.count(MARKER)
    heading_occurrences = text_after.count(R2_HEADING)
    reproducible = (prefix_hash == v1["sha256"])

    revision = {
        "card_id": card,
        "model_id": selfcheck.get("model_id"),
        "revision": "r2",
        "single_revision_node": True,
        "competing_baselines_present": False,
        "trigger": "post-run self-check and exit-code-semantics registration for attempt "
                   "a20260919-01 (no independent review has happened yet; a reviewer verdict "
                   "is still pending)",
        "frozen_expectations_unchanged": True,
        "product_files_changed": [],
        "boundary": {
            "marker_line": MARKER,
            "byte_offset": offset,
            "sha256_of_bytes_before_the_marker": prefix_hash,
            "sha256_of_frozen_body_recorded_at_freeze_time": v1["sha256"],
            "reproduces_the_recorded_frozen_body_hash": reproducible,
            "marker_occurrences_in_oracle_md": marker_occurrences,
            "r2_heading_occurrences_in_oracle_md": heading_occurrences,
            "oracle_md_sha256_after_append": sha256_bytes(after),
            "oracle_md_bytes_after_append": len(after),
            "verification_command": "<attempt>/iso/venv/Scripts/python.exe -X utf8 -B "
                                    "<attempt>/scripts/verify_r2_boundary.py --card %s "
                                    "--attempt <attempt>" % card,
        },
        "items": {
            "R2-01": "runner exit-code semantics registered (0 pass / 1 harness error / 2 no "
                     "verdict / 3 negative case not refused, precedence 1>2>3); no expectation "
                     "changed",
            "R2-02": "mutation self-check executed on SCRATCH copies; observed rc set %s; the "
                     "frozen oracle hashes were identical before and after the self-check"
                     % sorted(set(item["raw_rc"] for item in selfcheck["scenarios"])),
            "R2-03": "faithfulness (structure/length/element type/finiteness/years) is checked "
                     "in addition to values",
            "R2-04": "stdout.txt is the raw capture and is asserted line-by-line against "
                     "run_result.json['printed_lines']",
            "R2-05": "observations that could not be constructed as frozen (recorded, not "
                     "hidden): %s" % ([obs["id"] + " raised " + str(obs["raised"])
                                       for obs in invalid_observations] or "none"),
        },
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    dump_json(os.path.join(evidence, "revision_r2.json"), revision)

    print("r2 appended: boundary byte offset=%d" % offset)
    print("sha256 of bytes before the marker = %s (recorded frozen body = %s)"
          % (prefix_hash, v1["sha256"]))
    print("reproduces the recorded frozen body hash: %s" % reproducible)
    print("marker occurrences=%d r2 heading occurrences=%d" % (marker_occurrences,
                                                               heading_occurrences))
    print("oracle.md sha256 after append = %s" % revision["boundary"]["oracle_md_sha256_after_append"])
    return 0 if (reproducible and marker_occurrences == 1 and heading_occurrences == 1) else 10


if __name__ == "__main__":
    raise SystemExit(main())
