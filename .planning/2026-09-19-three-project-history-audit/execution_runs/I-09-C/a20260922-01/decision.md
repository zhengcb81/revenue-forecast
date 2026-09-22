# decision.md — I-09-C / a20260922-01

**本卡不产生新的专业设计决定 → `decision.md` 记 `not_applicable_with_reason`：**

- 跨进程锁与崩溃恢复机制、发布包事务边界、writer/producer 契约变更 —— 均为 I-09-A（设计，accepted_scoped）
  与 I-09-B（实现，accepted_scoped）已裁定范围；本卡是**独立验收**，只测量、不设计、不改产品。
  发现的产品问题退回 I-09-B（见 `handoff.json.carried_findings`），不在本卡修。
- 本卡唯一需要裁决的事项发生在**预检锚点**：`scripts/revenue_forecast.py:55` 锚点
  既 ≠ 卡值也 ≠ 已登记漂移 → 按父指令 STOP；随后由 **parent 裁决 B（proceed-with-disclosure +
  四项硬要求）**解除。裁决全文、四项硬要求的落地、STOP 触发事实留痕均在
  `preflight_anchors.md §4/§6` 与 `binding.json.source_anchor_check.stop_criterion_record`，
  不在本文件重复。该裁决由父 agent 作出，实现者未自行放行。
- 冻结期望（P-C1..P-C5、失败停止条件、关闭标准、I-09-A F1–F12）一字未改；实测与其不符处
  （F12 rc=120；F5 锁未实现不可构造）按原样记为偏差/缺口，不回改 oracle、不重跑到绿。
