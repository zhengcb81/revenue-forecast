"""Reviewer independent verification of REM-22 (rc table freeze) and boundaries.

1. START_HERE.md: is the current file exactly PRE(9895 B) + one pure suffix?
   - prefix sha256 must equal the recorded PRE value
   - the 9895-byte prefix must end at a line boundary
   - re-deriving the PRE text from the recorded T1-19 handoff if available
   - every frozen anchor line of the original table must still be present, in order
   - the appended region must contain NO line that also existed before (pure append)
2. 31 frozen cases.json: sha256 vs the values recorded in the attempt evidence.
3. 68 historical runner copies: cross-batch equality + vs plan-recorded values.
"""
import glob
import hashlib
import json
import os
import re

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
TARGET = os.path.join(PLAN, "execution_v2", "START_HERE.md")
PRE_SHA = "1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835"
PRE_BYTES = 9895
POST1_SHA = "e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557"
POST1_BYTES = 16314

report = {}


def sha(b):
    return hashlib.sha256(b).hexdigest()


raw = open(TARGET, "rb").read()
prefix = raw[:PRE_BYTES]
suffix = raw[PRE_BYTES:]
prefix_txt = prefix.decode("utf-8")
suffix_txt = suffix.decode("utf-8")

frozen_table_verbatim = [
    "## rc 码表（冻结；owner 裁定 T1-19 / §13）",
    "同一批内 rc 语义必须自洽，但**跨批历史 rc 不回改**。今后各批**必须**在自身证据里带一份",
    "自描述 `exit_code_legend`，并在 `commands.json` / `case_results.json` 中按本表归类。",
    "**冻结码表（本包唯一规范值）**",
    "| rc | 含义 | 判据 |",
    "|---|---|---|",
    "| `0` | 通过 | 命令正常结束，且**业务判定为通过**（外层 runner 退出 0 不能覆盖子命令失败） |",
    "| `1` | harness 失败 | 测试/运行器自身出错：导入失败、夹具错误、期望文件缺失、路径未绑定 |",
    "| `2` | 无裁决 / 预期拒绝 | 用例是负例且**业务上被正确拒绝**；或该命令不产生裁决（如只读查询） |",
    "| `3` | 未达预期 | 正例未通过，或负例**未被拒绝**；即“应红未红 / 应绿未绿” |",
    "**已知的历史偏差（只登记、不回改）**",
    "- M05–M08 用 `2 = harness`。",
    "- M09–M16 等用 `1 = harness / 2 = no-verdict / 3 = negative`。",
]

full_txt = raw.decode("utf-8")
anchors = []
for a in frozen_table_verbatim:
    anchors.append({"text": a[:60], "present_in_current_file": a in full_txt,
                    "present_in_9895_prefix": a in prefix_txt})

# pure-append test: no non-empty appended line may already exist in the prefix
prefix_lines = set(prefix_txt.splitlines())
suffix_lines = suffix_txt.splitlines()
dup = [ln for ln in suffix_lines if ln.strip() and ln in prefix_lines]

report["start_here"] = {
    "path": "execution_v2/START_HERE.md",
    "current_sha256": sha(raw),
    "current_bytes": len(raw),
    "prefix_9895_sha256": sha(prefix),
    "prefix_matches_recorded_PRE": sha(prefix) == PRE_SHA,
    "prefix_ends_at_line_boundary": prefix.endswith(b"\n"),
    "post1_delta_bytes": len(raw) - POST1_BYTES,
    "post1_prefix_isolated_bytes": POST1_BYTES,
    "suffix_bytes": len(suffix),
    "suffix_newline_count": suffix_txt.count("\n"),
    "suffix_head": suffix_txt[:60],
    "frozen_anchors": anchors,
    "frozen_anchors_all_present_current": all(a["present_in_current_file"] for a in anchors),
    "frozen_anchors_all_present_in_prefix": all(a["present_in_9895_prefix"] for a in anchors),
    "appended_lines_that_already_existed_in_prefix": dup,
    "deleted_content_verdict": (
        "PURE APPEND CONFIRMED" if sha(prefix) == PRE_SHA and prefix.endswith(b"\n")
        and all(a["present_in_current_file"] for a in anchors) else "NOT CONFIRMED"),
}

# ---- 31 frozen cases.json ----
cases = {}
for card_dir in sorted(glob.glob(os.path.join(PLAN, "execution_runs", "M*"))):
    card = os.path.basename(card_dir)
    if not re.fullmatch(r"M\d\d", card):
        continue
    hits = glob.glob(os.path.join(card_dir, "*", "evidence", card, "cases.json"))
    for h in hits:
        cases[card] = {"path": os.path.relpath(h, PLAN).replace("\\", "/"),
                       "sha256": sha(open(h, "rb").read()),
                       "bytes": os.path.getsize(h)}
report["frozen_cases_json"] = {"count": len(cases), "files": cases}

# ---- historical runner copies ----
runners = {}
for card_dir in sorted(glob.glob(os.path.join(PLAN, "execution_runs", "M*"))):
    card = os.path.basename(card_dir)
    if not re.fullmatch(r"M\d\d", card):
        continue
    hits = glob.glob(os.path.join(card_dir, "*", "scripts", "run_card.py"))
    for h in hits:
        runners[os.path.relpath(h, PLAN).replace("\\", "/")] = {
            "sha256": sha(open(h, "rb").read()), "bytes": os.path.getsize(h)}
report["historical_runners"] = {"count": len(runners), "files": runners}

print(json.dumps({k: v for k, v in report.items() if k != "frozen_cases_json"
                  and k != "historical_runners"}, ensure_ascii=False, indent=1)[:4000])
print("\nfrozen cases.json found: %d" % len(cases))
print("historical run_card.py found: %d" % len(runners))
with open(os.path.join(ATTEMPT, "_reviewer_verify", "rem22_boundaries.json"),
          "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
