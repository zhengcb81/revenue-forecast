## 独立 reviewer session 点复审（裁决）

**结论：`accepted_scoped`（仅 formula 资格）。**
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M04/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示，且本卡另有一处未关闭的停止条件）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。**本卡命中 `STOP_DISCLOSURE_ADAPTATION` 且该停止条件仍然 ACTIVE**：SMIC 只披露**期末**月产能（`94.8 万片/月`），从不披露**年度平均可用产能**。把期末数年化再乘披露利用率 `85.6%` 得 `9,737,856` 片合格产出，对披露已售 `8,021,000` 片 **差 `+1,716,856` 片 = 21.4045%**，**远超运行前冻结的 0.5% 容差**（reviewer 独立复算 `948,000×12=11,376,000`；`×0.856=9,737,856`；隐含可用产能 `8,021,000/0.856=9,370,327.10` 片、月均 `780,860.59` 片 = 期末年化的 `82.3693%`）。该缺口**未解决、未淡化、未回填 `other_revenue` 平账**；`DEC-M04-1` 仍待行业/会计在(a)平均产能披露/(b)经审计爬坡桥/(c)逐发行人 `not_applicable_with_reason` 之间裁定。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）。
- 未授予任何跨公司/跨期间外推；未授予 D/E/F 完成；未授予 `yield=1` 的正当性（`SR-M04-A` 未决：若披露利用率的分母是铭牌产能而非可用产能，则 `yield=1` 高估产出）。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`；**有映射 ≠ 适配通过**。

**独立复算（reviewer 自造输入）**：17 例全部通过。
- `capacity=[1000,1200], utilization=[0.5,0.5], yield=[0.75,0.75], unit_revenue=[4,4], timing_factor=[1.0,0.5], other_revenue=[0,-100]` → `[1500.0, 800.0]`
- defaults：四必填 driver → `[1440.0]`（`timing_factor`=1.0、`other_revenue`=0.0）
- 域下界：`yield=[0.0]` + `other_revenue=[55]` → `[55.0]`；`utilization=[0.0]` → `[0.0]`
- 连续性正例 `capacity=[100,120]` → `[144.0, 172.8]`；断裂 `years=[2027,2029]` → `capacity_utilization.years must be consecutive and increasing`
- 保真：全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`yield=[1.0000001]` / `utilization=[-1e-09]` / 缺 `capacity` / `other_revenue=[-2.0]`（净收入为负）/ `timing_factor=[1.5]`。
- 注册串读回：`revenue = capacity * utilization * yield * unit_revenue * timing_factor + other_revenue`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加**：
- `oracle.md` **无重复章节**；`oracle.json` 可由 `scripts/oracle_M04.py` **逐字节重生成**（`input.json` `a9b3c6cf79ca0fff…`、`oracle.json` `97657e43c311ace8…`、`cases.json` `189d6a37a0b7259a…` 三件 IDENTICAL；脚本自报 `SMIC 年化产出 9737856 vs 披露 8021000，gap 1716856 / 21.4045%`，`隐含可用产能 9370327.10 / 82.3693%`）。
- 预注册值未被改动：`card_M04.md` 的 `期望输出 [730]` = `oracle.json.expected_float [730.0]`；`frozen_tolerance_pct = "0.5"` 与 `verdict = "FAILS the frozen 0.5% tolerance by a wide margin"` 仍在盘上；`oracle.json` mtime 01:21:34 早于 r2/r3 两轮修订。
- `F-M04-01`（印刷笔误 `781,861` → `780,860.59 wafers/month`）已处置：旧值现仅存于叙述性引用（`handoff.json.open_questions` ×1、`review.md` ×2、`revision_r2.json.stale` ×1），**"ACTIVE STOP 结论不变"一并保留**。

**P1（本卡必须处置，否则"当前版本"的 oracle 层无凭据）**：**`oracle.md` 根本没有 r2 追加段，但本文件 `### Frozen expectations were NOT rewritten` 段逐字声称"`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body"。**
- 盘上事实：`oracle.md` = 10,495 B，sha256 `1a69465bf1f12e12122e9596e78faf7028f73fae2f6b3431cb199298d24f7c5c`，mtime **01:21:15**（早于 r2 的 01:45 与 r3 的 02:04），`修订 r2` 出现次数 **0**。
- 根因：共享的 `scripts/apply_r2_patches.py:83` 把 oracle.md 追加写死在 `if card == "M03":` 分支内；四卡该脚本（`965c71fe3c9eb3e10bfa…`）与 `revise_r2.py`（`b0e6295c25069e027de2…`）逐字节相同。
- 处置（见 §11.3，二选一，**不得维持现状**）：① 由实现者在 `oracle.md` 末尾**追加**一节 r2 索引（附追加前字节数与 sha256 `1a69465bf1f1…`/10,495 B，并如实注明"事后补记：r2 轮曾声称已追加但实际未落盘"）；或 ② 把 `review.md` 措辞改为"`oracle.md` **未被修订**，与运行前冻结件逐字节相同"并把 `source_manifest.json` 的 `version`/`note` 改为 `v1_frozen_unamended` / `r2 did NOT append a section to this file`。
- **注意**：`source_manifest.json` 对本卡显示 MATCH，恰恰因为**从未追加**，不能读成"账目更规范"。

**P1（本卡必须处置）**：`handoff.json.evidence_paths` 含 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，**该文件在本卡 attempt 内不存在**（仅 M01 有）；本文件自检段却逐字引用它。处置：补落该文件，或删去该路径并改写自检段。（**缓解**：reviewer 已用同一 harness 独立复现 rc=0/1/2/3 四例全对。）

**九条复审项关闭情况**：`F-M01-01` = 仅 M01 有记录（本卡无 `first_run_forensics.json`）；`F-M01-02` CLOSED（独立复现四例全对）；`F-M01-03` CLOSED；`F-M02-01` CLOSED-AS-RESERVED（仍为 owner 裁定项，未自决，未改产品）；`F-M03-01` = not applicable to this card；**`F-M04-01` CLOSED（笔误已改，ACTIVE STOP 结论未变）**；`NEW-1` not_applicable（M03 only）；`NEW-2` CLOSED；`NEW-3` not_applicable（M01 only）；`NEW-4` CLOSED。

**其余记账发现**：
- **P1**：`handoff.json.revision_history` 4 条真实轮次被记成 6 条（r2/r3 各逐字重复一次）。
- **P2**：`status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M04/qualification.json.formula.status` 仍为 `review_pending`、`not_yet_independently_reviewed=true`。
- **P3**：`revision_r3.json` 自我 sha256 不可复现（其余 hash 声明全部相符）；`revision_r2.review_items` 扫入 `F-M03-01`/`F-M04-01`；`before/`+`after/` 三份文件与其他三卡同拷贝。

**订正要求（由实现者执行；见 §11）**：同上。**特别提醒**：`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动；`STOP_DISCLOSURE_ADAPTATION` 在 `DEC-M04-1` 获行业/会计裁定前**不得**关闭，`review.md` 头部与 `handoff.json.stop_conditions_hit` 的 ACTIVE 表述**不得**删除或弱化。
