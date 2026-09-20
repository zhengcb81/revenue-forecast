"""r3 hygiene patch: remove the last stale values and unify the F-LK2 numbers.

Every replacement is additive in meaning: the new text carries a version note and
points at the measured evidence.  Writes only inside the attempt directory.
"""

from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- decision.md -----------------------------------------------------------

D1_OLD = "| lease 锁等待 | 其所服务相位（acquire ⇒ 请求段；release ⇒ 清理段） | `min(10.0, 相位预算)`；"
D1_NEW = ("| lease 锁等待 | 其所服务相位（acquire ⇒ 请求段；release ⇒ 清理段） | "
          "`lock_budget_for(相位预算) = min(相位预算, 60)`（**v1.3 更正**：此处旧文本写 `min(10.0, …)`，"
          "与 ADR-2 正文 v1.2 的 60 不一致；以 60 为准，见 §14 F-I04C-11/12）；")

D2_OLD = ("| **ADR-10**（新） | \"最后一个参与者 resume\" 在 **owner 已先退出**时不成立：最后退出者不是 owner，"
          "v1 直接不 resume ⇒ worker 永久 paused，而 refcount 已空 | 三条互补规则：")
D2_NEW = ("| **ADR-10**（新，**v1.3 已被 §12 的 R1–R5 取代**：本行的 `released_took_ownership` 动作名与"
          "\"认领周期并写义务\"的做法都已在 r2 删除，见 §12 ADR-10 / ADR-10e） | "
          "\"最后一个参与者 resume\" 在 **owner 已先退出**时不成立：最后退出者不是 owner，"
          "v1 直接不 resume ⇒ worker 永久 paused，而 refcount 已空 | 三条互补规则：")

D3_OLD = ("**因此 v1 的自称\"任何情况下都不留下 paused 且无人有义务\"是错的**")
D3_NEW = ("**因此 v1 的自称\"任何情况下都不留下 paused 且无人有义务\"是错的**（**v1.3 追认**：该自称已在 §12 的 R5 中"
          "正式放弃——R5 允许\"paused 且无可归因义务\"作为 fail-closed 终态，由人工或 wiki 侧证据解除；"
          "\"任何情况下都不留下\"不再是本协议的性质）")

# ---- oracle.md -------------------------------------------------------------

O1_OLD = "- `owner`：`{generation, owner_lease}`；`gen` 单调不减，每次\"从无到有\"的新周期 +1。"
O1_NEW = ("- `owner`：`{generation, owner_lease, pid, boot_uuid, os_start_time}`（v1.3 更正：字段在 r2 扩展）；"
          "`generation` 是**每文件**计数器，每次\"从无到有\"的新周期 +1，文件被收尾删除后下一周期从 1 重新开始"
          "（**不是**全局单调；见 decision.md ADR-12 与 §R2-1、证据 `evidence/run/F-GEN/`）。")

O2_OLD = "| 锁等待 | `min(10, 相位预算)`；"
O2_NEW = ("| 锁等待 | `lock_budget_for(相位预算) = min(相位预算, 60)`（v1.3 更正：旧文本写 `min(10, …)`；"
          "上限常数 60 = OPEN-3，见 decision.md §8 O-3 与 §14）；")

O3_OLD = ("- **无锁对照 F-LK2 的数字是定性的**：同一配置连续 5 次 finals `[3, 15, 9, 2, 186]`，复审独立复跑得 34")
O3_NEW = ("- **无锁对照 F-LK2 的数字是定性的**：同一配置连续 5 次 finals `[16, 35, 10, 56, 18]`"
          "（⇒ lost `[184, 165, 190, 144, 182]`，与 finals 相容；来源 `evidence/lock-and-legacy.txt` 的 F-LK2 记录），"
          "复审独立复跑得 34")


def patch(path, pairs):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    ok = True
    for old, new in pairs:
        if old not in text:
            print(f"MISS in {os.path.basename(path)}: {old[:70]}")
            ok = False
            continue
        text = text.replace(old, new)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"patched {os.path.basename(path)}: ok={ok}")
    return ok


def main():
    ok = patch(os.path.join(ATTEMPT, "decision.md"), [
        (D1_OLD, D1_NEW), (D2_OLD, D2_NEW), (D3_OLD, D3_NEW),
    ])
    ok &= patch(os.path.join(ATTEMPT, "oracle.md"), [
        (O1_OLD, O1_NEW), (O2_OLD, O2_NEW), (O3_OLD, O3_NEW),
    ])
    with open(os.path.join(ATTEMPT, "handoff.json"), "r", encoding="utf-8") as handle:
        json.load(handle)
    print("handoff.json still valid JSON; all_patched =", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
