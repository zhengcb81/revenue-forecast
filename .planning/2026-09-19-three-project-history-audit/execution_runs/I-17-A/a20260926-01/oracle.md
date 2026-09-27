# I-17-A 冻结 oracle（a20260926-01）

> **状态：SKELETON（首动作落骨架）→ 待补 sha / 门0 / 变异结果后转 FROZEN**
> 卡：`execution_v2/card_I-17-A.md`（11 行）· 角色：`implementer`（独立观测者）· 复审另派（本工位不自签）

## 0. 运行时（真实时间，不沿用卡文日期）
- 实际运行启动：`2026-09-27T08:27:47+01:00`（`Get-Date` 原始输出见 §5）
- 时区：`GMT Standard Time`（本日 `UTC+01:00`）；账本时间戳为 `+00:00`（UTC）
- 现在 = **2026-09-27（本地 08:2x）**；**日期按实际运行启动**

## 1. 卡文 4 动作判据（逐字，L6-L9 + 退出）
1. 从原历史账本列必须保留的7 daily、2 weekly及monthly等原要求、后继是否获准替代、适用服务承诺；由reviewer签定具体要求清单。不能将所有旧周期盲目复活，也不能因耗时长删除仍有效要求。
2. 为每项填写真实开始时间、到期时间、时区、观察频率、允许中断和失败恢复规则；没有这些字段不开始计时。日期按实际运行启动，不沿用本文日期。
3. 每次记录真实采样和异常，覆盖pause/resume、重复请求与版本一致性；如失败，按事先规则重启该资格窗口，不把中断删掉拼接。
4. 时间未到时保留in_progress；只有用户明确要求后才创建持续监测自动化，当前卡不自动安装任务。
> 退出：每项真实时长与内容足够，或明确仍pending；普通只读功能资格不受未相关自然窗口牵连。

**硬判据派生**
- `F1` 每项必须同时有 `start/due/timezone/frequency/interruption_allowed/recovery_rule/status`，缺 ⇒ **不开始计时**、登记 `pending`（合格）
- `F2` 失败 ⇒ 按事先 `recovery_rule` **重启该资格窗口**，**中断原样保留**、不删不拼
- `F3` 时间未到 ⇒ `in_progress`（不提前判完成）
- `F4` **零任务安装**、**零周期重启**、观察 = **只读采样**，采样只落本目录
- `F5` 不放行参数 · 不自签 · 不派 `I-17-B` · 禁五份计划文件 · 禁 `.planning` 外写 · 禁 git 写 · **禁 `git status`** · 禁联网

## 2. 只读来源（V2-4）+ 历史账本 `sha`
| # | 来源 | sha256 / 说明 |
|---|---|---|
| S1 | `execution_v2/card_I-17-A.md` | `_SHA_CARD_` |
| S2 | `OWNER_DECISIONS.md` §三十八 / §三十九 | `_SHA_OWNERDEC_` |
| S3 | 上游 `execution_runs/I-16-B/a20260926-02/`（`deployment_record.md`·`verification.json`·`handoff.json`） | `_SHA_DR_` / `_SHA_VER_` / `_SHA_HO_` |
| S4 | 历史账本 `assurance/runs/weekly_manifest.json` | `_SHA_WM_` |
| S4b | 历史账本 `assurance/runs/weekly_alert.jsonl` | `_SHA_WA_` |
| S4c | 同目录旁证（同一账本目录内读取，非新增来源）`daily_manifest.json` / `daily_alert.jsonl` / `monthly_manifest.json` / `legacy_periods.json` / `ledger.json` / `rollback_manifest.json` / `slo-fc1303.json` | `_SHA_EXTRA_` |

## 3. 门 0 自探留档（写 / 回读 / 删 —— 原始输出）
`_GATE0_PENDING_`

## 4. 变异计划（≥3，红绿均留 `rc` 原始输出）
`_MUT_PENDING_`

## 5. 原始时间输出
`_TIME_PENDING_`
